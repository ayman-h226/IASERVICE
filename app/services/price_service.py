import datetime
from ..config import (
    COUT_PAR_KM, COUT_PAR_MINUTE,
    PLANCHER, PLAFOND,
    MULT_CREUSE, MULT_STD, MULT_POINTE,
    AJUST_OFFRE_FORTE, AJUST_OFFRE_FAIBLE
)

# Un "bandit state" simpliste
BANDIT_STATE = {
    "acceptance_rate": 0.5
}

def get_current_tranche() -> float:
    now_h = datetime.datetime.now().hour
    if 0 <= now_h < 8:
        return MULT_CREUSE
    elif 8 <= now_h < 18:
        return MULT_STD
    else:
        return MULT_POINTE

def get_offre_demande_adjustment():
    rate = BANDIT_STATE["acceptance_rate"]
    if rate > 0.7:
        return AJUST_OFFRE_FORTE
    elif rate < 0.3:
        return AJUST_OFFRE_FAIBLE
    else:
        return 0.0

def calculate_price_for_crowdshipper(
    dist_fixed: float, time_fixed: float,
    dist_var: float, time_var: float,
    taille: str
) -> float:
    """
    dist_fixed/time_fixed = partie relais->destination
    dist_var/time_var = partie crowd->relais
    On additionne le coût, puis on applique les multiplicateurs, etc.
    """
    # partie fixe
    base_fixed = (dist_fixed * COUT_PAR_KM) + (time_fixed * COUT_PAR_MINUTE)
    # partie variable
    base_var = (dist_var * COUT_PAR_KM) + (time_var * COUT_PAR_MINUTE)
    cost = base_fixed + base_var

    # horaire
    cost *= get_current_tranche()

    # offre/demande
    cost *= (1 + get_offre_demande_adjustment())

    # ajuster selon taille
    if taille in ["XL","XXL"]:
        cost *= 1.10
    elif taille == "XS":
        cost *= 0.95

    # clamp
    cost = max(PLANCHER, min(PLAFOND, cost))
    return round(cost, 2)

def update_price_logic(id_livraison: int, accepte: bool):
    """
    Mise à jour bandit (acceptance_rate).
    """
    if accepte:
        BANDIT_STATE["acceptance_rate"] = min(1.0, BANDIT_STATE["acceptance_rate"] + 0.05)
    else:
        BANDIT_STATE["acceptance_rate"] = max(0.0, BANDIT_STATE["acceptance_rate"] - 0.05)
