import math
from typing import List
from sqlalchemy.orm import Session

from ..models.db_models import Delivery, Crowdshipper
from ..models.schemas import ProposeResponse
from ..config import MAX_RADIUS_RELAIS, TOP_CANDIDATES
from .map_service import get_distance_time_gmaps
from .price_service import calculate_price_for_crowdshipper

def filter_crowdshippers(delivery: Delivery, crowdshippers: List[Crowdshipper]) -> List[int]:
    """
    Retourne la liste d'ID crowdshippers éligibles, triés par distance crowdshipper->relais
    On utilise le param MAX_RADIUS_RELAIS, TOP_CANDIDATES
    """
    if delivery.distance_km is None or delivery.temps_mn is None:
        # On s'attend à ce que delivery ait distance/temps déjà calculé
        pass

    results = []
    for c in crowdshippers:
        if not c.disponible:
            continue
        if not check_capacity(delivery.taille, c.capacite_taille):
            continue

        dist_crowd_relais, _ = get_distance_time_gmaps(c.position_gps, delivery.point_depart)

        if dist_crowd_relais <= MAX_RADIUS_RELAIS:
            # On stocke (id, distance crowd->relais)
            results.append((c.id, dist_crowd_relais))

    # Trier par distance
    results.sort(key=lambda x: x[1])
    # garder le top X
    final_ids = [r[0] for r in results[:TOP_CANDIDATES]]
    return final_ids

def propose_prices(delivery: Delivery, crowdshippers: List[Crowdshipper]) -> ProposeResponse:
    """
    Retourne un mapping => { "proposals": { str(crowd_id): price } }
    Le prix se calcule en combinant la partie "delivery" (relais->destination)
    et la partie "crowdshipper->relais".
    """
    # On réutilise filter_crowdshippers pour la base
    eligible_ids = filter_crowdshippers(delivery, crowdshippers)

    proposals_map = {}
    for cid in eligible_ids:
        cship = next((c for c in crowdshippers if c.id == cid), None)
        if cship:
            # distance/temps crowd->relais
            dist_cr, time_cr = get_distance_time_gmaps(cship.position_gps, delivery.point_depart)
            # partie fixe (delivery.distance_km, delivery.temps_mn)
            # partie variable (dist_cr, time_cr)
            price_val = calculate_price_for_crowdshipper(
                delivery.distance_km,
                delivery.temps_mn,
                dist_cr,
                time_cr,
                delivery.taille
            )
            proposals_map[str(cid)] = price_val

    return ProposeResponse(proposals=proposals_map)

def check_capacity(taille_colis: str, taille_capa: str) -> bool:
    order = ["XS","S","M","L","XL","XXL"]
    try:
        idx_colis = order.index(taille_colis)
        idx_capa = order.index(taille_capa)
        return idx_capa >= idx_colis
    except ValueError:
        return False
