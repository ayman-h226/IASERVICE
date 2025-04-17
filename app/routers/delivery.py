from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import db_models, schemas

from ..services.map_service import get_distance_time_gmaps

router = APIRouter()

@router.post("/create", response_model=schemas.DeliveryDB)
def create_delivery(payload: schemas.DeliveryCreate, db: Session = Depends(get_db)):
    # Créer la livraison dans la DB, initialement distance/temps = null
    new_delivery = db_models.Delivery(
        point_depart=payload.point_depart,
        point_arrivee=payload.point_arrivee,
        taille=payload.taille
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    return new_delivery

@router.post("/update_distance_time/{delivery_id}", response_model=schemas.DeliveryDB)
def update_delivery_distance_time(delivery_id: int, db: Session = Depends(get_db)):
    # Ex: on va appeler l'API Google Maps pour (point_depart -> point_arrivee)
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    dist_km, time_mn = get_distance_time_gmaps(delivery.point_depart, delivery.point_arrivee)
    delivery.distance_km = dist_km
    delivery.temps_mn = time_mn

    db.commit()
    db.refresh(delivery)
    return delivery

@router.get("/{delivery_id}", response_model=schemas.DeliveryDB)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(db_models.Delivery).filter(db_models.Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Not found")
    return delivery
