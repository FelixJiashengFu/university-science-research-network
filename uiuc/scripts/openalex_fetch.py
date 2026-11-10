"""Match roster names to OpenAlex authors and download their works.

Needs OPENALEX_API_KEY in the environment (free key from openalex.org). Never commit it.
Outputs (cached, re-runnable):
  data/raw/openalex/authors/<slug>.json   candidate search results
  data/raw/openalex/works/<AID>.jsonl     compact works per matched author
  data/processed/matches.csv              roster -> OpenAlex author id
"""
import csv, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

KEY = os.environ["OPENALEX_API_KEY"]
INST = "I157725225"  # University of Illinois Urbana-Champaign
FIELD = {"Mathematics": "26", "Physics": "31", "Chemistry": "16"}
OUT = "data/raw/openalex"
os.makedirs(f"{OUT}/authors", exist_ok=True); os.makedirs(f"{OUT}/works", exist_ok=True)

def get(path, **params):
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(params)
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "uiuc-science-research-network/0.1"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            if getattr(e, "code", None) == 404: return None
            time.sleep(2 ** a)
    print("FAILED", url[:120], file=sys.stderr); return None

ALIAS = {}
def norm(s):
    s = ALIAS.get(s, s).replace("ø", "o").replace("Ø", "O").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"[^a-z ]", " ", s).split()

def slug(s): return "-".join(norm(s))

def name_score(roster, cand):
    a, b = norm(roster), norm(cand)
    if not a or not b: return 0
    last_ok = a[-1] == b[-1] or a[-1] in b
    first_ok = a[0] == b[0] or (len(b[0]) == 1 and b[0] == a[0][0]) or a[0] in b
    return (0.6 if last_ok else 0) + (0.3 if first_ok else 0) + 0.1 * SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()

# manual fixes where OpenAlex splits a person and the search picks a tiny fragment (checked by hand)
# Checked by hand. OpenAlex often splits one person into several author records; the first id is the main
# record, the rest are fragments whose works are merged in. NONE: the only candidates are other people.
OVERRIDE = {"Rui Loja Fernandes": ["A5101438698"], "Polly Yu": ["A5080899968"], "Josh Long": ["A5044571663"],
            "Joaquín Rodríguez-López": ["A5007986677", "A5106521711"], "Liwei Zheng": ["A5050877745"], "Sangjin Kim": ["A5126371026"],
            "Qian Chen": ["A5100428457"], "Catherine J. Murphy": ["A5030076676", "A5142094665"], "Kevin Ford": ["A5110362193", "A5013873679"],
            "Megan A. Steves": ["A5016083292"]}
NONE = {"Wei Wei", "Frank Quan"}  # only other people with the same name in OpenAlex
POOL = list(json.load(open(f"{OUT}/candidates.json")).values()) if os.path.exists(f"{OUT}/candidates.json") else []
def match(row, noaff=False):
    if row["name"] in NONE: return None, 0
    if row["name"] in OVERRIDE:
        ids = OVERRIDE[row["name"]]
        c = get("authors/" + ids[0], select="id,display_name,works_count,summary_stats,orcid")
        if c: return dict(c, _manual=True, _extra=ids[1:]), 9.0
    fn = f"{OUT}/authors/{slug(row['name'])}{'.noaff' if noaff else ''}.json"
    if not noaff and not os.path.exists(fn) and POOL:
        res = [c for c in POOL if name_score(row["name"], c["display_name"]) >= 0.85
               or any(name_score(row["name"], x) >= 0.85 for x in (c.get("display_name_alternatives") or [])[:20])]
        if res: json.dump(res, open(fn, "w"))
    if os.path.exists(fn): res = json.load(open(fn))
    else:
        q = " ".join(norm(row["name"]))
        extra = {} if noaff else {"filter": f"affiliations.institution.id:{INST}"}
        res = get("authors", search=q, per_page=10, **extra,
                  select="id,display_name,display_name_alternatives,works_count,cited_by_count,summary_stats,topics,last_known_institutions,orcid")
        if res is None: return None, 0
        res = res.get("results", [])
        json.dump(res, open(fn, "w"))
    best, bs = None, 0
    for c in res:
        ns = max([name_score(row["name"], c["display_name"])] + [name_score(row["name"], x) for x in (c.get("display_name_alternatives") or [])[:20]])
        if ns < (0.95 if noaff else 0.85): continue
        fields = [t.get("field", {}).get("id", "").split("/")[-1] for t in (c.get("topics") or [])[:10]]
        fscore = sum(1 for f in fields if f in (FIELD[row["dept"]], "31", "16", "26", "17", "19", "22", "13", "25")) / 10
        cur = any("Illinois Urbana" in i.get("display_name", "") for i in c.get("last_known_institutions") or [])
        s = ns + 0.5 * fscore + 0.2 * cur + 0.1 * min(c["works_count"], 300) / 300
        if noaff and fields[:5].count(FIELD[row["dept"]]) < 2: continue
        if s > bs: best, bs = c, s
    if best is None and not noaff:
        b2, s2 = match(row, noaff=True)
        if b2: b2 = dict(b2, _noaff=True)
        return b2, s2
    return best, bs

def works(aid, extra=()):
    fn = f"{OUT}/works/{aid}.jsonl"
    if not extra:  # e.g. called by refresh/refresh.py with the main id only
        extra = next((v[1:] for v in OVERRIDE.values() if v[0] == aid), ())
    ids = (aid,) + tuple(extra)
    if os.path.exists(fn): return
    cursor, rows = "*", []
    while cursor:
        r = get("works", filter="author.id:" + "|".join(ids), per_page=200, cursor=cursor,
                select="id,doi,title,publication_year,cited_by_count,type,authorships,primary_topic,topics,keywords,primary_location")
        if not r: break
        for w in r["results"]:
            au = w.get("authorships") or []
            loc = (w.get("primary_location") or {}).get("source") or {}
            pt = w.get("primary_topic") or {}
            rows.append({
                "id": w["id"].split("/")[-1], "doi": w.get("doi"), "title": w.get("title"),
                "year": w.get("publication_year"), "cites": w.get("cited_by_count"), "type": w.get("type"),
                "venue": loc.get("display_name"), "n_authors": len(au),
                "authors": [aid if a["author"]["id"].split("/")[-1] in ids else a["author"]["id"].split("/")[-1] for a in au if a.get("author", {}).get("id")] if len(au) <= 60 else [],
                "topic": pt and {"id": pt["id"].split("/")[-1], "name": pt["display_name"],
                                 "subfield": pt["subfield"]["display_name"], "field": pt["field"]["display_name"], "domain": pt["domain"]["display_name"]},
                "topics": [t["id"].split("/")[-1] for t in (w.get("topics") or [])],
                "keywords": [k["display_name"] for k in (w.get("keywords") or [])][:6],
                "own": sorted({i.get("id", "").split("/")[-1] for a in au if (a.get("author") or {}).get("id") and a["author"]["id"].split("/")[-1] in ids for i in (a.get("institutions") or [])}),
                "orgs": sorted({(i.get("id", "").split("/")[-1], i.get("display_name"), i.get("type"), i.get("country_code"))
                                for a in au for i in (a.get("institutions") or []) if i.get("type") in ("company", "nonprofit", "government", "facility", "healthcare")})[:40],
            })
        cursor = r["meta"].get("next_cursor")
        if len(r["results"]) < 200: break
    with open(fn, "w") as f:
        for x in rows: f.write(json.dumps(x, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    roster = list(csv.DictReader(open("data/processed/roster.csv")))
    with ThreadPoolExecutor(2) as ex: results = list(ex.map(match, roster))
    out = []
    for row, (c, s) in zip(roster, results):
        row = dict(row); row.update(openalex_id=c["id"].split("/")[-1] if c else "", openalex_name=c["display_name"] if c else "",
                                    match_score=round(s, 3), match_note=("manual override" if c and c.get("_manual") else "no UIUC affiliation in OpenAlex (new hire?)" if c and c.get("_noaff") else ""), works_count=c["works_count"] if c else 0,
                                    h_index=(c.get("summary_stats") or {}).get("h_index", "") if c else "", orcid=(c or {}).get("orcid") or "", extra_ids=" ".join(c.get("_extra", [])) if c else "")
        out.append(row)
    with open("data/processed/matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print("matched", sum(1 for r in out if r["openalex_id"]), "/", len(out))
    if "--works" in sys.argv:
        jobs = {r["openalex_id"]: r["extra_ids"].split() for r in out if r["openalex_id"]}
        ids = sorted(jobs)
        with ThreadPoolExecutor(4) as ex: list(ex.map(lambda a: works(a, jobs[a]), ids))
        print("works done", len(ids))
