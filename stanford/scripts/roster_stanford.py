"""Parse Stanford department faculty pages (Drupal 'hb' theme) into data/processed/roster.csv."""
import re, csv, html, os, sys, urllib.request, time
A = {"User-Agent": "Mozilla/5.0 (research-network roster parser)"}
SITES = {
  "Mathematics": ("https://mathematics.stanford.edu", "/people/faculty-lecturers"),
  "Physics": ("https://physics.stanford.edu", "/people/faculty"),
  "Chemistry": ("https://chemistry.stanford.edu", "/people/faculty"),
  "Applied Physics": ("https://appliedphysics.stanford.edu", "/people/faculty"),
}
def fetch(url):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=A), timeout=60).read().decode("utf8", "ignore")
        except Exception as e: err = e; time.sleep(2)
    print("fail", url, err, file=sys.stderr); return ""
def clean(s): return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ").strip()
def parse(h):
    out = []
    # each person: heading link to /people/<slug>
    for m in re.finditer(r'<h[23][^>]*>\s*<a href="(/people/[^"#?]+)"[^>]*>(.*?)</a>', h, re.S):
        seg = h[m.end(): m.end() + 6000]
        nxt = re.search(r'<h[23][^>]*>\s*<a href="/people/', seg)
        if nxt: seg = seg[:nxt.start()]
        t = re.search(r'person-title.*?<(?:div|em)[^>]*class="field-content[^"]*"[^>]*>(.*?)</(?:div|em)>', seg, re.S)
        areas = [clean(x) for x in re.findall(r'<a href="/research/[^"]*"[^>]*>(.*?)</a>', seg)]
        out.append(dict(slug=m.group(1), name=clean(m.group(2)), title=clean(t.group(1)) if t else "", areas="; ".join(areas)))
    if not out:  # physics-style grid cards
        for m in re.finditer(r'data-link-url="(/people/[^"#?]+)" data-link-text="([^"]+)"', h):
            seg = h[m.end(): m.end() + 8000]
            nxt = seg.find('data-link-url="/people/')
            if nxt > 0: seg = seg[:nxt]
            t = re.search(r'person-title.*?class="field-content[^"]*"[^>]*>(.*?)</(?:div|em)>', seg, re.S)
            areas = [clean(x) for x in re.findall(r'<a href="/research/[^"]*"[^>]*>(.*?)</a>', seg)]
            out.append(dict(slug=m.group(1), name=clean(m.group(2)), title=clean(t.group(1)) if t else "", areas="; ".join(areas)))
    return out
rows = {}
for dept, (base, path) in SITES.items():
    n0 = len(rows)
    for page in range(0, 15):
        fn = f"data/raw/roster/{dept.replace(' ', '_')}_{page}.html"
        h = open(fn).read() if os.path.exists(fn) else fetch(base + path + (f"?page={page}" if page else ""))
        if not h: break
        open(fn, "w").write(h)
        ps = parse(h); new = 0
        for p in ps:
            k = (dept, p["slug"])
            if k not in rows: rows[k] = dict(p, dept=dept, url=base + p["slug"]); new += 1
        if not new: break
    print(dept, len(rows) - n0)
os.makedirs("data/processed", exist_ok=True)
with open("data/raw/roster/all_parsed.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["name", "dept", "title", "areas", "url", "slug"]); w.writeheader(); w.writerows(rows.values())

# ---- Applied Physics: list view grouped in blocks (Faculty / Courtesy / Adjunct / Emeritus / In Memoriam)
h = open("data/raw/roster/Applied_Physics_0.html").read()
for b in re.split(r'id="block-views-block-faculty-block-', h)[1:]:
    t = re.search(r'block__title">(.*?)<', b); t = t.group(1).strip() if t else ""
    for pid, n in re.findall(r'<a href="/profile/(\d+)" hreflang="und">([^<]+)</a></span>', b):
        rows[("Applied Physics", pid)] = dict(slug=f"/profile/{pid}", name=html.unescape(n).strip(), title=t, areas="", dept="Applied Physics",
                                              url=f"https://appliedphysics.stanford.edu/profile/{pid}")

# ---- filter to active professorial faculty and merge joint appointments
EXCL = re.compile(r"emerit|lecturer|adjunct|courtesy|in memoriam|visiting", re.I)
import unicodedata
NICK = {"jon": "jonathan", "mike": "michael", "sasha": "alexander", "tom": "thomas"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    n = re.sub(r"\(.*?\)", "", n); n = re.sub(r"\b[A-Z]\.\s*", "", n)
    p = n.lower().replace("-", " ").split(); return (NICK.get(p[0], p[0]), p[-1]) if p else ("", "")
merged = {}
for r in rows.values():
    if EXCL.search(r["title"]) and "by courtesy" not in r["title"].lower(): continue
    if r["dept"] == "Mathematics" and re.search(r"of (Physics|Computer Science)\b(?! and)", r["title"]) and "Mathematics" not in r["title"].split(",")[0].replace("by courtesy, of Mathematics", ""):
        r = dict(r, courtesy_math=True)  # e.g. physicist with courtesy math appointment: keep but mark
    k = key(r["name"])
    note = "joining " + re.search(r"Joining (\d{4})", r["name"]).group(1) if "Joining" in r["name"] else ""
    name = re.sub(r"\s*\(.*?\)", "", r["name"]).strip()
    if k in merged:
        merged[k]["depts"].add(r["dept"]); merged[k]["areas"] += ("; " if merged[k]["areas"] and r["areas"] else "") + r["areas"]
        continue
    merged[k] = dict(name=name, dept=r["dept"], depts={r["dept"]}, title=r["title"], areas=r["areas"], url=r["url"], note=note)
out = []
for m in merged.values():
    # a person listed by Math only via a courtesy appointment belongs to their home dept
    if m["dept"] == "Mathematics" and len(m["depts"]) > 1 and re.search(r"Professor of (Physics|Applied Physics)", m["title"]):
        m["dept"] = sorted(m["depts"] - {"Mathematics"})[0]
    out.append(dict(name=m["name"], dept=m["dept"], campus="Stanford", title=m["title"] or "Professor",
                    all_depts="/".join(sorted(m["depts"])), areas=m["areas"], url=m["url"], source=m["url"].split("/people")[0].split("/profile")[0], note=m["note"]))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
import collections
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
