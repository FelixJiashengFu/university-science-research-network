"""Generic school network builder (adapted from stanford/scripts/build_graph.py).

usage: python3 build_graph.py <slug>   -> writes schools/<slug>/site/data/*.json and data/processed/*.csv
Research areas come from OpenAlex subfields (no department area lists for inferred rosters).

Inputs : data/processed/matches.csv, data/raw/openalex/works/*.jsonl
Outputs: site/data/<network>.json  (sigma/graphology format with precomputed x,y)
         site/data/profs.json      (details for the side panel)
         data/processed/{professors,edges_coauthor,edges_similarity,topics}.csv
"""
import csv, json, math, os, collections, itertools, re
import networkx as nx, sys
import numpy as np

SLUG = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{HERE}/raw/{SLUG}/works"
os.chdir(f"{HERE}/../{SLUG}")

MIN_SCORE = 1.0          # minimum match score to trust an OpenAlex author match
BIG_COLLAB = 100         # works with more authors are "large collaborations"
os.makedirs("site/data", exist_ok=True); os.makedirs("data/processed", exist_ok=True)

DEPT_COLOR = {"Mathematics": "#3b82f6", "Physics": "#ef4444", "Chemistry": "#10b981"}
COMPANY_COLOR, STARTUP_COLOR = "#f97316", "#e11d48"
FIELD_COLOR = {"Mathematics": "#93c5fd", "Physics and Astronomy": "#fca5a5", "Chemistry": "#6ee7b7",
               "Materials Science": "#fcd34d", "Computer Science": "#c4b5fd", "Engineering": "#fdba74",
               "Earth and Planetary Sciences": "#a3e635", "Environmental Science": "#86efac",
               "Biochemistry, Genetics and Molecular Biology": "#f9a8d4", "Chemical Engineering": "#5eead4",
               "Decision Sciences": "#d8b4fe", "Energy": "#fde047", "Medicine": "#fda4af", "Neuroscience": "#f0abfc"}

# ---------- load ----------
profs = {}
for r in csv.DictReader(open("data/processed/matches.csv")):
    if not r["openalex_id"] or float(r["match_score"]) < MIN_SCORE: continue
    aid = r["openalex_id"]
    if aid in profs:  # same person listed by two departments (joint appointment)
        profs[aid]["all_depts"] = "/".join(sorted(set(profs[aid]["all_depts"].split("/")) | set(r["all_depts"].split("/"))))
        continue
    profs[aid] = dict(r)
works = {}            # work id -> work
prof_works = collections.defaultdict(set)
for aid in profs:
    fn = f"{RAW}/{aid}.jsonl"
    if not os.path.exists(fn): continue
    for line in open(fn):
        w = json.loads(line)
        if w.get("type") in ("erratum", "retraction", "paratext", "peer-review"): continue
        works.setdefault(w["id"], w); prof_works[aid].add(w["id"])
print("profs", len(profs), "works", len(works))

topic_info = {}
prof_topic = collections.defaultdict(collections.Counter)
for aid, ws in prof_works.items():
    for wid in ws:
        t = works[wid].get("topic")
        if not t: continue
        topic_info[t["id"]] = t
        prof_topic[aid][t["id"]] += 1

# ---------- co-authorship ----------
coauth = collections.Counter(); coauth_big = collections.Counter(); shared = collections.defaultdict(list)
work_profs = collections.defaultdict(set)
for aid, ws in prof_works.items():
    for wid in ws: work_profs[wid].add(aid)
for wid, ps in work_profs.items():
    if len(ps) < 2: continue
    big = works[wid]["n_authors"] > BIG_COLLAB
    for a, b in itertools.combinations(sorted(ps), 2):
        (coauth_big if big else coauth)[(a, b)] += 1
        if not big: shared[(a, b)].append(wid)

# ---------- topic similarity (cosine on topic-count vectors, tf-idf weighted) ----------
tids = sorted(topic_info); tix = {t: i for i, t in enumerate(tids)}
P = sorted(prof_topic); pix = {p: i for i, p in enumerate(P)}
M = np.zeros((len(P), len(tids)))
for p, c in prof_topic.items():
    for t, n in c.items(): M[pix[p], tix[t]] = math.log1p(n)
df = (M > 0).sum(0); M = M * np.log((1 + len(P)) / (1 + df))
M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
S = M @ M.T; np.fill_diagonal(S, 0)
sim_edges = {}
for i, p in enumerate(P):
    for j in np.argsort(-S[i])[:6]:
        if S[i, j] < 0.2: continue
        k = tuple(sorted((p, P[j]))); sim_edges[k] = float(S[i, j])

# ---------- topic co-occurrence across professors ----------
topic_profs = collections.defaultdict(set)
for p, c in prof_topic.items():
    for t, n in c.items():
        if n >= 2: topic_profs[t].add(p)

def dept(p): return profs[p]["dept"]

# ---------- professor details for the side panel ----------
details = {}
for p in profs:
    ws = sorted(prof_works[p], key=lambda w: -(works[w]["cites"] or 0))
    fields = collections.Counter(works[w]["topic"]["field"] for w in prof_works[p] if works[w].get("topic"))
    years = [works[w]["year"] for w in prof_works[p] if works[w].get("year")]
    co = [(b if a == p else a, n) for (a, b), n in coauth.items() if p in (a, b)]
    cob = [(b if a == p else a, n) for (a, b), n in coauth_big.items() if p in (a, b)]
    details[p] = dict(
        name=profs[p]["name"], dept=dept(p), depts=profs[p]["all_depts"], areas=profs[p]["areas"], title=profs[p]["title"], url=profs[p]["url"],
        openalex=f"https://openalex.org/{p}", orcid=profs[p]["orcid"], h=profs[p]["h_index"],
        n_works=len(prof_works[p]), cites=sum(works[w]["cites"] or 0 for w in prof_works[p]),
        years=[int(np.percentile(years, 3)), max(years)] if years else None,
        topics=[[topic_info[t]["name"], n] for t, n in prof_topic[p].most_common(10)],
        fields=fields.most_common(6),
        papers=[dict(t=works[w]["title"], y=works[w]["year"], c=works[w]["cites"], v=works[w]["venue"], d=works[w]["doi"] or f"https://openalex.org/{w}") for w in ws[:15]],
        coauthors=sorted(co, key=lambda x: -x[1]), collab=sorted(cob, key=lambda x: -x[1])[:20],
        similar=[[P[j], round(float(S[pix[p], j]), 3)] for j in np.argsort(-S[pix[p]])[:8]] if p in pix else [],
    )
json.dump(details, open("site/data/profs.json", "w"), ensure_ascii=False)

# ---------- network builders ----------
def layout(G, iters=300):
    if G.number_of_nodes() == 0: return {}
    pos = nx.forceatlas2_layout(G, max_iter=iters, weight="weight", scaling_ratio=4.0, gravity=1.0, strong_gravity=False,
                                distributed_action=True, seed=7)
    return {n: (float(x), float(y)) for n, (x, y) in pos.items()}

def communities(G):
    H = G.copy(); H.remove_nodes_from([n for n, d in G.nodes(data=True) if d.get("kind") != "prof"])
    if H.number_of_edges() == 0: return {}
    cs = nx.community.louvain_communities(H, weight="weight", seed=7, resolution=1.0)
    return {n: i for i, c in enumerate(sorted(cs, key=len, reverse=True)) for n in c}

def prof_node(G, p):
    d = details[p]
    G.add_node(p, kind="prof", label=d["name"], dept=d["dept"], color=DEPT_COLOR[d["dept"]],
               size=3 + 1.4 * max(d["n_works"], 1) ** 0.33)

def topic_node(G, t, n_profs):
    ti = topic_info[t]
    G.add_node("T" + t, kind="topic", label=ti["name"], field=ti["field"], subfield=ti["subfield"],
               color=FIELD_COLOR.get(ti["field"], "#d4d4d8"), size=2 + 1.1 * math.sqrt(n_profs))

def paper_node(G, w):
    W = works[w]
    G.add_node("W" + w, kind="paper", label=(W["title"] or "")[:90], year=W["year"], cites=W["cites"],
               url=W["doi"] or f"https://openalex.org/{w}", color="#a1a1aa", size=1 + 0.35 * math.log1p(W["cites"] or 0))

def export(G, name, title, desc, iters=300):
    pos = layout(G, iters); com = communities(G)
    nodes = [dict(key=n, attributes=dict(d, x=pos[n][0], y=pos[n][1], community=com.get(n, -1))) for n, d in G.nodes(data=True)]
    edges = [dict(source=u, target=v, attributes=d) for u, v, d in G.edges(data=True)]
    kinds = collections.Counter(d["kind"] for _, d in G.nodes(data=True))
    json.dump(dict(title=title, description=desc, stats=dict(nodes=G.number_of_nodes(), edges=G.number_of_edges(), **kinds),
                   nodes=nodes, edges=edges), open(f"site/data/{name}.json", "w"), ensure_ascii=False)
    print(name, G.number_of_nodes(), G.number_of_edges(), dict(kinds))
    return dict(id=name, title=title, description=desc, nodes=G.number_of_nodes(), edges=G.number_of_edges())

def add_coauth(G, keep=lambda a, b: True):
    for (a, b), n in coauth.items():
        if a in G and b in G and keep(a, b):
            G.add_edge(a, b, kind="coauthor", weight=float(n), color="#475569", size=0.6 + math.log1p(n))
    for (a, b), n in coauth_big.items():
        if a in G and b in G and keep(a, b) and not G.has_edge(a, b):
            G.add_edge(a, b, kind="collab", weight=0.3 * math.log1p(n), color="#cbd5e1", size=0.4)

def add_sim(G, keep=lambda a, b: True):
    for (a, b), s in sim_edges.items():
        if a in G and b in G and keep(a, b) and not G.has_edge(a, b):
            G.add_edge(a, b, kind="similar", weight=2 * s, color="#f59e0b", size=0.3 + 1.5 * s)

# 8. innovation & entrepreneurship: industry co-authorship (OpenAlex) + faculty-founded companies (curated, sourced)
org_info = {}; prof_org = collections.defaultdict(collections.Counter); org_works = collections.defaultdict(set)
for p in profs:
    for wid in prof_works[p]:
        for oid, oname, otype, cc in works[wid].get("orgs") or []:
            if otype != "company" or not oid: continue
            org_info[oid] = dict(name=oname, country=cc); prof_org[p][oid] += 1; org_works[oid].add(wid)
startups = []
if os.path.exists("data/manual/startups.csv"):
    name2aid = {profs[p]["name"]: p for p in profs}
    for r in csv.DictReader(open("data/manual/startups.csv")):
        if r["person"] in name2aid: startups.append(dict(r, aid=name2aid[r["person"]]))
for p in details:
    details[p]["industry"] = [[org_info[o]["name"], n] for o, n in prof_org[p].most_common(12)]
    details[p]["startups"] = [dict(company=s["company"], year=s["year"], role=s["role"], url=s["url"]) for s in startups if s["aid"] == p]
json.dump(details, open("site/data/profs.json", "w"), ensure_ascii=False)

def company_node(G, o, n):
    G.add_node("C" + o, kind="company", label=org_info[o]["name"], country=org_info[o]["country"], color=COMPANY_COLOR, size=2 + 1.2 * math.sqrt(n))
def startup_node(G, s):
    k = "V" + re.sub(r"[^a-z0-9]", "", s["company"].lower())
    if k not in G: G.add_node(k, kind="startup", label=s["company"], year=s["year"], url=s["url"], color=STARTUP_COLOR, size=6)
    return k
def add_innovation(G, min_works):
    for p, c in prof_org.items():
        if p not in G: continue
        for o, n in c.items():
            if n < min_works: continue
            if "C" + o not in G: company_node(G, o, len(org_works[o]))
            G.add_edge(p, "C" + o, kind="industry", weight=math.log1p(n), color="#fdba74", size=0.3 + 0.4 * math.log1p(n), n=n)
    for s in startups:
        if s["aid"] in G:
            G.add_edge(s["aid"], startup_node(G, s), kind="founded", weight=3.0, color="#e11d48", size=2.0)

index = []
# 1. MAIN network: professors + their topics + topic hierarchy + papers + all relation types
G = nx.Graph()
for p in profs:
    if p in details and details[p]["n_works"]: prof_node(G, p)
main_topics = set(t for t, ps in topic_profs.items() if len(ps) >= 2)
for p, c in prof_topic.items():
    main_topics |= {t for t, n in c.most_common(8) if n >= 2}
for t in main_topics:
    topic_node(G, t, len(topic_profs.get(t, ())) or 1)
    for p in prof_topic:
        if prof_topic[p][t] >= 2 and p in G:
            G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
# topic -> subfield -> field hierarchy
for t in main_topics:
    ti = topic_info[t]; sf = "S" + ti["subfield"]; fd = "F" + ti["field"]
    if sf not in G: G.add_node(sf, kind="subfield", label=ti["subfield"], field=ti["field"], color=FIELD_COLOR.get(ti["field"], "#d4d4d8"), size=5)
    if fd not in G: G.add_node(fd, kind="field", label=ti["field"], field=ti["field"], color=FIELD_COLOR.get(ti["field"], "#d4d4d8"), size=9)
    G.add_edge("T" + t, sf, kind="hierarchy", weight=0.5, color="#f1f5f9", size=0.3)
    G.add_edge(sf, fd, kind="hierarchy", weight=0.5, color="#f1f5f9", size=0.5)
for n in [n for n, d in G.nodes(data=True) if d["kind"] == "subfield"]:
    G.nodes[n]["size"] = 3 + 0.8 * math.sqrt(G.degree(n))
# papers: every internal co-authored paper + each professor's 5 most-cited papers
paper_set = {w for ws in shared.values() for w in ws}
for p in profs:
    paper_set |= set(sorted(prof_works[p], key=lambda w: -(works[w]["cites"] or 0))[:5])
for w in paper_set:
    paper_node(G, w)
    for p in work_profs[w]:
        if p in G: G.add_edge(p, "W" + w, kind="authored", weight=1.0, color="#d4d4d8", size=0.3)
    t = works[w].get("topic")
    if t and "T" + t["id"] in G: G.add_edge("W" + w, "T" + t["id"], kind="paper_topic", weight=0.3, color="#f1f5f9", size=0.2)
add_coauth(G); add_sim(G)
add_innovation(G, 3)
index.append(export(G, "main", "主网：教授 · 主题 · 学科 · 论文 · 全部关系",
                    "所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。", 150))

# 2. co-authorship only
G = nx.Graph()
for p in profs:
    if p in details and details[p]["n_works"]: prof_node(G, p)
add_coauth(G); G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "coauthor", "合作网", "只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。"))

# 3. research similarity
G = nx.Graph()
for p in P: prof_node(G, p)
add_sim(G); G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "similarity", "研究相似网", "按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。"))

# 4. cross-disciplinary bridges
cross = lambda a, b: dept(a) != dept(b)
G = nx.Graph()
for p in profs:
    if p in details and details[p]["n_works"]: prof_node(G, p)
add_coauth(G, cross); add_sim(G, cross)
for t, ps in topic_profs.items():
    ds = {dept(p) for p in ps}
    if len(ds) >= 2:
        topic_node(G, t, len(ps))
        for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "cross", "交叉学科网", "只保留跨系（数学×物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。"))

# 5. per department
for dname, zh in [("Mathematics", "数学"), ("Physics", "物理"), ("Chemistry", "化学")]:
    G = nx.Graph()
    for p in profs:
        if dept(p) == dname and details[p]["n_works"]: prof_node(G, p)
    add_coauth(G); add_sim(G)
    for t, ps in topic_profs.items():
        ps = [p for p in ps if p in G]
        if len(ps) >= 2:
            topic_node(G, t, len(ps))
            for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
    index.append(export(G, "dept-" + dname.lower().replace(" ", "-"), f"{zh}系子网", f"主要论文属于{zh}的教授、他们共同的研究主题与内部合作/相似关系。"))

# 6. per research area, from OpenAlex subfields of each professor's papers (>= 15% of papers, top 3)
prof_sub = {}
for p in profs:
    c = collections.Counter(works[w]["topic"]["subfield"] for w in prof_works[p] if works[w].get("topic"))
    tot = sum(c.values()) or 1
    prof_sub[p] = [sf for sf, n in c.most_common(3) if n / tot >= 0.15]
    details[p]["areas"] = profs[p]["areas"] = "; ".join(prof_sub[p])
json.dump(details, open("site/data/profs.json", "w"), ensure_ascii=False)
AREA_GROUPS = [
    ("theory-hep", "高能 · 核物理 · 引力", ["Nuclear and High Energy Physics"]),
    ("astro", "天体物理与宇宙学", ["Astronomy and Astrophysics", "Space and Planetary Science"]),
    ("cmp-amo", "凝聚态 · 原子分子光学", ["Condensed Matter Physics", "Atomic and Molecular Physics, and Optics", "Statistical and Nonlinear Physics", "Electronic, Optical and Magnetic Materials"]),
    ("chem-bio", "有机 · 化学生物学", ["Organic Chemistry", "Biochemistry", "Molecular Biology", "Drug Discovery", "Molecular Medicine"]),
    ("chem-phys", "物理化学 · 无机 · 材料与催化", ["Physical and Theoretical Chemistry", "Inorganic Chemistry", "Materials Chemistry", "Catalysis", "Electrochemistry", "Spectroscopy", "Analytical Chemistry", "Polymers and Plastics"]),
    ("math-geom", "数学：几何 · 拓扑 · 分析", ["Geometry and Topology", "Analysis", "Mathematical Physics"]),
    ("math-nt", "数学：代数 · 数论 · 组合", ["Algebra and Number Theory", "Discrete Mathematics and Combinatorics", "Logic"]),
    ("math-prob", "数学：概率 · 应用与计算数学", ["Statistics and Probability", "Applied Mathematics", "Computational Mathematics", "Numerical Analysis", "Modeling and Simulation", "Control and Optimization"]),
]
for key, zh, subs in AREA_GROUPS:
    G = nx.Graph()
    for p in profs:
        if details[p]["n_works"] and set(prof_sub[p]) & set(subs): prof_node(G, p)
    if G.number_of_nodes() < 4: continue
    add_coauth(G); add_sim(G)
    for t, ps in topic_profs.items():
        ps = [p for p in ps if p in G]
        if len(ps) >= 2:
            topic_node(G, t, len(ps))
            for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
    index.append(export(G, "area-" + key, f"方向子网：{zh}", f"论文主要落在 OpenAlex 子领域「{' / '.join(subs)}」的教授（该子领域占其论文 ≥15%），他们的共同主题与合作/相似关系。"))

# 7. topic map (topics only, linked when the same professor works on both)
G = nx.Graph()
pair = collections.Counter()
for p, c in prof_topic.items():
    ts = [t for t, n in c.most_common(25) if n >= 2]
    for a, b in itertools.combinations(sorted(ts), 2): pair[(a, b)] += 1
used = {t for k in pair for t in k}
for t in used: topic_node(G, t, len(topic_profs.get(t, ())) or 1)
for (a, b), n in pair.items():
    if n >= 2: G.add_edge("T" + a, "T" + b, kind="cooccur", weight=float(n), color="#cbd5e1", size=0.3 + 0.5 * n)
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "topics", "研究主题地图", "研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。"))

G = nx.Graph()
for p in profs:
    if details[p]["n_works"]: prof_node(G, p)
add_innovation(G, 2); add_coauth(G)
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "innovation", "创新创业网",
    "教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 如有人工整理的教授创办公司（data/manual/startups.csv），一并列出；③ 教授之间的合写关系。"))
with open("data/processed/industry_links.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["openalex_id", "name", "dept", "company_id", "company", "country", "joint_works"])
    for p, c in prof_org.items():
        for o, n in c.most_common(): w.writerow([p, details[p]["name"], dept(p), o, org_info[o]["name"], org_info[o]["country"], n])

json.dump(index, open("site/data/index.json", "w"), ensure_ascii=False, indent=1)

# ---------- flat CSV exports ----------
with open("data/processed/professors.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["openalex_id", "name", "dept", "all_depts", "title", "n_works", "citations", "h_index", "top_topics"])
    for p, d in details.items():
        w.writerow([p, d["name"], d["dept"], d["depts"], d["title"], d["n_works"], d["cites"], d["h"], "; ".join(t for t, _ in d["topics"][:5])])
with open("data/processed/edges_coauthor.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["a", "b", "a_name", "b_name", "shared_works", "large_collab_works"])
    for k in sorted(set(coauth) | set(coauth_big)):
        w.writerow([k[0], k[1], details[k[0]]["name"], details[k[1]]["name"], coauth.get(k, 0), coauth_big.get(k, 0)])
with open("data/processed/edges_similarity.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["a", "b", "a_name", "b_name", "cosine"])
    for (a, b), s in sorted(sim_edges.items(), key=lambda x: -x[1]): w.writerow([a, b, details[a]["name"], details[b]["name"], round(s, 4)])
with open("data/processed/topics.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["topic_id", "topic", "subfield", "field", "n_profs", "depts"])
    for t, ps in sorted(topic_profs.items(), key=lambda x: -len(x[1])):
        ti = topic_info[t]; w.writerow([t, ti["name"], ti["subfield"], ti["field"], len(ps), "/".join(sorted({dept(p) for p in ps}))])
