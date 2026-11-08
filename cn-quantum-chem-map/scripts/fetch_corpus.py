"""Download the US/Canada quantum & computational chemistry corpus from OpenAlex.

Needs OPENALEX_API_KEY in the environment (free key, never commit it).
The corpus is the union of five OpenAlex queries (2000 onward, at least one US/CA author institution):
  topic   primary topic in Advanced Chemical Physics Studies, Spectroscopy and Quantum Chemical Studies,
          Advanced Physical and Chemical Molecular Interactions, Machine Learning in Materials Science
  qc      concepts: ab initio quantum chemistry methods, quantum chemistry, relativistic QC, TDDFT, coupled cluster
  dft     concept: density functional theory
  md      concept: molecular dynamics
  journal published in J. Chem. Theory Comput., J. Chem. Phys., J. Comput. Chem., WIREs Comput. Mol. Sci.,
          Int. J. Quantum Chem., Theor. Chem. Acc.
Output: data/raw/works_<query>.jsonl (compact, one work per line). Re-running skips finished queries.
"""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["OPENALEX_API_KEY"]
BASE = "authorships.institutions.country_code:" + os.environ.get("COUNTRIES", "CN|HK|MO") + ",publication_year:2000-2026"
QUERIES = {
    "topic": "primary_topic.id:T10002|T11177|T12044|T11948",
    "qc": "concepts.id:C183971685|C22994065|C81263218|C20853536|C19637589",
    "dft": "concepts.id:C152365726",
    "md": "concepts.id:C59593255",
    "journal": "primary_location.source.issn:1549-9618|0021-9606|0192-8651|1759-0876|0020-7608|1432-881X",
}
SELECT = "id,doi,title,publication_year,cited_by_count,type,authorships,primary_topic,primary_location"
OUT = os.environ.get("OUT_DIR") or os.path.join(os.path.dirname(__file__), "..", "data", "raw")

def get(params):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for a in range(7):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "research-atlas/0.1"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:
            print("retry", a, getattr(e, "code", e), file=sys.stderr); time.sleep(2 ** a)
    raise RuntimeError("failed " + url[:150])

def compact(w):
    au = w.get("authorships") or []
    src = (w.get("primary_location") or {}).get("source") or {}
    pt = w.get("primary_topic") or {}
    return {
        "id": w["id"].rsplit("/", 1)[-1], "doi": w.get("doi"), "title": w.get("title"), "year": w.get("publication_year"),
        "cites": w.get("cited_by_count") or 0, "type": w.get("type"), "venue": src.get("display_name"),
        "topic": pt.get("display_name"), "n_authors": len(au),
        "au": [[a["author"]["id"].rsplit("/", 1)[-1], a["author"].get("display_name"), a.get("author_position"),
                [[i["id"].rsplit("/", 1)[-1], i.get("display_name"), i.get("type"), i.get("country_code")]
                 for i in (a.get("institutions") or []) if i.get("id")]]
               for a in au[:60] if (a.get("author") or {}).get("id")],
    }

def run(name):
    fn = os.path.join(OUT, f"works_{name}.jsonl")
    if os.path.exists(fn): print(name, "cached"); return
    cursor, n, tmp = "*", 0, fn + ".part"
    with open(tmp, "w") as f:
        while cursor:
            r = get({"filter": f"{BASE},{QUERIES[name]}", "per_page": 200, "cursor": cursor, "select": SELECT})
            for w in r["results"]: f.write(json.dumps(compact(w), ensure_ascii=False) + "\n")
            n += len(r["results"]); cursor = r["meta"].get("next_cursor")
            if not r["results"]: break
            if n % 10000 < 200: print(name, n, "/", r["meta"]["count"], flush=True)
    os.rename(tmp, fn); print(name, "done", n)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(5) as ex: list(ex.map(run, QUERIES))
