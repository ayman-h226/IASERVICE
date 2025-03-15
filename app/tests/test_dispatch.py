import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_dispatch_single_livraison():
    """Vérifie qu'une livraison est bien assignée à au moins un livreur valide."""
    payload = {
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
                "disponible": True
            },
            {
                "id_crowdshipper": 102,
                "moyen_transport": "Moto",
                "capacité_taille": "XL",
                "disponible": True
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/dispatch/assign", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    
    # La livraison 1 doit être affectée à AU MOINS UN livreur
    assert "1" in result, "La livraison aurait dû être assignée à au moins un livreur."
    assert isinstance(result["1"], list), "Les livreurs doivent être une liste."
    assert len(result["1"]) > 0, "Au moins un livreur aurait dû être assigné."

def test_dispatch_multiple_livraisons():
    """Vérifie que plusieurs livraisons peuvent être assignées à plusieurs livreurs."""
    payload = {
        "livraisons": [
            {
                "id_livraison": 1,
                "adresse_depart": "A",
                "adresse_arrivee": "B",
                "distance_km": 10,
                "taille": "L"
            },
            {
                "id_livraison": 2,
                "adresse_depart": "C",
                "adresse_arrivee": "D",
                "distance_km": 20,
                "taille": "XL"
            }
        ],
        "crowdshippers": [
            {
                "id_crowdshipper": 101,
                "moyen_transport": "Moto",
                "capacité_taille": "L",
                "disponible": True
            },
            {
                "id_crowdshipper": 102,
                "moyen_transport": "Voiture",
                "capacité_taille": "XL",
                "disponible": True
            },
            {
                "id_crowdshipper": 103,
                "moyen_transport": "Camion",
                "capacité_taille": "XL",
                "disponible": True
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/dispatch/assign", json=payload)
    assert response.status_code == 200
    
    result = response.json()

    # Vérifier que chaque livraison a AU MOINS UN livreur assigné
    for id_livraison in ["1", "2"]:
        assert id_livraison in result, f"La livraison {id_livraison} aurait dû être assignée."
        assert isinstance(result[id_livraison], list), "Les livreurs doivent être une liste."
        assert len(result[id_livraison]) > 0, f"Au moins un livreur aurait dû être assigné à la livraison {id_livraison}."

def test_dispatch_no_valid_livreur():
    """Vérifie qu'une livraison sans livreur disponible n'est PAS assignée."""
    payload = {
        "livraisons": [
            {
                "id_livraison": 1,
                "adresse_depart": "X",
                "adresse_arrivee": "Y",
                "distance_km": 15,
                "taille": "XXL"
            }
        ],
        "crowdshippers": [
            {
                "id_crowdshipper": 101,
                "moyen_transport": "Vélo",
                "capacité_taille": "M",
                "disponible": True
            },
            {
                "id_crowdshipper": 102,
                "moyen_transport": "Moto",
                "capacité_taille": "L",
                "disponible": True
            }
        ]
    }
    response = requests.post(f"{BASE_URL}/dispatch/assign", json=payload)
    assert response.status_code == 200
    result = response.json()
    
    # Vérifie que la livraison n'est PAS assignée (aucun livreur valide)
    assert "1" not in result, "Aucun livreur valide ne devait être assigné."
