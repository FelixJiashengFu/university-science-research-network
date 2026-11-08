"""Build data for the North America Top-20 deep dives (top20/site/data/) and the China-US comparison
(compare/site/data/) from the two OpenAlex corpora and the two professor networks.

Inputs (run fetch_corpus.py for each map first; raw corpora are not committed):
  na-quantum-chem-map/data/raw/works_*.jsonl   US|CA corpus (same five queries)
  cn-quantum-chem-map/data/raw/works_*.jsonl   CN|HK|MO corpus
  na-quantum-chem-map/site/data/network.json, cn-quantum-chem-map/site/data/network.json
  cn-quantum-chem-map/site/data/basemap.json   (province lookup for Chinese institutions)
Definitions
  US paper = at least one author institution in the US; CN paper = at least one in CN/HK/MO.
  Sub-field of a paper = work_area() below, identical to the maps.
  Top-10% = among all US-or-CN papers of the same sub-field and year, citation count >= the 90th percentile.
  Ranking of the NA Top 20 = 0.4 * pct(citations of corpus papers) + 0.2 * pct(h-index)
                             + 0.2 * pct(corpus papers) + 0.2 * pct(co-author degree in the map), percentiles over all 1,044 PIs.
"""
import bisect, collections, glob, json, math, os, statistics, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AREAS = [("es", "电子结构与量子化学方法"), ("ex", "激发态、光谱与非绝热动力学"), ("rd", "反应动力学与速率理论"),
         ("md", "分子动力学与统计力学"), ("mat", "计算材料与密度泛函"), ("ml", "机器学习与数据驱动化学")]
TOPIC_AREA = {"Advanced Chemical Physics Studies": "es", "Spectroscopy and Quantum Chemical Studies": "ex",
              "Advanced Physical and Chemical Molecular Interactions": "rd", "Machine Learning in Materials Science": "ml",
              "Photochemistry and Electron Transfer Studies": "ex", "Protein Structure and Dynamics": "md",
              "Computational Drug Discovery Methods": "md", "Lipid Membrane Structure and Behavior": "md",
              "Quantum Computing Algorithms and Architecture": "es", "Molecular Spectroscopy and Structure": "ex",
              "Phase Equilibria and Thermodynamics": "md", "Material Dynamics and Properties": "md"}
def work_area(w):
    t = w.get("topic") or ""
    if t in TOPIC_AREA: return TOPIC_AREA[t]
    if "qc" in w["q"]: return "es"
    if "md" in w["q"]: return "md"
    if "dft" in w["q"]: return "mat"
    return "es" if "journal" in w["q"] else "mat"
CORE_ISSN_VENUES = {"The Journal of Chemical Physics", "Journal of Chemical Theory and Computation", "Journal of Computational Chemistry",
                    "Wiley Interdisciplinary Reviews Computational Molecular Science", "International Journal of Quantum Chemistry", "Theoretical Chemistry Accounts"}
CN_CC = {"CN", "HK", "MO"}

def load(folder):
    W = {}
    for fn in sorted(glob.glob(f"{R}/{folder}/data/raw/works_*.jsonl")):
        q = os.path.basename(fn)[6:-6]
        for line in open(fn):
            w = json.loads(line)
            if w["id"] in W: W[w["id"]]["q"].add(q)
            else: w["q"] = {q}; W[w["id"]] = w
    return W
print("loading corpora", file=sys.stderr)
NA, CN = load("na-quantum-chem-map"), load("cn-quantum-chem-map")
ALL = dict(NA)
for k, w in CN.items():
    if k in ALL: ALL[k]["q"] |= w["q"]
    else: ALL[k] = w
for w in ALL.values():
    cc = {i[3] for a in w["au"] for i in a[3]}
    w["us"], w["cn"], w["ca"] = "US" in cc, bool(cc & CN_CC), "CA" in cc
    w["ar"] = work_area(w)
VALID = [w for w in ALL.values() if w.get("year") and 2000 <= w["year"] <= 2025 and w.get("type") not in ("erratum", "retraction", "paratext")]
print("works", len(ALL), "valid", len(VALID), file=sys.stderr)
netNA = json.load(open(f"{R}/na-quantum-chem-map/site/data/network.json"))
netCN = json.load(open(f"{R}/cn-quantum-chem-map/site/data/network.json"))
YEARS = list(range(2000, 2026))

# ---------------------------------------------------------------- top-10% thresholds (US ∪ CN papers)
cits = collections.defaultdict(list)
for w in VALID:
    if w["us"] or w["cn"]: cits[(w["ar"], w["year"])].append(w["cites"])
THR = {k: sorted(v)[int(0.9 * (len(v) - 1))] for k, v in cits.items()}
for w in VALID: w["top10"] = (w["us"] or w["cn"]) and w["cites"] >= THR.get((w["ar"], w["year"]), 1e9) and w["cites"] > 0

# ---------------------------------------------------------------- comparison
def side(w, c): return w["us"] if c == "US" else w["cn"]
C = {"meta": {"works_us": sum(w["us"] for w in VALID), "works_cn": sum(w["cn"] for w in VALID), "works_both": sum(w["us"] and w["cn"] for w in VALID),
              "years": YEARS, "areas": AREAS}}
C["yearly"] = {c: [sum(1 for w in VALID if side(w, c) and w["year"] == y) for y in YEARS] for c in ("US", "CN")}
C["yearly_area"] = {c: {a: [0] * len(YEARS) for a, _ in AREAS} for c in ("US", "CN")}
for w in VALID:
    for c in ("US", "CN"):
        if side(w, c): C["yearly_area"][c][w["ar"]][w["year"] - 2000] += 1
C["collab"] = [sum(1 for w in VALID if w["us"] and w["cn"] and w["year"] == y) for y in YEARS]
def agg(ws):
    ws = list(ws); n = len(ws)
    if not n: return {}
    old = [w for w in ws if 2010 <= w["year"] <= 2019]
    return {"n": n, "n21": sum(1 for w in ws if 2020 <= w["year"] <= 2024), "n10_19": len(old),
            "mcit": round(statistics.mean(w["cites"] for w in old), 2) if old else None,
            "medcit": statistics.median(w["cites"] for w in old) if old else None,
            "top10": round(100 * sum(w["top10"] for w in ws) / n, 2),
            "team": round(statistics.mean(w["n_authors"] for w in ws if w["n_authors"]), 2),
            "core": round(100 * sum(1 for w in ws if w.get("venue") in CORE_ISSN_VENUES) / n, 2)}
C["area"] = {c: {a: agg(w for w in VALID if side(w, c) and w["ar"] == a) for a, _ in AREAS} for c in ("US", "CN")}
C["all"] = {c: agg(w for w in VALID if side(w, c)) for c in ("US", "CN")}
def cagr(c, a, y0=2010, y1=2024):
    s = C["yearly_area"][c][a]; v0, v1 = s[y0 - 2000], s[y1 - 2000]
    return round(100 * ((v1 / v0) ** (1 / (y1 - y0)) - 1), 2) if v0 else None
C["cagr"] = {c: {a: cagr(c, a) for a, _ in AREAS} for c in ("US", "CN")}
C["team_year"] = {c: [round(statistics.mean([w["n_authors"] for w in VALID if side(w, c) and w["year"] == y and w["n_authors"]] or [0]), 2) for y in YEARS] for c in ("US", "CN")}
C["core_year"] = {c: [round(100 * sum(1 for w in VALID if side(w, c) and w["year"] == y and w.get("venue") in CORE_ISSN_VENUES) / max(1, sum(1 for w in VALID if side(w, c) and w["year"] == y)), 2) for y in YEARS] for c in ("US", "CN")}
C["top10_year"] = {c: [round(100 * sum(1 for w in VALID if side(w, c) and w["year"] == y and w["top10"]) / max(1, sum(1 for w in VALID if side(w, c) and w["year"] == y)), 2) for y in YEARS] for c in ("US", "CN")}
C["collab_share"] = {c: [round(100 * C["collab"][i] / max(1, C["yearly"][c][i]), 2) for i in range(len(YEARS))] for c in ("US", "CN")}
vc = {c: collections.Counter(w.get("venue") for w in VALID if side(w, c) and w["year"] >= 2021 and w.get("venue")) for c in ("US", "CN")}
C["venues"] = {c: vc[c].most_common(12) for c in ("US", "CN")}
# top-cited papers 2021-2025 per side
C["top_papers"] = {c: [{"t": w["title"], "y": w["year"], "v": w.get("venue"), "c": w["cites"], "doi": (w.get("doi") or "").replace("https://doi.org/", ""), "w": w["id"], "ar": w["ar"]}
                        for w in sorted((w for w in VALID if side(w, c) and w["year"] >= 2021), key=lambda w: -w["cites"])[:10]] for c in ("US", "CN")}

# ---------------------------------------------------------------- PIs / networks
def pip(pt, poly):
    x, y = pt; inside = False
    for ring in poly:
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]; xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi: inside = not inside
            j = i
    return inside
base = json.load(open(f"{R}/cn-quantum-chem-map/site/data/basemap.json"))["features"]
def province(lng, lat):
    for f in base:
        if f["properties"]["k"] != "admin1": continue
        g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        if any(pip((lng, lat), p) for p in polys): return f["properties"]["a"]
    best = min((f for f in base if f["properties"]["k"] == "admin1"), key=lambda f: min((x - lng) ** 2 + (y - lat) ** 2 for p in ([f["geometry"]["coordinates"]] if f["geometry"]["type"] == "Polygon" else f["geometry"]["coordinates"]) for r in p for x, y in r))
    return best["properties"]["a"]
US_STATE_ZH = {}
def netstats(net, keep):
    nodes = [n for n in net["nodes"] if keep(n)]; ids = {n["id"] for n in nodes}
    E = [e for e in net["edges"] if e[0] in ids and e[1] in ids]
    adj = collections.defaultdict(set)
    for a, b, k in E: adj[a].add(b); adj[b].add(a)
    seen, comps = set(), []
    for n in ids:
        if n in seen: continue
        st, comp = [n], 0; seen.add(n)
        while st:
            x = st.pop(); comp += 1
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        comps.append(comp)
    cl = []
    for n in ids:
        nb = list(adj[n]); k = len(nb)
        if k < 2: continue
        links = sum(1 for i in range(k) for j in range(i + 1, k) if nb[j] in adj[nb[i]])
        cl.append(2 * links / (k * (k - 1)))
    N = len(ids)
    inst = {i["id"]: i for i in net["inst"]}
    sameinst = sum(1 for a, b, k in E if next(n for n in nodes if n["id"] == a)["i"] == next(n for n in nodes if n["id"] == b)["i"]) if len(E) < 20000 else None
    return {"pis": N, "edges": len(E), "mean_degree": round(2 * len(E) / N, 2), "density": round(2 * len(E) / (N * (N - 1)), 5),
            "isolated_pct": round(100 * sum(1 for n in ids if not adj[n]) / N, 1), "giant_pct": round(100 * max(comps) / N, 1),
            "clustering": round(sum(cl) / N, 3), "same_inst_edge_pct": round(100 * sameinst / max(1, len(E)), 1),
            "mean_weight": round(statistics.mean(k for a, b, k in E), 2) if E else 0}
pisUS = [n for n in netNA["nodes"] if {i["id"]: i for i in netNA["inst"]}[n["i"]]["cc"] == "US"]
pisCN = netCN["nodes"]
instNA = {i["id"]: i for i in netNA["inst"]}; instCN = {i["id"]: i for i in netCN["inst"]}
C["net"] = {"US": netstats(netNA, lambda n: instNA[n["i"]]["cc"] == "US"), "CN": netstats(netCN, lambda n: True)}
def pistats(pis):
    hs = sorted(n["h"] or 0 for n in pis)
    return {"n": len(pis), "h_median": statistics.median(hs), "h_mean": round(statistics.mean(hs), 1), "h_p90": hs[int(.9 * (len(hs) - 1))],
            "np_median": statistics.median(n["np"] for n in pis), "area": dict(collections.Counter(n["a"] for n in pis)),
            "h_hist": dict(collections.Counter(min(150, 10 * ((n["h"] or 0) // 10)) for n in pis)),
            "start_hist": dict(collections.Counter(5 * (n["y0"] // 5) for n in pis))}
C["pi"] = {"US": pistats(pisUS), "CN": pistats(pisCN)}
for c, pis, I in (("US", pisUS, instNA), ("CN", pisCN, instCN)):
    by = collections.Counter(n["i"] for n in pis)
    ks = sorted(by.values(), reverse=True); tot = sum(ks); cum = 0; lor = [[0, 0]]
    for i, k in enumerate(sorted(ks)):
        cum += k; lor.append([round((i + 1) / len(ks), 4), round(cum / tot, 4)])
    g = 1 - 2 * sum((lor[i][0] - lor[i - 1][0]) * (lor[i][1] + lor[i - 1][1]) / 2 for i in range(1, len(lor)))
    C["pi"][c].update({"institutions": len(by), "gini": round(g, 3), "lorenz": lor[:: max(1, len(lor) // 80)] + [lor[-1]],
                       "top10_inst_pct": round(100 * sum(ks[:10]) / tot, 1),
                       "top_inst": [[I[i].get("zh") or I[i]["n"], I[i]["n"], k] for i, k in by.most_common(15)]})
    reg = collections.Counter()
    for n in pis:
        ii = I[n["i"]]
        reg[(province(ii["lng"], ii["lat"]) if c == "CN" else ii.get("reg")) or "?"] += 1
    C["pi"][c]["regions"] = reg.most_common(15)

# rankings (same composite for both sides)
def corpus_cites(W, ids):
    cit, npp = collections.Counter(), collections.Counter()
    for w in W.values():
        for a in {a[0] for a in w["au"]}:
            if a in ids: cit[a] += w["cites"]; npp[a] += 1
    return cit, npp
def rank(nodes, W):
    ids = {n["id"] for n in nodes}; cit, npp = corpus_cites(W, ids)
    def pct(v):
        s = sorted(v.values()); return {k: bisect.bisect_right(s, x) / len(s) for k, x in v.items()}
    P = [pct({n["id"]: cit[n["id"]] for n in nodes}), pct({n["id"]: n["h"] or 0 for n in nodes}), pct({n["id"]: npp[n["id"]] for n in nodes}), pct({n["id"]: n["deg"] for n in nodes})]
    sc = {n["id"]: .4 * P[0][n["id"]] + .2 * P[1][n["id"]] + .2 * P[2][n["id"]] + .2 * P[3][n["id"]] for n in nodes}
    return sorted(nodes, key=lambda n: -sc[n["id"]]), sc, cit, npp
rankNA, scNA, citNA, npNA = rank(netNA["nodes"], NA)
rankCN, scCN, citCN, npCN = rank(netCN["nodes"], CN)
def row(n, I, sc, cit, npp):
    i = I[n["i"]]; return {"id": n["id"], "n": n["n"], "inst": i.get("zh") or i["n"], "inst_en": i["n"], "cc": i["cc"], "a": n["a"], "h": n["h"], "cit": cit[n["id"]], "np": npp[n["id"]], "deg": n["deg"], "score": round(sc[n["id"]], 4)}
C["rank"] = {"US": [row(n, instNA, scNA, citNA, npNA) for n in rankNA if instNA[n["i"]]["cc"] == "US"][:20], "CN": [row(n, instCN, scCN, citCN, npCN) for n in rankCN][:20]}
os.makedirs(f"{R}/compare/site/data", exist_ok=True)
json.dump(C, open(f"{R}/compare/site/data/compare.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("compare.json", os.path.getsize(f"{R}/compare/site/data/compare.json"), file=sys.stderr)

# ---------------------------------------------------------------- Top 20 deep dives (NA and China)
def deep_dives(top, net, W, inst, sc, cit, home, rest, outdir, profiles):
    byN = {n["id"]: n for n in net["nodes"]}
    out = []
    for rk, n in enumerate(top, 1):
        me = n["id"]; ps = [w for w in W.values() if any(a[0] == me for a in w["au"]) and w.get("year")]
        co = collections.Counter(); coname = {}; coinst = collections.defaultdict(collections.Counter); pair = collections.Counter()
        instc = collections.Counter(); instinfo = {}
        for w in ps:
            others = []
            for aid, nm, pos, insts in w["au"]:
                if aid == me: continue
                others.append(aid); co[aid] += 1; coname[aid] = nm
                for iid, iname, t, cc in insts[:1]: coinst[aid][(iname, t, cc)] += 1
                for iid, iname, t, cc in insts: instinfo[iid] = (iname, t, cc)
            for iid in {i[0] for a in w["au"] if a[0] != me for i in a[3]}: instc[iid] += 1
            if w["n_authors"] <= 30:
                others = sorted(set(others))
                for i in range(len(others)):
                    for j in range(i + 1, len(others)): pair[(others[i], others[j])] += 1
        keep = [a for a, k in co.most_common(60) if k >= 2][:45]; ks = set(keep)
        def cat(a):
            if a in byN: return "pi"
            (iname, t, cc), _ = coinst[a].most_common(1)[0] if coinst[a] else ((None, None, None), 0)
            if cc and cc not in home: return "intl"
            return {"education": "edu", "company": "company"}.get(t, "lab" if t else "edu")
        nodes = [{"id": a, "n": coname[a], "k": co[a], "c": cat(a), "inst": (coinst[a].most_common(1)[0][0][0] if coinst[a] else None), "pi": a in byN} for a in keep]
        edges = [[a, b, k] for (a, b), k in pair.items() if a in ks and b in ks and k >= 2]
        yr = collections.Counter(w["year"] for w in ps); yc = collections.Counter()
        for w in ps: yc[w["year"]] += w["cites"]
        ven = collections.Counter(w.get("venue") for w in ps if w.get("venue"))
        arc = collections.Counter(work_area(w) for w in ps)
        def pub(w): return {"t": w["title"], "y": w["year"], "v": w.get("venue"), "c": w["cites"], "doi": (w.get("doi") or "").replace("https://doi.org/", ""), "w": w["id"], "na": w["n_authors"]}
        i = inst[n["i"]]
        out.append({"rank": rk, "id": me, "n": n["n"], "inst": i.get("zh") or i["n"], "inst_en": i["n"], "city": i.get("city"), "reg": i.get("reg"), "cc": i["cc"], "lat": i["lat"], "lng": i["lng"],
                    "a": n["a"], "h": n["h"], "cit_all": n["cit"], "cit": cit[me], "np": len(ps), "deg": n["deg"], "score": round(sc[me], 4), "orcid": n["orcid"], "kw": n["kw"],
                    "y0": min(yr), "y1": max(yr), "years": [[y, yr[y], yc[y]] for y in range(min(yr), 2026)], "areas": dict(arc),
                    "venues": ven.most_common(8), "top": [pub(w) for w in sorted(ps, key=lambda w: -w["cites"])[:12]],
                    "recent": [pub(w) for w in sorted(ps, key=lambda w: (-(w["year"] or 0), -w["cites"]))[:6]],
                    "partners": [[instinfo[iid][0], instinfo[iid][1], instinfo[iid][2], k] for iid, k in instc.most_common(12)],
                    "net_pi": sorted([[x, k, byN[x]["n"]] for x, k in ((b if a == me else a, k) for a, b, k in net["edges"] if me in (a, b))], key=lambda r: -r[1])[:30],
                    "ego": {"nodes": nodes, "edges": edges},
                    "coauthors_total": len(co)})
    PROF = json.load(open(profiles)) if os.path.exists(profiles) else {}  # hand-written research summaries
    for p in out: p["profile"] = PROF.get(p["id"])
    os.makedirs(outdir, exist_ok=True)
    json.dump({"built": __import__("time").strftime("%Y-%m-%d"), "areas": AREAS, "profs": out, "all_n": len(net["nodes"]), "all_area": dict(collections.Counter(n["a"] for n in net["nodes"])),
               "next": rest}, open(f"{outdir}/top20.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(outdir, os.path.getsize(f"{outdir}/top20.json"), file=sys.stderr)

deep_dives(rankNA[:20], netNA, NA, instNA, scNA, citNA, {"US", "CA"}, [row(n, instNA, scNA, citNA, npNA) for n in rankNA[20:50]], f"{R}/top20/site/data", f"{R}/top20/data/manual/profiles.json")
deep_dives(rankCN[:20], netCN, CN, instCN, scCN, citCN, CN_CC, [row(n, instCN, scCN, citCN, npCN) for n in rankCN[20:50]], f"{R}/cn-top20/site/data", f"{R}/cn-top20/data/manual/profiles.json")
