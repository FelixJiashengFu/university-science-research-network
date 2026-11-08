"""Fetch every OpenAlex work (2000-2026) in the quantum/computational chemistry corpus that has at least one
company-affiliated author in the chosen region, using the same five corpus queries as na-quantum-chem-map
and cn-quantum-chem-map.

Usage: python3 scripts/fetch_openalex_companies.py [na|cn]      (default na)
  na  US + Canada          -> data/raw/company_works.jsonl
  cn  mainland China + Hong Kong + Macao -> data/raw/cn_company_works.jsonl
Needs OPENALEX_API_KEY in the environment (never commit it).
"""
import json, os, sys, time, urllib.parse, urllib.request

KEY = os.environ["OPENALEX_API_KEY"]
REGION = (sys.argv[1] if len(sys.argv) > 1 else "na").lower()
COUNTRIES = {"na": "US|CA", "cn": "CN|HK|MO"}[REGION]
BASE = f"authorships.institutions.type:company,authorships.institutions.country_code:{COUNTRIES},publication_year:2000-2026"
QUERIES = {
    "topic": "primary_topic.id:T10002|T11177|T12044|T11948",
    "qc": "concepts.id:C183971685|C22994065|C81263218|C20853536|C19637589",
    "dft": "concepts.id:C152365726",
    "md": "concepts.id:C59593255",
    "journal": "primary_location.source.issn:1549-9618|0021-9606|0192-8651|1759-0876|0020-7608|1432-881X",
}
SELECT = "id,doi,title,publication_year,cited_by_count,authorships,primary_topic"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", {"na": "company_works.jsonl", "cn": "cn_company_works.jsonl"}[REGION])

def get(params):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for a in range(7):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "na-companies-report/0.1"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print("retry", a, getattr(e, "code", e), file=sys.stderr); time.sleep(2 ** a)
    raise RuntimeError("failed " + url[:150])

def compact(w, q):
    au = []
    for a in w.get("authorships") or []:
        au.append({"a": ((a.get("author") or {}).get("id") or "").rsplit("/", 1)[-1],
                   "n": (a.get("author") or {}).get("display_name"),
                   "i": [{"id": (i.get("id") or "").rsplit("/", 1)[-1], "n": i.get("display_name"),
                          "t": i.get("type"), "c": i.get("country_code"),
                          "l": [x.rsplit("/", 1)[-1] for x in i.get("lineage") or []]} for i in a.get("institutions") or []]})
    pt = w.get("primary_topic") or {}
    return {"id": w["id"].rsplit("/", 1)[-1], "doi": w.get("doi"), "title": w.get("title"), "year": w.get("publication_year"),
            "cites": w.get("cited_by_count"), "topic": pt.get("display_name"),
            "subfield": (pt.get("subfield") or {}).get("display_name"), "q": [q], "au": au}

def main():
    works = {}
    for q, f in QUERIES.items():
        cursor, n = "*", 0
        while cursor:
            d = get({"filter": f"{BASE},{f}", "per_page": 200, "cursor": cursor, "select": SELECT})
            for w in d["results"]:
                k = w["id"].rsplit("/", 1)[-1]
                if k in works: works[k]["q"].append(q)
                else: works[k] = compact(w, q)
            n += len(d["results"]); cursor = d["meta"].get("next_cursor")
            if not d["results"]: break
        print(q, n, "unique so far", len(works), file=sys.stderr)
    with open(OUT, "w") as fh:
        for w in works.values(): fh.write(json.dumps(w, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
