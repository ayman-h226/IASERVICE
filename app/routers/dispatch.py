# app/routers/dispatch.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import db_models, schemas # db_models pour les requêtes directes
from ..services.dispatch_service import filter_crowdshippers, propose_prices

router = APIRouter()

@router.post("/assign", response_model=schemas.DispatchResponse)
def assign_livraison(req: schemas.DispatchRequest, db: Session = Depends(get_db)):
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == req.id_livraison).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Récupérer tous les crowdshippers (à optimiser si la liste est énorme)
    # Potentiellement, Spring pourrait fournir une liste pré-filtrée de crowdshippers
    # ou des critères pour un filtre DB plus fin ici.
    all_crowdshippers = db.query(db_models.Crowdshipper).all() 
    
    # filter_crowdshippers a maintenant besoin de db
    assignment = filter_crowdshippers(delivery, all_crowdshippers, db=db) 
    return schemas.DispatchResponse(assignment=assignment)


@router.post("/propose", response_model=schemas.ProposeResponse) # Ajout du response_model
def propose_tarifs(req: schemas.DispatchRequest, db: Session = Depends(get_db)):
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == req.id_livraison).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Idem que pour /assign, récupérer les crowdshippers
    all_crowdshippers = db.query(db_models.Crowdshipper).all()

    # propose_prices a maintenant besoin de db
    proposals = propose_prices(delivery, all_crowdshippers, db=db)
    # La fonction propose_prices retourne déjà un ProposeResponse, donc pas besoin de re-wrapper.
    return proposals