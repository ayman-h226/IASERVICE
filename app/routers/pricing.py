from fastapi import APIRouter, Body
from ..services.price_service import bandit
from ..models.delivery_model import DeliveryIn, DeliveryOut

router = APIRouter()

@router.post("/calculate", response_model=DeliveryOut)
def calculate_price(delivery_in: DeliveryIn = Body(...)):
    """
    Endpoint qui calcule un tarif dynamique pour une livraison.
    """
    # Ex: on utilise distance_km pour moduler
    proposed_price = bandit.choisir_prix(delivery_in.id_livraison)

    # Pour la démo, on ne fait rien d'autre que renvoyer ce prix.
    return DeliveryOut(
        id_livraison=delivery_in.id_livraison,
        distance_km=delivery_in.distance_km,
        taille=delivery_in.taille,
        tarif_recommande=proposed_price
    )

@router.post("/update")
def update_price(id_livraison: int, accepte: bool):
    """
    Endpoint pour mettre à jour le bandit en fonction du retour (accepté/refusé).
    """
    bandit.mettre_a_jour(id_livraison, accepte)
    return {"status": "updated", "id_livraison": id_livraison, "accepte": accepte}
