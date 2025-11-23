from flask import Flask, render_template, jsonify
from math import radians, sin, cos, sqrt, atan2
from itertools import permutations

app = Flask(__name__)

# --- Points (start = Rond-Point Victoire, destination = Gare Centrale)
START = {"name": "Rond-Point Victoire", "lat": -4.33787, "lon": 15.30553,
         "photo": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Place_des_artistes_Victoire_Kinshasa.jpg"}
DEST = {"name": "Gare Centrale", "lat": -4.30122, "lon": 15.31827,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/6/6b/Gare_central_de_Kinshasa.jpg"}

# Example intermediate stops (you can replace/add)
STOPS = [
    {"name": "Matonge", "lat": -4.34022, "lon": 15.31599,
     "photo": ""},  # add an URL or leave empty to use placeholder
    {"name": "Boulevard du 30 Juin", "lat": -4.301955, "lon": 15.31419,
     "photo": ""},
    {"name": "Centre-ville (arrêt intermédiaire)", "lat": -4.30800, "lon": 15.31150,
     "photo": ""}
]

# Haversine distance (meters)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # earth radius (m)
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Build a route (list of points) and compute total distance
def route_distance(points):
    total = 0.0
    segments = []
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        d = haversine(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
        segments.append({"from": p1['name'], "to": p2['name'], "distance_m": round(d, 1)})
        total += d
    return round(total, 1), segments

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data.json')
def data():
    # generate all routes: START -> permute(STOPS) -> DEST
    routes = []
    for perm in permutations(STOPS):
        points = [START] + list(perm) + [DEST]
        total_m, segments = route_distance(points)
        routes.append({
            "points": [{"name": p['name'], "lat": p['lat'], "lon": p['lon'], "photo": p.get('photo','')} for p in points],
            "total_distance_m": total_m,
            "segments": segments
        })
    # find shortest
    routes_sorted = sorted(routes, key=lambda r: r['total_distance_m'])
    shortest = routes_sorted[0]
    return jsonify({"start": START, "dest": DEST, "stops": STOPS, "all_routes": routes, "shortest_route": shortest})

if __name__ == '__main__':
    app.run(debug=True)
