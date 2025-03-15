import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.parametrize("distance_km, expected_min, expected_max", [
    (5, 5, 20),   # Courte distance (petit prix attendu)
    (20, 10, 50),  # Distance moyenne (prix modéré)
    (50, 30, 80)   # Longue distance (prix plus élevé)
])
def test_tarification_dynamique(distance_km, expected_min, expected_max):
    """Teste si la tarification dynamique génère des prix cohérents."""
    payload = {
        "id_livraison": 1,
        "adresse_depart": "Depart-10",
        "adresse_arrivee": "Arrivee-90",
        "distance_km": distance_km,
        "taille": "L"
    }
    response = requests.post(f"{BASE_URL}/pricing/calculate", json=payload)
    assert response.status_code == 200
    tarif = response.json()["tarif_recommande"]
    assert expected_min <= tarif <= expected_max, f"Tarif inattendu : {tarif}"

def test_update_tarification():
    """Vérifie si l'algorithme ajuste bien le prix après acceptation/refus."""
    
    # 1. Récupérer le prix initial
    payload = {
        "id_livraison": 1,
        "adresse_depart": "Depart-10",
        "adresse_arrivee": "Arrivee-90",
        "distance_km": 15.0,
        "taille": "L"
    }
    response = requests.post(f"{BASE_URL}/pricing/calculate", json=payload)
    assert response.status_code == 200
    prix_initial = response.json()["tarif_recommande"]

    # 2. Simuler une acceptation
    requests.post(f"{BASE_URL}/pricing/update?id_livraison=1&accepte=true")

    # 3. Récupérer le prix après acceptation
    response = requests.post(f"{BASE_URL}/pricing/calculate", json=payload)
    prix_apres_acceptation = response.json()["tarif_recommande"]
    assert prix_apres_acceptation < prix_initial, "Le prix aurait dû baisser après acceptation."

    # 4. Simuler un refus
    requests.post(f"{BASE_URL}/pricing/update?id_livraison=1&accepte=false")

    # 5. Récupérer le prix après refus
    response = requests.post(f"{BASE_URL}/pricing/calculate", json=payload)
    prix_apres_refus = response.json()["tarif_recommande"]
    assert prix_apres_refus > prix_apres_acceptation, "Le prix aurait dû augmenter après refus."
