from fastapi import APIRouter, Body
from typing import List
from ..models.delivery_model import DeliveryIn, CrowdshipperIn
from ..services.dispatch_service import dispatch_livreurs

router = APIRouter()

@router.post("/assign")
def assign_deliveries(
    livraisons: List[DeliveryIn] = Body(...),
    crowdshippers: List[CrowdshipperIn] = Body(...)
):
    """
    Endpoint qui effectue le dispatching intelligent.
    Retourne un dictionnaire indiquant quelle livraison est assignée à quel livreur.
    """
    """Affiche ce que FastAPI reçoit"""
    print("Livraisons reçues :", livraisons)
    print("Livreurs reçus :", crowdshippers)
    
    if not livraisons or not crowdshippers:
        raise HTTPException(status_code=400, detail="Les données sont invalides")
    
    assignments = dispatch_livreurs(livraisons, crowdshippers)
    return assignments
