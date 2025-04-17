
---

# IASERVICE – Crowdshipping IA Module (Version Mise à Jour)

Ce projet fournit un **microservice IA** pour le **crowdshipping**, permettant de :  
1. **Attribuer** intelligemment des livraisons à des crowdshippers.  
2. **Calculer** un **prix personnalisé** tenant compte de la distance “crowdshipper → relais” et de la distance “relais → destination”.

---

## Sommaire

1. [Contexte et Objectifs](#contexte-et-objectifs)  
2. [Modèles et Entités](#modèles-et-entités)  
3. [Architecture du Projet](#architecture-du-projet)  
4. [Algorithmes et Approches](#algorithmes-et-approches)  
   - 4.1 [Mise à jour des Distance/Temps d’une Livraison](#41-mise-à-jour-des-distancetemps-dune-livraison)  
   - 4.2 [Dispatching Intelligent](#42-dispatching-intelligent)  
   - 4.3 [Tarification Dynamique et Personnalisée](#43-tarification-dynamique-et-personnalisée)  
5. [Flux d’Exécution Typique](#flux-dexécution-typique)  
6. [Configuration Globale (config.py)](#configuration-globale-configpy)  
7. [Installation et Lancement](#installation-et-lancement)  
8. [Documentation de lAPI](#documentation-de-lapi)  
   - 8.1 [Exemples d’Appels](#81-exemples-dappels)  
9. [Tests et Qualité](#tests-et-qualité)  
10. [Docker (Production)](#docker-production)  
11. [Conclusion et Pistes Futures](#conclusion-et-pistes-futures)

---

## 1. Contexte et Objectifs

Le **crowdshipping** repose sur un réseau de livreurs dits *indépendants* (crowdshippers). Chaque **nouvelle livraison** doit être attribuée à un ou plusieurs livreurs potentiels, puis un **prix** doit être calculé.  
- **Contrainte** : la plateforme doit prendre en compte la capacité (taille du colis), la disponibilité du livreur et la distance supplémentaire qu’il devra parcourir.  
- **Objectif** : éviter de proposer un même tarif à tous ; la tarification doit refléter la “partie fixe” (relais → destination) et la “partie variable” (crowdshipper → relais).

Le présent microservice gère :  
1. **L’enrichissement** d’une livraison avec `distance_km` et `temps_mn` (relais→destination) après un **appel carto**.  
2. **Le dispatch** (filtrage et sélection) des crowdshippers proches du relais et aptes à transporter le colis.  
3. **La tarification dynamique**, personnalisée pour chaque crowdshipper, en prenant en compte l’heure, le taux d’acceptation (bandit), etc.

---

## 2. Modèles et Entités

### 2.1. **Livraison**
- **id** (int) : identifiant unique.  
- **point_depart** (point relais) : coordonnées GPS (ex. `"48.853,2.3498"`) ou un code.  
- **point_arrivee** (lieu de livraison) : coordonnées GPS (ex. `"48.860,2.3420"`).  
- **taille** (str) : XS, S, M, L, XL, …  
- **distance_km** (float, *initialement null*) : la distance entre (point_depart → point_arrivee), renseignée après l’appel à l’API de cartographie.  
- **temps_mn** (float, *initialement null*) : le temps estimé pour (relais → destination).

### 2.2. **Crowdshipper**
- **id_crowdshipper** (int).  
- **position_gps** (str) : `"lat,long"`.  
- **capacite_taille** (str) : ex. “L”, “XL”, “XXL”.  
- **disponible** (bool) : livreur connecté ou non.

---

## 3. Architecture du Projet

```
IASERVICE/
├── app/
│   ├── main.py               # Point d’entrée FastAPI
│   ├── config.py             # Config globale (tarifs, etc.)
│   ├── routers/              # Routes API (pricing, dispatch, propose...)
│   ├── services/             # Logique métier (tarification, dispatch, etc.)
│   ├── models/               # Schémas Pydantic
│   ├── data/                 # Données JSON (simulation)
│   ├── utils/                # Fonctions utilitaires
│   ├── tests/                # Tests
├── scripts/                  # Scripts externes (simulate_data…)
├── docker/                   # Dockerfile
├── requirements.txt          # Dépendances
└── README.md                 # Documentation
```

Les **routes** sont regroupées dans `app/routers/`, la **logique** dans `services/`, et la **configuration** (coûts, multiplicateurs, etc.) se trouve dans `config.py`.

---

## 4. Algorithmes et Approches

### 4.1. Mise à jour des Distance/Temps d’une Livraison

Lorsque l’on crée ou reçoit une **nouvelle livraison**, on initialise `distance_km = null` et `temps_mn = null`.  
Ensuite :  
1. **Appel** à l’API carto pour `(point_depart → point_arrivee)`.  
2. **Récupération** de `distance_km` et `temps_mn` (tenant compte du trafic si possible).  
3. **Mise à jour** de la livraison.  

Cette distance/temps correspond à la “**partie fixe**” du trajet, commune à tous les livreurs.

### 4.2. Dispatching Intelligent

1. **Filtre** des crowdshippers :  
   - **Capacité** : le livreur peut-il transporter la taille demandée ?  
   - **Disponibilité** : booléen.  
2. **Calcul** de la distance (crowdshipper → relais) pour chacun.  
   - On peut faire un second appel carto, ou utiliser un calcul haversine simplifié.  
   - Seuls ceux qui sont sous un certain rayon (ex. `MAX_RADIUS_RELAIS=30 km`) ou top N plus proches sont retenus.  
3. **Résultat** : on obtient la **liste** des crowdshippers “éligibles” pour la livraison.

### 4.3. Tarification Dynamique et Personnalisée

Une fois qu’on a la liste `[c1, c2, …]`, on veut un **prix** pour chacun. L’idée est de distinguer :  
- **Partie fixe** : distance/temps du relais → destination (déjà stocké dans la livraison).  
- **Partie variable** : distance/temps du crowdshipper → relais.  

On peut alors utiliser la formule :

\[
\text{Prix total} = \text{tarifPartieFixe}(distance_{\text{relais→dest}}) + \text{tarifPartieVar}(distance_{\text{crowdshipper→relais}})
\]

puis appliquer :  
- **Multiplicateurs horaires** (creuse, standard, pointe).  
- **Ajustement** offre/demande (ex. bandit manchot).  
- **Plafond / plancher**.

De plus, un **bandit manchot** (simple) est mis à jour via un endpoint `POST /pricing/update` :  
- **accepte = true** => on augmente un peu le taux d’acceptation.  
- **accepte = false** => on le diminue.  

Le prix s’adapte donc au fur et à mesure des retours de la plateforme (acceptations/refus).

---

## 5. Flux d’Exécution Typique

1. **Création de la livraison** :  
   - Données : `(id, point_depart, point_arrivee, taille, distance_km=null, temps_mn=null)`.  
2. **Appel carto** pour remplir `distance_km, temps_mn` entre `point_depart` (relais) et `point_arrivee` (destination).  
3. **Dispatch** :  
   - Récupération des crowdshippers potentiels (ex. en BDD, en JSON).  
   - Filtre par capacité, disponibilité.  
   - Calcul distance `crowdshipper → relais`.  
   - Sélection du top N (ou < MAX_RADIUS_RELAIS).  
4. **Tarification personnalisée** :  
   - Pour chaque crowdshipper restant, on fait :  
     \[
     \text{prix} = f(\text{distance\_livraison}, \text{temps\_livraison}) 
                  + g(\text{distance\_crowd→relais}, \text{temps\_crowd→relais})
     \]  
   - Ajustements horaires, bandit, etc.  
   - On renvoie une liste JSON du style :  
     ```json
     {
       "id_livraison": 42,
       "crowdshippers": [
         { "id_crowdshipper": 101, "prix_personnalise": 15.0 },
         { "id_crowdshipper": 102, "prix_personnalise": 13.5 }
       ]
     }
     ```
5. **Acceptation ou refus** :  
   - L’application (mobile ou web) signale via `/pricing/update` si c’est accepté ou refusé, pour affiner la stratégie de prix (bandit).  
6. **Réassignation** :  
   - Si le crowdshipper annule, on peut relancer le flux (dispatch, tarification) pour trouver un remplaçant.

---

## 6. Configuration Globale (config.py)

Les **paramètres** suivants sont chargés depuis des variables d’environnement ou valeurs par défaut :

- **COUT_PAR_KM**, **COUT_PAR_MINUTE** : coefficients de base pour distance/temps.  
- **PLANCHER**, **PLAFOND** : bornes du tarif final.  
- **MULT_CREUSE**, **MULT_STD**, **MULT_POINTE** : multiplicateurs horaires.  
- **AJUST_OFFRE_FORTE**, **AJUST_OFFRE_FAIBLE** : ajustements si beaucoup/pas assez de livreurs.  
- **MAX_RADIUS_RELAIS**, **TOP_CANDIDATES** : règles pour le dispatch (distance max, top N).

Exemple :
```python
COUT_PAR_KM = 1.5
COUT_PAR_MINUTE = 0.2
PLANCHER = 5.0
PLAFOND = 50.0
MULT_CREUSE = 0.9
MULT_STD = 1.0
MULT_POINTE = 1.2
AJUST_OFFRE_FORTE = -0.1
AJUST_OFFRE_FAIBLE = 0.15
MAX_RADIUS_RELAIS = 30.0
TOP_CANDIDATES = 5
```

---

## 7. Installation et Lancement

### 7.1. Cloner le projet et installer

```bash
git clone <repo>
cd IASERVICE
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

*(Sous Windows PowerShell: `.\.venv\Scripts\Activate.ps1`.)*

### 7.2. Lancer l’API

```bash
uvicorn app.main:app --reload
```
Accès via [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 8. Documentation de l’API

### 8.1. Exemples d’Appels

1. `POST /dispatch/assign`  
   - **But** : filtrer et sélectionner les crowdshippers éligibles pour une livraison donnée (déjà enrichie avec distance/temps).  
   - **Body** (exemple) :  
     ```json
     {
       "livraisons": [
         {
           "id_livraison": 1,
           "origine": "48.8530,2.3498",
           "destination": "48.8600,2.3420",
           "taille": "L",
           "distance_km": 5.0,
           "temps_mn": 12
         }
       ],
       "crowdshippers": [
         {
           "id_crowdshipper": 101,
           "position_gps": "48.8566,2.3522",
           "capacite_taille": "XL",
           "disponible": true
         }
       ]
     }
     ```
   - **Sortie** :  
     ```json
     {
       "assignment": {
         "1": [101]
       }
     }
     ```

2. `POST /dispatch/propose`  
   - **But** : idem que `/assign`, mais **calcul** en plus un **prix personnalisé** pour chaque crowdshipper (en considérant *crowdshipper→relais* + la partie “livraison”).  
   - **Sortie** (exemple) :  
     ```json
     {
       "proposals": {
         "1": [
           {
             "id_crowdshipper": 101,
             "price": 15.0
           },
           {
             "id_crowdshipper": 102,
             "price": 13.5
           }
         ]
       }
     }
     ```

3. `POST /pricing/update`  
   - **But** : informer l’algorithme (bandit) qu’une offre a été acceptée ou refusée.  
   - **Body** :  
     ```json
     {
       "id_livraison": 1,
       "accepte": true
     }
     ```
   - **Sortie** :  
     ```json
     {
       "status": "updated",
       "id_livraison": 1,
       "accepte": true
     }
     ```

*(On peut également avoir `POST /pricing/calculate` pour un calcul direct de prix, mais dans le flux complet, on préfère passer par la route de proposition après dispatch.)*

---

## 9. Tests et Qualité

- **Pytest** : tous les tests (unitaires et d’intégration) se trouvent dans `app/tests/`.  
- Lancement :

```bash
pytest app/tests
```

- Nettoyage des caches de test :

```bash
python scripts/clean_tests.py
```

---

## 10. Docker (Production)

1. **Construire l’image** :

```bash
docker build -t iaservice .
```

2. **Exécuter** le conteneur :

```bash
docker run -p 8000:8000 iaservice
```

3. L’API sera accessible sur `http://127.0.0.1:8000`.

Pour un déploiement **kubernetes**, on peut créer un **Deployment** faisant référence à cette image et un **Service** exposant le port 8000.

---

## 11. Conclusion et Pistes Futures

Ce microservice IA fournit un **flux complet** pour :  
1. **Enrichir** la livraison en lui associant la distance/temps *relais → destination*.  
2. **Identifier** les crowdshippers capables et proches du relais.  
3. **Calculer** pour chacun un **prix personnalisé** en intégrant leur distance “crowdshipper → relais” (partie variable) et la distance “relais → destination” (partie fixe).  
4. **Mettre à jour** un bandit manchot via les retours d’acceptation ou refus.

**Évolutions** envisageables :  
- Intégration d’une **BD** (PostgreSQL, Redis) pour stocker l’historique.  
- Passage à un **Vehicle Routing Problem** plus complet (OR-Tools) si on veut assigner plusieurs livraisons à plusieurs crowdshippers de façon globale.  
- **Sécurité** (JWT / OAuth2) pour restreindre l’accès aux endpoints.  
- **Monitoring** (Prometheus, Grafana) pour suivre le taux d’acceptation, le temps de réponse, etc.

**Fin du README**.