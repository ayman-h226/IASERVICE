import os
from dotenv import load_dotenv

load_dotenv()  # charge .env si présent

# === BASE DE DONNÉES ===
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/postgres")

# === GOOGLE MAPS ===
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyDWY1RgMpjD0o5I_HqIQJARVPmVqRVb4f8")

# === TARIFICATION ===
COUT_PAR_KM = float(os.getenv("COUT_PAR_KM", "1.5"))
COUT_PAR_MINUTE = float(os.getenv("COUT_PAR_MINUTE", "0.2"))

PLANCHER = float(os.getenv("PLANCHER", "5.0"))
PLAFOND = float(os.getenv("PLAFOND", "50.0"))

MULT_CREUSE = float(os.getenv("MULT_CREUSE", "0.9"))
MULT_STD = float(os.getenv("MULT_STD", "1.0"))
MULT_POINTE = float(os.getenv("MULT_POINTE", "1.2"))

AJUST_OFFRE_FORTE = float(os.getenv("AJUST_OFFRE_FORTE", "-0.1"))
AJUST_OFFRE_FAIBLE = float(os.getenv("AJUST_OFFRE_FAIBLE", "0.15"))

MAX_RADIUS_RELAIS = float(os.getenv("MAX_RADIUS_RELAIS", "30.0"))
TOP_CANDIDATES = int(os.getenv("TOP_CANDIDATES", "5"))
