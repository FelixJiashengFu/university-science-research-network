"""Industry links: for each matched professor, works that have at least one company-affiliated co-author.

Output: data/raw/openalex/industry/<AID>.jsonl  (one line per work: id, year, cites, title, doi, companies[])
"""
import csv, json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.argv = sys.argv[:1]
from openalex_fetch import get  # noqa: E402

OUT = "data/raw/openalex/industry"; os.makedirs(OUT, exist_ok=True)

def fetch(aid):
    fn = f"{OUT}/{aid}.jsonl"
    if os.path.exists(fn): return
    cursor, rows = "*", []
    while cursor:
        r = get("works", filter=f"author.id:{aid},institutions.type:company", per_page=200, cursor=cursor,
                select="id,doi,title,publication_year,cited_by_count,authorships")
        if r is None: return  # do not cache failures
        for w in r["results"]:
            comps = {}
            for a in w.get("authorships") or []:
                for i in a.get("institutions") or []:
                    if i.get("type") == "company" and i.get("id"):
                        comps[i["id"].split("/")[-1]] = [i.get("display_name"), i.get("country_code")]
            rows.append({"id": w["id"].split("/")[-1], "year": w.get("publication_year"), "cites": w.get("cited_by_count"),
                         "title": w.get("title"), "doi": w.get("doi"), "n_authors": len(w.get("authorships") or []),
                         "companies": [[k, *v] for k, v in comps.items()]})
        cursor = r["meta"].get("next_cursor")
        if len(r["results"]) < 200: break
    with open(fn, "w") as f:
        for x in rows: f.write(json.dumps(x, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ids = sorted({r["openalex_id"] for r in csv.DictReader(open("data/processed/matches.csv")) if r["openalex_id"]})
    with ThreadPoolExecutor(3) as ex: list(ex.map(fetch, ids))
    print("industry done", len(os.listdir(OUT)), "/", len(ids))
