
---

## **README – Crowdshipping AI Module**

Ce projet implémente un **microservice IA** qui gère :

1. **Tarification dynamique**  
   - Propose un prix en fonction de la distance, du contexte d’offre/demande et du taux d’acceptation ou de refus.  
2. **Dispatching intelligent**  
   - Attribue automatiquement des livraisons aux livreurs en fonction de leurs disponibilités et capacités.

Le but est de fournir un **service modulaire** et **facile à intégrer** pour toute application de crowdshipping, notamment un **backend mobile**.

---

## **1. Arborescence du Projet**

```
crowdshipping_ai/
├── app/
│   ├── main.py               # Point d’entrée du serveur FastAPI
│   ├── config.py             # Configuration du projet
│   ├── routers/              # Routes API (pricing, dispatch)
│   ├── services/             # Logique métier (tarification, dispatch)
│   ├── models/               # Modèles de données (Pydantic)
│   ├── data/                 # Données générées (JSON simulé)
│   ├── utils/                # Fonctions utilitaires (BDD…)
│   ├── tests/                # Tests unitaires/intégration
├── scripts/                  # Scripts externes (simulate_data, clean_tests…)
├── train/                    # Scripts d’entraînement de modèles (facultatif)
├── docker/                   # Configuration Docker
├── requirements.txt          # Dépendances du projet
└── README.md                 # Documentation du projet
```

---

## **2. Installation**

### **2.1. Cloner le projet**
```bash
git clone https://github.com/votre-repository/crowdshipping_ai.git
cd crowdshipping_ai
```

### **2.2. Créer et activer l’environnement virtuel**
#### **Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
#### **Windows (CMD)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```
#### **macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### **2.3. Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

## **3. Lancer l'Application**

### **3.1. Démarrer l’API FastAPI**
```bash
uvicorn app.main:app --reload
```
L’API sera accessible sur :  
- **Swagger UI** : [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)  
- **Redoc UI** : [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)  

---

## **4. Endpoints Importants pour le Backend**

L’équipe backend mobile peut **intégrer** ces endpoints pour **interagir** avec le microservice IA.

### **4.1. Endpoint de Tarification Dynamique**

#### **POST** `/pricing/calculate`
- **Description** : Calcule le **prix recommandé** pour une livraison donnée.
- **Body (JSON)** :
  ```json
  {
    "id_livraison": 1,
    "adresse_depart": "Depart-10",
    "adresse_arrivee": "Arrivee-90",
    "distance_km": 15.0,
    "taille": "L"
  }
  ```
- **Réponse (JSON)** :
  ```json
  {
    "id_livraison": 1,
    "distance_km": 15.0,
    "taille": "L",
    "tarif_recommande": 18.75
  }
  ```
  - `tarif_recommande` est le prix calculé par l’algorithme IA.

#### **POST** `/pricing/update`
- **Description** : Met à jour l’algorithme de tarification **après acceptation ou refus** d’une livraison.
- **Paramètres Query** :  
  - `id_livraison` (int)  
  - `accepte` (bool)
- **Exemple** :
  ```
  /pricing/update?id_livraison=1&accepte=true
  ```
- **Réponse (JSON)** :
  ```json
  {
    "status": "updated",
    "id_livraison": 1,
    "accepte": true
  }
  ```
  - Signifie que l’IA a **pris en compte** l’acceptation ou le refus pour ajuster le prix.

---

### **4.2. Endpoint de Dispatching Intelligent**

#### **POST** `/dispatch/assign`
- **Description** : Attribue automatiquement **une ou plusieurs livraisons** à **un ou plusieurs livreurs**.
- **Body (JSON)** :
  ```json
  {
    "livraisons": [
      {
        "id_livraison": 1,
        "adresse_depart": "Point-10",
        "adresse_arrivee": "Point-50",
        "distance_km": 12.3,
        "taille": "XL"
      }
    ],
    "crowdshippers": [
      {
        "id_crowdshipper": 101,
        "moyen_transport": "Voiture",
        "capacité_taille": "XL",
        "disponible": true
      }
    ]
  }
  ```
- **Réponse (JSON)** :
  ```json
  {
    "1": [101]
  }
  ```
  - Signifie que la livraison **ID=1** a été affectée au livreur **101**.  
  - Si la logique permet plusieurs livreurs par livraison, la valeur associée à `1` peut être une **liste**.

---

## **5. Utilisation avec Docker**

### **5.1. Construire l’image Docker**
```bash
docker build -t crowdshipping_ai .
```

### **5.2. Exécuter le conteneur Docker**
```bash
docker run -p 8000:8000 crowdshipping_ai
```
L’API est alors **disponible** sur `http://127.0.0.1:8000`.

---

## **6. Génération de Données Simulées**

Pour **tester** le module IA avec des **données fictives** :
```bash
python scripts/simulate_data.py
```
**Fichiers JSON** générés dans `app/data/` :  
- `livraisons.json` (livraisons fictives)  
- `crowdshippers.json` (livreurs fictifs)  
- `tarification_dynamique.json` (tarifs dynamiques)  
- `assignations.json` (affectations)

Ces données peuvent être **importées** en base de données ou **utilisées pour des tests**.

---

## **7. Lancer les Tests**

### **7.1. Exécuter tous les tests**
```bash
pytest app/tests
```
Cela vérifie **la logique de tarification** et **le dispatching**.

### **7.2. Nettoyer les fichiers temporaires**
```bash
python scripts/clean_tests.py
```
**Supprime** les répertoires `__pycache__` et `.pytest_cache`.

---

## **8. Dépannage & Résolution des Erreurs**

### **8.1. Erreur 500 sur `/dispatch/assign`**
Lance l’API avec `--log-level debug` :
```bash
uvicorn app.main:app --reload --log-level debug
```
Les **logs** afficheront pourquoi l’algorithme de dispatch plante (ex: problème de logique dans le solver OR-Tools).

### **8.2. Vérifier les Imports et l’Environnement Virtuel**
- **Activez** `.venv` si besoin :  
  ```bash
  .venv\Scripts\activate
  ```
- **Réinstallez** éventuellement les dépendances :  
  ```bash
  pip install --force-reinstall -r requirements.txt
  ```

---

## **9. Récapitulatif des Commandes Principales**

| Action                                  | Commande                                              |
|----------------------------------------|-------------------------------------------------------|
| **Créer et activer `venv` (Windows)**  | `python -m venv .venv && .venv\Scripts\Activate.ps1`  |
| **Installer les dépendances**          | `pip install -r requirements.txt`                    |
| **Lancer l’API**                       | `uvicorn app.main:app --reload`                      |
| **Tester l’API**                       | `pytest app/tests`                                    |
| **Nettoyer fichiers temporaires**      | `python scripts/clean_tests.py`                       |
| **Générer des données fictives**       | `python scripts/simulate_data.py`                     |
| **Lancer l’API avec Docker**           | `docker run -p 8000:8000 crowdshipping_ai`            |

---

## **10. À l’Attention de l’Équipe Backend Mobile**

Pour **intégrer** ce microservice IA dans votre **backend** :

1. **Appeler** `/pricing/calculate` pour **obtenir un prix** en temps réel à chaque nouvelle demande de livraison.  
2. **Envoyer** à `/pricing/update` la décision (acceptation/refus) du livreur pour que l’IA s’adapte.  
3. **Utiliser** `/dispatch/assign` dès que vous avez un lot de livraisons et une liste de livreurs disponibles.  
4. **Stocker** éventuellement les résultats dans votre base de données (statuts, prix finaux).  
5. **Superviser** le module IA pour ajuster les **paramètres** de tarification (plafond, plancher) via `app.config.py`.  

Cela vous permettra de **relier** les fonctionnalités IA (tarification et dispatching) à votre **système existant**.

---

## **11. Contact & Support**

Si vous avez des questions ou besoins particuliers :

- **Auteur** : `Votre Nom`  
- **Email** : `votre.email@exemple.com`  
- **GitHub** : [`https://github.com/votre-repository`](https://github.com/votre-repository)

N’hésitez pas à **ouvrir une issue** sur GitHub ou à me **contacter directement** pour toute demande.

---

### 🎯 **Ce README fournit désormais toutes les informations nécessaires** :
- **Installation & lancement**  
- **Endpoints à appeler** pour la **tarification** et le **dispatch**  
- **Commandes Docker & tests**  
- **Points clés** pour l’équipe backend mobile  

🚀 **Bonne implémentation !**
