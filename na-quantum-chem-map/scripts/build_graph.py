"""Pick principal investigators from the corpus, place them on the map, build the co-authorship web.

Steps
 1. Merge data/raw/works_*.jsonl (dedupe by work id, remember which queries hit each work).
 2. Per author: corpus papers, papers as last author (the PI slot in chemistry), most recent institution.
 3. Candidates: >= MIN_PAPERS corpus papers, active since ACTIVE_SINCE, last-author share >= MIN_LAST,
    current institution is a US/Canadian university (OpenAlex type "education").
 4. Author + institution records from OpenAlex singletons (free; cached in data/raw/authors, data/raw/institutions).
    Keep authors whose corpus papers are >= MIN_SHARE of everything they published since 2000.
 5. Edges = number of shared corpus papers between two selected PIs (papers with <= 60 authors).
Writes data/processed/{professors,edges,institutions}.csv and site/data/network.json.
"""
import collections, csv, glob, json, math, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KEY = os.environ.get("OPENALEX_API_KEY", "")
MIN_PAPERS, ACTIVE_SINCE, MIN_LAST, MIN_SHARE = int(os.environ.get("MIN_PAPERS", 10)), 2021, 0.30, 0.25
MIN_SHARE_CORE, MIN_CORE = 0.08, 20
MIN_THEORY = 0.25  # share of corpus titles with theory/method words; drops experimental chemical-physics groups
import re
THEORY_RX = re.compile(r"(?i)theor|calculat|comput|simulat|ab initio|first[- ]principles|density[- ]functional|\bDFT\b|molecular dynamics|model|method|algorithm|machine learning|neural|quantum chemi|coupled[- ]cluster|potential energy surface|perturbation|approximation|functional|wave ?function|monte carlo|free energy|semiclassical|basis set|predict|embedding|hamiltonian|kinetic energy")

def get(path):
    url = "https://api.openalex.org/" + path
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "na-quantum-chem-map/0.1"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            if getattr(e, "code", None) == 404: return None
            time.sleep(2 ** a)
    return None

def cached(kind, oid, select):
    fn = f"{R}/data/raw/{kind}/{oid}.json"
    if os.path.exists(fn): return json.load(open(fn))
    d = get(f"{kind}/{oid}?select={select}")
    if d is not None: json.dump(d, open(fn, "w"))
    return d

# ---- 1. corpus
works = {}
for fn in sorted(glob.glob(f"{R}/data/raw/works_*.jsonl")):
    q = os.path.basename(fn)[6:-6]
    for line in open(fn):
        w = json.loads(line)
        if w["id"] in works: works[w["id"]]["q"].add(q)
        else: w["q"] = {q}; works[w["id"]] = w
print("works", len(works), file=sys.stderr)

# ---- 2. per-author stats
CORE_TOPICS = {"Advanced Chemical Physics Studies", "Advanced Physical and Chemical Molecular Interactions"}
def is_core(w): return bool(w["q"] & {"qc", "journal"}) or w.get("topic") in CORE_TOPICS
A = collections.defaultdict(lambda: {"n": 0, "core": 0, "th": 0, "last": 0, "multi": 0, "years": [], "inst": collections.Counter(), "name": None, "q": collections.Counter()})
INST = {}
for w in works.values():
    if not w.get("year") or w.get("type") in ("erratum", "retraction", "paratext"): continue
    na = len(w["au"]); th = bool(THEORY_RX.search(w.get("title") or ""))
    for aid, name, pos, insts in w["au"]:
        a = A[aid]; a["n"] += 1; a["name"] = name; a["years"].append(w["year"]); a["core"] += is_core(w); a["th"] += th
        for q in w["q"]: a["q"][q] += 1
        if na >= 2:
            a["multi"] += 1
            if pos == "last": a["last"] += 1
        for iid, iname, itype, cc in insts:
            INST[iid] = (iname, itype, cc)
            a["inst"][iid] += 1 + max(0, w["year"] - 2015)  # recent affiliations dominate

import unicodedata
def clean(t):
    if not t: return t
    t = t.replace("\u0131\u0301", "\u00ed").replace("\u2010", "-").replace("\u2011", "-").replace("\u0131\u0302", "\u00ee")
    return unicodedata.normalize("NFC", t)
SYSTEM_RX = re.compile(r"(?i)\bsystem\b|^state university of new york$|^university of north carolina$|^university of texas system")
def is_system(name): return bool(SYSTEM_RX.search(name or ""))

def current_inst(a):
    top = a["inst"].most_common()
    if not top: return None
    for iid, wt in top:
        if wt < 0.5 * top[0][1]: break  # a lab (LBNL, PNNL, ...) may outrank the university the PI also belongs to
        nm, t, cc = INST[iid]
        if t == "education" and cc in ("US", "CA") and not is_system(nm): return iid
    return None

cand = []
for aid, a in A.items():
    if a["n"] < MIN_PAPERS or max(a["years"]) < ACTIVE_SINCE: continue
    if a["multi"] and a["last"] / a["multi"] < MIN_LAST: continue
    iid = current_inst(a)
    if iid: cand.append((aid, iid))
print("candidates", len(cand), file=sys.stderr)

# ---- 3. singletons
os.makedirs(f"{R}/data/raw/authors", exist_ok=True); os.makedirs(f"{R}/data/raw/institutions", exist_ok=True)
with ThreadPoolExecutor(8) as ex:
    AU = dict(zip([c[0] for c in cand], ex.map(lambda c: cached("authors", c[0], "id,display_name,orcid,works_count,cited_by_count,summary_stats,counts_by_year,last_known_institutions,topics"), cand)))
iids = sorted({c[1] for c in cand} | {i["id"].rsplit("/", 1)[-1] for d in AU.values() if d for i in (d.get("last_known_institutions") or [])})
with ThreadPoolExecutor(8) as ex:
    IN = dict(zip(iids, ex.map(lambda i: cached("institutions", i, "id,display_name,geo,type,country_code,homepage_url,ror,display_name_acronyms,lineage"), iids)))

def works_since_2000(d):
    by = {c["year"]: c["works_count"] for c in d.get("counts_by_year") or []}  # only last ~10 years
    recent = sum(v for y, v in by.items() if y >= 2000)
    return max(recent, d.get("works_count", 0) * 0.9 if not by else recent)

# ---- 4. select
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

sel, dropped = {}, []
for aid, iid in cand:
    d = AU.get(aid); inst = IN.get(iid)
    if not d or not inst or not (inst.get("geo") or {}).get("latitude"): continue
    lk = [i["id"].rsplit("/", 1)[-1] for i in d.get("last_known_institutions") or []]
    lk_info = [IN.get(i) for i in lk if IN.get(i)]
    # trust OpenAlex's last known institution when it is a US/CA university (handles recent moves)
    for li in lk_info:
        if li.get("type") == "education" and li.get("country_code") in ("US", "CA") and (li.get("geo") or {}).get("latitude") and not is_system(li.get("display_name")):
            inst, iid = li, li["id"].rsplit("/", 1)[-1]; break
    else:
        if lk_info and all(li.get("country_code") not in ("US", "CA") for li in lk_info): continue  # moved abroad
    share = A[aid]["n"] / max(1, works_since_2000(d))
    # theorists: a quarter of all output is in the corpus, or a clear core of method/theory papers
    # (JCP/JCTC/quantum-chemistry concepts) inside a broader output (e.g. computational organic chemistry)
    if share < MIN_SHARE and not (share >= MIN_SHARE_CORE and A[aid]["core"] >= MIN_CORE): continue
    if A[aid]["th"] / A[aid]["n"] < MIN_THEORY:
        dropped.append((aid, d["display_name"], IN[iid]["display_name"], A[aid]["n"], round(A[aid]["th"] / A[aid]["n"], 3))); continue
    sel[aid] = {"aid": aid, "iid": iid, "share": share, "d": d, "core": A[aid]["core"], "th": A[aid]["th"] / A[aid]["n"]}
print("selected", len(sel), file=sys.stderr)

# ---- 5. papers, edges, areas
papers = collections.defaultdict(list); E = collections.Counter(); areac = collections.defaultdict(collections.Counter)
for w in works.values():
    ids = [a[0] for a in w["au"] if a[0] in sel]
    if not ids: continue
    ar = work_area(w)
    for x in ids: papers[x].append(w); areac[x][ar] += 1
    if w["n_authors"] <= 60:
        ids = sorted(set(ids))
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)): E[(ids[i], ids[j])] += 1

def pub(w, me):
    co = [clean(a[1]) for a in w["au"] if a[0] in sel and a[0] != me][:6]
    return {"t": clean(w.get("title") or "")[:300], "y": w["year"], "v": w.get("venue"), "c": w["cites"],
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""), "w": w["id"], "co": co}

insts = {}
nodes = []
for aid, s in sel.items():
    d, iid = s["d"], s["iid"]; inst = IN[iid]; g = inst["geo"]
    insts.setdefault(iid, {"id": iid, "n": inst["display_name"], "lat": g["latitude"], "lng": g["longitude"], "city": g.get("city"),
                           "reg": g.get("region"), "cc": inst.get("country_code"), "url": inst.get("homepage_url"), "k": 0})
    insts[iid]["k"] += 1
    ps = papers[aid]
    top = sorted(ps, key=lambda w: -w["cites"])[:10]
    recent = [w for w in sorted(ps, key=lambda w: -(w["year"] or 0)) if w not in top][:4]
    area = areac[aid].most_common(1)[0][0]
    nodes.append({"id": aid, "n": clean(d["display_name"]), "i": iid, "a": area, "ac": dict(areac[aid]), "np": len(ps),
                  "h": (d.get("summary_stats") or {}).get("h_index"), "cit": d.get("cited_by_count"),
                  "orcid": (d.get("orcid") or "").replace("https://orcid.org/", ""),
                  "kw": [t["display_name"] for t in (d.get("topics") or [])[:5]],
                  "top": [pub(w, aid) for w in top], "rec": [pub(w, aid) for w in recent],
                  "y0": min(w["year"] for w in ps), "y1": max(w["year"] for w in ps)})
edges = [[a, b, k] for (a, b), k in E.items()]
deg = collections.Counter()
for a, b, k in edges: deg[a] += 1; deg[b] += 1
for n in nodes: n["deg"] = deg[n["id"]]

os.makedirs(f"{R}/data/processed", exist_ok=True); os.makedirs(f"{R}/site/data", exist_ok=True)
with open(f"{R}/data/processed/professors.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["openalex_id", "name", "institution_id", "institution", "city", "region", "country", "area", "corpus_papers", "core_theory_papers", "theory_title_share", "corpus_share", "h_index", "coauthor_degree", "orcid"])
    for n in sorted(nodes, key=lambda n: (insts[n["i"]]["n"], n["n"])):
        I = insts[n["i"]]; wr.writerow([n["id"], n["n"], n["i"], I["n"], I["city"], I["reg"], I["cc"], dict(AREAS)[n["a"]], n["np"], sel[n["id"]]["core"], round(sel[n["id"]]["th"], 3), round(sel[n["id"]]["share"], 3), n["h"], n["deg"], n["orcid"]])
with open(f"{R}/data/processed/excluded_experimental.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["openalex_id", "name", "institution", "corpus_papers", "theory_title_share"]); wr.writerows(sorted(dropped, key=lambda x: x[2]))
with open(f"{R}/data/processed/edges.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["source", "target", "shared_papers"]); wr.writerows(sorted(edges, key=lambda e: -e[2]))
with open(f"{R}/data/processed/institutions.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["openalex_id", "name", "lat", "lng", "city", "region", "country", "professors"])
    for I in sorted(insts.values(), key=lambda I: -I["k"]): wr.writerow([I["id"], I["n"], I["lat"], I["lng"], I["city"], I["reg"], I["cc"], I["k"]])
meta = {"works": len(works), "professors": len(nodes), "edges": len(edges), "institutions": len(insts), "areas": AREAS,
        "built": time.strftime("%Y-%m-%d"), "params": {"min_theory": MIN_THEORY, "min_core": MIN_CORE, "min_share_core": MIN_SHARE_CORE, "min_papers": MIN_PAPERS, "active_since": ACTIVE_SINCE, "min_last_author": MIN_LAST, "min_share": MIN_SHARE}}
json.dump({"meta": meta, "inst": list(insts.values()), "nodes": nodes, "edges": edges}, open(f"{R}/site/data/network.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(json.dumps(meta, ensure_ascii=False), os.path.getsize(f"{R}/site/data/network.json"), file=sys.stderr)
