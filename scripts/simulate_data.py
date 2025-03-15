import os
import json
import random
from datetime import datetime, timedelta

# Répertoires et chemins de sortie
OUTPUT_DIR = os.path.join("app", "data")
FILES = {
    "livraisons": os.path.join(OUTPUT_DIR, "livraisons.json"),
    "crowdshippers": os.path.join(OUTPUT_DIR, "crowdshippers.json"),
    "tarification_dynamique": os.path.join(OUTPUT_DIR, "tarification_dynamique.json"),
    "assignations": os.path.join(OUTPUT_DIR, "assignations.json"),
}

# Vérifie et crée le dossier s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Paramètres de génération
N_LIVRAISONS = 5000
N_CROWDSHIPPERS = 1000

# Logique pour gérer la taille (ordre)
TAILLES = ["M", "L", "XL", "XXL"]
TAILLE_RANK = {"M": 1, "L": 2, "XL": 3, "XXL": 4}

# Transport
MOYENS_TRANSPORT = ["Velo", "Moto", "Voiture", "Camion"]

# Statuts
STATUTS = ["En attente", "En cours", "Livree", "Annulee"]

def generate_livraisons(n=N_LIVRAISONS):
    """
    Génère la table 'livraisons' avec un statut aléatoire.
    """
    livraisons = []
    for i in range(n):
        livraisons.append({
            "id_livraison": i + 1,
            "adresse_depart": f"Depart-{random.randint(1, 500)}",
            "adresse_arrivee": f"Arrivee-{random.randint(501, 1000)}",
            "distance_km": round(random.uniform(1, 50), 2),
            "taille": random.choice(TAILLES),
            "statut": random.choice(STATUTS)
        })
    return livraisons

def generate_crowdshippers(n=N_CROWDSHIPPERS):
    """
    Génère la table 'crowdshippers' (livreurs) avec un moyen de transport,
    une capacité_taille aléatoire et un statut de disponibilité.
    """
    crowdshippers = []
    for i in range(n):
        crowdshippers.append({
            "id_crowdshipper": i + 1,
            "moyen_transport": random.choice(MOYENS_TRANSPORT),
            "capacité_taille": random.choice(TAILLES),
            "disponible": random.choice([True, False])
        })
    return crowdshippers

def can_carry(crowdshipper_taille, colis_taille):
    """
    Vérifie si la capacité_taille du livreur >= taille du colis.
    Exemple : un livreur XL peut transporter M, L ou XL.
    """
    return TAILLE_RANK[crowdshipper_taille] >= TAILLE_RANK[colis_taille]

def generate_tarification_dynamique(livraisons):
    """
    Génère la table 'tarification_dynamique' uniquement pour les livraisons
    dont le statut est 'En attente' ou 'En cours'.
    On suppose qu'on ne génère pas de tarification pour les livraisons 'Livré' ou 'Annulé'.
    """
    results = []
    count_tarif = 0

    for livraison in livraisons:
        if livraison["statut"] in ["En attente", "En cours"]:
            count_tarif += 1
            results.append({
                "id_tarif": count_tarif,
                "id_livraison": livraison["id_livraison"],
                "demande_globale": random.randint(50, 300),  # ex: nombre global de colis en attente
                "nombre_livreurs": random.randint(10, 100),  # ex: livreurs dispos en global
                "prix_initial": round(random.uniform(5, 15), 2),
                "prix_max": round(random.uniform(25, 50), 2),
                "prix_propose": round(random.uniform(10, 40), 2),
                "date_calcul": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
            })

    return results

def generate_assignations(livraisons, crowdshippers):
    """
    Génère la table 'assignations' de manière réaliste:
    - On ne crée d'assignation que si la livraison est 'En attente' ou 'En cours'.
    - Le livreur doit être disponible.
    - La capacité_taille du livreur doit être >= taille du colis.
    - 1 seule assignation par livraison max.
    """
    results = []
    count_assign = 0

    for livraison in livraisons:
        # Ne pas assigner si la livraison est déjà 'Livré' ou 'Annulé'.
        if livraison["statut"] not in ["En attente", "En cours"]:
            continue

        # 70% de chance d'être assignée, sinon on considère qu'elle n'est pas encore prise.
        if random.random() < 0.7:
            # Filtrer les livreurs valides
            livreurs_valides = [
                c for c in crowdshippers
                if c["disponible"] is True and can_carry(c["capacité_taille"], livraison["taille"])
            ]

            if livreurs_valides:
                # On choisit un livreur valide au hasard
                livreur = random.choice(livreurs_valides)
                count_assign += 1

                temps_estime = round(
                    livraison["distance_km"] / random.uniform(20, 40), 2
                )  # ex: vitesse entre 20 et 40 km/h

                results.append({
                    "id_assignation": count_assign,
                    "id_livraison": livraison["id_livraison"],
                    "id_crowdshipper": livreur["id_crowdshipper"],
                    "distance_km": livraison["distance_km"],
                    "temps_estime": temps_estime,
                    "date_assignation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    return results

if __name__ == "__main__":
    print("🚀 Génération de données réalistes en cours...")

    # 1. Générer les données principales
    livraisons = generate_livraisons()
    crowdshippers = generate_crowdshippers()

    # 2. Générer la tarification dynamique (pour livraisons en attente ou en cours)
    tarification_dynamique = generate_tarification_dynamique(livraisons)

    # 3. Générer les assignations (dispatcher les livreurs valides)
    assignations = generate_assignations(livraisons, crowdshippers)

    # 4. Sauvegarder chaque table dans un fichier distinct
    datasets = {
        "livraisons": livraisons,
        "crowdshippers": crowdshippers,
        "tarification_dynamique": tarification_dynamique,
        "assignations": assignations
    }

    for table_name, file_path in FILES.items():
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(datasets[table_name], f, indent=4, ensure_ascii=False)

    print(f"✅ Données générées et sauvegardées dans : {OUTPUT_DIR}")
    print(f"   - livraisons.json : {len(livraisons)} lignes")
    print(f"   - crowdshippers.json : {len(crowdshippers)} lignes")
    print(f"   - tarification_dynamique.json : {len(tarification_dynamique)} lignes")
    print(f"   - assignations.json : {len(assignations)} lignes")
