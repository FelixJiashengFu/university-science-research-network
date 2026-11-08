"""Build site/data/basemap.json from Natural Earth 1:50m (public domain).
Inputs (downloaded once into data/raw/ne/): ne_50m_admin_1_states_provinces.geojson,
ne_50m_admin_0_countries.geojson, ne_50m_lakes.geojson from github.com/nvkelso/natural-earth-vector.
Keeps US states + Canadian provinces, neighbouring countries as context, and the big lakes; rounds to 0.01 deg."""
import json, os, sys
R = os.path.join(os.path.dirname(__file__), "..")
NE = os.path.join(R, "data", "raw", "ne")
BBOX = (-170, 14, -50, 84)

def rnd(c, d=2):
    if isinstance(c[0], (int, float)): return [round(c[0], d), round(c[1], d)]
    out = [rnd(x, d) for x in c]
    if out and isinstance(out[0][0], (int, float)):  # ring: drop consecutive duplicates
        ded = [out[0]] + [p for i, p in enumerate(out[1:], 1) if p != out[i - 1]]
        return ded if len(ded) >= 4 else out
    return out

def inbox(geom):
    def pts(c):
        if isinstance(c[0], (int, float)): yield c
        else:
            for x in c: yield from pts(x)
    return any(BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3] for x, y in pts(geom["coordinates"]))

feats = []
for f in json.load(open(f"{NE}/ne_50m_admin_1_states_provinces.geojson"))["features"]:
    p = f["properties"]
    if p["iso_a2"] in ("US", "CA"):
        feats.append({"type": "Feature", "properties": {"k": "admin1", "c": p["iso_a2"], "n": p["name"], "a": p["postal"], "zh": p.get("name_zh")},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
for f in json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))["features"]:
    p = f["properties"]
    if p["ISO_A2"] not in ("US", "CA") and inbox(f["geometry"]):
        feats.append({"type": "Feature", "properties": {"k": "other", "n": p["NAME"]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
for f in json.load(open(f"{NE}/ne_50m_lakes.geojson"))["features"]:
    if inbox(f["geometry"]) and (f["properties"].get("scalerank") or 9) <= 3:
        feats.append({"type": "Feature", "properties": {"k": "lake", "n": f["properties"].get("name")},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
os.makedirs(f"{R}/site/data", exist_ok=True)
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{R}/site/data/basemap.json", "w"), separators=(",", ":"))
print(len(feats), os.path.getsize(f"{R}/site/data/basemap.json"))
