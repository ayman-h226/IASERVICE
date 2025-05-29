# app/services/price_service.py

import datetime
from sqlalchemy.orm import Session
from fastapi import Depends # Pour l'injection de dépendance si appelé depuis un endpoint

from ..config import (
    COUT_PAR_KM, COUT_PAR_MINUTE,
    PLANCHER, PLAFOND,
    MULT_CREUSE, MULT_STD, MULT_POINTE,
    AJUST_OFFRE_FORTE, AJUST_OFFRE_FAIBLE
)
from ..models.db_models import BanditState # Importer le nouveau modèle
# Supposer que get_db est disponible si appelé depuis un endpoint FastAPI
# from ..database import get_db # Décommenter si nécessaire et si ce service est appelé directement par des routes

# --- NOUVELLES FONCTIONS POUR GERER L'ETAT DU BANDIT EN BDD ---
DEFAULT_ACCEPTANCE_RATE = 0.5
BANDIT_STATE_KEY = "global_acceptance_rate"

def get_bandit_acceptance_rate(db: Session) -> float:
    state = db.query(BanditState).filter(BanditState.state_key == BANDIT_STATE_KEY).first()
    if state:
        return state.state_value
    # Si non trouvé, initialiser avec la valeur par défaut
    initial_state = BanditState(state_key=BANDIT_STATE_KEY, state_value=DEFAULT_ACCEPTANCE_RATE)
    db.add(initial_state)
    db.commit()
    db.refresh(initial_state)
    return initial_state.state_value

def _update_bandit_acceptance_rate_in_db(db: Session, new_rate: float):
    state = db.query(BanditState).filter(BanditState.state_key == BANDIT_STATE_KEY).first()
    if state:
        state.state_value = new_rate
    else:
        # Ce cas ne devrait pas arriver si get_bandit_acceptance_rate est appelé avant
        new_state = BanditState(state_key=BANDIT_STATE_KEY, state_value=new_rate)
        db.add(new_state)
    db.commit()
# --- FIN DES NOUVELLES FONCTIONS POUR LE BANDIT ---

def get_current_tranche() -> float:
    now_h = datetime.datetime.now().hour
    if 0 <= now_h < 8:
        return MULT_CREUSE
    elif 8 <= now_h < 18:
        return MULT_STD
    else:
        return MULT_POINTE

# Modifié pour prendre db en argument
def get_offre_demande_adjustment(db: Session): # Ajout de db: Session
    rate = get_bandit_acceptance_rate(db) # Appel modifié
    if rate > 0.7:
        return AJUST_OFFRE_FORTE
    elif rate < 0.3:
        return AJUST_OFFRE_FAIBLE
    else:
        return 0.0

def calculate_price_for_crowdshipper(
    dist_fixed: float, time_fixed: float,
    dist_var: float, time_var: float,
    taille: str,
    db: Session # Ajout de db: Session pour get_offre_demande_adjustment
) -> float:
    base_fixed = (dist_fixed * COUT_PAR_KM) + (time_fixed * COUT_PAR_MINUTE)
    base_var = (dist_var * COUT_PAR_KM) + (time_var * COUT_PAR_MINUTE)
    cost = base_fixed + base_var

    cost *= get_current_tranche()
    cost *= (1 + get_offre_demande_adjustment(db=db)) # Appel modifié

    if taille in ["XL","XXL"]:
        cost *= 1.10
    elif taille == "XS":
        cost *= 0.95

    cost = max(PLANCHER, min(PLAFOND, cost))
    return round(cost, 2)

# Modifié pour prendre db en argument
def update_price_logic(id_livraison: int, accepte: bool, db: Session): # Ajout de db: Session
    """
    Mise à jour bandit (acceptance_rate).
    """
    current_rate = get_bandit_acceptance_rate(db) # Appel modifié
    if accepte:
        new_rate = min(1.0, current_rate + 0.05)
    else:
        new_rate = max(0.0, current_rate - 0.05)
    _update_bandit_acceptance_rate_in_db(db, new_rate) # Appel modifié