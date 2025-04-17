from fastapi import APIRouter
from ..models.schemas import UpdatePricingRequest
from ..services.price_service import update_price_logic

router = APIRouter()

@router.post("/update")
def update_pricing_logic(req: UpdatePricingRequest):
    """
    Met à jour le bandit manchot selon acceptation / refus
    """
    update_price_logic(req.id_livraison, req.accepte)
    return {
        "status": "updated",
        "id_livraison": req.id_livraison,
        "accepte": req.accepte
    }
