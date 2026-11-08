"""China half of the industry report (chapter 07) and the China-US comparison.

Called by build_report.py. Inputs:
  data/manual/cn_companies.csv   curated Chinese companies (same columns as companies.csv plus *_en columns for English)
  data/manual/cn_market.json     Chinese deals, revenues, forecasts and sources
  data/raw/cn_company_works.jsonl  OpenAlex works with a CN/HK/MO company author (fetch_openalex_companies.py cn)
  data/raw/cn_professors.csv, cn_basemap.json  from cn-quantum-chem-map
Every visible Chinese string goes through T(zh, en) so build_report.py can write the English dictionary.
"""
import csv, json, math, os, re, collections, statistics
from build_report import (P, esc, num, fmt_usd, hbar, hstack, stacked_cols, lines, scatter, heat, legend, basemap_svg, proj,
                          CATS, CORDER, TIERS, T, norm_person)

USD_PER_RMB = 1 / 7.2   # conversion used for every RMB figure (stated on the page)

CITY = {
 "Beijing": (39.90, 116.40, "北京"), "Shanghai": (31.23, 121.47, "上海"), "Shenzhen": (22.54, 114.06, "深圳"), "Hangzhou": (30.27, 120.15, "杭州"),
 "Hefei": (31.82, 117.23, "合肥"), "Guangzhou": (23.13, 113.26, "广州"), "Suzhou": (31.30, 120.62, "苏州"), "Chengdu": (30.57, 104.07, "成都"),
 "Wuhan": (30.59, 114.31, "武汉"), "Hong Kong": (22.32, 114.17, "香港"), "Nanjing": (32.06, 118.80, "南京"), "Tianjin": (39.08, 117.20, "天津"),
 "Yantai": (37.46, 121.45, "烟台"), "Ningde": (26.66, 119.55, "宁德"), "Lianyungang": (34.60, 119.22, "连云港"), "Xi'an": (34.34, 108.94, "西安"),
 "Changsha": (28.23, 112.94, "长沙"), "Jinan": (36.65, 117.12, "济南"), "Dalian": (38.91, 121.61, "大连"), "Xiamen": (24.48, 118.09, "厦门"),
 "Qingdao": (36.07, 120.38, "青岛"), "Shijiazhuang": (38.04, 114.51, "石家庄"), "Zhuhai": (22.27, 113.58, "珠海"), "Taizhou": (32.46, 119.92, "泰州"),
}
CN_MAP = dict(file="cn_basemap.json", par=(25, 47, 0, 105), box=[(74, 18), (134, 18), (78, 53), (130, 53), (105, 54), (105, 17)],
              clip=lambda lon, lat: lon < 60 or lon > 150 or lat < 5, label=T("中国量子化学/计算化学企业总部地图", "Map of Chinese quantum/computational chemistry company headquarters"),
              names=[(T("北京", "Beijing"), 116.4, 39.9, 0, -30), (T("上海", "Shanghai"), 121.47, 31.23, 46, 8), (T("杭州", "Hangzhou"), 120.15, 30.27, 34, 36),
                     (T("合肥", "Hefei"), 117.23, 31.82, -40, -14), (T("深圳 / 香港", "Shenzhen / Hong Kong"), 114.1, 22.4, 0, 40), (T("成都", "Chengdu"), 104.07, 30.57, 0, -24)])

def cluster(c):
    city = c["city"]
    if city in ("Beijing", "Tianjin", "Shijiazhuang"): return T("京津冀", "Beijing–Tianjin–Hebei")
    if city == "Shanghai": return T("上海", "Shanghai")
    if city in ("Hangzhou", "Suzhou", "Nanjing", "Taizhou", "Lianyungang"): return T("长三角其他（杭州/苏州/南京）", "Other Yangtze Delta (Hangzhou/Suzhou/Nanjing)")
    if city == "Hefei": return T("合肥", "Hefei")
    if city in ("Shenzhen", "Guangzhou", "Hong Kong", "Zhuhai"): return T("粤港澳大湾区", "Greater Bay Area")
    return T("其他地区", "Other regions")

# OpenAlex corpus sectors for Chinese companies (finer than the NA list: state-owned energy and metals dominate)
CN_RULES = [
    ("QC", r"origin quantum|quantumctek|spinq|qboson|turingq|quantum"),
    ("AISW", r"xtalpi|jingtai|hongzhiwei|dp technology|deep potential|shenshi|mindrank|stonewise|metis|helixon|biomap|moleculemind|insilico|megarobo|dptech"),
    ("TECH", r"bytedance|tencent|huawei|microsoft research asia|alibaba|baidu|inspur|china mobile|china telecom|china unicom|\bjd\b|sensetime|iflytek|zte|lenovo|sugon|hikvision|ant group|meituan|netease|kuaishou|xiaomi|beijing academy of artificial"),
    ("PHARMA", r"pharma|wuxi|hengrui|biotech|medicine|biopharm|drug|cspc|sino biopharm|fosun|innovent|beigene|hutchmed|hitgen|pharmaron|medical|health|bio-|biolog|genomics|bgi"),
    ("BATT", r"contemporary amperex|catl|\bbyd\b|saic|first automotive|faw|weichai|geely|gotion|eve energy|svolt|great wall motor|dongfeng|changan|gac|battery|lithium|ganfeng|tianqi"),
    ("ENERGY", r"sinopec|petroleum|petrochina|cnooc|offshore oil|oil|oilfield|energy|power|grid|nuclear|coal|huadian|three gorges|chn energy|electric|cgn|spic|huaneng|datang|guodian|cnpc|yanchang|shenhua|gas|ccteg"),
    ("METAL", r"nonferrous|steel|iron|ansteel|baosteel|shougang|aluminum|metal|mining|zijin|grinm|baogang|hbis|pangang|chinalco|abrasives|advanced technology & materials|building materials|jiuquan|taiyuan|magnesium|rare earth|tungsten|copper|titanium"),
    ("CHEM", r"chemical|chemistry|sinochem|wanhua|kingfa|yuntianhua|organic|chemchina|hengli|rongsheng|zhejiang longsheng|polymer|plastics|coating|fertilizer|syngenta|petrochemical"),
    ("DEF", r"aero engine|aviation|avic|avichina|north industries|norinco|aerospace|electronics technology group|shipbuilding|state shipbuilding|commercial aircraft|aircraft|crrc|casc|casic|academy of machinery|southwest technology|ordnance|weapon|nuclear industry|engineering physics|space"),
]
CN_SECTORS = {
    "ENERGY": (T("能源、电网与核电", "Energy, grid and nuclear"), "var(--a-md)"),
    "METAL": (T("钢铁、有色与建材", "Steel, non-ferrous metals and building materials"), "var(--c-gov)"),
    "CHEM": (T("化工", "Chemicals"), "var(--a-mat)"),
    "BATT": (T("电池与汽车", "Batteries and automotive"), "var(--a-ex)"),
    "DEF": (T("军工、航空航天与装备", "Defence, aerospace and heavy equipment"), "var(--c-info)"),
    "TECH": (T("科技巨头与 AI 实验室", "Tech giants and AI labs"), "var(--c-tech)"),
    "PHARMA": (T("医药与 CRO", "Pharma and CROs"), "var(--a-ml)"),
    "AISW": (T("计算化学软件与 AI 发现", "Computational chemistry software and AI discovery"), "var(--a-es)"),
    "QC": (T("量子计算（化学应用）", "Quantum computing (chemistry applications)"), "var(--a-rd)"),
    "OTHER": (T("其他 / 未分类", "Other / unclassified"), "var(--c-other)"),
}
# common buckets for the China–US comparison
BUCKET = {"na": {"SW": "AI", "AIDD": "AI", "AIMAT": "AI", "INFO": "AI", "QC": "QC", "PHARMA": "PH", "CHEM": "IND", "TECH": "TECH", "GOV": "DEF", "OTHER": "OTH"},
          "cn": {"AISW": "AI", "QC": "QC", "PHARMA": "PH", "ENERGY": "IND", "METAL": "IND", "CHEM": "IND", "BATT": "IND", "TECH": "TECH", "DEF": "DEF", "OTHER": "OTH"}}
BUCKETS = [("IND", T("能源、化工、材料与制造", "Energy, chemicals, materials and manufacturing"), "var(--a-md)"),
           ("TECH", T("科技巨头", "Tech giants"), "var(--c-tech)"),
           ("PH", T("医药", "Pharma"), "var(--a-ex)"),
           ("DEF", T("军工航天 / 政府承包", "Defence, aerospace / government contractors"), "var(--c-gov)"),
           ("AI", T("专业软件与 AI 发现", "Specialist software and AI discovery"), "var(--a-es)"),
           ("QC", T("量子计算", "Quantum computing"), "var(--a-rd)"),
           ("OTH", T("其他", "Other"), "var(--c-other)")]

NOT_COMPANY = re.compile(r"^$")

def cn_sector(name):
    n = (name or "").lower()
    for k, rx in CN_RULES:
        if re.search(rx, n): return k
    return "OTHER"

def clean(n): return re.sub(r"\s*\((China|Hong Kong|Macao|Macau)\)\s*$", "", n or "")

def gbar(rows, series, label, w=640, lw=190, bh=11, gap=10, fmt=lambda v: f"{v:,.0f}"):
    """grouped horizontal bars. rows: [label]; series: [(name, color, [values])]"""
    k = len(series); h = 24 + len(rows) * (k * bh + gap)
    vmax = max([v for s in series for v in s[2]] + [1])
    from build_report import ticks, tl, svg_open, TIPJS_ATTR
    tk, top = ticks(vmax); x0, x1 = lw, w - 64
    sx = lambda v: x0 + (x1 - x0) * v / top
    o = [svg_open(w, h, label)]
    for t in tk:
        o.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="14" y2="{h-4}" stroke="var(--grid)"/><text x="{sx(t):.1f}" y="10" text-anchor="middle" fill="var(--muted)" font-size="10.5">{tl(t)}</text>')
    for i, r in enumerate(rows):
        y = 20 + i * (k * bh + gap)
        o.append(f'<text x="{x0-8}" y="{y+k*bh/2+4:.1f}" text-anchor="end" fill="var(--ink-2)">{esc(r)}</text>')
        for j, (nm, c, vals) in enumerate(series):
            v = vals[i]; yy = y + j * bh
            o.append(f'<rect x="{x0}" y="{yy}" width="{max(1.2, sx(v)-x0):.1f}" height="{bh-1.5}" rx="2" fill="{c}"{TIPJS_ATTR(f"{r} · {nm}：{fmt(v)}")}/>'
                     f'<text x="{sx(v)+4:.1f}" y="{yy+bh-3:.1f}" fill="var(--ink-2)" font-family="var(--mono)" font-size="10">{esc(fmt(v))}</text>')
    o.append("</svg>")
    return "".join(o)


def build(ctx):
    """ctx: F_ (figure factory), charts, sec, NA stats. Returns dict with sections, stats, companies."""
    F_, charts, sec = ctx["F_"], ctx["charts"], ctx["sec"]
    C = list(csv.DictReader(open(P("data", "manual", "cn_companies.csv"), encoding="utf-8")))
    M = json.load(open(P("data", "manual", "cn_market.json"), encoding="utf-8"))
    profs = list(csv.DictReader(open(P("data", "raw", "cn_professors.csv"), encoding="utf-8")))
    prof_by_id = {p["openalex_id"]: p for p in profs}
    prof_by_name = collections.defaultdict(list)
    for p in profs: prof_by_name[norm_person(p["name"])].append(p)
    inst_zh = {}
    try:
        for r in csv.DictReader(open(P("data", "raw", "cn_institutions.csv"), encoding="utf-8")):
            if r.get("name_zh"): inst_zh[r["name"]] = r["name_zh"]
    except FileNotFoundError: pass

    # ---- translate the data columns once
    for c in C:
        for col in ("name", "subfields", "last_round", "note", "status"):
            if c.get(col) and c.get(col + "_en"): T(c[col], c[col + "_en"])
        for a, b in zip([x for x in c["subfields"].split(";") if x], [x for x in c.get("subfields_en", "").split(";") if x]):
            T(a.strip(), b.strip())
        c["f"] = num(c["funding_musd"]); c["v"] = num(c["valuation_musd"]); c["rev"] = num(c["revenue_musd"])
        c["emp"] = num(c["employees"]); c["yr"] = int(c["founded"]) if c["founded"] else None
        c["lat"], c["lon"], c["city_zh"] = CITY[c["city"]]
        T(c["city_zh"], c["city"])
        c["founders"] = [x.strip() for x in c["academic_founders"].split(";") if x.strip()]
        c["univs"] = [x.strip() for x in c["univ_links"].split(";") if x.strip()]
        c["prof_matches"] = [p for fd in c["founders"] for p in prof_by_name.get(norm_person(fd), [])]
    n = len(C)

    # ---- corpus
    works = [json.loads(l) for l in open(P("data", "raw", "cn_company_works.jsonl"), encoding="utf-8")]
    comp = {}; yr_sector = collections.defaultdict(collections.Counter); comp_univ = collections.Counter(); univ_names = {}
    prof_comp = collections.defaultdict(collections.Counter); n_cw = 0
    for w in works:
        cs = {}; us = {}
        for a in w["au"]:
            for i in a["i"]:
                if i["t"] == "company" and i["c"] in ("CN", "HK", "MO"):
                    cs[i["id"]] = i
                    d = comp.setdefault(i["id"], {"id": i["id"], "name": clean(i["n"]), "country": i["c"], "papers": 0, "cites": 0, "authors": set(), "years": collections.Counter()})
                    d["authors"].add(a["a"])
                elif i["t"] == "education" and i["c"] in ("CN", "HK", "MO"):
                    us[i["id"]] = i["n"]
        if not cs: continue
        n_cw += 1
        for cid in cs:
            d = comp[cid]; d["papers"] += 1; d["cites"] += w["cites"] or 0; d["years"][w["year"]] += 1
        for s in {cn_sector(comp[cid]["name"]) for cid in cs}: yr_sector[w["year"]][s] += 1
        for cid in cs:
            for uid, un in us.items(): comp_univ[(cid, uid)] += 1; univ_names[uid] = un
        for a in w["au"]:
            if a["a"] in prof_by_id:
                for cid in cs: prof_comp[a["a"]][cid] += 1
    for d in comp.values(): d["sector"] = cn_sector(d["name"]); d["nauth"] = len(d["authors"])
    CL = sorted(comp.values(), key=lambda d: -d["papers"]); n_comp = len(CL)
    sec_papers = collections.Counter(); sec_counts = collections.Counter()
    for d in CL: sec_papers[d["sector"]] += d["papers"]; sec_counts[d["sector"]] += 1

    with open(P("data", "processed", "cn_corpus_companies.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["openalex_id", "name", "country", "sector", "papers", "authors", "citations", "first_year", "last_year", "papers_2020_plus"])
        for d in CL:
            ys = [y for y in d["years"] if y]
            wr.writerow([d["id"], d["name"], d["country"], CN_SECTORS[d["sector"]][0], d["papers"], d["nauth"], d["cites"], min(ys), max(ys), sum(v for y, v in d["years"].items() if y and y >= 2020)])
    with open(P("data", "processed", "cn_professor_company_links.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["professor_id", "professor", "institution", "company_id", "company", "co_papers"])
        for pid, cc in prof_comp.items():
            for cid, v in cc.most_common(): wr.writerow([pid, prof_by_id[pid]["name"], prof_by_id[pid]["institution"], cid, comp[cid]["name"], v])

    # ---- curated stats
    by_cat = collections.Counter(c["category"] for c in C)
    by_status = collections.Counter(c["status"] for c in C)
    funded = [c for c in C if c["f"]]
    fund_total = sum(c["f"] for c in funded)
    fund_AB = sum(c["f"] for c in funded if c["funding_conf"] in ("A", "B"))
    fund_cat = collections.Counter(); fund_cat_c = collections.Counter()
    for c in funded: (fund_cat if c["funding_conf"] in ("A", "B") else fund_cat_c)[c["category"]] += c["f"]
    with_founders = [c for c in C if c["founders"]]
    univ_ct = collections.Counter(u for c in C for u in c["univs"])
    young = [c for c in C if c["yr"] and c["yr"] >= 2015]
    by_cluster = collections.Counter(cluster(c) for c in C)
    fund_cluster = collections.Counter()
    for c in funded: fund_cluster[cluster(c)] += c["f"]
    listed = [c for c in C if c["status"] == "上市"]
    cat_leg = legend([(CATS[k][0], CATS[k][1]) for k in CORDER])
    S = {}

    # ================= C1 landscape
    s1 = []
    s1.append(F_(T("中国：八大赛道的公司数量", "China: companies in the eight segments"), T(f"本报告精选收录的 {n} 家中国企业", f"The {n} Chinese companies selected for this report"),
                 hbar([(CATS[k][0], by_cat[k], CATS[k][1]) for k in sorted(CORDER, key=lambda k: -by_cat[k]) if by_cat[k]], T("中国公司数量按赛道", "Chinese companies by segment"), unit=" 家", lw=170),
                 T("赛道定义与北美部分完全相同；「大型药企计算化学部门」在中国包括药明康德、康龙化成等 CRO。", "Segments are defined exactly as in the North American part; in China \"large pharma computational chemistry\" also covers CROs such as WuXi AppTec and Pharmaron.")))
    tier_series = [(t, col, [sum(1 for c in C if c["category"] == k and c["tier"] == t) for k in CORDER]) for t, col in zip(TIERS, ["var(--a-md)", "var(--a-mat)", "var(--a-es)"])]
    s1.append(F_(T("中国：规模结构", "China: size structure"), "各赛道内三个规模层级的公司数", legend([(t, c) for t, c, _ in tier_series]) +
                 stacked_cols([CATS[k][0].split("（")[0].replace("与", "/")[:6] for k in CORDER], tier_series, T("中国规模结构", "China size structure"), unit=" 家")))
    bins = list(range(1950, 2030, 5))
    yr_series = [(CATS[k][0], CATS[k][1], [sum(1 for c in C if c["category"] == k and c["yr"] and b <= c["yr"] < b + 5) for b in bins]) for k in CORDER]
    first = next(i for i, b in enumerate(bins) if any(s[2][i] for s in yr_series))
    s1.append(F_(T("中国：成立年份", "China: founding years"), T("每 5 年成立的公司数", "Companies founded per five-year period"), cat_leg +
                 stacked_cols([f"{b}–{str(b+4)[2:]}" for b in bins[first:]], [(a, b_, v[first:]) for a, b_, v in yr_series], T("中国成立年份", "China founding years"), unit=" 家"),
                 T("国企和药企大多成立于 2000 年前；专业软件、AI 药物发现与量子计算公司几乎全部成立于 2015 年后，2018–2021 年是创业高峰。", "State-owned and pharma companies mostly predate 2000; nearly all specialist software, AI drug discovery and quantum companies were founded after 2015, peaking in 2018–2021."), wide=True))
    T("国有", "State-owned")
    st_rows = [(s, by_status[s], None) for s in ["私营", "上市", "国有", "被收购", "已关闭", "不明"] if by_status[s]]
    s1.append(F_(T("中国：企业状态", "China: ownership status"), "当前所有权状态", hbar(st_rows, T("中国企业状态", "China ownership status"), unit=" 家", lw=80),
                 T("「国有」指央企或地方国企及其研究院；中国大型企业中国有比例远高于北美。", "\"State-owned\" means central or local state-owned enterprises and their research institutes; far more of China's large companies are state-owned than in North America.")))
    exch = collections.Counter()
    for c in listed:
        t = c["ticker"]
        exch[T("科创板", "STAR Market") if t.startswith("688") else T("港交所", "HKEX") if t.endswith(".HK") else T("沪深主板/创业板", "Shanghai/Shenzhen main boards and ChiNext") if re.match(r"^\d{6}", t) else T("海外", "Overseas")] += 1
    s1.append(F_(T("上市地点", "Listing venues"), T("上市公司的交易所分布", "Exchanges of the listed companies"), hbar([(k, v, "var(--accent)") for k, v in exch.most_common()], T("上市地点", "Listing venues"), unit=" 家", lw=150),
                 T("科创板和港交所 18C 章是硬科技公司的主要上市通道：晶泰科技 2024 年成为首家 18C 上市公司。", "The STAR Market and HKEX Chapter 18C are the main listing routes for deep-tech companies; XtalPi became the first Chapter 18C listing in 2024.")))

    # ================= C2 geography
    pts = []
    for c in C:
        r = 4 + (math.sqrt(c["f"]) / 6 if c["f"] else 0) + (3 if c["tier"] == "大型" else 0)
        tip = f"{c['name']} · {c['city_zh']}\n{CATS[c['category']][0]} · {c['tier']} · 成立 {c['founded']}" + (f"\n融资 {fmt_usd(c['f'])}" if c["f"] else "")
        pts.append((c["lon"], c["lat"], CATS[c["category"]][1], min(r, 16), tip, c["category"]))
    s2 = [ctx["mapfig"](T("中国企业总部真实地理分布", "Where Chinese company headquarters are"), basemap_svg(pts, w=900, h=700, cfg=CN_MAP), "cnmap",
                        T("坐标为总部城市中心；同城多家公司按螺旋错开。底图沿用本站「中国量化地图」。", "Positions are HQ city centres; companies in the same city are spread on a small spiral. Basemap as in this site's China QC map."))]
    cl = [k for k, _ in by_cluster.most_common()]
    s2.append(F_(T("中国产业集群：公司数", "Chinese clusters: companies"), "按总部所在都会区归并", hbar([(k, by_cluster[k], "var(--accent)" if k != "其他地区" else "var(--c-other)") for k in cl], T("中国集群公司数", "Chinese clusters by company count"), unit=" 家", lw=210)))
    s2.append(F_(T("中国产业集群：已知融资", "Chinese clusters: known funding"), "私营公司累计融资（含估计）", hbar([(k, fund_cluster[k], "var(--accent)" if k != "其他地区" else "var(--c-other)") for k in sorted(fund_cluster, key=lambda k: -fund_cluster[k])], T("中国集群融资", "Chinese clusters by funding"), lw=210, fmt=fmt_usd),
                 T("北京（华深智药、深势、百图生科、玻色）一家独大，上海（新生探途、图灵、不筹）和大湾区（量旋、英矽 IPO）其次；合肥是「量子之都」，本源、国盾、国仪都在这里。上市公司的二级市场融资不计入。", "Beijing (Helixon, DP Technology, BioMap, QBoson) leads by far, followed by Shanghai (Anew Labs, TuringQ, Buchou) and the Greater Bay Area (SpinQ, the Insilico IPO); Hefei is the \"quantum capital\", home to Origin Quantum, QuantumCTek and CIQTEK. Secondary-market money raised by listed companies is not counted.")))
    s2.append(F_(T("中国：集群 × 赛道", "China: cluster × segment"), "每个集群在各赛道的公司数", heat([r.split("（")[0] for r in cl], [CATS[k][0].split("（")[0][:7] for k in CORDER], [[sum(1 for c in C if cluster(c) == r and c["category"] == k) for k in CORDER] for r in cl], T("中国集群赛道热力图", "China cluster-by-segment heatmap"))))

    # ================= C3 capital
    s3 = []
    fc_rows = [k for k in sorted(CORDER, key=lambda k: -(fund_cat[k] + fund_cat_c[k])) if fund_cat[k] + fund_cat_c[k] > 0]
    s3.append(F_(T("中国：各赛道累计股权融资", "China: cumulative equity funding by segment"), "私营公司已披露累计融资；深色 = 有公开报道，浅色 = 本报告估计",
                 legend([("有来源（A/B）", "var(--accent)"), ("估计（C）", "var(--c-est)")]) + hstack([(CATS[k][0], [fund_cat[k], fund_cat_c[k]]) for k in fc_rows], ["var(--accent)", "var(--c-est)"], ["有来源", "估计"], T("中国赛道融资", "China funding by segment")),
                 T(f"人民币金额按 1 美元 = 7.2 元折算。上市公司 IPO 募资计入其上市前累计融资（如晶泰科技、国盾量子），与北美口径略有不同。", "RMB amounts converted at US$1 = RMB 7.2. For listed companies, IPO proceeds are included in cumulative funding (e.g. XtalPi, QuantumCTek), slightly unlike the North American basis.")))
    top_f = sorted(funded, key=lambda c: -c["f"])[:15]
    s3.append(F_(T("中国：融资额前 15 的公司", "China: top 15 companies by funding"), "累计股权融资（百万美元）",
                 hbar([(c["name"].split("（")[0][:20], c["f"], CATS[c["category"]][1] if c["funding_conf"] != "C" else "var(--c-est)", f"{c['name']}：{fmt_usd(c['f'])}（{c['funding_conf']}）") for c in top_f], T("中国融资前15", "China top 15 by funding"), lw=180, fmt=fmt_usd, bh=16, gap=5),
                 T("浅灰色条为估计值。", "Light grey bars are estimates.")))
    deals = M["deals"]
    for d in deals: T(d["name"], d["name_en"]); T(d["note"], d.get("note_en", d["note"])) if d["note"] else None; T(d["type"], {"并购": "M&A", "融资": "Funding", "IPO": "IPO", "资产交易": "Asset deal"}.get(d["type"], d["type"]))
    s3.append(F_(T("中国：重大交易时间线", "China: timeline of major deals"), "并购、IPO、超大额融资与授权交易（金额，百万美元）",
                 hbar([(f"{d['year']} · {d['name']}", d["usd_m"], "var(--a-ex)" if d["type"] == "资产交易" else "var(--a-rd)" if d["type"] == "IPO" else "var(--accent)", f"{d['year']} {d['name']}：{fmt_usd(d['usd_m'])}") for d in sorted(deals, key=lambda d: d["year"])],
                      T("中国交易时间线", "China deal timeline"), w=720, lw=300, fmt=fmt_usd, bh=15, gap=5),
                 legend([(T("授权/资产交易", "Licensing / asset deal"), "var(--a-ex)"), ("IPO", "var(--a-rd)"), (T("融资", "Funding"), "var(--accent)")]) +
                 T("授权交易金额为「潜在总额」（含里程碑），实际首付款通常只占一小部分。", "Licensing amounts are headline totals including milestones; the upfront payment is usually a small fraction."), wide=True))
    deal_tbl = ('<div class="tbl-wrap"><table class="data"><thead><tr><th class="n">年份</th><th>交易</th><th>类型</th><th class="n">金额</th><th>说明</th><th>来源</th></tr></thead><tbody>' +
                "".join(f'<tr><td class="n">{d["year"]}</td><td>{esc(d["name"])}</td><td>{esc(d["type"])}</td><td class="n">{fmt_usd(d["usd_m"])}</td><td style="white-space:normal">{esc(d["note"])}</td><td><a href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["src"])}</a></td></tr>' for d in sorted(deals, key=lambda d: (-d["year"], -d["usd_m"]))) +
                "</tbody></table></div>")

    # ================= C4 revenue
    s4 = []
    pub = M["public_revenue"]
    for r in pub: T(r["name"], r["name_en"]); T(r["fy"], r.get("fy_en", r["fy"]))
    s4.append(F_(T("中国上市公司最新年收入", "Latest annual revenue of Chinese listed companies"), "最新完整财年（百万美元）",
                 hbar([(f"{r['name']}（{r['fy']}）", r["usd_m"], r.get("color") or "var(--accent)", f"{r['name']} {r['fy']}：{fmt_usd(r['usd_m'])}") for r in sorted(pub, key=lambda r: -r["usd_m"])], T("中国上市公司收入", "Chinese listed company revenue"), lw=230, fmt=fmt_usd),
                 T("药明康德一家的收入就比北美全部计算化学软件上市公司加起来大一个数量级——但它卖的是外包实验与生产服务，计算化学只是其中一环。", "WuXi AppTec alone earns an order of magnitude more than all North American listed computational chemistry software companies combined, but it sells outsourced lab and manufacturing services, of which computation is only one part.")))
    hist = M["revenue_history"]
    for k in hist: T(k, hist[k]["name_en"])
    yrs = sorted({int(y) for s in hist.values() for y in s["data"]})
    s4.append(F_(T("收入轨迹：晶泰科技、国仪量子、成都先导、国盾量子", "Revenue paths: XtalPi, CIQTEK, HitGen, QuantumCTek"), "历年收入（百万美元）", legend([(k, v["color"]) for k, v in hist.items()]) +
                 lines(yrs, [(k, v["color"], [v["data"].get(str(y)) for y in yrs], False) for k, v in hist.items()], T("中国收入轨迹", "China revenue paths"), unit="M", yfmt=lambda v: f"${v:g}M"),
                 T("人民币按 7.2 折算。", "RMB converted at 7.2.")))

    # ================= C5 forecasts / macro
    s5 = []
    for blk in M["macro_charts"]:
        T(blk["title"], blk["title_en"]); T(blk["sub"], blk["sub_en"]); T(blk["cap"], blk["cap_en"])
        s5.append(F_(blk["title"], blk["sub"], hbar([(str(k), v, blk.get("color", "var(--a-rd)")) for k, v in blk["data"].items()], blk["title"], lw=80, fmt=lambda v, u=blk["unit"]: f"{u}{v:g}"), blk["cap"]))
    ys_fit = list(range(2015, 2026)); yv = [sum(yr_sector[y].values()) for y in ys_fit]
    mx_, my_ = statistics.mean(ys_fit), statistics.mean(yv)
    slope = sum((a - mx_) * (b - my_) for a, b in zip(ys_fit, yv)) / sum((a - mx_) ** 2 for a in ys_fit); icpt = my_ - slope * mx_
    # China grows faster than linearly: fit log-linear too and show both
    lv = [math.log(max(v, 1)) for v in yv]; ml = statistics.mean(lv)
    gs = sum((a - mx_) * (b - ml) for a, b in zip(ys_fit, lv)) / sum((a - mx_) ** 2 for a in ys_fit); gi = ml - gs * mx_
    proj_x = list(range(2005, 2031))
    s5.append(F_(T("中国企业参与学术研究的趋势与外推", "Chinese company participation in research: trend and extrapolation"), T("中国企业作者参与的量子/计算化学论文数（OpenAlex），2026–2030 为外推", "Quantum/computational chemistry papers with a Chinese company author (OpenAlex); 2026–2030 extrapolated"),
                 legend([(T("实际", "Actual"), "var(--cn)"), (T("线性外推", "Linear extrapolation"), "var(--a-mat)"), (T("指数外推", "Exponential extrapolation"), "var(--a-ex)")]) +
                 lines(proj_x, [("实际", "var(--cn)", [sum(yr_sector[y].values()) if y <= 2025 else None for y in proj_x], False),
                                ("线性", "var(--a-mat)", [round(icpt + slope * y) if y >= 2025 else None for y in proj_x], True),
                                ("指数", "var(--a-ex)", [round(math.exp(gi + gs * y)) if y >= 2025 else None for y in proj_x], True)], T("中国论文外推", "China paper extrapolation"), vline=2025),
                 T(f"2015–2025 年中国企业论文年均增长约 {(math.exp(gs)-1)*100:.0f}%（对数线性拟合）。线性外推 2030 年约 {icpt+slope*2030:.0f} 篇，指数外推约 {math.exp(gi+gs*2030):.0f} 篇；两者之间的差距就是不确定性。统计外推，不是预测。",
                   f"Papers with Chinese company authors grew about {(math.exp(gs)-1)*100:.0f}% a year in 2015–2025 (log-linear fit). A linear extrapolation gives about {icpt+slope*2030:.0f} papers in 2030 and an exponential one about {math.exp(gi+gs*2030):.0f}; the gap between them is the uncertainty. A statistical extrapolation, not a forecast."), wide=True))
    for f in M["forecasts"]:
        for k in ("metric", "base", "target", "kind", "src", "cagr"): T(f[k], f[k + "_en"]) if f.get(k + "_en") else None
    fc_tbl = ('<div class="tbl-wrap"><table class="data"><thead><tr><th>指标</th><th class="n">基准值</th><th class="n">预测值</th><th class="n">年复合增速</th><th>性质</th><th>来源</th></tr></thead><tbody>' +
              "".join(f'<tr><td>{esc(f["metric"])}</td><td class="n">{esc(f["base"])}</td><td class="n">{esc(f["target"])}</td><td class="n">{esc(f["cagr"])}</td><td>{esc(f["kind"])}</td><td><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["src"])}</a></td></tr>' for f in M["forecasts"]) + "</tbody></table></div>")

    # ================= C6 corpus footprint
    s6 = []
    order = sorted(CN_SECTORS, key=lambda k: -sec_papers[k])
    s6.append(F_(T("中国论文足迹：哪些行业在做量子/计算化学", "China's paper footprint: which industries do quantum/computational chemistry"), T(f"{n_comp} 家中国企业在 OpenAlex 语料中的论文数（按行业）", f"Papers by {n_comp} Chinese companies in the OpenAlex corpus (by industry)"),
                 hbar([(CN_SECTORS[k][0], sec_papers[k], CN_SECTORS[k][1], f"{CN_SECTORS[k][0]}：{sec_counts[k]} 家，{sec_papers[k]:,} 篇") for k in order], T("中国行业论文", "China papers by industry"), lw=230, unit=" 篇"),
                 T("与北美最大的不同：中国企业论文的主力是能源、电网、钢铁有色和军工国企及其研究院，专业软件与 AI 公司占比很小。", "The biggest difference from North America: Chinese corporate papers come mostly from state-owned energy, grid, steel/metals and defence groups and their institutes; specialist software and AI companies are a small share.")))
    for d in CL[:25]: T(d["name"], d["name"])
    s6.append(F_(T("中国企业论文 Top 25", "Top 25 Chinese companies by papers"), T("量子/计算化学论文最多的中国企业", "Chinese companies with the most quantum/computational chemistry papers"),
                 hbar([(d["name"][:30], d["papers"], CN_SECTORS[d["sector"]][1], f"{d['name']}：{d['papers']} 篇，被引 {d['cites']:,}") for d in CL[:25]], T("中国企业论文Top25", "China top 25"), lw=250, unit=" 篇", bh=15, gap=4)))
    yr_x = list(range(2005, 2026))
    s6.append(F_(T("中国各行业企业论文的年度变化", "Chinese corporate papers by industry and year"), "每年有该行业企业作者参与的论文数（2005–2025）", legend([(CN_SECTORS[k][0], CN_SECTORS[k][1]) for k in order]) +
                 stacked_cols([str(y) for y in yr_x], [(CN_SECTORS[k][0], CN_SECTORS[k][1], [yr_sector[y][k] for y in yr_x]) for k in order], T("中国行业年度论文", "China papers by industry per year"), unit=" 篇"),
                 T("2019 年后增长明显加速，字节跳动、腾讯、华为等科技公司从无到有。", "Growth speeds up after 2019, and tech companies such as ByteDance, Tencent and Huawei appear from nothing."), wide=True))
    top_u = collections.Counter()
    for (cid, uid), v in comp_univ.items(): top_u[uid] += v
    for u, _ in top_u.most_common(15): T(univ_names[u], univ_names[u])
    s6.append(F_(T("与中国企业合作最多的大学", "Universities working most with Chinese companies"), "合写的量子/计算化学论文数", hbar([(univ_names[u][:42], v, "var(--a-md)") for u, v in top_u.most_common(15)], T("中国合作大学", "China partner universities"), w=700, lw=290, unit=" 篇", bh=15, gap=4)))
    corp_rows = "".join(f'<tr><td class="n">{i+1}</td><td>{esc(d["name"])}</td><td>{d["country"]}</td><td><span class="dot" style="background:{CN_SECTORS[d["sector"]][1]}"></span> {esc(CN_SECTORS[d["sector"]][0])}</td><td class="n">{d["papers"]}</td><td class="n">{d["nauth"]}</td><td class="n">{d["cites"]:,}</td><td class="n">{min(y for y in d["years"] if y)}–{max(y for y in d["years"] if y)}</td><td class="n">{sum(v for y,v in d["years"].items() if y and y>=2020)}</td></tr>' for i, d in enumerate(CL))
    corp_tbl = (f'<div class="filters"><input id="q3" type="search" placeholder="{T(f"搜索全部 {n_comp} 家中国企业…", f"Search all {n_comp} Chinese companies…")}" aria-label="{T("搜索中国企业", "Search Chinese companies")}"><span class="muted" id="cnt3"></span></div>'
                '<div class="tbl-wrap" style="max-height:520px"><table class="data sortable" id="ptab3"><thead><tr><th class="n">#</th><th>企业（OpenAlex 机构名）</th><th>国家</th><th>行业（自动分类）</th><th class="n">论文</th><th class="n">作者</th><th class="n">被引</th><th class="n">年份跨度</th><th class="n">2020 后论文</th></tr></thead><tbody>' + corp_rows + "</tbody></table></div>")

    # ================= C7 academia
    s7 = []
    UZ = {"Tsinghua University": "清华大学", "University of Science and Technology of China": "中国科学技术大学", "Chinese Academy of Sciences": "中国科学院",
          "Peking University": "北京大学", "Massachusetts Institute of Technology": "麻省理工学院", "Stanford University": "斯坦福大学",
          "Shanghai Jiao Tong University": "上海交通大学", "University of Illinois Urbana-Champaign": "伊利诺伊大学厄巴纳-香槟分校",
          "Toyota Technological Institute at Chicago": "芝加哥丰田技术研究院"}
    for u, _ in univ_ct.most_common(16): T(UZ.get(u, u), u)
    s7.append(F_(T("中国学术创始人来自哪些大学", "Which universities Chinese academic founders come from"), T(f"{len(with_founders)} 家有可考学术创始人的公司", f"{len(with_founders)} companies with a traceable academic founder"),
                 hbar([(UZ.get(u, u)[:34], v, "var(--cn)") for u, v in univ_ct.most_common(16)], T("中国创始人大学", "China founder universities"), lw=250, unit=" 家", bh=15, gap=4),
                 T("清华大学是最大的衍生源头（量旋、华翊、弧光、镁伽、望石等），中国科学技术大学撑起合肥量子三强（本源、国盾、国仪）；晶泰、剂泰的创始人来自 MIT，华深智药、分子之心的创始人曾在美国任教。", "Tsinghua is the largest source of founders (SpinQ, HYQ, Arclight, MegaRobo, StoneWise and others), and USTC is behind the three Hefei quantum companies (Origin Quantum, QuantumCTek, CIQTEK); the founders of XtalPi and METiS came from MIT, and those of Helixon and MoleculeMind taught in the United States.")))
    pc_rows = sorted(((pid, sum(cc.values()), len(cc)) for pid, cc in prof_comp.items()), key=lambda x: -x[1])[:20]
    for p, _, _ in pc_rows: T(prof_by_id[p]["institution"][:22], prof_by_id[p]["institution"][:22])
    s7.append(F_(T("与企业合写最多的中国量化教授", "Chinese QC professors who write most with companies"), T("来自本站「中国量化地图」的教授名单；数字 = 与中国企业合写论文数", "From this site's China QC map; number = papers co-written with Chinese companies"),
                 hbar([(f"{prof_by_id[p]['name']}（{prof_by_id[p]['institution'][:22]}）", v, "var(--cn)", f"{prof_by_id[p]['name']}：{k} 家企业 {v} 篇") for p, v, k in pc_rows], T("中国教授企业合作", "China professor-company collaboration"), lw=340, unit=" 篇", bh=15, gap=4), wide=True))

    S["parts"] = dict(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, s6=s6, s7=s7, deal_tbl=deal_tbl, fc_tbl=fc_tbl, corp_tbl=corp_tbl)
    S["C"] = C; S["M"] = M
    S["stats"] = dict(n=n, n_comp=n_comp, n_cw=n_cw, fund_total=fund_total, fund_AB=fund_AB, by_cat=by_cat, fund_cat=fund_cat, fund_cat_c=fund_cat_c,
                      with_founders=len(with_founders), young=len(young), listed=len(listed), yr_sector=yr_sector, sec_papers=sec_papers, CL=CL,
                      matched=sum(1 for c in C if c["prof_matches"]), by_status=by_status, by_cluster=by_cluster, rev_total=sum(r["usd_m"] for r in pub))
    return S


def compare(ctx, NA, CN):
    """China–US comparison section. NA/CN: stats dicts (NA from build_report.main)."""
    F_ = ctx["F_"]; out = []
    us, cn = "var(--us)", "var(--cn)"
    lab_na, lab_cn = T("北美", "North America"), T("中国", "China")
    out.append(F_(T("精选企业：各赛道数量对比", "Selected companies by segment: comparison"), T("同一套赛道定义下的公司数", "Company counts under the same segment definitions"), legend([(lab_na, us), (lab_cn, cn)]) +
                  gbar([CATS[k][0] for k in CORDER], [(lab_na, us, [NA["by_cat"][k] for k in CORDER]), (lab_cn, cn, [CN["by_cat"][k] for k in CORDER])], T("赛道对比", "Segment comparison"), lw=170),
                  T("精选名录两边都不可能穷尽，比较的是结构而不是绝对数。", "Neither directory can be exhaustive; compare the structure, not the absolute numbers.")))
    nf = lambda S, k: S["fund_cat"][k] + S["fund_cat_c"][k]
    out.append(F_(T("已知私营融资：各赛道对比", "Known private funding by segment: comparison"), T("累计股权融资（含估计，百万美元）", "Cumulative equity funding (including estimates, US$ millions)"), legend([(lab_na, us), (lab_cn, cn)]) +
                  gbar([CATS[k][0] for k in CORDER], [(lab_na, us, [nf(NA, k) for k in CORDER]), (lab_cn, cn, [nf(CN, k) for k in CORDER])], T("融资对比", "Funding comparison"), lw=170, fmt=fmt_usd),
                  T(f"北美私营融资合计 {fmt_usd(NA['fund_total'])}，中国 {fmt_usd(CN['fund_total'])}（人民币按 7.2 折算）。量子硬件是两边差距最大的赛道。", f"Private funding totals {fmt_usd(NA['fund_total'])} in North America and {fmt_usd(CN['fund_total'])} in China (RMB at 7.2). Quantum hardware is the segment with the widest gap.")))
    yrs = list(range(2000, 2026))
    na_y = [sum(NA["yr_sector"][y].values()) for y in yrs]; cn_y = [sum(CN["yr_sector"][y].values()) for y in yrs]
    cross = next((y for y, a, b in zip(yrs, na_y, cn_y) if b > a), None)
    out.append(F_(T("企业参与的量子/计算化学论文：中美对比", "Quantum/computational chemistry papers with company authors: China vs North America"), T("每年至少有一位本国企业作者的论文数（OpenAlex，同一语料口径）", "Papers per year with at least one domestic company author (OpenAlex, same corpus definition)"),
                  legend([(lab_na, us), (lab_cn, cn)]) + lines(yrs, [(lab_na, us, na_y, False), (lab_cn, cn, cn_y, False)], T("中美企业论文", "Corporate papers, China vs NA")),
                  (T(f"中国企业论文在 {cross} 年首次超过北美。", f"Chinese corporate papers first overtook North America's in {cross}.") if cross else T("北美企业论文数仍多于中国。", "North American corporate papers still outnumber China's.")) +
                  T("2026 年为不完整年份，未画出。", "2026 is incomplete and not shown."), wide=True))
    # bucket mix
    def mix(S, reg):
        c = collections.Counter()
        for k, v in S["sec_papers"].items(): c[BUCKET[reg].get(k, "OTH")] += v
        tot = sum(c.values()) or 1
        return [c[b] / tot * 100 for b, _, _ in BUCKETS]
    m_na, m_cn = mix(NA, "na"), mix(CN, "cn")
    out.append(F_(T("企业论文的行业结构", "Industry mix of corporate papers"), T("各行业占本国企业论文的百分比（公司-论文对）", "Share of each industry in the country's corporate papers (company–paper pairs)"),
                  legend([(nm, col) for _, nm, col in BUCKETS]) + hstack([(lab_na, m_na), (lab_cn, m_cn)], [c for _, _, c in BUCKETS], [nm for _, nm, _ in BUCKETS], T("行业结构", "Industry mix"), lw=90, bh=34, fmt=lambda v: f"{v:.0f}%"),
                  T(f"能源、化工、材料与制造在中国占 {m_cn[0]:.0f}%，在北美占 {m_na[0]:.0f}%；专业软件与 AI 发现在北美占 {m_na[4]:.0f}%，在中国只占 {m_cn[4]:.0f}%。", f"Energy, chemicals, materials and manufacturing make up {m_cn[0]:.0f}% in China and {m_na[0]:.0f}% in North America; specialist software and AI discovery make up {m_na[4]:.0f}% in North America but only {m_cn[4]:.0f}% in China."), wide=True))
    rows = [
        (T("精选企业数", "Selected companies"), f"{NA['n']}", f"{CN['n']}"),
        (T("论文足迹中的企业", "Companies in the paper footprint"), f"{NA['n_comp']}", f"{CN['n_comp']}"),
        (T("企业参与论文（2000–2026）", "Papers with company authors (2000–2026)"), f"{NA['n_cw']:,}", f"{CN['n_cw']:,}"),
        (T("已知私营融资", "Known private funding"), fmt_usd(NA["fund_total"]), fmt_usd(CN["fund_total"])),
        (T("融资中有公开来源的比例", "Share of funding with a public source"), f"{NA['fund_AB']/NA['fund_total']*100:.0f}%", f"{CN['fund_AB']/CN['fund_total']*100:.0f}%"),
        (T("量子计算公司", "Quantum computing companies"), f"{NA['by_cat']['QC']}", f"{CN['by_cat']['QC']}"),
        (T("学术衍生企业", "Academic spin-outs"), f"{NA['with_founders']}", f"{CN['with_founders']}"),
        (T("2015 年后成立", "Founded after 2015"), f"{NA['young']}", f"{CN['young']}"),
        (T("2025 年企业论文", "Corporate papers in 2025"), f"{sum(NA['yr_sector'][2025].values()):,}", f"{sum(CN['yr_sector'][2025].values()):,}"),
    ]
    tbl = ('<div class="tbl-wrap"><table class="data"><thead><tr><th>指标</th><th class="n">' + lab_na + '</th><th class="n">' + lab_cn + '</th></tr></thead><tbody>' +
           "".join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n">{c}</td></tr>' for a, b, c in rows) + "</tbody></table></div>")
    return out, tbl
