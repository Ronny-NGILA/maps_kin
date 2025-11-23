# map_with_photos.py
import osmnx as ox
import networkx as nx
import folium
from geopy.distance import geodesic

# -------------------------
# Coordonnées (lat, lon)
# -------------------------
points = {
    "Rond-Point Victoire": (-4.33787, 15.30553),
    "Gare Centrale": (-4.30122, 15.31827),
    "Place de la Reconstruction": (-4.3748, 15.3456),
    "Gare de Matete": (-4.38845, 15.35275)
}

# Exemple d'URLs d'images (Wikimedia Commons) - remplace par tes images si tu veux
images = {
    "Rond-Point Victoire": "https://upload.wikimedia.org/wikipedia/commons/1/11/Place_dite_%22de_la_Victoire%22_%C3%A0_Kinshasa..jpg",
    "Gare Centrale": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Gare_central_de_Kinshasa.jpg",
    "Place de la Reconstruction": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Tour_de_l%27%C3%89changeur.jpg",
    "Gare de Matete": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Matete_-_Kinshasa.jpg/800px-Matete_-_Kinshasa.jpg"
}

# -------------------------
# Charger le graphe OSM (zone autour de Kinshasa)
# Ajuste bbox si nécessaire
# -------------------------
north, south, east, west = -4.25, -4.40, 15.38, 15.25
G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
# garder la plus grande composante
G = G.subgraph(max(nx.strongly_connected_components(G), key=len)).copy()

# -------------------------
# Récupérer les noeuds OSM proches
# -------------------------
nodes = {}
for name, (lat, lon) in points.items():
    nodes[name] = ox.nearest_nodes(G, lon, lat)

# -------------------------
# Trajets (shortest path par longueur)
# -------------------------
main_route = nx.shortest_path(G, nodes["Rond-Point Victoire"], nodes["Gare Centrale"], weight='length')

route_reconstr = (
    nx.shortest_path(G, nodes["Rond-Point Victoire"], nodes["Place de la Reconstruction"], weight='length')
    + nx.shortest_path(G, nodes["Place de la Reconstruction"], nodes["Gare Centrale"], weight='length')[1:]
)

route_matete = (
    nx.shortest_path(G, nodes["Rond-Point Victoire"], nodes["Gare de Matete"], weight='length')
    + nx.shortest_path(G, nodes["Gare de Matete"], nodes["Gare Centrale"], weight='length')[1:]
)

# -------------------------
# Calcul distances (km)
# -------------------------
def route_length_km(route):
    return nx.path_weight(G, route, weight='length') / 1000.0

dist_main = route_length_km(main_route)
dist_reconstr = route_length_km(route_reconstr)
dist_matete = route_length_km(route_matete)
geo_direct = geodesic(points["Rond-Point Victoire"], points["Gare Centrale"]).km

print("Distances (par route):")
print(f" Trajet principal Victoire -> Gare : {dist_main:.2f} km")
print(f" Via Reconstruction : {dist_reconstr:.2f} km")
print(f" Via Matete : {dist_matete:.2f} km")
print(f" Distance à vol d'oiseau : {geo_direct:.2f} km")

# -------------------------
# Distances entre arrêts et gare centrale (géodésiques)
# -------------------------
print("\nDistances entre chaque arrêt et la Gare Centrale (km, géodésique):")
for name, coord in points.items():
    if name == "Gare Centrale":
        continue
    d = geodesic(coord, points["Gare Centrale"]).km
    print(f" {name} -> Gare Centrale : {d:.2f} km")

# -------------------------
# Créer la carte Folium
# -------------------------
m = folium.Map(location=[-4.33, 15.32], zoom_start=13)

# Ajouter marqueurs avec photo dans popup (HTML)
for name, (lat, lon) in points.items():
    img_html = ""
    if name in images:
        img_html = f'<br><img src="{images[name]}" alt="{name}" width="240">'
    popup_html = f"<b>{name}</b><br>Lat: {lat}, Lon: {lon}{img_html}"
    folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=300),
                  tooltip=name).add_to(m)

# Fonction utilitaire pour tracer une route
def add_route(route, color, label):
    coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
    folium.PolyLine(coords, color=color, weight=5, opacity=0.8, tooltip=label).add_to(m)

add_route(main_route, "red", "Trajet principal")
add_route(route_reconstr, "orange", "Via Reconstruction")
add_route(route_matete, "purple", "Via Matete")

# Sauvegarder
out_file = "carte_kinshasa_photos.html"
m.save(out_file)
print(f"\nCarte enregistrée : {out_file}")
