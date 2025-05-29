import googlemaps
from datetime import datetime
from ..config import GOOGLE_MAPS_API_KEY

# Initialisation globale (on crée le client si la clé existe)
gmaps_client = None
if GOOGLE_MAPS_API_KEY:
    try:
        gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du client Google Maps : {e}")
        gmaps_client = None

def get_distance_time_gmaps(origin: str, destination: str) -> (float, float):
    """
    Calcule distance & durée (en km et minutes) via Google Maps Directions API.
    origin et destination: "lat,long" (ex: "48.8566,2.3522").
    Renvoie (distance_km, temps_mn) en float.
    """
    if not gmaps_client:
        # Si la clé n'est pas dispo ou invalid
        return (9999.0, 9999.0)

    try:
        lat_o, lon_o = map(float, origin.split(","))
        lat_d, lon_d = map(float, destination.split(","))
    except:
        # Erreur de parsing
        return (9999.0, 9999.0)

    now = datetime.now()
    try:
        directions_result = gmaps_client.directions(
            (lat_o, lon_o),
            (lat_d, lon_d),
            mode="driving",
            departure_time=now
        )
        if not directions_result:
            return (9999.0, 9999.0)

        route = directions_result[0]
        leg = route["legs"][0]
        
        dist_meters = leg["distance"]["value"]      # ex: 12345
        duration_seconds = leg["duration"]["value"] # ex: 2345

        dist_km = dist_meters / 1000.0
        time_mn = duration_seconds / 60.0
        return (round(dist_km, 2), round(time_mn, 2))

    except Exception as e:
        print(f"Erreur lors de l'appel Google Maps: {e}")
        return (9999.0, 9999.0)
