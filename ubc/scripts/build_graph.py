"""Build the main network + themed sub-networks from matched professors and their OpenAlex works.

Inputs : data/processed/matches.csv, data/raw/openalex/works/*.jsonl
Outputs: site/data/<network>.json  (sigma/graphology format with precomputed x,y)
         site/data/profs.json      (details for the side panel)
         data/processed/{professors,edges_coauthor,edges_similarity,topics}.csv
"""
import csv, json, math, os, sys, collections, itertools, re
if os.environ.get("PYTHONHASHSEED") != "0":  # ties in top topics/subfields follow set order, which follows the string hash seed:
    os.environ["PYTHONHASHSEED"] = "0"         # pin it so two rebuilds of the same data give identical files
    os.execv(sys.executable, [sys.executable] + sys.argv)
import networkx as nx
import numpy as np

MIN_SCORE = 1.0          # minimum match score to trust an OpenAlex author match
BIG_COLLAB = 99          # works with more authors are "large collaborations" (OpenAlex lists at most 100 authorships, so 100 means truncated)
os.makedirs("site/data", exist_ok=True)

DEPT_COLOR = {"Mathematics": "#3b82f6", "Physics & Astronomy": "#ef4444", "Chemistry": "#10b981"}
DEPT_ZH = {"Mathematics": "数学", "Physics & Astronomy": "物理与天文", "Chemistry": "化学"}
CAMPUS_ZH = {"Vancouver": "温哥华", "Okanagan": "奥卡纳根"}
TRIUMF = "I1304378839"  # TRIUMF, the national particle-accelerator lab on the Vancouver campus
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
        profs[aid]["areas"] = "; ".join(x for x in (profs[aid]["areas"], r["areas"]) if x)
        continue
    profs[aid] = dict(r)
works = {}            # work id -> work
prof_works = collections.defaultdict(set)
for aid in profs:
    fn = f"data/raw/openalex/works/{aid}.jsonl"
    if not os.path.exists(fn): continue
    for line in open(fn):
        w = json.loads(line)
        if w.get("type") in ("erratum", "retraction", "paratext", "peer-review", "dataset", "supplementary-materials"): continue  # datasets: mostly CCDC crystal-structure depositions, up to ~200 per chemist
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
        name=profs[p]["name"], dept=dept(p), campus=profs[p]["campus"], depts=profs[p]["all_depts"], areas=profs[p]["areas"], title=profs[p]["title"], url=profs[p]["url"],
        openalex=f"https://openalex.org/{p}", orcid=profs[p]["orcid"], h=profs[p]["h_index"],
        n_works=len(prof_works[p]), cites=sum(works[w]["cites"] or 0 for w in prof_works[p]),
        years=[int(np.percentile(years, 3)), max(years)] if years else None,
        topics=[[topic_info[t]["name"], n] for t, n in prof_topic[p].most_common(10)],
        fields=fields.most_common(6),
        papers=[dict(t=works[w]["title"], y=works[w]["year"], c=works[w]["cites"], v=works[w]["venue"], d=works[w]["doi"] or f"https://openalex.org/{w}") for w in ws[:15]],
        coauthors=sorted(co, key=lambda x: -x[1]), collab=sorted(cob, key=lambda x: -x[1])[:20],
        similar=[[P[j], round(float(S[pix[p], j]), 3)] for j in np.argsort(-S[pix[p]])[:8]] if p in pix else [],
    )
qmi = set()
if os.path.exists("data/manual/qmi_investigators.csv"):
    for r in csv.DictReader(open("data/manual/qmi_investigators.csv")):
        if r["in_roster"].startswith("yes"): qmi.add(r["name"].replace("W. Andrew", "Andrew"))
tri_works = {p: sum(1 for w in prof_works[p] if TRIUMF in (works[w].get("own") or [])) for p in profs}
for p in details:
    details[p]["qmi"] = profs[p]["name"] in qmi
    details[p]["triumf"] = tri_works[p]
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
    G.add_node(p, kind="prof", label=d["name"], dept=d["dept"], campus=d["campus"], color=DEPT_COLOR[d["dept"]],
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
        if works[wid]["n_authors"] > BIG_COLLAB: continue  # a company on a 100+-author collaboration paper is not an industry tie
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
            sp = "founder" not in s["role"]
            G.add_edge(s["aid"], startup_node(G, s), kind="spinoff" if sp else "founded", weight=3.0, color="#fb7185" if sp else "#e11d48", size=1.5 if sp else 2.0)

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
index.append(export(G, "coauthor", "合作网", "只看教授之间真实合写的论文（作者少于 100 人的论文为深色边，≥100 作者的大型合作论文为浅色边）。"))

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
index.append(export(G, "cross", "交叉学科网", "只保留跨系（数学×物理与天文×化学，两个校区合计）的合作、相似关系，以及被至少两个系的教授共同研究的主题。"))

# 5. per department
for dname, zh in DEPT_ZH.items():
    G = nx.Graph()
    for p in profs:
        if dept(p) == dname and details[p]["n_works"]: prof_node(G, p)
    add_coauth(G); add_sim(G)
    for t, ps in topic_profs.items():
        ps = [p for p in ps if p in G]
        if len(ps) >= 2:
            topic_node(G, t, len(ps))
            for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
    index.append(export(G, "dept-" + re.sub(r"[^a-z]+", "-", dname.lower()), f"{zh}系子网", f"{zh}系教授（温哥华 + 奥卡纳根两个校区）、他们共同的研究主题与内部合作/相似关系。"))

# 5b. per campus
for cname, zh in CAMPUS_ZH.items():
    G = nx.Graph()
    for p in profs:
        if profs[p]["campus"] == cname and details[p]["n_works"]: prof_node(G, p)
    add_coauth(G); add_sim(G)
    for t, ps in topic_profs.items():
        ps = [p for p in ps if p in G]
        if len(ps) >= 2:
            topic_node(G, t, len(ps))
            for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
    index.append(export(G, "campus-" + cname.lower(), f"{zh}校区子网", f"{zh}校区数学、物理与天文、化学三系教授，他们共同的研究主题与合作/相似关系。"))

# 6. research-area sub-networks. Vancouver: research fields / areas listed on the department sites
#    (data/raw/roster/*_areas.txt, *_fields.txt). Okanagan: research interests on the directory profiles.
#    Plus QMI investigators (institute site) and TRIUMF co-affiliation (OpenAlex author affiliations on papers).
AREAS = [
    ("math-alg", "数学：代数 · 代数几何 · 数论 · 拓扑", "Mathematics", ["Algebra and Algebraic Geometry", "Number Theory", "Topology", "number theory", "algebraic topology", "arithmetic"]),
    ("math-ana", "数学：调和分析 · 偏微分方程 · 微分几何 · 数学物理", "Mathematics", ["Harmonic Analysis", "Partial Differential Equations", "Differential Geometry", "Mathematical Physics", "convex analysis", "variational"]),
    ("math-prob", "数学：概率 · 离散数学 · 组合", "Mathematics", ["Probability", "Discrete Mathematics", "Combinatori", "graph theory", "Stochastic"]),
    ("math-bio", "数学：数学生物 · 非线性动力学与应用偏微分方程", "Mathematics", ["Mathematical Biology", "Nonlinear Dynamics", "ecology"]),
    ("math-comp", "数学：流体 · 科学计算 · 信息数学与优化", "Mathematics", ["Fluids", "Scientific Computing", "Mathematics of Information", "optimization"]),
    ("phys-astro", "物理：天文 · 天体物理 · 宇宙学", "Physics & Astronomy", ["Astronomy & Astrophysics", "Astrophysics", "cosmology"]),
    ("phys-cmp", "物理：凝聚态 · 量子材料", "Physics & Astronomy", ["Condensed Matter", "superconductor"]),
    ("phys-amo-qi", "物理：原子分子光学 · 量子信息", "Physics & Astronomy", ["Atomic, Molecular & Optical", "Quantum Information"]),
    ("phys-particle", "物理：粒子与核物理", "Physics & Astronomy", ["Particle & Nuclear"]),
    ("phys-theory", "物理：理论物理 · 引力", "Physics & Astronomy", ["Theoretical Physics", "General relativity"]),
    ("phys-applied-med", "物理：应用物理 · 生物物理 · 医学物理", "Physics & Astronomy", ["Applied Physics", "Biophysics", "Medical"]),
    ("chem-org", "化学：有机 · 合成 · 催化", "Chemistry", ["Organic Chemistry", "Chemical Synthesis", "Catalytic Processes", "catalysis", "Natural product"]),
    ("chem-inorg-mat", "化学：无机 · 材料与高分子 · 界面与表面", "Chemistry", ["Inorganic Chemistry", "Materials & Polymer", "Interfacial and Surface", "Main-group", "Organometallic", "Surfaces", "carbon materials"]),
    ("chem-phys", "化学：物理与理论化学 · 化学物理 · 分子光谱", "Chemistry", ["Physical & Theoretical", "Chemical Physics", "Molecular Spectroscopy", "Computational", "spectroscopy"]),
    ("chem-bio-anal", "化学：生物与药物化学 · 分析 · 环境 · 核化学", "Chemistry", ["Biological & Medicinal", "Analytical Chemistry", "Environmental Chemistry", "Nuclear and Radiochemistry", "enzym", "metabol", "glycobiology", "Chemical biology", "Single-molecule", "Biosynthetic"]),
]
GROUPS = [(key, zh, f"院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「{' / '.join(kw[:4])}」等的{DEPT_ZH[dn]}系教授，他们的共同主题与合作/相似关系。",
           (lambda dn, kw: lambda p: dn in profs[p]["all_depts"].split("/") and any(k.lower() in (profs[p]["areas"] or "").lower() for k in kw))(dn, kw)) for key, zh, dn, kw in AREAS]
GROUPS += [
    ("qmi", "量子材料（Blusson 量子物质研究所 QMI 研究员）", "Stewart Blusson 量子物质研究所（QMI）官网 Investigators 名单中、属于物理与天文系和化学系的教授（data/manual/qmi_investigators.csv）。",
        lambda p: details[p]["qmi"]),
    ("triumf", "粒子 · 核 · 加速器（与 TRIUMF 联署）", "至少 5 篇论文同时署名 TRIUMF（加拿大国家粒子加速器实验室，位于温哥华校区）的教授（OpenAlex 作者机构）。",
        lambda p: tri_works[p] >= 5),
]
for key, zh, desc, pred in GROUPS:
    G = nx.Graph()
    for p in profs:
        if details[p]["n_works"] and pred(p): prof_node(G, p)
    if G.number_of_nodes() < 4: continue
    add_coauth(G); add_sim(G)
    for t, ps in topic_profs.items():
        ps = [p for p in ps if p in G]
        if len(ps) >= 2:
            topic_node(G, t, len(ps))
            for p in ps: G.add_edge(p, "T" + t, kind="topic", weight=math.log1p(prof_topic[p][t]), color="#e5e7eb", size=0.3)
    index.append(export(G, "area-" + key, f"方向子网：{zh}", desc))

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

# 7b. research institutes, hospitals and labs outside the university (OpenAlex institution types nonprofit / facility / government / healthcare)
inst_info = {}; prof_inst = collections.defaultdict(collections.Counter)
for p in profs:
    for wid in prof_works[p]:
        if works[wid]["n_authors"] > BIG_COLLAB: continue  # same for labs and institutes on collaboration papers
        for oid, oname, otype, cc in works[wid].get("orgs") or []:
            if otype == "company" or not oid: continue
            inst_info[oid] = dict(name=oname, type=otype, country=cc); prof_inst[p][oid] += 1
for p in details: details[p]["institutes"] = [[inst_info[o]["name"], n] for o, n in prof_inst[p].most_common(10)]
json.dump(details, open("site/data/profs.json", "w"), ensure_ascii=False)
G = nx.Graph()
for p in profs:
    if details[p]["n_works"]: prof_node(G, p)
inst_np = collections.Counter(o for p in prof_inst for o, n in prof_inst[p].items() if n >= 3)
for p, c in prof_inst.items():
    for o, n in c.items():
        if n < 3 or inst_np[o] < 2: continue
        if "I" + o not in G:
            G.add_node("I" + o, kind="institute", label=inst_info[o]["name"], country=inst_info[o]["country"], otype=inst_info[o]["type"], color="#0ea5e9", size=2 + 1.5 * math.sqrt(inst_np[o]))
        G.add_edge(p, "I" + o, kind="institute_link", weight=math.log1p(n), color="#7dd3fc", size=0.3 + 0.4 * math.log1p(n), n=n)
add_coauth(G)
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "institutes", "研究机构网",
    "教授与校外研究机构、国家实验室、医院和资助机构的联系（OpenAlex 机构类型 nonprofit / facility / government / healthcare）：同一机构与该教授合写 ≥3 篇、且至少连到 2 位教授才显示；另含教授之间的合写关系。"))

G = nx.Graph()
for p in profs:
    if details[p]["n_works"]: prof_node(G, p)
add_innovation(G, 2); add_coauth(G)
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
index.append(export(G, "innovation", "创新创业网",
    "教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司，以及公开资料称为其实验室衍生的公司（逐条附来源与原文摘录，见 data/manual/startups.csv）；③ 教授之间的合写关系。"))
with open("data/processed/industry_links.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["openalex_id", "name", "dept", "company_id", "company", "country", "joint_works"])
    for p, c in prof_org.items():
        for o, n in c.most_common(): w.writerow([p, details[p]["name"], dept(p), o, org_info[o]["name"], org_info[o]["country"], n])

json.dump(index, open("site/data/index.json", "w"), ensure_ascii=False, indent=1)

# ---------- flat CSV exports ----------
with open("data/processed/professors.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["openalex_id", "name", "dept", "campus", "all_depts", "title", "n_works", "citations", "h_index", "top_topics"])
    for p, d in details.items():
        w.writerow([p, d["name"], d["dept"], d["campus"], d["depts"], d["title"], d["n_works"], d["cites"], d["h"], "; ".join(t for t, _ in d["topics"][:5])])
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

# OpenAlex titles occasionally carry U+FFFD (undecodable characters); drop them from the published data
import glob
for fn in glob.glob("site/data/*.json"):
    s = open(fn, encoding="utf-8").read()
    if "\ufffd" in s: open(fn, "w", encoding="utf-8").write(s.replace("\ufffd", ""))
