# animated_route.py
import osmnx as ox
import networkx as nx
import folium
from folium.plugins import AntPath, TimestampedGeoJson
from geopy.distance import geodesic
import datetime
import math

# mêmes points que précédemment (à ajuster si besoin)
points = {
    "Rond-Point Victoire": (-4.33787, 15.30553),
    "Gare Centrale": (-4.30122, 15.31827),
    "Place de la Reconstruction": (-4.3748, 15.3456),
    "Gare de Matete": (-4.38845, 15.35275)
}

north, south, east, west = -4.25, -4.40, 15.38, 15.25
G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
G = G.subgraph(max(nx.strongly_connected_components(G), key=len)).copy()

nodes = {name: ox.nearest_nodes(G, lon=lon, lat=lat) for name, (lat, lon) in points.items()}

route = nx.shortest_path(G, nodes["Rond-Point Victoire"], nodes["Gare Centrale"], weight='length')
coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

m = folium.Map(location=[-4.33, 15.32], zoom_start=13)

# AntPath (ligne animée)
AntPath(locations=coords, color='red', weight=6, delay=200).add_to(m)

# Construire un TimestampedGeoJson pour animer un marqueur "véhicule" le long de la route
# On génère un point toutes les N secondes (simulé)
features = []
start_time = datetime.datetime.now()
# vitesse simulée (m/s) pour créer timestamps
speed_m_s = 10.0  # ~36 km/h ; ajuste si tu veux plus lent/rapide

# créer séquence de positions espacées par distance (en mètres) ~ 50m
def interpolate_coords(coords, step_m=50):
    out = []
    for i in range(len(coords)-1):
        (lat1, lon1) = coords[i]
        (lat2, lon2) = coords[i+1]
        # distance approximative (m)
        dist = geodesic((lat1, lon1), (lat2, lon2)).meters
        steps = max(1, int(math.ceil(dist/step_m)))
        for s in range(steps):
            frac = s/steps
            lat = lat1 + (lat2-lat1)*frac
            lon = lon1 + (lon2-lon1)*frac
            out.append((lat, lon, dist * frac))
    out.append((coords[-1][0], coords[-1][1], 0))
    return out

interp = interpolate_coords(coords, step_m=40)

# build GeoJSON features with time
elapsed = 0.0
for i, (lat, lon, _) in enumerate(interp):
    timestamp = (start_time + datetime.timedelta(seconds=int(elapsed))).isoformat()
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "time": timestamp,
            "popup": f"Position {i}",
            "icon": "circle",
            "iconstyle": {"radius": 6}
        }
    }
    features.append(feature)
    # increment elapsed by step distance / speed approx (very rough)
    elapsed += 40.0 / speed_m_s

tgjson = {
    "type": "FeatureCollection",
    "features": features
}

TimestampedGeoJson(
    tgjson,
    period="PT1S",
    add_last_point=True,
    transition_time=200,
    loop=False,
    auto_play=False,
).add_to(m)

m.save("carte_kinshasa_animated.html")
print("Carte animée créée: carte_kinshasa_animated.html")
