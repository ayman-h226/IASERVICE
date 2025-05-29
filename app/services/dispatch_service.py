# app/services/dispatch_service.py

import math
from typing import List, Tuple # Ajout de Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException # Pour lever une exception

from ..models.db_models import Delivery, Crowdshipper
from ..models.schemas import ProposeResponse # Conserver si la structure de réponse est ok
from ..config import MAX_RADIUS_RELAIS, TOP_CANDIDATES
from .map_service import get_distance_time_gmaps
from .price_service import calculate_price_for_crowdshipper # Non modifié ici, mais price_service l'est

# --- FONCTIONS UTILITAIRES POUR HAVERSINE ET PARSING GPS ---
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371  # Rayon de la Terre en km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    rad_lat1 = math.radians(lat1)
    rad_lat2 = math.radians(lat2)
    a = math.sin(dLat / 2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(dLon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def parse_gps_coordinates(gps_str: str) -> Tuple[float, float] | None:
    try:
        lat, lon = map(float, gps_str.split(","))
        return lat, lon
    except (ValueError, TypeError):
        return None # Retourne None si le parsing échoue
# --- FIN DES FONCTIONS UTILITAIRES ---

def check_capacity(taille_colis: str, taille_capa: str) -> bool:
    order = ["XS","S","M","L","XL","XXL"] # Assurez-vous que cette liste est exhaustive
    try:
        idx_colis = order.index(taille_colis.upper())
        idx_capa = order.index(taille_capa.upper())
        return idx_capa >= idx_colis
    except ValueError:
        # Si une taille n'est pas dans la liste, considérer comme non compatible
        # ou logguer une erreur et retourner False.
        print(f"Warning: Taille inconnue lors de la vérification de capacité: {taille_colis} ou {taille_capa}")
        return False


def filter_crowdshippers(delivery: Delivery, crowdshippers: List[Crowdshipper], db: Session) -> List[int]: # Ajout db pour un éventuel usage futur
    if delivery.distance_km is None or delivery.temps_mn is None:
        # Lever une exception si les données de livraison ne sont pas prêtes
        raise HTTPException(
            status_code=400, # Bad Request
            detail=f"Delivery {delivery.id} is missing pre-calculated distance/time. Please call /update_distance_time first."
        )

    delivery_start_coords = parse_gps_coordinates(delivery.point_depart)
    if not delivery_start_coords:
        raise HTTPException(status_code=400, detail=f"Invalid point_depart GPS format for delivery {delivery.id}.")
    del_lat, del_lon = delivery_start_coords

    # 1. Pré-filtrage Haversine
    haversine_candidates = []
    for c in crowdshippers:
        if not c.disponible:
            continue
        if not check_capacity(delivery.taille, c.capacite_taille):
            continue
        
        crowdshipper_coords = parse_gps_coordinates(c.position_gps)
        if not crowdshipper_coords:
            print(f"Warning: Invalid GPS format for crowdshipper {c.id}. Skipping.")
            continue
        cs_lat, cs_lon = crowdshipper_coords
        
        # Calcul Haversine
        # Augmenter légèrement MAX_RADIUS_RELAIS pour Haversine car c'est une ligne droite
        # Par exemple, 20-50% de plus, à ajuster selon la géographie
        haversine_max_radius = MAX_RADIUS_RELAIS * 1.3 
        dist_h = haversine_distance(cs_lat, cs_lon, del_lat, del_lon)
        
        if dist_h <= haversine_max_radius:
            haversine_candidates.append({'crowdshipper': c, 'haversine_dist': dist_h})
            
    # Trier par distance Haversine
    haversine_candidates.sort(key=lambda x: x['haversine_dist'])
    
    # Sélectionner un sur-ensemble pour les appels Google Maps (ex: TOP_CANDIDATES * 2 ou 3)
    # Limiter aussi à un nombre absolu max pour éviter trop d'appels si beaucoup sont proches
    # Exemple: au moins TOP_CANDIDATES, mais pas plus de 20 (ou TOP_CANDIDATES * 3)
    num_to_gmaps_call = max(TOP_CANDIDATES, min(len(haversine_candidates), TOP_CANDIDATES * 3, 20))
    gmaps_call_candidates = [cand['crowdshipper'] for cand in haversine_candidates[:num_to_gmaps_call]]

    # 2. Calcul Google Maps sur le sous-ensemble réduit
    results_with_gmaps_dist = []
    for c in gmaps_call_candidates:
        # Pas besoin de re-parser c.position_gps si on l'a déjà
        dist_crowd_relais, _ = get_distance_time_gmaps(c.position_gps, delivery.point_depart)
        
        if dist_crowd_relais <= MAX_RADIUS_RELAIS:
            results_with_gmaps_dist.append({'id': c.id, 'gmaps_dist': dist_crowd_relais})

    # Trier par distance Google Maps réelle
    results_with_gmaps_dist.sort(key=lambda x: x['gmaps_dist'])
    
    # Garder le top X final
    final_ids = [r['id'] for r in results_with_gmaps_dist[:TOP_CANDIDATES]]
    return final_ids


def propose_prices(delivery: Delivery, crowdshippers: List[Crowdshipper], db: Session) -> ProposeResponse:
    # On réutilise filter_crowdshippers pour la base
    # filter_crowdshippers a besoin de la session db, donc on la passe
    eligible_ids = filter_crowdshippers(delivery, crowdshippers, db)

    proposals_map = {}
    # Créer un dictionnaire pour un accès rapide aux objets crowdshippers par ID
    crowdshippers_map = {c.id: c for c in crowdshippers}

    for cid in eligible_ids:
        # cship = next((c for c in crowdshippers if c.id == cid), None) # Moins efficace si la liste est grande
        cship = crowdshippers_map.get(cid) # Plus efficace
        if cship:
            dist_cr, time_cr = get_distance_time_gmaps(cship.position_gps, delivery.point_depart)
            price_val = calculate_price_for_crowdshipper(
                delivery.distance_km,
                delivery.temps_mn,
                dist_cr,
                time_cr,
                delivery.taille,
                db=db # Passer la session db ici aussi
            )
            proposals_map[str(cid)] = price_val
        else:
            print(f"Warning: Crowdshipper ID {cid} from eligible_ids not found in a_crowdshippers list for pricing.")


    return ProposeResponse(proposals=proposals_map)

# check_capacity est déplacé plus haut pour être utilisé par filter_crowdshippers