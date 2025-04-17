from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import db_models, schemas
from ..services.dispatch_service import filter_crowdshippers, propose_prices

router = APIRouter()

@router.post("/assign", response_model=schemas.DispatchResponse)
def assign_livraison(req: schemas.DispatchRequest, db: Session = Depends(get_db)):
    # On récupère la livraison en DB
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == req.id_livraison).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Filtrer crowdshippers
    crowdshippers = db.query(db_models.Crowdshipper).all()
    # renvoie la liste des IDs
    assignment = filter_crowdshippers(delivery, crowdshippers)
    return schemas.DispatchResponse(assignment=assignment)

@router.post("/propose")
def propose_tarifs(req: schemas.DispatchRequest, db: Session = Depends(get_db)):
    # On récupère la livraison
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == req.id_livraison).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # crowdshippers
    crowdshippers = db.query(db_models.Crowdshipper).all()

    proposals = propose_prices(delivery, crowdshippers)
    return proposals  # renvoie un dict du type { "proposals": {"101": 15.2, "102": 13.4} }
