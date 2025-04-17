from sqlalchemy import Column, Integer, String, Float, Boolean
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
