"""Infer the math / physics / chemistry faculty of one school from OpenAlex and download their works.

usage: OPENALEX_API_KEY=... python3 fetch.py <slug>        (slug from schools.json)

There is no shared faculty roster for these schools, so the roster is inferred from publications:
  1. corpus  = works 2019-2025 with an author affiliated to the school (institution lineage)
               and primary topic in Mathematics (26), Physics and Astronomy (31) or Chemistry (16)
  2. a person is a likely faculty member / group leader when, on papers carrying the school's affiliation,
     they have >= 10 papers (math >= 6), >= 2 papers in 2023-2025, last-author share >= 30% on papers
     with <= 50 authors (not required in math, where author order is alphabetical),
     h-index >= 12 (math >= 8) and OpenAlex lists the school among their last known institutions.
  3. department = the field of most of those papers. Capped at the 260 people with the highest h-index.
Outputs (raw/ is git-ignored, re-runnable from cache):
  raw/<slug>/corpus.jsonl, raw/<slug>/works/<AID>.jsonl
  ../<slug>/data/processed/matches.csv   (same columns as stanford/data/processed/matches.csv)
"""
import csv, json, os, sys, time, collections, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["OPENALEX_API_KEY"]
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(f"{HERE}/schools.json"))
FIELD = {"26": "Mathematics", "31": "Physics", "16": "Chemistry"}
CAP = 260

def get(path, **params):
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(params)
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "university-science-research-network/0.2"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            if getattr(e, "code", None) == 404: return None
            time.sleep(2 ** a)
    print("FAILED", url[:140], file=sys.stderr); return None

def corpus(slug, inst):
    fn = f"{HERE}/raw/{slug}/corpus.jsonl"
    if os.path.exists(fn): return [json.loads(l) for l in open(fn)]
    I = set(inst); rows = []
    for fid in FIELD:
        cursor = "*"
        while cursor:
            r = get("works", filter=f"authorships.institutions.lineage:{'|'.join(inst)},publication_year:2019-2025,primary_topic.field.id:{fid},type:article|review|preprint|letter",
                    per_page=200, cursor=cursor, select="id,publication_year,authorships")
            if not r: break
            for w in r["results"]:
                au = w.get("authorships") or []
                n = len(au)
                mine = [i for i, a in enumerate(au) if a.get("author", {}).get("id") and any(set(x.get("lineage") or [x.get("id")]) & {"https://openalex.org/" + k for k in I} for x in a.get("institutions") or [])]
                if not mine: continue
                rows.append({"y": w["publication_year"], "f": fid, "n": n,
                             "a": [[au[i]["author"]["id"].split("/")[-1], au[i]["author"].get("display_name"), i == n - 1 and n > 1] for i in mine]})
            cursor = r["meta"].get("next_cursor")
            if len(r["results"]) < 200: break
        print(slug, FIELD[fid], len(rows), flush=True)
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "w") as f:
        for x in rows: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    return rows

def works(slug, aid):
    fn = f"{HERE}/raw/{slug}/works/{aid}.jsonl"
    if os.path.exists(fn): return
    cursor, rows = "*", []
    while cursor:
        r = get("works", filter=f"author.id:{aid}", per_page=200, cursor=cursor,
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
                "authors": [a["author"]["id"].split("/")[-1] for a in au if a.get("author", {}).get("id")] if len(au) <= 60 else [],
                "topic": pt and {"id": pt["id"].split("/")[-1], "name": pt["display_name"],
                                 "subfield": pt["subfield"]["display_name"], "field": pt["field"]["display_name"], "domain": pt["domain"]["display_name"]},
                "topics": [t["id"].split("/")[-1] for t in (w.get("topics") or [])],
                "keywords": [k["display_name"] for k in (w.get("keywords") or [])][:6],
                "orgs": sorted({(i.get("id", "").split("/")[-1], i.get("display_name"), i.get("type"), i.get("country_code"))
                                for a in au for i in (a.get("institutions") or []) if i.get("type") in ("company", "nonprofit", "government", "facility", "healthcare")})[:40],
            })
        cursor = r["meta"].get("next_cursor")
        if len(r["results"]) < 200 or len(rows) > 3000: break
    with open(fn, "w") as f:
        for x in rows: f.write(json.dumps(x, ensure_ascii=False) + "\n")

def main(slug):
    c = CFG[slug]; inst = c["inst"]
    rows = corpus(slug, inst)
    S = collections.defaultdict(lambda: dict(n=0, last=0, small=0, recent=0, f=collections.Counter(), name=None, au=0))
    for w in rows:
        for aid, nm, last in w["a"]:
            s = S[aid]; s["n"] += 1; s["name"] = s["name"] or nm; s["f"][w["f"]] += 1; s["au"] += w["n"]
            if w["y"] >= 2023: s["recent"] += 1
            if w["n"] <= 50: s["small"] += 1; s["last"] += last
    cand = []
    for aid, s in S.items():
        fid = s["f"].most_common(1)[0][0]; math_ = fid == "26"
        if s["n"] < (6 if math_ else 10) or s["recent"] < 2: continue
        if not math_ and (s["small"] < 5 or s["last"] / s["small"] < 0.30): continue
        cand.append((aid, fid))
    print(slug, "candidates", len(cand), flush=True)
    info = {}
    ids = [a for a, _ in cand]
    for i in range(0, len(ids), 50):
        r = get("authors", filter="openalex_id:" + "|".join(ids[i:i + 50]), per_page=50,
                select="id,display_name,works_count,cited_by_count,summary_stats,last_known_institutions,orcid")
        for a in (r or {}).get("results", []): info[a["id"].split("/")[-1]] = a
    I = {"https://openalex.org/" + k for k in inst}
    keep = []
    for aid, fid in cand:
        a = info.get(aid)
        if not a: continue
        h = (a.get("summary_stats") or {}).get("h_index") or 0
        lki = a.get("last_known_institutions") or []
        if not any(set(x.get("lineage") or [x.get("id")]) & I for x in lki): continue
        if h < (8 if fid == "26" else 12) or a["works_count"] < (15 if fid == "26" else 25): continue
        keep.append((h, aid, fid, a))
    keep.sort(key=lambda x: -x[0]); keep = keep[:CAP]
    print(slug, "faculty", len(keep), collections.Counter(FIELD[f] for _, _, f, _ in keep), flush=True)
    out = f"{HERE}/../{slug}/data/processed"; os.makedirs(out, exist_ok=True)
    with open(f"{out}/matches.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "dept", "campus", "title", "all_depts", "areas", "url", "source", "note", "openalex_id", "openalex_name", "match_score", "match_note", "works_count", "h_index", "orcid"])
        for h, aid, fid, a in keep:
            s = S[aid]
            note = f"按论文推断 · 2019–2025 年本校署名论文 {s['n']} 篇" + (f"，其中末位作者 {s['last']} 篇" if fid != "26" else "")
            w.writerow([a["display_name"], FIELD[fid], "", note, FIELD[fid], "", "", "OpenAlex 推断", note,
                        aid, a["display_name"], 9, "inferred from publications", a["works_count"], h, a.get("orcid") or ""])
    os.makedirs(f"{HERE}/raw/{slug}/works", exist_ok=True)
    with ThreadPoolExecutor(4) as ex: list(ex.map(lambda x: works(slug, x[1]), keep))
    print(slug, "works done", flush=True)

if __name__ == "__main__":
    for s in sys.argv[1:]: main(s)
