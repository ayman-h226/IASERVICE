from pydantic import BaseModel

class DeliveryIn(BaseModel):
    id_livraison: int
    adresse_depart: str
    adresse_arrivee: str
    distance_km: float
    taille: str

class DeliveryOut(BaseModel):
    id_livraison: int
    distance_km: float
    taille: str
    tarif_recommande: float

class CrowdshipperIn(BaseModel):
    id_crowdshipper: int
    moyen_transport: str
    capacité_taille: str
    disponible: bool
