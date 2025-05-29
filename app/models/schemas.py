from pydantic import BaseModel
from typing import Optional, List, Dict

### SCHEMAS DB-LIKE ###

class DeliveryCreate(BaseModel):
    point_depart: str
    point_arrivee: str
    taille: str

class DeliveryDB(BaseModel):
    id: int
    point_depart: str
    point_arrivee: str
    taille: str
    distance_km: Optional[float] = None
    temps_mn: Optional[float] = None

    class Config:
        orm_mode = True

class CrowdshipperCreate(BaseModel):
    position_gps: str
    capacite_taille: str
    disponible: bool = True

class CrowdshipperDB(BaseModel):
    id: int
    position_gps: str
    capacite_taille: str
    disponible: bool

    class Config:
        orm_mode = True

### DISPATCH ###

class DispatchRequest(BaseModel):
    id_livraison: int

class DispatchResponse(BaseModel):
    assignment: List[int]  # liste de crowdshippers éligibles (ids)

class ProposeResponse(BaseModel):
    proposals: Dict[str, float] 
    # ex: { "101": 15.3, "102": 18.0 }

### PRICING ###

class UpdatePricingRequest(BaseModel):
    id_livraison: int
    accepte: bool
