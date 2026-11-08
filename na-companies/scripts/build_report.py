"""Build the North America quantum / computational chemistry companies report (site/index.html).

Inputs
  data/manual/companies.csv        curated company list (hand-compiled; every money figure has a confidence flag)
  data/manual/market.json          third-party market figures with source URLs, plus this report's own scenario assumptions
  data/raw/company_works.jsonl     OpenAlex works with a US/CA company author (scripts/fetch_openalex_companies.py)
  data/raw/professors.csv          NA quantum-chem professors (from na-quantum-chem-map)
  data/raw/basemap.json            US/CA basemap (from na-quantum-chem-map, Natural Earth, public domain)
Outputs
  site/index.html, data/processed/*.csv
All charts are inline SVG coloured with CSS variables from ../assets/site.css, so light and dark themes both work.
"""
import csv, json, math, os, re, collections, html, statistics

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(R, *a)
esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)

# English dictionary entries produced by this build (merged into ../i18n/en.json by scripts/i18n_merge.py)
I18N = {}
def T(zh, en):
    """Return zh and remember its English translation for the atlas dictionary."""
    if zh and en and zh != en: I18N[zh] = en
    return zh

def T_html(zh, en):
    """Pair the text nodes of a zh HTML block with those of its en twin (the host translates node by node)."""
    import re as _re
    tn = lambda h: [x.strip() for x in _re.split(r"<[^>]+>", h) if x.strip()]
    a, b = tn(zh), tn(en)
    if len(a) != len(b): raise SystemExit(f"T_html: {len(a)} zh vs {len(b)} en text nodes in block starting {zh[:40]!r}")
    for x, y in zip(a, b): T(x, y)
    return zh

# ---------------------------------------------------------------- categories
CATS = {
    "SW":     ("计算化学软件与平台", "var(--a-es)"),
    "QC":     ("量子计算（化学应用）", "var(--a-rd)"),
    "AIDD":   ("AI / 物理驱动药物发现", "var(--a-ml)"),
    "AIMAT":  ("AI 材料与自主实验室", "var(--a-mat)"),
    "PHARMA": ("大型药企计算化学部门", "var(--a-ex)"),
    "CHEM":   ("化工、能源与材料企业", "var(--a-md)"),
    "TECH":   ("科技巨头与 AI 实验室", "var(--c-tech)"),
    "INFO":   ("化学信息学与数据", "var(--c-info)"),
}
CORDER = list(CATS)
TIERS = ["初创", "中型", "大型"]
TIER_DEF = {"初创": "员工约 <100 人或早期私营", "中型": "约 100–1,000 人", "大型": "约 >1,000 人，或上市市值/估值 >10 亿美元"}

CITY = {  # lat, lon for every HQ city used in companies.csv
 "New York": (40.71, -74.01), "Wallingford": (41.46, -72.82), "Pleasanton": (37.66, -121.87), "Santa Fe": (35.69, -105.94),
 "San Diego": (32.72, -117.16), "Montreal": (45.50, -73.57), "Lancaster": (34.69, -118.14), "Radnor": (40.04, -75.36),
 "Irvine": (33.68, -117.83), "Los Altos": (37.39, -122.11), "Fayetteville": (36.06, -94.16), "Shawnee": (39.04, -94.72),
 "Cambridge": (42.37, -71.11), "Boston": (42.36, -71.06), "Walnut Creek": (37.91, -122.07), "Germantown": (39.17, -77.27),
 "Salt Lake City": (40.76, -111.89), "Sunnyvale": (37.37, -122.04), "San Jose": (37.34, -121.89), "Palo Alto": (37.44, -122.14),
 "College Park": (38.98, -76.94), "Berkeley": (37.87, -122.27), "Burnaby": (49.25, -122.98), "Toronto": (43.65, -79.38),
 "Broomfield": (39.92, -105.09), "Boulder": (40.01, -105.27), "Coquitlam": (49.28, -122.79), "Sherbrooke": (45.40, -71.89),
 "Dorval": (45.45, -73.75), "Vancouver": (49.28, -123.12), "Mississauga": (43.59, -79.64), "Durham": (35.99, -78.90),
 "San Francisco": (37.77, -122.42), "Burlingame": (37.58, -122.35), "Monrovia": (34.15, -118.00), "Fremont": (37.55, -121.99),
 "South San Francisco": (37.65, -122.41), "Somerville": (42.39, -71.10), "Seattle": (47.61, -122.33), "Redwood City": (37.49, -122.24),
 "Menlo Park": (37.45, -122.18), "Mountain View": (37.39, -122.08), "Denver": (39.74, -104.99), "Evanston": (42.05, -87.68),
 "Austin": (30.27, -97.74), "Rahway": (40.61, -74.28), "Princeton": (40.35, -74.66), "New Brunswick": (40.49, -74.45),
 "North Chicago": (42.33, -87.84), "Indianapolis": (39.77, -86.16), "Thousand Oaks": (34.17, -118.84), "Midland": (43.62, -84.25),
 "Wilmington": (39.74, -75.55), "Spring": (30.08, -95.42), "Corning": (42.14, -77.05), "Saint Paul": (44.95, -93.09),
 "Cincinnati": (39.10, -84.51), "Allentown": (40.60, -75.49), "Detroit": (42.33, -83.05), "Armonk": (41.13, -73.71),
 "Redmond": (47.67, -122.12), "Santa Clara": (37.35, -121.96), "Charlotte": (35.23, -80.84), "Columbus": (39.96, -83.00),
 "Clifton Park": (42.87, -73.77),
}
REGION_ZH = {"CA": "加利福尼亚", "MA": "马萨诸塞", "NY": "纽约", "ON": "安大略", "QC": "魁北克", "BC": "不列颠哥伦比亚", "NJ": "新泽西",
             "CO": "科罗拉多", "WA": "华盛顿州", "MD": "马里兰", "UT": "犹他", "PA": "宾夕法尼亚", "NM": "新墨西哥", "TX": "得克萨斯",
             "IL": "伊利诺伊", "CT": "康涅狄格", "MI": "密歇根", "NC": "北卡罗来纳", "OH": "俄亥俄", "IN": "印第安纳", "DE": "特拉华",
             "MN": "明尼苏达", "AR": "阿肯色", "KS": "堪萨斯"}

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def fmt_m(v):  # USD millions -> 中文金额
    if v is None: return "—"
    return f"{v/1000:.2f} 十亿" if v >= 1000 else f"{v:,.0f} 百万"

def fmt_usd(v):
    if v is None: return "—"
    return f"${v/1000:.1f}B" if v >= 1000 else f"${v:,.0f}M"

# ---------------------------------------------------------------- SVG chart kit
TIPJS_ATTR = lambda t: f' data-tip="{esc(t)}"'

def nice(v):
    if v <= 0: return 1
    e = 10 ** math.floor(math.log10(v)); f = v / e
    return (1 if f <= 1 else 2 if f <= 2 else 2.5 if f <= 2.5 else 5 if f <= 5 else 10) * e

def ticks(vmax, n=4):
    step = nice(vmax / n); top = step * math.ceil(vmax / step - 1e-9)
    return [step * i for i in range(int(round(top / step)) + 1)], top

def tl(v):
    if v >= 1000: return f"{v/1000:g}k" if v < 1e6 else f"{v/1e6:g}M"
    return f"{v:g}"

def svg_open(w, h, label):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{esc(label)}" style="max-width:{w}px;font-family:var(--body);font-size:12px">'

def hbar(rows, label, unit="", w=640, color="var(--accent)", lw=190, fmt=None, bh=20, gap=6, max_v=None):
    """rows: [(label, value, color|None, tip|None)]"""
    fmt = fmt or (lambda v: f"{v:,.0f}{unit}")
    h = 24 + len(rows) * (bh + gap)
    vmax = max_v or max([r[1] for r in rows] + [1])
    tk, top = ticks(vmax)
    x0, x1 = lw, w - 60
    sx = lambda v: x0 + (x1 - x0) * v / top
    o = [svg_open(w, h, label)]
    for t in tk:
        o.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="14" y2="{h-4}" stroke="var(--grid)"/>'
                 f'<text x="{sx(t):.1f}" y="10" text-anchor="middle" fill="var(--muted)" font-size="10.5">{tl(t)}</text>')
    for i, r in enumerate(rows):
        y = 20 + i * (bh + gap)
        c = r[2] if len(r) > 2 and r[2] else color
        tip = r[3] if len(r) > 3 and r[3] else f"{r[0]}：{fmt(r[1])}"
        o.append(f'<text x="{x0-8}" y="{y+bh/2+4:.1f}" text-anchor="end" fill="var(--ink-2)">{esc(r[0])}</text>')
        o.append(f'<rect x="{x0}" y="{y}" width="{max(1.5, sx(r[1])-x0):.1f}" height="{bh}" rx="3" fill="{c}"{TIPJS_ATTR(tip)}/>')
        o.append(f'<text x="{sx(r[1])+5:.1f}" y="{y+bh/2+4:.1f}" fill="var(--ink)" font-family="var(--mono)" font-size="11.5">{esc(fmt(r[1]))}</text>')
    o.append("</svg>")
    return "".join(o)

def stacked_cols(xlabels, series, label, w=640, h=300, unit="", tipfmt=None):
    """series: [(name, color, [values per x])]"""
    tot = [sum(s[2][i] for s in series) for i in range(len(xlabels))]
    tk, top = ticks(max(tot + [1]))
    x0, x1, y0, y1 = 44, w - 10, h - 34, 14
    sy = lambda v: y0 - (y0 - y1) * v / top
    bw = (x1 - x0) / len(xlabels)
    o = [svg_open(w, h, label)]
    for t in tk:
        o.append(f'<line x1="{x0}" x2="{x1}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="var(--grid)"/>'
                 f'<text x="{x0-6}" y="{sy(t)+4:.1f}" text-anchor="end" fill="var(--muted)" font-size="10.5">{tl(t)}</text>')
    step = max(1, math.ceil(len(xlabels) / 14))
    for i, xl in enumerate(xlabels):
        acc = 0; xx = x0 + i * bw + bw * 0.12
        for name, c, vals in series:
            v = vals[i]
            if v <= 0: continue
            ya, yb = sy(acc), sy(acc + v)
            tip = (tipfmt or (lambda n, x, v: f"{x} · {n}：{v:,.0f}{unit}"))(name, xl, v)
            o.append(f'<rect x="{xx:.1f}" y="{yb:.1f}" width="{bw*0.76:.1f}" height="{max(0.6, ya-yb):.1f}" fill="{c}"{TIPJS_ATTR(tip)}/>')
            acc += v
        if i % step == 0:
            o.append(f'<text x="{x0+i*bw+bw/2:.1f}" y="{y0+16}" text-anchor="middle" fill="var(--muted)" font-size="10.5">{esc(xl)}</text>')
    o.append(f'<line x1="{x0}" x2="{x1}" y1="{y0}" y2="{y0}" stroke="var(--axis)"/></svg>')
    return "".join(o)

def lines(xs, series, label, w=640, h=300, unit="", yfmt=tl, bands=None, vline=None, logy=False):
    """series: [(name, color, [y or None], dashed?)]; bands: [(color, [lo], [hi])]"""
    allv = [v for s in series for v in s[2] if v is not None] + [v for b in (bands or []) for v in b[2] if v is not None]
    x0, x1, y0, y1 = 50, w - 16, h - 34, 14
    if logy:
        lo = 10 ** math.floor(math.log10(min(v for v in allv if v > 0))); hi = 10 ** math.ceil(math.log10(max(allv)))
        sy = lambda v: y0 - (y0 - y1) * (math.log10(max(v, lo)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
        tk = [lo * 10 ** i for i in range(int(round(math.log10(hi / lo))) + 1)]
    else:
        tk, top = ticks(max(allv + [1])); sy = lambda v: y0 - (y0 - y1) * v / top
    xmin, xmax = xs[0], xs[-1]
    sx = lambda x: x0 + (x1 - x0) * (x - xmin) / (xmax - xmin)
    o = [svg_open(w, h, label)]
    for t in tk:
        o.append(f'<line x1="{x0}" x2="{x1}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="var(--grid)"/>'
                 f'<text x="{x0-6}" y="{sy(t)+4:.1f}" text-anchor="end" fill="var(--muted)" font-size="10.5">{esc(yfmt(t))}</text>')
    step = max(1, math.ceil(len(xs) / 12))
    for i, x in enumerate(xs):
        if i % step == 0 or i == len(xs) - 1:
            o.append(f'<text x="{sx(x):.1f}" y="{y0+16}" text-anchor="middle" fill="var(--muted)" font-size="10.5">{x}</text>')
    if vline is not None:
        o.append(f'<line x1="{sx(vline):.1f}" x2="{sx(vline):.1f}" y1="{y1}" y2="{y0}" stroke="var(--axis)" stroke-dasharray="3 3"/>'
                 f'<text x="{sx(vline)+4:.1f}" y="{y1+10}" fill="var(--muted)" font-size="10.5">预测 →</text>')
    for c, lo_, hi_ in bands or []:
        pts = [(sx(x), sy(v)) for x, v in zip(xs, hi_) if v is not None] + [(sx(x), sy(v)) for x, v in reversed(list(zip(xs, lo_))) if v is not None]
        o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{c}" opacity=".16"/>')
    for name, c, ys, dashed in series:
        seg = [(sx(x), sy(v), x, v) for x, v in zip(xs, ys) if v is not None]
        d = " ".join(("M" if i == 0 else "L") + f"{a:.1f},{b:.1f}" for i, (a, b, _, _) in enumerate(seg))
        o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2"{" stroke-dasharray=\"5 4\"" if dashed else ""}/>')
        for a, b, x, v in seg:
            o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.2" fill="{c}"{TIPJS_ATTR(f"{name} · {x}：{yfmt(v)}{unit}")}/>')
    o.append(f'<line x1="{x0}" x2="{x1}" y1="{y0}" y2="{y0}" stroke="var(--axis)"/></svg>')
    return "".join(o)

def scatter(pts, label, xlab, ylab, w=640, h=340, logy=True, xr=None):
    """pts: [(x, y, color, r, tip, label|None)]"""
    x0, x1, y0, y1 = 54, w - 14, h - 38, 14
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    xmin, xmax = xr or (min(xs) - 1, max(xs) + 1)
    lo = 10 ** math.floor(math.log10(min(ys))); hi = 10 ** math.ceil(math.log10(max(ys)))
    sx = lambda x: x0 + (x1 - x0) * (x - xmin) / (xmax - xmin)
    sy = lambda v: y0 - (y0 - y1) * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))
    o = [svg_open(w, h, label)]
    t = lo
    while t <= hi * 1.001:
        o.append(f'<line x1="{x0}" x2="{x1}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="var(--grid)"/>'
                 f'<text x="{x0-6}" y="{sy(t)+4:.1f}" text-anchor="end" fill="var(--muted)" font-size="10.5">{fmt_usd(t)}</text>')
        t *= 10
    for xv in range(int(math.ceil(xmin / 5) * 5), int(xmax) + 1, 5):
        o.append(f'<line x1="{sx(xv):.1f}" x2="{sx(xv):.1f}" y1="{y1}" y2="{y0}" stroke="var(--grid)"/>'
                 f'<text x="{sx(xv):.1f}" y="{y0+16}" text-anchor="middle" fill="var(--muted)" font-size="10.5">{xv}</text>')
    for x, y, c, r, tip, lab in pts:
        o.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r:.1f}" fill="{c}" fill-opacity=".78" stroke="var(--surface)" stroke-width="1"{TIPJS_ATTR(tip)}/>')
        if lab:
            o.append(f'<text x="{sx(x)+r+3:.1f}" y="{sy(y)+4:.1f}" fill="var(--ink-2)" font-size="10.5">{esc(lab)}</text>')
    o.append(f'<text x="{(x0+x1)/2}" y="{h-4}" text-anchor="middle" fill="var(--muted)" font-size="11">{esc(xlab)}</text>'
             f'<text x="12" y="{(y0+y1)/2}" transform="rotate(-90 12 {(y0+y1)/2})" text-anchor="middle" fill="var(--muted)" font-size="11">{esc(ylab)}</text></svg>')
    return "".join(o)

def heat(rows, cols, M, label, w=640, cell=None, fmt=lambda v: f"{v:g}"):
    lw = 120; ch = 24
    cw = cell or (w - lw - 10) / len(cols)
    h = 96 + len(rows) * ch
    mx = max([v for r in M for v in r] + [1])
    o = [svg_open(w, h, label)]
    for j, c in enumerate(cols):
        x = lw + j * cw + cw / 2
        o.append(f'<text x="{x:.1f}" y="86" text-anchor="start" transform="rotate(-40 {x:.1f} 86)" fill="var(--muted)" font-size="10.5">{esc(c)}</text>')
    for i, r in enumerate(rows):
        y = 92 + i * ch
        o.append(f'<text x="{lw-8}" y="{y+ch/2+4}" text-anchor="end" fill="var(--ink-2)" font-size="11.5">{esc(r)}</text>')
        for j, c in enumerate(cols):
            v = M[i][j]; a = 0.06 + 0.94 * (math.sqrt(v / mx) if v else 0)
            o.append(f'<rect x="{lw+j*cw+1:.1f}" y="{y+1}" width="{cw-2:.1f}" height="{ch-2}" rx="3" fill="var(--accent)" fill-opacity="{a:.2f}"{TIPJS_ATTR(f"{r} × {c}：{fmt(v)}")}/>')
            if v:
                o.append(f'<text x="{lw+j*cw+cw/2:.1f}" y="{y+ch/2+4}" text-anchor="middle" font-size="10.5" fill="{"var(--paper)" if a > .55 else "var(--ink)"}" font-family="var(--mono)">{esc(fmt(v))}</text>')
    o.append("</svg>")
    return "".join(o)

def hstack(rows, cols, names, label, w=640, lw=180, bh=22, gap=8, fmt=None):
    fmt = fmt or fmt_usd
    h = 24 + len(rows) * (bh + gap)
    tk, top = ticks(max(sum(v) for _, v in rows))
    x0, x1 = lw, w - 70
    sx = lambda v: x0 + (x1 - x0) * v / top
    o = [svg_open(w, h, label)]
    for t in tk:
        o.append(f'<line x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="14" y2="{h-4}" stroke="var(--grid)"/><text x="{sx(t):.1f}" y="10" text-anchor="middle" fill="var(--muted)" font-size="10.5">{fmt(t) if t else 0}</text>')
    for i, (lab, vals) in enumerate(rows):
        y = 20 + i * (bh + gap); acc = 0
        o.append(f'<text x="{x0-8}" y="{y+bh/2+4:.1f}" text-anchor="end" fill="var(--ink-2)">{esc(lab)}</text>')
        for v, c, nm in zip(vals, cols, names):
            if v > 0:
                o.append(f'<rect x="{sx(acc):.1f}" y="{y}" width="{sx(acc+v)-sx(acc):.1f}" height="{bh}" fill="{c}"{TIPJS_ATTR(f"{lab} · {nm}：{fmt(v)}")}/>')
            acc += v
        o.append(f'<text x="{sx(acc)+5:.1f}" y="{y+bh/2+4:.1f}" fill="var(--ink)" font-family="var(--mono)" font-size="11.5">{fmt(acc)}</text>')
    o.append("</svg>")
    return "".join(o)

def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{esc(n)}</span>' for n, c in items) + "</div>"

def fig(no, title, sub, body, cap="", wide=False):
    return (f'<figure class="chart{" wide" if wide else ""}"><div class="cno">图 {no:02d}</div><h3>{esc(title)}</h3>'
            f'<div class="sub">{sub}</div><div class="plot">{body}</div>' + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")

# ---------------------------------------------------------------- map
def proj(lon, lat, par=(33, 45, 23, -96)):
    # Lambert conformal conic; par = (standard parallel 1, standard parallel 2, origin lat, central lon)
    p1, p2, p0, l0 = map(math.radians, par)
    n = math.log(math.cos(p1) / math.cos(p2)) / math.log(math.tan(math.pi / 4 + p2 / 2) / math.tan(math.pi / 4 + p1 / 2))
    F = math.cos(p1) * math.tan(math.pi / 4 + p1 / 2) ** n / n
    rho = lambda p: F / math.tan(math.pi / 4 + p / 2) ** n
    p, l = math.radians(lat), math.radians(lon)
    return rho(p0) * 0 + rho(p) * math.sin(n * (l - l0)), rho(p0) - rho(p) * math.cos(n * (l - l0))

NA_MAP = dict(file="basemap.json", par=(33, 45, 23, -96), box=[(-128, 24), (-60, 24), (-128, 56), (-60, 56), (-96, 57), (-96, 24)],
              clip=lambda lon, lat: lat < 18 or lon < -140, label="北美量子化学/计算化学企业总部地图",
              names=[("旧金山湾区", -122.3, 37.6, -12, 40), ("波士顿/剑桥", -71.1, 42.36, 14, 30), ("纽约—新泽西", -74.3, 40.6, 16, 46),
                     ("多伦多", -79.4, 43.65, -40, -26), ("蒙特利尔", -73.6, 45.5, -10, -30), ("温哥华", -123.0, 49.27, -10, -28),
                     ("圣地亚哥", -117.16, 32.72, -10, 34), ("科罗拉多前山", -105.1, 40.0, 0, -26)])

def basemap_svg(points, w=1100, h=620, cfg=NA_MAP):
    gj = json.load(open(P("data", "raw", cfg["file"])))
    par = cfg["par"]; proj_ = lambda lon, lat: proj(lon, lat, par)
    box = cfg["box"]
    bx = [proj_(*b) for b in box]
    X0, X1 = min(b[0] for b in bx), max(b[0] for b in bx); Y0, Y1 = min(b[1] for b in bx), max(b[1] for b in bx)
    s = min(w / (X1 - X0), h / (Y1 - Y0))
    T = lambda lon, lat: ((proj_(lon, lat)[0] - X0) * s, h - (proj_(lon, lat)[1] - Y0) * s)
    def ring(rg):
        out, last = [], None
        for lon, lat in rg[::2] if len(rg) > 40 else rg:
            if cfg["clip"](lon, lat): continue
            x, y = T(lon, lat); pt = (round(x), round(y))
            if pt != last: out.append(pt); last = pt
        return "M" + "L".join(f"{a},{b}" for a, b in out) + "Z" if len(out) > 2 else ""
    paths = collections.defaultdict(list)
    for f in gj["features"]:
        g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        d = "".join(ring(rg) for poly in polys for rg in poly)
        if d: paths[f["properties"]["k"]].append(d)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{cfg['label']}" style="font-family:var(--body);font-size:12px">',
         f'<path d="{"".join(paths["other"])}" fill="var(--line-2)" stroke="none"/>',
         f'<path d="{"".join(paths["admin1"])}" fill="var(--raise)" stroke="var(--line)" stroke-width=".8"/>',
         f'<path d="{"".join(paths["lake"])}" fill="var(--surface)" stroke="var(--line)" stroke-width=".5"/>']
    # jitter co-located dots on a small spiral
    seen = collections.Counter()
    for lon, lat, c, r, tip, cat in sorted(points, key=lambda p: -p[3]):
        k = (round(lon, 1), round(lat, 1)); i = seen[k]; seen[k] += 1
        x, y = T(lon, lat)
        if i: a = i * 2.4; x += math.cos(a) * (4 + 2.2 * math.sqrt(i)) * 1.6; y += math.sin(a) * (4 + 2.2 * math.sqrt(i)) * 1.6
        o.append(f'<circle class="mdot" data-cat="{cat}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" fill-opacity=".85" stroke="var(--raise)" stroke-width="1"{TIPJS_ATTR(tip)}/>')
    for name, lon, lat, dx, dy in cfg["names"]:
        x, y = T(lon, lat)
        o.append(f'<text x="{x+dx:.0f}" y="{y+dy:.0f}" text-anchor="middle" fill="var(--ink-2)" font-size="13" font-weight="500" paint-order="stroke" stroke="var(--raise)" stroke-width="3">{name}</text>')
    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------------- corpus sector classifier
SECTOR_RULES = [
    ("SW", r"schrodinger|gaussian|biovia|accelrys|q chem|wavefunction|molsoft|openeye|chemical computing|simulations plus|certara|tripos|"
           r"synopsys|ansys|kitware|verachem|wasatch|parallel quantum|dirac solutions|nanoacademic|materials development|materials design|questek|"
           r"citrine|semichem|cadence|exabyte|enthought|qsimulate|schrödinger|optibrium|cresset|scienomics|silicon graphics|cray|hypercube"),
    ("QC", r"ionq|psiquantum|quantinuum|zapata|xanadu|1qbit|sandbox|rigetti|d-wave|quera|infleqtion|coldquanta|atom computing|qc ware|"
           r"photonic inc|nord quantique|anyon|good chemistry|oti lumionics|agnostiq|quantum circuits|strangeworks|polarisqb|proteinqure|menten"),
    ("AIDD", r"d\. ?e\. ?shaw|relay therap|silicon therap|roivant|psivant|altos labs|numerion|interx|recursion|atomwise|genesis therap|iambic|entos|"
             r"terray|nimbus|verseon|xaira|generate|arzeda|insitro|chai discovery|cyclica|valence|postera|reverie|inductive bio|isomorphic|"
             r"schrodinger therap|deep origin|achira|1910 genetics|model medicines|nference|atomic ai|absci|zymergen"),
    ("PHARMA", r"pfizer|merck|bristol|lilly|genentech|abbvie|amgen|janssen|johnson|glaxo|gsk|astrazeneca|boehringer|vertex|biogen|sanofi|novartis|"
               r"roche|abbott|neurocrine|gilead|regeneron|takeda|bayer|exact sciences|wyeth|schering|novo nordisk|alnylam|moderna|incyte|"
               r"array biopharma|celgene|biomarin|eisai|astellas|otsuka|daiichi|leidos biomedical|kinaxis|pharma|therapeutics|biosciences|bio\b"),
    ("CHEM", r"dow|dupont|exxon|chevron|shell|\bbp\b|air products|procter|basf|corning|\b3m\b|eastman|lubrizol|aramco|saudi arabia basic|sabic|"
             r"halliburton|schlumberger|goodyear|kimberly|altria|kodak|carestream|arcelor|celanese|ppg|albemarle|honeywell uop|uop|praxair|linde|"
             r"chemours|huntsman|cabot|w\. ?r\. ?grace|conocophillips|phillips 66|marathon|valero|nova chemicals|imperial oil|suncor|syncrude|"
             r"general motors|ford motor|toyota|bosch|mercedes|cnh|tesla|cummins|caterpillar|nissan|honda|chemical|materials resources|"
             r"zyvex|intermolecular|arthur d\. little|xerox|j\.a\. woollam|bruker|thermo fisher|universal display|unilever|colgate|clorox|"
             r"international flavors|givaudan|firmenich|steel|aluminum|alcoa|owens|ge global|general electric|ge research|energy|oil|petro|gas"),
    ("TECH", r"ibm|google|microsoft|meta\b|facebook|amazon|nvidia|intel\b|cerebras|anthropic|openai|ntt|jpmorgan|hewlett|hp inc|motorola|"
             r"seagate|western digital|lam research|applied materials|samsung|micron|advanced micro|texas instruments|globalfoundries|"
             r"taiwan semiconductor|kla\b|hitachi|at&t|bell lab|nokia|qualcomm|apple|ibm research|sk group|sk hynix|graphcore|groq|sambanova|"
             r"lucent|agilent|keysight|hrl|semiconductor"),
    ("GOV", r"\bues\b|science applications|universal technology|boeing|lockheed|pratt|general dynamics|northrop|leidos|eloret|spectral sciences|"
            r"cfd research|mitre|wyle|kbr|bennett|stinger|analytical mechanics|aerodyne|raytheon|united technologies|spectral energies|"
            r"advanced cooling|continuum dynamics|radiation monitoring|mpb technologies|battelle|sri international|southwest research|"
            r"physical sciences inc|aerospace corporation|bae systems|teledyne|jacobs|booz|l3harris|draper|ball aerospace|aerojet|"
            r"innovative scientific|metacomp|intelligent light|tech-x|nanosonic|luna innovations|agiltron"),
]
SECTOR_ZH = dict((k, v[0]) for k, v in CATS.items()); SECTOR_ZH["GOV"] = "国防/航天与政府科研承包商"; SECTOR_ZH["OTHER"] = "其他 / 未分类"; SECTOR_ZH["CHEM"] = "化工、能源、汽车与制造"
SECTOR_COL = dict((k, v[1]) for k, v in CATS.items()); SECTOR_COL["GOV"] = "var(--c-gov)"; SECTOR_COL["OTHER"] = "var(--c-other)"
NOT_COMPANY = re.compile(r"canadian light source|namesforlife", re.I)

def sector(name):
    n = name.lower()
    for k, rx in SECTOR_RULES:
        if re.search(rx, n): return k
    return "OTHER"

def clean_name(n):
    return re.sub(r"\s*\((United States|Canada)\)\s*$", "", n or "")

def norm_person(s):
    s = s.lower()
    s = re.sub(r"[áàä]", "a", s); s = re.sub(r"[éèë]", "e", s); s = re.sub(r"[íï]", "i", s); s = re.sub(r"[óö]", "o", s); s = re.sub(r"[úü]", "u", s); s = s.replace("ć", "c")
    s = re.sub(r"\b[a-z]\.\s*", "", s); s = re.sub(r"[^a-z ]", " ", s)
    parts = s.split()
    return (parts[0], parts[-1]) if len(parts) >= 2 else (s, s)

# ---------------------------------------------------------------- main
def main():
    C = list(csv.DictReader(open(P("data", "manual", "companies.csv"), encoding="utf-8")))
    M = json.load(open(P("data", "manual", "market.json"), encoding="utf-8"))
    profs = list(csv.DictReader(open(P("data", "raw", "professors.csv"), encoding="utf-8")))
    prof_by_id = {p["openalex_id"]: p for p in profs}
    prof_by_name = collections.defaultdict(list)
    for p in profs: prof_by_name[norm_person(p["name"])].append(p)

    for c in C:
        c["f"] = num(c["funding_musd"]); c["v"] = num(c["valuation_musd"]); c["rev"] = num(c["revenue_musd"])
        c["emp"] = num(c["employees"]); c["yr"] = int(c["founded"]) if c["founded"] else None
        c["lat"], c["lon"] = CITY[c["city"]]
        c["founders"] = [x.strip() for x in c["academic_founders"].split(";") if x.strip()]
        c["univs"] = [x.strip() for x in c["univ_links"].split(";") if x.strip()]
        c["prof_matches"] = []
        for fd in c["founders"]:
            for p in prof_by_name.get(norm_person(fd), []):
                c["prof_matches"].append(p)
    n = len(C)

    # ---------------- corpus
    works = [json.loads(l) for l in open(P("data", "raw", "company_works.jsonl"), encoding="utf-8")]
    comp = {}
    yr_sector = collections.defaultdict(collections.Counter)
    comp_univ = collections.Counter(); univ_names = {}
    prof_comp = collections.defaultdict(collections.Counter)
    company_work_ids = set()
    for w in works:
        cs = {}; us = {}
        for a in w["au"]:
            for i in a["i"]:
                if i["t"] == "company" and i["c"] in ("US", "CA") and not NOT_COMPANY.search(i["n"] or ""):
                    cs[i["id"]] = i
                    d = comp.setdefault(i["id"], {"id": i["id"], "name": clean_name(i["n"]), "country": i["c"], "papers": 0, "cites": 0, "authors": set(), "years": collections.Counter()})
                    d["authors"].add(a["a"])
                elif i["t"] == "education" and i["c"] in ("US", "CA"):
                    us[i["id"]] = i["n"]
        if not cs: continue
        company_work_ids.add(w["id"])
        for cid in cs:
            d = comp[cid]; d["papers"] += 1; d["cites"] += w["cites"] or 0; d["years"][w["year"]] += 1
        secs = {sector(comp[cid]["name"]) for cid in cs}
        for s in secs: yr_sector[w["year"]][s] += 1
        for cid in cs:
            for uid, un in us.items(): comp_univ[(cid, uid)] += 1; univ_names[uid] = un
        for a in w["au"]:
            if a["a"] in prof_by_id:
                for cid in cs: prof_comp[a["a"]][cid] += 1
    for d in comp.values(): d["sector"] = sector(d["name"]); d["nauth"] = len(d["authors"])
    CL = sorted(comp.values(), key=lambda d: -d["papers"])
    n_comp = len(CL); n_cw = len(company_work_ids)
    sec_counts = collections.Counter(d["sector"] for d in CL)
    sec_papers = collections.Counter()
    for d in CL: sec_papers[d["sector"]] += d["papers"]

    # write processed tables
    os.makedirs(P("data", "processed"), exist_ok=True)
    with open(P("data", "processed", "corpus_companies.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["openalex_id", "name", "country", "sector", "papers", "authors", "citations", "first_year", "last_year", "papers_2020_plus"])
        for d in CL:
            ys = [y for y in d["years"] if y]
            wr.writerow([d["id"], d["name"], d["country"], SECTOR_ZH[d["sector"]], d["papers"], d["nauth"], d["cites"], min(ys) if ys else "", max(ys) if ys else "", sum(v for y, v in d["years"].items() if y and y >= 2020)])
    with open(P("data", "processed", "company_university_links.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["company_id", "company", "university_id", "university", "co_papers"])
        for (cid, uid), v in comp_univ.most_common():
            if v >= 2: wr.writerow([cid, comp[cid]["name"], uid, univ_names[uid], v])
    with open(P("data", "processed", "professor_company_links.csv"), "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh); wr.writerow(["professor_id", "professor", "institution", "company_id", "company", "co_papers"])
        for pid, cc in prof_comp.items():
            for cid, v in cc.most_common(): wr.writerow([pid, prof_by_id[pid]["name"], prof_by_id[pid]["institution"], cid, comp[cid]["name"], v])

    # ---------------- curated stats
    by_cat = collections.Counter(c["category"] for c in C)
    by_tier = collections.Counter(c["tier"] for c in C)
    by_country = collections.Counter(c["country"] for c in C)
    by_status = collections.Counter(c["status"] for c in C)
    by_region = collections.Counter(c["region"] for c in C)
    funded = [c for c in C if c["f"]]
    fund_total = sum(c["f"] for c in funded)
    fund_AB = sum(c["f"] for c in funded if c["funding_conf"] in ("A", "B"))
    fund_cat = collections.Counter(); fund_cat_c = collections.Counter()
    for c in funded:
        (fund_cat if c["funding_conf"] in ("A", "B") else fund_cat_c)[c["category"]] += c["f"]
    with_founders = [c for c in C if c["founders"]]
    univ_ct = collections.Counter(u for c in C for u in c["univs"])
    young = [c for c in C if c["yr"] and c["yr"] >= 2015]
    med_young_f = statistics.median([c["f"] for c in young if c["f"]]) if young else 0
    matched = [c for c in C if c["prof_matches"]]

    def cluster(c):
        lat, lon = c["lat"], c["lon"]
        if 37 < lat < 38.1 and -122.6 < lon < -121.7: return "旧金山湾区"
        if 42.2 < lat < 42.5 and -71.3 < lon < -70.9: return "波士顿/剑桥"
        if 40.2 < lat < 41.2 and -74.8 < lon < -73.6: return "纽约—新泽西"
        if 43.4 < lat < 44 and -80 < lon < -79: return "多伦多"
        if 45.3 < lat < 45.7 and -74 < lon < -73.4: return "蒙特利尔"
        if 49 < lat < 49.5 and -123.3 < lon < -122.6: return "温哥华"
        if 32.5 < lat < 33.0: return "圣地亚哥"
        if 39.5 < lat < 40.2 and -105.4 < lon < -104.8: return "科罗拉多前山"
        if 33.5 < lat < 34.8 and -119 < lon < -117: return "洛杉矶/橙县"
        return "其他地区"
    by_cluster = collections.Counter(cluster(c) for c in C)
    fund_cluster = collections.Counter()
    for c in funded: fund_cluster[cluster(c)] += c["f"]
    top_cluster_share = sum(v for k, v in by_cluster.most_common(3) if k != "其他地区") / n

    # ================================================================== HTML
    F = []  # figures in order
    no = [0]
    def F_(title, sub, body, cap="", wide=False):
        no[0] += 1; return fig(no[0], title, sub, body, cap, wide)

    cat_leg = legend([(CATS[k][0], CATS[k][1]) for k in CORDER])

    # ---- 01 landscape
    s1 = []
    s1.append(F_("八大细分赛道的公司数量", f"本报告精选收录的 {n} 家北美企业", hbar([(CATS[k][0], by_cat[k], CATS[k][1]) for k in sorted(CORDER, key=lambda k: -by_cat[k])], "公司数量按赛道", unit=" 家", lw=170)))
    tier_series = [(t, col, [sum(1 for c in C if c["category"] == k and c["tier"] == t) for k in CORDER]) for t, col in zip(TIERS, ["var(--a-md)", "var(--a-mat)", "var(--a-es)"])]
    s1.append(F_("规模结构：初创、中型、大型", "各赛道内三个规模层级的公司数", legend([(t, c) for t, c, _ in tier_series]) +
                 stacked_cols([CATS[k][0].split("（")[0].replace("与", "/")[:6] for k in CORDER], tier_series, "规模结构", unit=" 家"),
                 "规模分层定义：" + "；".join(f"{k}：{esc(v)}" for k, v in TIER_DEF.items()) + "。"))
    bins = list(range(1980, 2030, 5))
    yr_series = [(CATS[k][0], CATS[k][1], [sum(1 for c in C if c["category"] == k and c["yr"] and b <= c["yr"] < b + 5) for b in bins]) for k in CORDER]
    pre = sum(1 for c in C if c["yr"] and c["yr"] < 1980)
    s1.append(F_("成立年份：三波创业潮", "每 5 年成立的公司数（不含 1980 年前成立的老牌企业 " + str(pre) + " 家）", cat_leg +
                 stacked_cols([f"{b}–{str(b+4)[2:]}" for b in bins], yr_series, "成立年份", unit=" 家"),
                 "第一波（1987–1998）是量子化学软件商业化；第二波（2012–2018）是量子计算与深度学习药物发现；第三波（2020 至今）是生成式 AI、大模型与自主实验室。", wide=True))
    st_order = ["私营", "上市", "被收购", "已关闭", "不明", "非营利"]
    s1.append(F_("企业状态", "当前所有权状态", hbar([(s, by_status[s], None) for s in st_order if by_status[s]], "企业状态", unit=" 家", lw=80)))
    s1.append(F_("美国与加拿大", "公司数与已知融资额", hbar([("美国 · 公司数", by_country["US"], "var(--us)"), ("加拿大 · 公司数", by_country["CA"], "var(--ca)")], "国家", unit=" 家", lw=120) +
                 hbar([("美国 · 融资", sum(c["f"] for c in funded if c["country"] == "US"), "var(--us)"), ("加拿大 · 融资", sum(c["f"] for c in funded if c["country"] == "CA"), "var(--ca)")], "国家融资", lw=120, fmt=fmt_usd),
                 "融资额仅统计私营公司已披露（含估计）的累计股权融资，不含上市公司的二级市场募资。"))

    # ---- 02 geography
    pts = []
    for c in C:
        r = 4 + (math.sqrt(c["f"]) / 6 if c["f"] else 0) + (3 if c["tier"] == "大型" else 0)
        tip = f"{c['name']} · {c['city']}, {c['region']}\n{CATS[c['category']][0]} · {c['tier']} · 成立 {c['founded']}" + (f"\n融资 {fmt_usd(c['f'])}" if c["f"] else "")
        pts.append((c["lon"], c["lat"], CATS[c["category"]][1], min(r, 16), tip, c["category"]))
    def mapfig(title, svg, mid, cap):
        no[0] += 1
        return (f'<figure class="chart wide mapfig" id="{mid}"><div class="cno">图 {no[0]:02d}</div><h3>{title}</h3><div class="sub">点 = 公司总部；颜色 = 赛道；大小 = 融资额（大型企业另加粗）。点击下方图例可筛选。</div>'
                f'<div class="legend mapleg">' + "".join(f'<span class="pill" data-cat="{k}" style="cursor:pointer"><i style="background:{CATS[k][1]};width:10px;height:10px;border-radius:3px;display:inline-block"></i>{CATS[k][0]}</span>' for k in CORDER) +
                f'</div><div class="plot">{svg}</div><figcaption>{cap}</figcaption></figure>')
    s2 = [mapfig(T("北美企业总部真实地理分布", "Where North American company headquarters are"), basemap_svg(pts), "namap", "坐标为总部城市中心；同城多家公司按螺旋错开。底图：Natural Earth（公有领域）。")]
    cl_order = [k for k, _ in by_cluster.most_common()]
    s2.append(F_("九大产业集群：公司数", "按总部所在都会区归并", hbar([(k, by_cluster[k], "var(--accent)" if k != "其他地区" else "var(--c-other)") for k in cl_order], "集群公司数", unit=" 家", lw=110)))
    s2.append(F_("九大产业集群：已知融资", "私营公司累计融资（含估计）", hbar([(k, fund_cluster[k], "var(--accent)" if k != "其他地区" else "var(--c-other)") for k in sorted(fund_cluster, key=lambda k: -fund_cluster[k])], "集群融资", lw=110, fmt=fmt_usd)))
    s2.append(F_("州/省分布", "总部所在州或省（前 14）", hbar([(f"{REGION_ZH.get(k, k)}（{k}）", v, "var(--ca)" if k in ("ON", "QC", "BC") else "var(--us)") for k, v in by_region.most_common(14)], "州省分布", unit=" 家", lw=150), wide=False))
    hm_rows = [k for k in cl_order]
    s2.append(F_("集群 × 赛道", "每个集群在各赛道的公司数", heat([k for k in hm_rows], [CATS[k][0].split("（")[0][:7] for k in CORDER], [[sum(1 for c in C if cluster(c) == r and c["category"] == k) for k in CORDER] for r in hm_rows], "集群赛道热力图")))

    # ---- 03 capital (past & present)
    s3 = []
    fc_rows = []
    for k in sorted(CORDER, key=lambda k: -(fund_cat[k] + fund_cat_c[k])):
        if fund_cat[k] + fund_cat_c[k] > 0: fc_rows.append(k)
    s3.append(F_("各赛道累计股权融资", "私营公司已披露累计融资；深色 = 有公开报道，浅色 = 本报告估计", legend([("有来源（A/B）", "var(--accent)"), ("估计（C）", "var(--c-est)")]) +
                 hstack([(CATS[k][0], [fund_cat[k], fund_cat_c[k]]) for k in fc_rows], ["var(--accent)", "var(--c-est)"], ["有来源", "估计"], "赛道融资"),
                 "单位：百万美元。上市公司（IonQ、Rigetti、D-Wave 等）的增发募资未计入，见下方「资本市场」表。"))
    top_f = sorted(funded, key=lambda c: -c["f"])[:20]
    s3.append(F_("融资额前 20 的私营公司", "累计股权融资（百万美元）", hbar([(c["name"].split("（")[0][:22], c["f"], CATS[c["category"]][1] if c["funding_conf"] != "C" else "var(--c-est)",
                                                                   f"{c['name']}：{fmt_usd(c['f'])}（{c['last_round']}；可信度 {c['funding_conf']}）") for c in top_f], "融资前20", lw=200, fmt=fmt_usd, bh=16, gap=5),
                 "浅灰色条为估计值。量子硬件（PsiQuantum、Quantinuum、SandboxAQ）与 AI 新锐（Xaira、Lila、Periodic Labs）占据前列。"))
    TOPLAB = {c["name"] for c in sorted(funded, key=lambda c: -c["f"])[:5]} | {"Nimbus Therapeutics", "Atomwise", "Citrine Informatics", "Rowan Scientific", "QSimulate"}
    sc = [(c["yr"], c["f"], CATS[c["category"]][1], 3 + math.sqrt(c["f"]) / 8, f"{c['name']}（{c['founded']}）：{fmt_usd(c['f'])}", c["name"].split("（")[0] if c["name"] in TOPLAB else None) for c in funded if c["yr"] and c["yr"] >= 1995]
    s3.append(F_("成立年份 × 融资规模", "越新的公司首轮越大：2023 年后单轮动辄数亿美元", cat_leg + scatter(sc, "成立年份与融资", "成立年份", "累计融资（对数）", xr=(1994, 2026)), wide=True))
    # valuation table + M&A
    mna = [c for c in C if c["status"] == "被收购" or "收购" in c["last_round"]]
    mna_rows = sorted([c for c in mna if c["v"] or "收购" in c["last_round"]], key=lambda c: c["last_round"])
    deal_events = M["deals"]
    s3.append(F_("重大交易时间线", "并购、IPO / SPAC、超大额融资（金额，百万美元）",
                 hbar([(f"{d['year']} · {d['name']}", d["usd_m"], "var(--a-ex)" if d["type"] == "并购" else "var(--a-rd)" if d["type"] in ("IPO", "SPAC") else "var(--accent)",
                        f"{d['year']} {d['name']}：{d['type']} {fmt_usd(d['usd_m'])}。来源：{d['src']}") for d in sorted(deal_events, key=lambda d: d["year"])], "交易时间线", w=720, lw=300, fmt=fmt_usd, bh=15, gap=5),
                 legend([("并购", "var(--a-ex)"), ("IPO/SPAC", "var(--a-rd)"), ("融资", "var(--accent)")]) + "并购金额为公告或媒体报道值；收购价越来越高，Dotmatics（51 亿美元）刷新了科学软件并购纪录。", wide=True))

    # ---- 04 revenue
    s4 = []
    pub = M["public_revenue"]
    s4.append(F_("上市/准上市公司最新年收入", "最新完整财年或公司指引（百万美元）",
                 hbar([(f"{r['name']}（{r['fy']}）", r["usd_m"], r.get("color") or "var(--accent)", f"{r['name']} {r['fy']}：{fmt_usd(r['usd_m'])}。{r['src']}") for r in sorted(pub, key=lambda r: -r["usd_m"])], "上市公司收入", lw=210, fmt=fmt_usd),
                 "IonQ 2025 年为公司指引中值（1.06–1.10 亿美元）。纯量子硬件公司收入仍以政府与研究合同为主。"))
    hist = M["revenue_history"]
    yrs = sorted({int(y) for s in hist.values() for y in s["data"]})
    s4.append(F_("收入轨迹：计算化学软件 vs 量子计算", "Schrödinger、Certara、IonQ 历年收入（百万美元，对数轴）",
                 legend([(k, v["color"]) for k, v in hist.items()]) +
                 lines(yrs, [(k, v["color"], [v["data"].get(str(y)) for y in yrs], False) for k, v in hist.items()], "收入轨迹", unit="M", yfmt=lambda v: f"${v:g}M", logy=True),
                 "软件公司收入稳定增长（Schrödinger 2019→2025 年复合增速约 20%）；IonQ 自 2021 年以来每年约翻倍，但基数小、亏损大。"))
    sd = M["schrodinger_mix"]
    s4.append(F_("Schrödinger 收入结构", "软件 vs 药物发现合作收入（百万美元）",
                 legend([("软件", "var(--a-es)"), ("药物发现", "var(--a-ml)")]) +
                 stacked_cols([str(y) for y in sd["years"]], [("软件", "var(--a-es)", sd["software"]), ("药物发现", "var(--a-ml)", sd["drug"])], "Schrödinger 收入结构", unit="M"),
                 "来源：Schrödinger 年报与 2025 年第四季度财报。2026 年指引：软件 ACV 2.18–2.28 亿美元。"))

    # ---- 05 macro & forecast
    s5 = []
    q = M["quantum_startup_investment"]
    s5.append(F_("全球量子初创投资", "McKinsey Quantum Technology Monitor（十亿美元）",
                 hbar([(str(y), v, "var(--a-rd)") for y, v in q["data"].items()], "量子投资", lw=60, fmt=lambda v: f"${v:g}B"),
                 f"2025 年 126 亿美元，是 2024 年的 6.3 倍；90% 流向量子计算公司。来源：{q['src_short']}。北美的 PsiQuantum（10 亿）、Quantinuum（6 亿）等超大单轮是主要推手（本报告判断，McKinsey 未给出国别拆分）。"))
    ai = M["ai_biotech_vc"]
    s5.append(F_("AI 生物技术风险投资", "Crunchbase 口径，经 IntuitionLabs 汇总（十亿美元）",
                 hbar([(str(y), v, "var(--a-ml)") for y, v in ai["data"].items()], "AI 生物 VC", lw=60, fmt=lambda v: f"${v:g}B"),
                 "2021 年泡沫后 2023 年见底，2024 年回升。2025 年数据源未给全年总额，故不列出。"))
    fc = M["forecasts"]
    # comp chem market projection, sourced CAGR
    cc = M["compchem_market"]
    yrs2 = list(range(2026, 2035))
    base = [cc["v2026"] * (1 + cc["cagr"]) ** (y - 2026) for y in yrs2]
    na_lo = [b * M["assumptions"]["na_share_lo"] for b in base]; na_hi = [b * M["assumptions"]["na_share_hi"] for b in base]
    na_mid = [(a + b) / 2 for a, b in zip(na_lo, na_hi)]
    s5.append(F_("计算化学市场规模预测", "全球（第三方预测，十亿美元）与北美份额（本报告估计区间）",
                 legend([("全球（Fortune Business Insights）", "var(--a-es)"), ("北美估计中值", "var(--us)"), ("北美估计区间", "var(--us)")]) +
                 lines(yrs2, [("全球", "var(--a-es)", base, False), ("北美中值", "var(--us)", na_mid, True)], "市场预测", yfmt=lambda v: f"${v:.1f}B", bands=[("var(--us)", na_lo, na_hi)]),
                 f"全球曲线：2026 年 {cc['v2026']} 十亿 → 2034 年 {cc['v2034']} 十亿美元，CAGR {cc['cagr']*100:.2f}%（{cc['src_short']}）。北美份额区间 {M['assumptions']['na_share_lo']*100:.0f}–{M['assumptions']['na_share_hi']*100:.0f}% 为本报告假设（依据：北美在样本公司数、融资额与企业论文中的占比），<b>不是</b>第三方数据。"))
    # quantum scenario
    scn = M["scenarios"]
    yrs3 = list(range(2023, 2031))
    hist_q = {2023: 1.3, 2024: 2.0, 2025: 12.6}
    ser = []
    for name, col, g in [("乐观", "var(--a-md)", scn["bull"]), ("基准", "var(--a-rd)", scn["base"]), ("悲观", "var(--a-ex)", scn["bear"])]:
        v = 12.6; ys = []
        for y in yrs3:
            if y <= 2025: ys.append(hist_q[y] if y == 2025 else None)
            else: v = v * (1 + g[y - 2026]); ys.append(round(v, 2))
        ser.append((name, col, ys, True))
    ser.insert(0, ("实际", "var(--ink)", [hist_q.get(y) for y in yrs3], False))
    s5.append(F_("量子初创年度投资情景（2026–2030）", "2023–2025 为 McKinsey 实际值；之后三条路径为本报告情景假设（十亿美元）",
                 legend([(s[0], s[1]) for s in ser]) + lines(yrs3, ser, "量子投资情景", yfmt=lambda v: f"${v:g}B", vline=2025),
                 "情景假设（年增速）：" + "；".join(f"{k}：{', '.join(f'{x*100:+.0f}%' for x in scn[kk])}" for k, kk in [("乐观", "bull"), ("基准", "base"), ("悲观", "bear")]) +
                 "。2025 年的 126 亿美元包含少数超大单轮（PsiQuantum 10 亿、Quantinuum 6 亿等），基准情景假设其部分回落。"))
    # corporate paper trend + extrapolation
    ys_all = list(range(2000, 2026))
    tot_y = [sum(yr_sector[y].values()) for y in ys_all]
    fit_x = list(range(2015, 2026)); fit_y = [sum(yr_sector[y].values()) for y in fit_x]
    mx_, my_ = statistics.mean(fit_x), statistics.mean(fit_y)
    slope = sum((a - mx_) * (b - my_) for a, b in zip(fit_x, fit_y)) / sum((a - mx_) ** 2 for a in fit_x)
    icpt = my_ - slope * mx_
    resid = statistics.pstdev([b - (icpt + slope * a) for a, b in zip(fit_x, fit_y)])
    proj_x = list(range(2000, 2031))
    s5.append(F_("企业参与学术研究的趋势与外推", "北美企业作者参与的量子/计算化学论文数（OpenAlex），2026–2030 为线性外推",
                 legend([("实际", "var(--accent)"), ("线性外推（2015–2025 拟合）", "var(--a-mat)")]) +
                 lines(proj_x, [("实际", "var(--accent)", [sum(yr_sector[y].values()) if y <= 2025 else None for y in proj_x], False),
                                ("外推", "var(--a-mat)", [round(icpt + slope * y) if y >= 2025 else None for y in proj_x], True)], "论文外推",
                       bands=[("var(--a-mat)", [icpt + slope * y - 1.96 * resid if y >= 2025 else None for y in proj_x], [icpt + slope * y + 1.96 * resid if y >= 2025 else None for y in proj_x])], vline=2025),
                 f"2015–2025 年每年约增加 {slope:.0f} 篇；按此外推 2030 年约 {icpt+slope*2030:.0f} 篇（95% 区间 ±{1.96*resid:.0f}）。这是统计外推，不考虑 AI 驱动的结构性加速。2026 年数据未完整，未用于拟合。", wide=True))

    # ---- 06 research footprint (OpenAlex)
    s6 = []
    sec_order = sorted(SECTOR_ZH, key=lambda k: -sec_papers[k])
    s6.append(F_("论文足迹：哪些行业在做量子/计算化学", f"{n_comp} 家北美企业在 OpenAlex 语料中的论文数（按行业，合写按公司计）",
                 hbar([(SECTOR_ZH[k], sec_papers[k], SECTOR_COL[k], f"{SECTOR_ZH[k]}：{sec_counts[k]} 家公司，{sec_papers[k]:,} 篇（公司-论文对）") for k in sec_order], "行业论文", lw=200, unit=" 篇")))
    s6.append(F_("企业论文 Top 25", "量子/计算化学论文最多的北美企业", hbar([(d["name"][:26], d["papers"], SECTOR_COL[d["sector"]], f"{d['name']}：{d['papers']} 篇，{d['nauth']} 位作者，被引 {d['cites']:,}") for d in CL[:25]], "企业论文Top25", lw=210, unit=" 篇", bh=15, gap=4)))
    yr_x = list(range(2000, 2026))
    s6.append(F_("各行业企业论文的年度变化", "每年有该行业企业作者参与的论文数（2000–2025）",
                 legend([(SECTOR_ZH[k], SECTOR_COL[k]) for k in sec_order]) +
                 stacked_cols([str(y) for y in yr_x], [(SECTOR_ZH[k], SECTOR_COL[k], [yr_sector[y][k] for y in yr_x]) for k in sec_order], "行业年度论文", unit=" 篇"),
                 "2020 年后科技巨头（Google、Microsoft、NVIDIA、Meta、IBM）与量子公司的论文快速增加，传统化工与国防承包商占比下降。", wide=True))
    top_u = collections.Counter()
    for (cid, uid), v in comp_univ.items(): top_u[uid] += v
    s6.append(F_("与企业合作最多的大学", "与北美企业合写的量子/计算化学论文数", hbar([(univ_names[u][:42], v, "var(--a-md)") for u, v in top_u.most_common(15)], "合作大学", w=700, lw=290, unit=" 篇", bh=15, gap=4)))
    top_pairs = [(f"{comp[c]['name'][:20]} × {univ_names[u][:34]}", v, SECTOR_COL[comp[c]["sector"]]) for (c, u), v in comp_univ.most_common(15)]
    s6.append(F_("最强的企业–大学合作对", "合写论文数", hbar(top_pairs, "合作对", w=760, lw=400, unit=" 篇", bh=15, gap=4)))

    # ---- 07 academia ↔ industry
    s7 = []
    s7.append(F_("学术创始人来自哪些大学", f"{len(with_founders)} 家有可考学术创始人的公司（一家公司可对应多所大学）",
                 hbar([(u[:32], v, "var(--accent)" if u not in ("University of Toronto", "Simon Fraser University", "McGill University", "University of British Columbia", "University of Waterloo", "Université de Sherbrooke", "Mila") else "var(--ca)") for u, v in univ_ct.most_common(16)], "创始人大学", lw=240, unit=" 家", bh=15, gap=4),
                 "蓝色为美国大学，绿色为加拿大。斯坦福与哈佛、多伦多大学是最大的衍生企业来源。"))
    pc_rows = sorted(((pid, sum(cc.values()), len(cc)) for pid, cc in prof_comp.items()), key=lambda x: -x[1])[:20]
    s7.append(F_("与企业合写最多的北美量化教授", "来自「北美量化地图」1,044 位教授名单；数字 = 与北美企业合写论文数",
                 hbar([(f"{prof_by_id[p]['name']}（{prof_by_id[p]['institution'][:22]}）", v, "var(--a-md)", f"{prof_by_id[p]['name']}：与 {k} 家企业合写 {v} 篇；最常合作：{', '.join(comp[c]['name'] for c, _ in prof_comp[p].most_common(3))}") for p, v, k in pc_rows], "教授企业合作", lw=330, unit=" 篇", bh=15, gap=4), wide=True))

    # ---------------- tables
    def company_table(ALL):
        rows = []
        for c in sorted(ALL, key=lambda c: (CORDER.index(c["category"]), -(c["f"] or 0), c["name"])):
            pm = "；".join(sorted({f"{p['name']}（{p['institution']}）" for p in c["prof_matches"]}))
            rows.append(f'<tr data-cat="{c["category"]}" data-tier="{c["tier"]}" data-country="{c["country"]}">'
                        f'<td><b>{esc(c["name"])}</b><div class="muted" style="font-size:12px;white-space:normal;max-width:300px">{esc(c["subfields"].replace(";", " · "))}</div></td>'
                        f'<td><span class="dot" style="background:{CATS[c["category"]][1]}"></span> {esc(CATS[c["category"]][0])}</td><td>{esc(c["tier"])}</td>'
                        f'<td class="n">{esc(c["founded"])}</td><td>{esc(c.get("city_zh") or c["city"])}{(", " + esc(c["region"])) if c["region"] else ""}</td><td>{esc(c["status"])}{(" · " + esc(c["ticker"])) if c["ticker"] else ""}</td>'
                        f'<td class="n" data-v="{c["emp"] or 0}">{("~" + format(int(c["emp"]), ",")) if c["emp"] else "—"}</td>'
                        f'<td class="n" data-v="{c["f"] or 0}">{fmt_usd(c["f"]) if c["f"] else "—"}{(" <span class=conf>" + c["funding_conf"] + "</span>") if c["f"] else ""}</td>'
                        f'<td style="white-space:normal;min-width:180px">{esc(c["last_round"])}</td>'
                        f'<td class="n" data-v="{c["v"] or 0}">{fmt_usd(c["v"]) if c["v"] else "—"}</td>'
                        f'<td class="n" data-v="{c["rev"] or 0}">{(fmt_usd(c["rev"]) + " (" + c["revenue_year"] + ")") if c["rev"] else "—"}</td>'
                        f'<td style="white-space:normal;min-width:200px">{esc("、".join(c["founders"]))}{("<div class=muted style=font-size:12px>" + esc("、".join(c["univs"])) + "</div>") if c["univs"] else ""}</td>'
                        f'<td style="white-space:normal;min-width:160px">{esc(pm) if pm else "—"}</td>'
                        f'<td style="white-space:normal;min-width:180px" class="muted">{esc(c["note"])}</td></tr>')
        head = ["公司 / 细分方向", "赛道", "规模", "成立", "总部", "状态", "员工", "累计融资", "最近融资/交易", "估值/交易价", "最新年收入", "学术创始人 / 关联大学", T("在本站量化地图中的教授", "Professors on this site's QC maps"), "备注"]
        return ('<div class="filters"><input id="q" type="search" placeholder="搜索公司、方向、创始人…" aria-label="搜索公司">'
                '<select id="fcat" aria-label="赛道"><option value="">全部赛道</option>' + "".join(f'<option value="{k}">{CATS[k][0]}</option>' for k in CORDER) + '</select>'
                '<select id="ftier" aria-label="规模"><option value="">全部规模</option>' + "".join(f"<option>{t}</option>" for t in TIERS) + '</select>'
                '<select id="fcountry" aria-label="国家"><option value="">' + T('中国 + 美国 + 加拿大', 'China + US + Canada') + '</option><option value="US">美国</option><option value="CA">加拿大</option><option value="CN">' + T('中国', 'China') + '</option></select>'
                '<span class="muted" id="cnt"></span></div>'
                '<div class="tbl-wrap" style="max-height:640px"><table class="data sortable" id="ctab"><thead><tr>' + "".join(f'<th class="{"n" if h in ("成立","员工","累计融资","估值/交易价","最新年收入") else ""}">{h}</th>' for h in head) +
                "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
                '<p class="note">可信度：<b>A</b> 公司财报/官方公告；<b>B</b> 主流媒体或数据库报道；<b>C</b> 本报告根据公开信息估计，误差可能较大。员工数均为约数。点击表头可排序。</p>')

    def corpus_table():
        rows = "".join(f'<tr data-sec="{d["sector"]}"><td class="n">{i+1}</td><td>{esc(d["name"])}</td><td>{"🇺🇸" if d["country"]=="US" else "🇨🇦"} {d["country"]}</td>'
                       f'<td><span class="dot" style="background:{SECTOR_COL[d["sector"]]}"></span> {esc(SECTOR_ZH[d["sector"]])}</td><td class="n">{d["papers"]}</td><td class="n">{d["nauth"]}</td><td class="n">{d["cites"]:,}</td>'
                       f'<td class="n">{min(y for y in d["years"] if y)}–{max(y for y in d["years"] if y)}</td><td class="n">{sum(v for y,v in d["years"].items() if y and y>=2020)}</td></tr>'
                       for i, d in enumerate(CL))
        return ('<div class="filters"><input id="q2" type="search" placeholder="搜索全部 ' + str(n_comp) + ' 家企业…" aria-label="搜索企业"><span class="muted" id="cnt2"></span></div>'
                '<div class="tbl-wrap" style="max-height:520px"><table class="data sortable" id="ptab"><thead><tr><th class="n">#</th><th>企业（OpenAlex 机构名）</th><th>国家</th><th>行业（自动分类）</th><th class="n">论文</th><th class="n">作者</th><th class="n">被引</th><th class="n">年份跨度</th><th class="n">2020 后论文</th></tr></thead><tbody>' + rows + "</tbody></table></div>")

    def mna_table():
        rows = "".join(f'<tr><td class="n">{d["year"]}</td><td>{esc(d["name"])}</td><td>{esc(d["type"])}</td><td class="n">{fmt_usd(d["usd_m"])}</td><td style="white-space:normal">{esc(d["note"])}</td><td><a href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["src"])}</a></td></tr>' for d in sorted(deal_events, key=lambda d: (-d["year"], -d["usd_m"])))
        return '<div class="tbl-wrap"><table class="data"><thead><tr><th class="n">年份</th><th>交易</th><th>类型</th><th class="n">金额</th><th>说明</th><th>来源</th></tr></thead><tbody>' + rows + "</tbody></table></div>"

    def forecast_table():
        rows = "".join(f'<tr><td>{esc(f["metric"])}</td><td class="n">{esc(f["base"])}</td><td class="n">{esc(f["target"])}</td><td class="n">{esc(f["cagr"])}</td><td>{esc(f["kind"])}</td><td><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["src"])}</a></td></tr>' for f in fc)
        return '<div class="tbl-wrap"><table class="data"><thead><tr><th>指标</th><th class="n">基准值</th><th class="n">预测值</th><th class="n">年复合增速</th><th>性质</th><th>来源</th></tr></thead><tbody>' + rows + "</tbody></table></div>"

    def capmkt_table():
        rows = "".join(f'<tr><td>{esc(r["name"])}</td><td>{esc(r["ticker"])}</td><td style="white-space:normal">{esc(r["what"])}</td><td><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["src"])}</a></td></tr>' for r in M["capital_markets"])
        return '<div class="tbl-wrap"><table class="data"><thead><tr><th>公司</th><th>代码</th><th>资本市场要点</th><th>来源</th></tr></thead><tbody>' + rows + "</tbody></table></div>"

    def sec(no_, title, lede, inner):
        return f'<section class="block" id="s{no_}"><div class="wrap"><div class="sec-head"><div class="no">{no_}</div><div><h2>{title}</h2><p>{lede}</p></div></div>{inner}</div></section>'
    charts = lambda L: '<div class="charts">' + "".join(L) + "</div>"
    def part(cls, tag, title, lede):
        return f'<div class="part {cls}"><div class="wrap"><span class="tag">{tag}</span><h2>{title}</h2><p>{lede}</p></div></div>'

    # ---------------- China half + comparison
    import build_cn
    ctx = dict(F_=F_, charts=charts, sec=sec, mapfig=mapfig)
    na_stats = dict(n=n, n_comp=n_comp, n_cw=n_cw, fund_total=fund_total, fund_AB=fund_AB, by_cat=by_cat, fund_cat=fund_cat, fund_cat_c=fund_cat_c,
                    with_founders=len(with_founders), young=len(young), yr_sector=yr_sector, sec_papers=sec_papers)
    CN = build_cn.build(ctx); cp = CN["parts"]; cs = CN["stats"]
    vs_figs, vs_tbl = build_cn.compare(ctx, na_stats, cs)

    # ---------------- findings
    q25 = M["quantum_startup_investment"]["data"]
    findings = [
        (f"{n} 家", f"精选收录的北美量子/计算化学企业（美国 {by_country['US']}、加拿大 {by_country['CA']}），另有 {n_comp} 家企业出现在 OpenAlex 论文语料中。"),
        (f"{fmt_usd(fund_total)}", f"私营公司已知累计融资，其中 {fund_AB/fund_total*100:.0f}% 有公开报道，其余为估计。"),
        (f"{top_cluster_share*100:.0f}%", "的公司集中在三大集群：旧金山湾区、波士顿/剑桥、纽约—新泽西。"),
        (f"{len(young)} 家", f"成立于 2015 年后；其中有融资数据的公司融资中位数 {fmt_usd(med_young_f)}。"),
        (f"6.3×", f"2025 年全球量子初创投资 {q25['2025']} 十亿美元，是 2024 年的 6.3 倍（McKinsey）。"),
        (f"{len(with_founders)} 家", f"有可考的学术创始人；其中 {len(matched)} 家的创始人出现在本站的北美量化教授名单中。"),
    ]
    cn_find = [(T(f"{cs['n']} 家", f"{cs['n']}"), T(f"精选收录的中国量子/计算化学企业，另有 {cs['n_comp']} 家中国企业出现在 OpenAlex 论文语料中。", f"Chinese quantum/computational chemistry companies selected, plus {cs['n_comp']} Chinese companies in the OpenAlex paper corpus.")),
               (fmt_usd(cs["fund_total"]), T(f"中国公司已知累计融资（人民币按 7.2 折算），其中 {cs['fund_AB']/cs['fund_total']*100:.0f}% 有公开报道。", f"known cumulative funding of Chinese companies (RMB at 7.2); {cs['fund_AB']/cs['fund_total']*100:.0f}% is publicly reported.")),
               (f"{cs['sec_papers']['ENERGY'] * 100 // max(1, sum(cs['sec_papers'].values()))}%", T("的中国企业论文来自能源、电网与核电企业，北美是科技巨头与专业软件商领跑。", "of Chinese corporate papers come from energy, grid and nuclear companies; in North America tech giants and specialist software vendors lead.")),
               (T(f"{cs['by_cat']['QC']} 家", f"{cs['by_cat']['QC']}"), T("中国量子计算相关企业：合肥（本源、国盾、国仪）与北京、深圳、上海四地并进，2026 年迎来上市潮。", "Chinese quantum computing companies: Hefei (Origin, QuantumCTek, CIQTEK), Beijing, Shenzhen and Shanghai advance together, with a wave of listings in 2026."))]

    # ---------------- assemble
    CM = CN["M"]
    for k in ("summary_html", "outlook_html", "method_html", "compare_html"): T_html(CM[k], CM[k + "_en"]) if CM.get(k + "_en") else None
    H3 = lambda t: f"<h3 style='margin:28px 0 10px'>{t}</h3>"
    toc = [("00", "核心发现"), ("01", T("北美", "North America")), ("08", T("中国", "China")), ("15", T("中美对比", "China vs North America")), ("16", "企业名录"), ("17", "方法与来源")]
    body = []
    body.append(f'''<header class="hero"><div class="wrap"><div class="eyebrow">{T("07 · 中美企业 · Industry Report", "07 · Companies · Industry Report")}</div>
<h1>{T("中美量子化学与计算化学产业报告", "Quantum and Computational Chemistry Industry Report: China and North America")}</h1>
<p class="lede">{T("从 1987 年的 Gaussian 到 2026 年合肥、北京、深圳的量子上市潮，计算化学的商业化有两个中心。本报告用同一套口径盘点北美（美国与加拿大）和中国的软件商、量子计算公司、AI 药物与材料发现公司，以及药企、化工、能源和科技巨头的计算化学部门，量化它们的地理分布、资本投入、收入、产学关系与未来走向，并做中美对比。", "From Gaussian in 1987 to the 2026 wave of quantum listings in Hefei, Beijing and Shenzhen, computational chemistry has two commercial centres. With one consistent method this report surveys North America (US and Canada) and China: software vendors, quantum computing companies, AI drug and materials discovery companies, and the computational chemistry groups of pharma, chemical, energy and tech companies. It measures their geography, capital, revenue, ties to academia and outlook, and compares the two.")}</p>
<div class="hero-figs"><div><b>{n} + {cs["n"]}</b><span>{T("精选企业（北美 + 中国）", "Selected companies (NA + China)")}</span></div><div><b>{n_comp} + {cs["n_comp"]}</b><span>{T("论文语料中的企业", "Companies in the paper corpus")}</span></div><div><b>{fmt_usd(fund_total)}</b><span>{T("北美已知私营融资", "Known private funding, North America")}</span></div><div><b>{fmt_usd(cs["fund_total"])}</b><span>{T("中国已知融资", "Known funding, China")}</span></div><div><b>{n_cw:,} / {cs["n_cw"]:,}</b><span>{T("企业参与论文（北美 / 中国）", "Papers with company authors (NA / China)")}</span></div><div><b>{no[0]}</b><span>{T("张统计图", "charts")}</span></div></div>
<nav class="toc">{"".join(f'<a href="#s{a}">{a} {b}</a>' for a, b in toc)}</nav>
</div></header>''')
    fnd = lambda L: '<div class="findings">' + "".join(f'<div class="finding"><b>{a}</b>{b}</div>' for a, b in L) + "</div>"
    body.append(sec("00", "核心发现", T("北美六个数字、中国四个数字，概括两地产业现状。", "Six numbers for North America and four for China sum up the two industries."),
                    H3(T("北美", "North America")) + fnd(findings) + H3(T("中国", "China")) + fnd(cn_find) +
                    '<div class="prose">' + M["summary_html"] + CM["summary_html"] + "</div>"))
    body.append(part("na", "PART 1", T("北美", "North America"), T("美国与加拿大：113 家精选企业，第 01–07 节。", "United States and Canada: 113 selected companies, sections 01–07.")))
    body.append(sec("01", "产业版图：八大赛道", "按主营业务把企业归入八条赛道。大型企业以药企、化工和科技巨头的内部计算化学团队为主；初创企业集中在量子计算与 AI 驱动的分子发现。", charts(s1)))
    body.append(sec("02", "地理集群", "企业总部的真实分布。北美的计算化学产业高度集中在少数几个大学密集的都会区。", charts(s2)))
    body.append(sec("03", "资本投入：过去与现在", "股权融资、并购与上市。资本正以前所未有的规模涌入量子硬件和「AI 科学家」类公司。", charts(s3) + H3("重大交易明细") + mna_table() + H3("上市公司资本市场动态") + capmkt_table()))
    body.append(sec("04", "收入：谁在赚钱", "多数初创仍未盈利。真正形成规模收入的，是卖软件许可的老牌公司和卖算力/合同的量子硬件上市公司。", charts(s4)))
    body.append(sec("05", "趋势与预测", "第三方预测（带来源）与本报告情景分析（带假设）严格分开标注。", charts(s5) + H3("预测数据一览") + forecast_table() + '<div class="prose">' + M["outlook_html"] + "</div>"))
    body.append(sec("06", "论文足迹：企业在做什么研究", f"用与「北美量化地图」相同的 OpenAlex 语料口径，找出所有有北美企业作者的量子/计算化学论文（{n_cw:,} 篇，2000–2026），这是比精选名录更完整的「长尾」。", charts(s6) +
                    H3("全部 " + str(n_comp) + " 家企业") + corpus_table() +
                    '<p class="note">行业为按机构名的规则自动分类，「其他」中仍有不少小型咨询公司与专业企业。OpenAlex 将少数国家实验室运营方也标为 company（已剔除 Canadian Light Source）。</p>'))
    body.append(sec("07", "产学关系", "企业与大学的连接有两种：教授创办公司，以及教授与企业研究员合写论文。后者直接链接到本站「北美量化地图」中的教授。", charts(s7)))
    body.append(part("cn", "PART 2", T("中国", "China"), T(f"中国内地与香港：{cs['n']} 家精选企业，第 08–14 节。结构、赛道定义和可信度标记与北美部分完全一致。", f"Mainland China and Hong Kong: {cs['n']} selected companies, sections 08–14. Structure, segment definitions and reliability grades match the North American part.")))
    body.append(sec("08", T("中国产业版图", "China's industry landscape"), T("中国的大公司以国企、CRO 与科技巨头为主；创业公司集中在 AI 药物/材料发现和量子计算，几乎都成立于 2015 年后。", "China's large companies are mostly state-owned enterprises, CROs and tech giants; start-ups cluster in AI drug/materials discovery and quantum computing, almost all founded after 2015."), charts(cp["s1"])))
    body.append(sec("09", T("中国地理集群", "China's geographic clusters"), T("北京、上海—杭州、合肥、深圳—香港四极。合肥凭中国科大成为量子产业中心。", "Four poles: Beijing, Shanghai–Hangzhou, Hefei and Shenzhen–Hong Kong. Hefei, home to USTC, is the centre of the quantum industry."), charts(cp["s2"])))
    body.append(sec("10", T("中国资本投入", "Capital in China"), T("国家资本与市场化资本并行：国家创业投资引导基金、国资产业基金与高瓴、红杉等共同出手，2026 年量子赛道融资创历史新高。", "State and market capital run side by side: the national venture guidance fund, state industrial funds and firms such as Hillhouse and HongShan all invest, and quantum funding hit a record in 2026."), charts(cp["s3"]) + H3(T("中国重大交易明细", "Major deals in China")) + cp["deal_tbl"]))
    body.append(sec("11", T("中国收入", "Revenue in China"), T("规模收入集中在 CRO 与上市量子/仪器公司；纯 AI 发现公司的收入仍依赖少数大额合作。", "Large revenues sit with CROs and listed quantum/instrument companies; pure AI discovery companies still depend on a few large partnerships."), charts(cp["s4"])))
    body.append(sec("12", T("中国趋势与预测", "Trends and forecasts for China"), "第三方预测（带来源）与本报告情景分析（带假设）严格分开标注。", charts(cp["s5"]) + H3("预测数据一览") + cp["fc_tbl"] + '<div class="prose">' + CM["outlook_html"] + "</div>"))
    body.append(sec("13", T("中国论文足迹", "China's paper footprint"), T(f"同一 OpenAlex 语料口径，限定中国内地、香港、澳门企业作者（{cs['n_cw']:,} 篇，2000–2026）。", f"Same OpenAlex corpus definition, limited to company authors in mainland China, Hong Kong and Macao ({cs['n_cw']:,} papers, 2000–2026)."), charts(cp["s6"]) + H3(T(f"全部 {cs['n_comp']} 家中国企业", f"All {cs['n_comp']} Chinese companies")) + cp["corp_tbl"]))
    body.append(sec("14", T("中国产学关系", "Academia and industry in China"), T("创始人来自哪些大学，以及哪些「中国量化地图」上的教授与企业合写最多。", "Which universities founders come from, and which professors on the China QC map write most with companies."), charts(cp["s7"])))
    body.append(part("vs", "PART 3", T("中美对比", "China vs North America"), T("同一口径下的结构差异。", "Structural differences under the same definitions.")))
    body.append(sec("15", T("中美对比", "China vs North America"), T("北美是「专业软件 + 风险资本」驱动，中国是「国企研发 + 国家资本 + 新一代创业公司」驱动。", "North America is driven by specialist software plus venture capital; China by state-owned R&D, state capital and a new generation of start-ups."), charts(vs_figs) + H3(T("关键指标对照", "Key indicators side by side")) + vs_tbl + '<div class="prose">' + CM["compare_html"] + "</div>"))
    body.append(sec("16", "企业名录", T(f"全部 {n + cs['n']} 家精选企业（北美 {n}、中国 {cs['n']}），可搜索、按国家/赛道/规模筛选、排序。原始数据见仓库", f"All {n + cs['n']} selected companies ({n} North American, {cs['n']} Chinese); search, filter by country, segment or size, and sort. Raw data in the repository") + " <code>na-companies/data/</code>。", company_table(C + CN["C"])))
    body.append(sec("17", "方法与来源", "数据如何来、哪里可能不准。", '<div class="prose">' + M["method_html"].replace("%%NCW%%", f"{n_cw:,}") + CM["method_html"] + "<h3>主要来源</h3><ol class='src'>" +
                    "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["name"])}</a></li>' for s in M["sources"] + CM["sources"]) + "</ol></div>"))
    for s_ in CM["sources"]: T(s_["name"], s_.get("name_en", s_["name"]))
    page = TEMPLATE.replace("%%BODY%%", "\n".join(body))
    os.makedirs(P("site"), exist_ok=True)
    open(P("site", "index.html"), "w", encoding="utf-8").write(page)
    stats = {"cn_companies": cs["n"], "cn_corpus_companies": cs["n_comp"], "cn_company_works": cs["n_cw"], "cn_funding_total_musd": round(cs["fund_total"]), "companies": n, "corpus_companies": n_comp, "company_works": n_cw, "funding_total_musd": round(fund_total), "funding_sourced_share": round(fund_AB / fund_total, 3),
             "by_category": by_cat, "by_tier": by_tier, "by_country": by_country, "academic_spinouts": len(with_founders), "founder_prof_matches": len(matched), "charts": no[0]}
    json.dump(stats, open(P("data", "processed", "summary.json"), "w"), ensure_ascii=False, indent=1)
    # strings assembled from several pieces or written as plain zh in shared helpers
    for _zh, _en in {
        "中美量化企业报告": "China–North America quantitative chemistry industry report",
        "00 核心发现": "00 Key findings", "01 北美": "01 North America", "08 中国": "08 China", "15 中美对比": "15 China vs North America",
        "16 企业名录": "16 Company directory", "17 方法与来源": "17 Methods and sources",
        "长三角其他": "Other Yangtze Delta",
        "并购、IPO、超大额融资与授权交易（金额，百万美元）": "M&A, IPOs, mega-rounds and licensing deals (amount, US$ millions)",
        "投资界": "PEdaily", "东方财富": "Eastmoney", "投中网": "ChinaVenture", "36氪": "36Kr", "中国金融信息网": "CNFIN", "新华网": "Xinhua", "国家发改委": "NDRC", "同花顺": "10jqka",
        "最新完整财年（百万美元）": "Latest full fiscal year (US$ millions)", "历年收入（百万美元）": "Revenue by year (US$ millions)",
        "2026 1–9月": "2026 Jan–Sep", "合写的量子/计算化学论文数": "Co-authored quantum/computational chemistry papers",
        "中国企业论文在 2024 年首次超过北美。2026 年为不完整年份，未画出。": "Chinese corporate papers first overtook North America's in 2024. 2026 is a partial year and is not plotted.",
        "数据截至 2026 年 11 月。公司资料为人工整理并标注可信度，论文数据来自 OpenAlex（CC0）。人民币按 1 美元 = 7.2 元折算。预测部分区分第三方预测与本报告情景假设，不构成投资建议。":
            "Data as of November 2026. Company profiles are curated by hand and labelled for confidence; paper data come from OpenAlex (CC0). RMB is converted at 7.2 per US dollar. Forecasts separate third-party projections from this report's own scenario assumptions and are not investment advice.",
    }.items(): T(_zh, _en)
    import sys as _sys
    if "build_report" in _sys.modules: I18N.update(_sys.modules["build_report"].I18N)  # build_cn imports this file as a second module
    json.dump(dict(sorted(I18N.items())), open(P("data", "processed", "i18n_en_additions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False), os.path.getsize(P("site", "index.html")))


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>中美量化企业报告</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;900&display=swap">
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/nav.js" data-root=".." defer></script>
<style>
:root{--c-tech:#4f6d7a;--c-info:#8a8f5a;--c-gov:#9a6b4f;--c-other:#b3b0a6;--c-est:#c9c5ba}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c-tech:#8fb3c2;--c-info:#c4c98a;--c-gov:#d29b7a;--c-other:#5c6a72;--c-est:#4a565e}}
:root[data-theme="dark"]{--c-tech:#8fb3c2;--c-info:#c4c98a;--c-gov:#d29b7a;--c-other:#5c6a72;--c-est:#4a565e}
body{background:var(--paper)}
.toc{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:22px;font-size:13.5px}
.toc a{color:var(--ink-2)} .toc a:hover{color:var(--accent)}
.prose{max-width:820px;margin-top:26px;color:var(--ink-2)} .prose h3{margin:22px 0 8px;color:var(--ink)} .prose p,.prose li{font-size:15px}
.prose b{color:var(--ink)} .src{font-size:13px;columns:2 340px} .src li{margin-bottom:4px;break-inside:avoid}
.filters{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 12px}
.filters input,.filters select{font:inherit;font-size:14px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--raise);color:var(--ink)}
.filters input{flex:1 1 240px}
.conf{font:500 10.5px var(--mono);border:1px solid var(--line);border-radius:4px;padding:0 4px;color:var(--muted);margin-left:3px}
table.sortable th{cursor:pointer} table.sortable th:hover{color:var(--accent)}
table.data td{vertical-align:top}
.mapleg .pill.off{opacity:.35}
.part{margin:0;padding:64px 0 8px;border-top:1px solid var(--line)}
.part .wrap{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
.part .tag{font:500 12px var(--mono);letter-spacing:.14em;color:var(--muted)}
.part h2{font-size:clamp(28px,4vw,40px);font-weight:900}
.part p{flex-basis:100%;color:var(--ink-2);margin:6px 0 0;max-width:760px}
.part.cn h2{color:var(--cn)} .part.na h2{color:var(--us)} .part.vs h2{color:var(--accent)}
.plot svg text{user-select:none}
code{font-family:var(--mono);font-size:.9em}
@media (max-width:640px){.hero-figs b{font-size:24px}.plot{overflow-x:auto;-webkit-overflow-scrolling:touch}.plot svg{min-width:560px}figure.chart.wide .plot svg{min-width:640px}}
</style>
</head>
<body data-nav="bar">
%%BODY%%
<footer class="site"><div class="wrap">数据截至 2026 年 11 月。公司资料为人工整理并标注可信度，论文数据来自 OpenAlex（CC0）。人民币按 1 美元 = 7.2 元折算。预测部分区分第三方预测与本报告情景假设，不构成投资建议。</div></footer>
<div class="viz-tip" id="tip" hidden></div>
<script>
(function(){
  const tip=document.getElementById('tip'),EN=()=>document.documentElement.lang==='en';
  // English tooltips: same dictionary the host uses for the page (window.CHEMHUB_I18N_EN), exact line, then number template, then segments
  function tr(s){const D=window.CHEMHUB_I18N_EN;if(!D||!EN()||!/[\u3400-\u9fff]/.test(s))return s;if(D[s])return D[s];
    const nums=[];const k=s.replace(/\d[\d,.]*/g,m=>{nums.push(m);return '{'+(nums.length-1)+'}';});if(D[k])return D[k].replace(/\{(\d+)\}/g,(_,i)=>nums[i]);
    return s.split(/( · |：|，|（|）)/).map(g=>g==='：'?': ':g==='，'?', ':g==='（'?' (':g==='）'?')':(D[g]||g)).join('').replace(/ 家$/,'').replace(/ 篇$/,' papers');}
  document.addEventListener('pointerover',e=>{const t=e.target.closest('[data-tip]');if(!t)return;tip.innerHTML=t.getAttribute('data-tip').split('\n').map(tr).map((l,i)=>i?'<div class="m">'+l.replace(/</g,'&lt;')+'</div>':'<b>'+l.replace(/</g,'&lt;')+'</b>').join('');tip.hidden=false;});
  document.addEventListener('pointermove',e=>{if(tip.hidden)return;const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=Math.min(e.clientY+14,innerHeight-tip.offsetHeight-8);tip.style.left=x+'px';tip.style.top=y+'px';});
  document.addEventListener('pointerout',e=>{if(e.target.closest('[data-tip]'))tip.hidden=true;});
  // map legend filter
  document.querySelectorAll('.mapfig').forEach(fg=>{const on=new Set();fg.querySelectorAll('.mapleg .pill').forEach(p=>p.addEventListener('click',()=>{const c=p.dataset.cat;on.has(c)?on.delete(c):on.add(c);
    fg.querySelectorAll('.mapleg .pill').forEach(q=>q.classList.toggle('off',on.size&&!on.has(q.dataset.cat)));
    fg.querySelectorAll('.mdot').forEach(d=>d.style.display=(!on.size||on.has(d.dataset.cat))?'':'none');}));});
  // sortable tables
  document.querySelectorAll('table.sortable').forEach(tb=>{tb.querySelectorAll('th').forEach((th,i)=>th.addEventListener('click',()=>{
    const body=tb.tBodies[0],rows=[...body.rows],dir=th.dataset.dir==='d'?1:-1;th.dataset.dir=dir===1?'a':'d';
    const val=r=>{const c=r.cells[i];if(c.dataset.v!==undefined)return +c.dataset.v;const t=c.textContent.trim();const n=parseFloat(t.replace(/[^0-9.\-]/g,''));return th.classList.contains('n')&&!isNaN(n)?n:t;};
    rows.sort((a,b)=>{const x=val(a),y=val(b);return (x>y?1:x<y?-1:0)*dir;});rows.forEach(r=>body.appendChild(r));}));});
  // filters
  function filt(){const q=(document.getElementById('q').value||'').toLowerCase(),c=document.getElementById('fcat').value,t=document.getElementById('ftier').value,k=document.getElementById('fcountry').value;let n=0;
    document.querySelectorAll('#ctab tbody tr').forEach(r=>{const ok=(!q||r.textContent.toLowerCase().includes(q))&&(!c||r.dataset.cat===c)&&(!t||r.dataset.tier===t)&&(!k||r.dataset.country===k);r.style.display=ok?'':'none';n+=ok;});
    document.getElementById('cnt').textContent=EN()?n+' companies':n+' 家';}
  ['q','fcat','ftier','fcountry'].forEach(id=>document.getElementById(id).addEventListener('input',filt));filt();
  function filt2(){const q=(document.getElementById('q2').value||'').toLowerCase();let n=0;document.querySelectorAll('#ptab tbody tr').forEach(r=>{const ok=!q||r.textContent.toLowerCase().includes(q);r.style.display=ok?'':'none';n+=ok;});document.getElementById('cnt2').textContent=EN()?n+' companies':n+' 家';}
  document.getElementById('q2').addEventListener('input',filt2);filt2();
  function filt3(){const q=(document.getElementById('q3').value||'').toLowerCase();let n=0;document.querySelectorAll('#ptab3 tbody tr').forEach(r=>{const ok=!q||r.textContent.toLowerCase().includes(q);r.style.display=ok?'':'none';n+=ok;});document.getElementById('cnt3').textContent=EN()?n+' companies':n+' 家';}
  document.getElementById('q3').addEventListener('input',filt3);filt3();
})();
</script>
</body>
</html>'''

if __name__ == "__main__":
    main()
