import random
from app.config import PRIX_MIN, PRIX_MAX

class MultiArmedBandit:
    """
    Implémentation simplifiée d'un bandit manchot pour tarification dynamique.
    """
    def __init__(self, prix_min=PRIX_MIN, prix_max=PRIX_MAX):
        self.prix_min = prix_min
        self.prix_max = prix_max
        self.historique = {}

    def choisir_prix(self, id_livraison: int) -> float:
        """
        Choisit un prix initial ou en cours pour la livraison donnée.
        """
        if id_livraison not in self.historique:
            self.historique[id_livraison] = random.uniform(self.prix_min, self.prix_max)
        return self.historique[id_livraison]

    def mettre_a_jour(self, id_livraison: int, accepte: bool):
        """
        Met à jour le tarif en fonction de l'acceptation ou du refus.
        Stratégie très simplifiée : on diminue si accepté, on augmente si refusé.
        """
        if id_livraison in self.historique:
            if accepte:
                self.historique[id_livraison] *= 0.95
            else:
                self.historique[id_livraison] *= 1.05

# Instance globale
bandit = MultiArmedBandit()
