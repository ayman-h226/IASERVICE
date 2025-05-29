# app/routers/pricing.py

from fastapi import APIRouter, Depends # Ajout de Depends
from sqlalchemy.orm import Session # Ajout de Session

from ..models.schemas import UpdatePricingRequest
from ..services.price_service import update_price_logic
from ..database import get_db # Ajout de get_db

router = APIRouter()

@router.post("/update")
def update_pricing_route(req: UpdatePricingRequest, db: Session = Depends(get_db)): # Nom de fonction unique et ajout de db
    """
    Met à jour le bandit manchot selon acceptation / refus
    """
    update_price_logic(req.id_livraison, req.accepte, db=db) # Passer db
    return {
        "status": "updated",
        "id_livraison": req.id_livraison,
        "accepte": req.accepte
    }