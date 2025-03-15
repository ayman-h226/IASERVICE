# Crowdshipping AI Module

Ce projet implémente un **microservice IA** pour la tarification dynamique et le dispatching 
intelligent dans un contexte de crowdshipping.

## Arborescence
crowdshipping_ai/ 
├── app/ 
│   ├── main.py 
│   ├── config.py 
│   ├── routers/
│   ├── services/
│   ├── models/ 
│   ├── data/ 
│   ├── utils/ 
│   └── tests/ 
├── train/ 
├── docker/ 
├── requirements.txt
└── README.md

## Installation

1. Créer un environnement virtuel et l'activer
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'application
   ```bash
   uvicorn app.main:app --reload
   ```

4. Construire l'image Docker
   ```bash
   docker build -t crowdshipping_ai .
   ```

5. Exécuter le conteneur Docker
   ```bash
   docker run -p 8000:8000 crowdshipping_ai
   ```

6. Lancer les tests
   ```bash
   pytest app/tests
   ```


## Nettoyer les fichiers temporaires créés par pytest

Lorsque tu exécutes pytest, il peut générer plusieurs fichiers temporaires et des dossiers `.pytest_cache` et `__pycache__`.

### Solution  : Exécuter une commande manuelle pour nettoyer

Exécute cette commande dans le terminal à la racine du projet :

```bash
find . -type d -name "__pycache__" -exec rm -r {} + && rm -rf .pytest_cache
```

👉 Sous Windows, utilise :

```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force .pytest_cache
```


### Exécuter le script pour generer des data fictive.
```
python scripts/simulate_data.py
```


### Lancer l'api.
```
uvicorn app.main:app --reload
uvicorn app.main:app --reload --root-path .
python -m uvicorn app.main:app --reload

```
