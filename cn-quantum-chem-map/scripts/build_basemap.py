"""Build site/data/basemap.json for the China map from Natural Earth 1:50m (public domain).
Inputs (downloaded once into data/raw/ne/ from github.com/nvkelso/natural-earth-vector/geojson):
ne_50m_admin_1_states_provinces.geojson, ne_50m_admin_0_countries.geojson, ne_50m_lakes.geojson.
Keeps China's provinces (+ Hong Kong, Macao, Taiwan drawn as provincial-level units), neighbouring
countries as context and large lakes; coordinates rounded to 0.01 deg. Labels are short Chinese names."""
import json, os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NE = os.path.join(R, "data", "raw", "ne")
BBOX = (68, 14, 140, 56)

def rnd(c, d=2):
    if isinstance(c[0], (int, float)): return [round(c[0], d), round(c[1], d)]
    out = [rnd(x, d) for x in c]
    if out and isinstance(out[0][0], (int, float)):
        ded = [out[0]] + [p for i, p in enumerate(out[1:], 1) if p != out[i - 1]]
        return ded if len(ded) >= 4 else out
    return out

def inbox(geom):
    def pts(c):
        if isinstance(c[0], (int, float)): yield c
        else:
            for x in c: yield from pts(x)
    return any(BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3] for x, y in pts(geom["coordinates"]))

def clamp(c):
    if isinstance(c[0], (int, float)): return [min(max(c[0], 40), 160), min(max(c[1], -12), 75)]
    return [clamp(x) for x in c]

def short(zh):
    zh = zh or ""
    for s in ("壮族自治区", "回族自治区", "维吾尔自治区", "自治区", "特别行政区", "省", "市"):
        if zh.endswith(s): return zh[: -len(s)]
    return zh

feats = []
for f in json.load(open(f"{NE}/ne_50m_admin_1_states_provinces.geojson"))["features"]:
    p = f["properties"]
    if p["iso_a2"] == "CN":
        feats.append({"type": "Feature", "properties": {"k": "admin1", "c": "CN", "n": p["name"], "a": short(p.get("name_zh"))},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
SAR = {"HKG": ("HK", "香港"), "MAC": ("MO", "澳门"), "TWN": ("TW", "台湾")}
for f in json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))["features"]:
    p = f["properties"]
    if p["ADM0_A3"] == "CHN": continue
    if p["ADM0_A3"] in SAR:
        c, zh = SAR[p["ADM0_A3"]]
        feats.append({"type": "Feature", "properties": {"k": "admin1", "c": c, "n": p["NAME"], "a": zh},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    elif inbox(f["geometry"]):  # clamp far-off parts (Russia wraps the antimeridian) so no chord crosses the map
        feats.append({"type": "Feature", "properties": {"k": "other", "n": p["NAME"]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": clamp(rnd(f["geometry"]["coordinates"]))}})
for f in json.load(open(f"{NE}/ne_50m_lakes.geojson"))["features"]:
    if inbox(f["geometry"]) and (f["properties"].get("scalerank") or 9) <= 3:
        feats.append({"type": "Feature", "properties": {"k": "lake", "n": f["properties"].get("name")},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
os.makedirs(f"{R}/site/data", exist_ok=True)
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{R}/site/data/basemap.json", "w"), separators=(",", ":"), ensure_ascii=False)
print(len(feats), os.path.getsize(f"{R}/site/data/basemap.json"))
