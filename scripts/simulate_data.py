import json
import random

def generate_crowdshippers(n=5):
    res = []
    for i in range(n):
        item = {
            "id_crowdshipper": 100+i,
            "position_gps": f"48.{8500+random.randint(1,200)},2.{3300+random.randint(1,200)}",
            "capacite_taille": random.choice(["S","M","L","XL","XXL"]),
            "disponible": random.choice([True, False])
        }
        res.append(item)
    return res

def generate_deliveries(n=3):
    res = []
    for i in range(n):
        item = {
            "id_livraison": i+1,
            "origine": f"48.{8500+random.randint(1,200)},2.{3300+random.randint(1,200)}",
            "destination": f"48.{8500+random.randint(1,200)},2.{3300+random.randint(1,200)}",
            "taille": random.choice(["S","M","L","XL"])
        }
        res.append(item)
    return res

if __name__ == "__main__":
    cships = generate_crowdshippers(10)
    with open("app/data/crowdshippers.json", "w", encoding="utf-8") as f:
        json.dump(cships, f, indent=2)

    delivs = generate_deliveries(5)
    with open("app/data/deliveries.json", "w", encoding="utf-8") as f:
        json.dump(delivs, f, indent=2)

    print("Simulated data generated.")
