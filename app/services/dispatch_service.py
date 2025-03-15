from ortools.linear_solver import pywraplp
from typing import List, Dict

def dispatch_livreurs(livraisons: List[dict], crowdshippers: List[dict]) -> Dict:
    """
    Utilise un solveur d'optimisation (ex: OR-Tools) pour assigner plusieurs livreurs à une livraison
    en respectant la compatibilité de la taille et la disponibilité.
    """

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return {"error": "Solver non disponible"}

    x = {}
    # Création des variables de décision (binaire : 1 si assigné, 0 sinon)
    for l in livraisons:
        for c in crowdshippers:
            x[(l["id_livraison"], c["id_crowdshipper"])] = solver.BoolVar(
                f"x_{l['id_livraison']}_{c['id_crowdshipper']}"
            )

    # Contraintes:
    # 1) Un livreur indisponible ne peut être assigné
    for c in crowdshippers:
        if not c["disponible"]:
            for l in livraisons:
                solver.Add(x[(l["id_livraison"], c["id_crowdshipper"])] == 0)

    # 2) Respect de la taille (ex: "L", "M", "XL"...)
    for l in livraisons:
        for c in crowdshippers:
            if c["capacité_taille"] < l["taille"]:  
                # On force la variable à 0 si la capacité est insuffisante
                solver.Add(x[(l["id_livraison"], c["id_crowdshipper"])] == 0)

    # Fonction Objectif: Minimiser la somme des distances
    objective = solver.Sum(
        l["distance_km"] * x[(l["id_livraison"], c["id_crowdshipper"])]
        for l in livraisons for c in crowdshippers
    )
    solver.Minimize(objective)

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return {"error": "Solution non optimale ou solver bloqué"}

    # Récupération des résultats (une livraison peut être assignée à plusieurs livreurs)
    assignment_result = {}
    for l in livraisons:
        assignment_result[l["id_livraison"]] = []  # On initialise une liste vide pour chaque livraison
        for c in crowdshippers:
            if x[(l["id_livraison"], c["id_crowdshipper"])].solution_value() == 1:
                assignment_result[l["id_livraison"]].append(c["id_crowdshipper"])

    return assignment_result
