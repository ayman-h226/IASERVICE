# app/models/db_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    point_depart = Column(String, nullable=False)   # "48.853,2.3498"
    point_arrivee = Column(String, nullable=False)  # "48.860,2.3420"
    taille = Column(String, nullable=False)         # "XS","S","M","L","XL"
    distance_km = Column(Float, nullable=True)      # mis à jour après API carto
    temps_mn = Column(Float, nullable=True)         # idem

class Crowdshipper(Base):
    __tablename__ = "crowdshippers"

    id = Column(Integer, primary_key=True, index=True)
    position_gps = Column(String, nullable=False)     # "48.8566,2.3522"
    capacite_taille = Column(String, nullable=False)  # "XS","S","M","L","XL"
    disponible = Column(Boolean, default=True)

# MODÈLE POUR LE BANDIT
class BanditState(Base):
    __tablename__ = "ia_bandit_state"

    state_key = Column(String, primary_key=True, index=True) # ex: "global_acceptance_rate"
    state_value = Column(Float, nullable=False)