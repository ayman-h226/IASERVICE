
---

# IASERVICE – Crowdshipping IA Module

Ce projet fournit un **microservice IA** en Python avec FastAPI pour une application de **crowdshipping**, permettant de :
1.  **Enrichir** les informations d'une livraison avec la distance et le temps de trajet estimés.
2.  **Attribuer** intelligemment des livraisons à des crowdshippers éligibles.
3.  **Calculer** un **prix personnalisé** pour chaque crowdshipper, tenant compte de la distance “crowdshipper → point de départ du colis” et de la distance “point de départ du colis → destination finale”, ainsi que d'autres facteurs dynamiques.

---

## Sommaire

1.  [Contexte et Objectifs](#1-contexte-et-objectifs)
2.  [Modèles et Entités](#2-modèles-et-entités)
3.  [Architecture du Projet](#3-architecture-du-projet)
4.  [Fonctionnalités Clés et Algorithmes](#4-fonctionnalités-clés-et-algorithmes)
    *   4.1 [Mise à Jour des Distances/Temps d’une Livraison](#41-mise-à-jour-des-distancestemps-dune-livraison)
    *   4.2 [Dispatching Intelligent des Crowdshippers](#42-dispatching-intelligent-des-crowdshippers)
    *   4.3 [Tarification Dynamique et Personnalisée avec Bandit Manchot](#43-tarification-dynamique-et-personnalisée-avec-bandit-manchot)
5.  [Flux d’Exécution Typique (Intégration avec un Backend Principal)](#5-flux-dexécution-typique-intégration-avec-un-backend-principal)
6.  [Configuration (Variables d'Environnement)](#6-configuration-variables-denvironnement)
7.  [Installation et Lancement](#7-installation-et-lancement)
8.  [Documentation de l'API (Swagger UI)](#8-documentation-de-lapi-swagger-ui)
9.  [Simulations et Tests Manuels](#9-simulations-et-tests-manuels)
    *   9.1 [Prérequis](#91-prérequis)
    *   9.2 [Exemple de Simulation de Flux Complet](#92-exemple-de-simulation-de-flux-complet)
10. [Docker (Production)](#10-docker-production)
11. [Pistes d'Améliorations Futures](#11-pistes-daméliorations-futures)

---

## 1. Contexte et Objectifs

Le **crowdshipping** s'appuie sur un réseau de livreurs indépendants (crowdshippers). Ce microservice IA vise à optimiser l'attribution des livraisons et la tarification proposée aux crowdshippers. Il prend en compte :
*   La capacité et la disponibilité du livreur.
*   La distance que le livreur doit parcourir pour récupérer le colis (`crowdshipper → point de départ`).
*   La distance du trajet principal de la livraison (`point de départ → destination finale`).
*   Des facteurs dynamiques comme l'heure de la journée et un taux d'acceptation (via un algorithme de bandit manchot).

L'objectif est de proposer une tarification juste et attractive, personnalisée pour chaque situation.

---

## 2. Modèles et Entités

Le service interagit avec une base de données commune (partagée avec le backend principal) contenant les entités suivantes :

### 2.1. **Livraison (`deliveries`)**
*   **id** (int) : Identifiant unique.
*   **point_depart** (str) : Coordonnées GPS du point de récupération du colis (ex. `"48.853,2.3498"`).
*   **point_arrivee** (str) : Coordonnées GPS du point de livraison final.
*   **taille** (str) : Taille du colis (ex. "XS", "S", "M", "L", "XL").
*   **distance_km** (float, *nullable*) : Distance du trajet `point_depart → point_arrivee`, calculée via une API cartographique.
*   **temps_mn** (float, *nullable*) : Temps estimé pour le trajet `point_depart → point_arrivee`.

### 2.2. **Crowdshipper (`crowdshippers`)**
*   **id** (int) : Identifiant unique du crowdshipper.
*   **position_gps** (str) : Position actuelle du crowdshipper.
*   **capacite_taille** (str) : Capacité maximale de transport du crowdshipper (ex. "L", "XL").
*   **disponible** (bool) : Statut de disponibilité du crowdshipper.

### 2.3. **État du Bandit IA (`ia_bandit_state`)**
*   **state_key** (str) : Clé identifiant l'état (ex. `"global_acceptance_rate"`).
*   **state_value** (float) : Valeur de l'état (ex. le taux d'acceptation actuel).
    *Cette table est utilisée par le module IA pour persister l'apprentissage de l'algorithme de tarification dynamique.*

---

## 3. Architecture du Projet

Le projet est structuré comme suit (principaux dossiers et fichiers) :

```
IASERVICE/
├── app/
│   ├── main.py               # Point d’entrée FastAPI, initialisation
│   ├── config.py             # Chargement de la configuration depuis .env
│   ├── database.py           # Configuration de la connexion BDD
│   ├── models/
│   │   ├── db_models.py      # Modèles SQLAlchemy (Delivery, Crowdshipper, BanditState)
│   │   └── schemas.py        # Schémas Pydantic pour la validation API
│   ├── routers/              # Endpoints API (delivery, dispatch, pricing)
│   │   ├── delivery.py
│   │   ├── dispatch.py
│   │   └── pricing.py
│   └── services/             # Logique métier
│       ├── dispatch_service.py # Filtrage des crowdshippers, calcul des propositions
│       ├── map_service.py    # Interaction avec l'API Google Maps
│       └── price_service.py  # Calcul des prix, gestion du bandit manchot
├── docker/
│   └── Dockerfile            # Configuration pour la conteneurisation
├── .env                      # Fichier pour les variables d'environnement (non versionné)
├── .gitignore                # Fichiers à ignorer par Git
├── requirements.txt          # Dépendances Python
└── README.md                 # Cette documentation
```

---

## 4. Fonctionnalités Clés et Algorithmes

### 4.1. Mise à Jour des Distances/Temps d’une Livraison
*   **Endpoint :** `POST /delivery/update_distance_time/{delivery_id}`
*   **Logique :**
    1.  Récupère une livraison existante via son `delivery_id`.
    2.  Appelle une API cartographique externe (Google Maps Directions API) en utilisant `point_depart` et `point_arrivee` de la livraison.
    3.  Met à jour les champs `distance_km` et `temps_mn` de la livraison dans la base de données avec les résultats obtenus.
    *   *Prérequis : La livraison doit exister en base de données.*

### 4.2. Dispatching Intelligent des Crowdshippers
*   **Fonction clé :** `filter_crowdshippers` (utilisée par `/dispatch/propose`)
*   **Logique :**
    1.  **Pré-filtrage Haversine :** Calcule la distance à vol d'oiseau (Haversine) entre chaque crowdshipper disponible et capable, et le `point_depart` de la livraison.
    2.  Sélectionne un sous-ensemble des crowdshippers les plus proches par Haversine (ex: `TOP_CANDIDATES * 2`).
    3.  **Calcul précis :** Pour ce sous-ensemble, calcule la distance routière réelle (`crowdshipper → point_depart`) via l'API Google Maps.
    4.  Filtre à nouveau pour ne garder que ceux dans un rayon défini (`MAX_RADIUS_RELAIS`).
    5.  Trie les candidats finaux par distance routière et retourne les `TOP_CANDIDATES` IDs.
    *   *Prérequis : La livraison doit avoir ses `distance_km` et `temps_mn` (relais->destination) calculés au préalable.*

### 4.3. Tarification Dynamique et Personnalisée avec Bandit Manchot
*   **Endpoint :** `POST /dispatch/propose` (pour obtenir les propositions), `POST /pricing/update` (pour mettre à jour le bandit).
*   **Logique (`propose_prices` et `calculate_price_for_crowdshipper`) :**
    1.  Utilise les crowdshippers éligibles retournés par `filter_crowdshippers`.
    2.  Pour chaque crowdshipper éligible :
        *   Calcule le coût basé sur :
            *   La distance/temps du trajet principal de la livraison (`delivery.distance_km`, `delivery.temps_mn`).
            *   La distance/temps pour que le crowdshipper atteigne le point de départ du colis (calculée via Google Maps).
        *   Applique des multiplicateurs :
            *   Horaire (heures creuses, standard, de pointe).
            *   Ajustement basé sur l'offre/demande (via un taux d'acceptation du bandit manchot).
            *   Ajustement pour la taille du colis.
        *   Applique un prix plancher et plafond.
    3.  **Bandit Manchot :**
        *   L'état du bandit (actuellement un `global_acceptance_rate`) est stocké dans la table `ia_bandit_state` en BDD.
        *   L'endpoint `/pricing/update` est appelé par le backend principal lorsqu'une proposition de prix est acceptée ou refusée par un crowdshipper.
        *   Cela met à jour le `global_acceptance_rate` en BDD, permettant au système d'ajuster les futurs prix pour optimiser le taux d'acceptation.

---

## 5. Flux d’Exécution Typique (Intégration avec un Backend Principal)

Ce module IA est conçu pour être appelé par un backend principal (ex: en Spring Boot) qui gère le flux global de l'application.

1.  **Création de la Livraison (par le Backend Principal) :**
    *   Le backend principal reçoit une nouvelle demande de livraison (via une app mobile/web).
    *   Il crée un enregistrement pour cette livraison dans la base de données commune (table `deliveries`), en renseignant `point_depart`, `point_arrivee`, `taille`. Les champs `distance_km` et `temps_mn` sont initialement `NULL`.
2.  **Enrichissement de la Livraison (appel au Module IA) :**
    *   Le backend principal appelle `POST /delivery/update_distance_time/{delivery_id}` du module IA.
    *   Le module IA calcule la distance et le temps pour le trajet `point_depart → point_arrivee` via Google Maps et met à jour l'enregistrement de la livraison en BDD.
3.  **Obtention des Propositions de Dispatch et Prix (appel au Module IA) :**
    *   Le backend principal appelle `POST /dispatch/propose` du module IA, en fournissant `id_livraison`.
    *   Le module IA :
        *   Récupère la livraison (maintenant enrichie) et les crowdshippers depuis la BDD.
        *   Exécute le dispatching intelligent (Haversine + Google Maps) pour trouver les meilleurs candidats.
        *   Calcule un prix personnalisé pour chaque candidat en utilisant la tarification dynamique et le bandit manchot.
        *   Renvoie une réponse JSON au backend principal avec les propositions (ex: `{"proposals": {"crowd_id_1": price_1, "crowd_id_2": price_2}}`).
4.  **Gestion des Réponses par le Backend Principal :**
    *   Le backend principal présente les propositions aux crowdshippers concernés via les applications.
5.  **Mise à Jour du Bandit (appel au Module IA) :**
    *   Lorsqu'un crowdshipper accepte ou refuse une proposition, le backend principal appelle `POST /pricing/update` du module IA avec `id_livraison` et `accepte: true/false`.
    *   Le module IA met à jour l'état de son bandit manchot (le `global_acceptance_rate`) dans la table `ia_bandit_state` en BDD.

---

## 6. Configuration (Variables d'Environnement)

Le service est configuré via un fichier `.env` à la racine du projet. Un fichier `.env.example` devrait être fourni comme modèle.
Principales variables :
*   `DATABASE_URL`: URL de connexion à la base de données PostgreSQL.
*   `GOOGLE_MAPS_API_KEY`: Clé pour l'API Google Maps Directions.
*   `COUT_PAR_KM`, `COUT_PAR_MINUTE`: Coefficients de base pour la tarification.
*   `PLANCHER`, `PLAFOND`: Bornes du tarif final.
*   `MULT_CREUSE`, `MULT_STD`, `MULT_POINTE`: Multiplicateurs horaires.
*   `AJUST_OFFRE_FORTE`, `AJUST_OFFRE_FAIBLE`: Ajustements pour le bandit.
*   `MAX_RADIUS_RELAIS`: Rayon maximal pour la recherche de crowdshippers (après calcul Google Maps).
*   `TOP_CANDIDATES`: Nombre de meilleurs candidats à retourner.

Ces valeurs sont chargées par `app/config.py`.

---

## 7. Installation et Lancement

### 7.1. Prérequis
*   Python 3.9+
*   PostgreSQL (ou une base de données compatible avec SQLAlchemy)
*   Une clé API Google Maps Directions valide

### 7.2. Installation
1.  Clonez le dépôt :
    ```bash
    git clone https://github.com/ayman-h226/IASERVICE.git
    cd IASERVICE
    ```
2.  Créez un environnement virtuel et activez-le :
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Pour Linux/macOS
    # .\.venv\Scripts\Activate.ps1 # Pour Windows PowerShell
    ```
3.  Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
4.  Créez un fichier `.env` à la racine du projet en vous basant sur `.env.example` (si fourni) et renseignez vos configurations (BDD, clé Google Maps, etc.).

### 7.3. Lancement du Service
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Le service sera accessible sur `http://localhost:8000`.

---

## 8. Documentation de l'API (Swagger UI)

Une fois le service lancé, la documentation interactive de l'API (générée par FastAPI avec Swagger UI) est disponible à l'adresse :
[**http://localhost:8000/docs**](http://localhost:8000/docs)

Vous y trouverez la liste des endpoints, les schémas de requête et de réponse, et vous pourrez même tester les API directement depuis votre navigateur.
Une documentation alternative ReDoc est aussi disponible sur [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 9. Simulations et Tests Manuels

Pour tester le flux manuellement (par exemple avec `curl` ou des outils comme Postman/Insomnia), suivez les étapes du flux d'exécution typique.

### 9.1. Prérequis pour la Simulation
1.  Assurez-vous que le service IA est lancé (`uvicorn app.main:app --reload`).
2.  Assurez-vous que votre base de données est accessible et que les tables (`deliveries`, `crowdshippers`, `ia_bandit_state`) ont été créées (FastAPI le fait au démarrage via `Base.metadata.create_all(bind=engine)`).
3.  **Peuplez manuellement votre base de données** avec au moins :
    *   Une ou plusieurs livraisons dans la table `deliveries` (avec `id`, `point_depart`, `point_arrivee`, `taille` ; laissez `distance_km` et `temps_mn` à `NULL`).
    *   Quelques crowdshippers dans la table `crowdshippers` (avec `id`, `position_gps`, `capacite_taille`, `disponible`).

    *Exemple d'insertion SQL (adaptez à votre client SQL) :*
    ```sql
    -- Insérer une livraison (remplacez les valeurs par les vôtres)
    INSERT INTO deliveries (id, point_depart, point_arrivee, taille) VALUES (1, '48.853,2.3498', '48.860,2.3420', 'M');

    -- Insérer des crowdshippers
    INSERT INTO crowdshippers (id, position_gps, capacite_taille, disponible) VALUES (101, '48.850,2.3450', 'L', true);
    INSERT INTO crowdshippers (id, position_gps, capacite_taille, disponible) VALUES (102, '48.855,2.3550', 'M', true);
    INSERT INTO crowdshippers (id, position_gps, capacite_taille, disponible) VALUES (103, '48.900,2.4000', 'XL', true); -- Plus loin

    -- (Optionnel) Initialiser l'état du bandit si la table est vide
    -- INSERT INTO ia_bandit_state (state_key, state_value) VALUES ('global_acceptance_rate', 0.5);
    -- Le service le fera automatiquement au premier accès si non existant.
    ```

### 9.2. Exemple de Simulation de Flux Complet (avec `curl`)

Supposons que vous avez inséré une livraison avec `id=1`.

**Étape 1 : Mettre à jour distance/temps de la livraison**
```bash
curl -X POST "http://localhost:8000/delivery/update_distance_time/1" -H "accept: application/json"
```
*Vérifiez la réponse. Elle devrait contenir la livraison avec `distance_km` et `temps_mn` remplis.*

**Étape 2 : Obtenir les propositions de dispatch et prix**
```bash
curl -X POST "http://localhost:8000/dispatch/propose" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"id_livraison": 1}'
```
*Analysez la réponse JSON. Elle devrait contenir `{"proposals": {"crowdshipper_id_1": price_1, ...}}`.*

**Étape 3 : Simuler une acceptation pour mettre à jour le bandit**
(Supposons que le crowdshipper `101` a accepté la proposition pour la livraison `1`)
```bash
curl -X POST "http://localhost:8000/pricing/update" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"id_livraison": 1, "accepte": true}'
```
*Vérifiez la réponse de statut. Vous pouvez aussi vérifier en base de données que `ia_bandit_state.state_value` a changé (augmenté légèrement).*

**Étape 4 : Simuler un refus**
```bash
curl -X POST "http://localhost:8000/pricing/update" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"id_livraison": 1, "accepte": false}'
```
*Vérifiez que `ia_bandit_state.state_value` a diminué.*

---

## 10. Docker (Production)

Un `Dockerfile` est fourni pour faciliter la conteneurisation de l'application.

1.  **Construire l'image Docker :**
    (Assurez-vous que votre fichier `.env` est configuré pour la production ou utilisez des variables d'environnement Docker au moment de l'exécution)
    ```bash
    docker build -t iaservice .
    ```
2.  **Exécuter le conteneur Docker :**
    ```bash
    # Exemple simple, en passant les variables d'environnement
    docker run -p 8000:8000 \
           -e DATABASE_URL="postgresql://user:pass@host:port/dbname" \
           -e GOOGLE_MAPS_API_KEY="VOTRE_CLE_ICI" \
           iaservice
    ```
    Pour une utilisation en production, considérez l'utilisation de Gunicorn avec des workers Uvicorn dans le `CMD` du Dockerfile et une gestion plus robuste des secrets.

---

## 11. Pistes d'Améliorations Futures


*   **Tests Automatisés Robustes :** Réintroduire et développer des tests unitaires et d'intégration avec Pytest, utilisant une base de données de test et des mocks pour les API externes.
*   **Sécurité Renforcée :** Implémenter une authentification solide pour les API (ex: OAuth2, API Key via headers sécurisés).
*   **Cache pour Google Maps :** Mettre en place un cache (ex: Redis) pour les résultats de l'API Google Maps afin de réduire les coûts et la latence.
*   **Algorithme de Bandit plus Sophistiqué :** Explorer des bandits contextuels ou des algorithmes comme UCB1 ou Thompson Sampling.
*   **Optimisation des Requêtes BDD :** Pour `db.query(db_models.Crowdshipper).all()`, si le nombre de crowdshippers devient très grand, implémenter un filtrage plus fin au niveau de la requête BDD (ex: basé sur une zone géographique grossière si possible).
*   **Tâches Asynchrones :** Pour les opérations potentiellement longues (comme les appels API externes), utiliser des tâches en arrière-plan (FastAPI BackgroundTasks, Celery) pour ne pas bloquer la réponse.
*   **Monitoring et Observabilité :** Intégrer des outils comme Prometheus et Grafana pour suivre les métriques de performance, les taux d'erreur, et l'efficacité du bandit.

---

