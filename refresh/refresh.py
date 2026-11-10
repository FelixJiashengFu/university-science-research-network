"""Monthly data refresh: re-download from OpenAlex and rebuild the pages of one part of the atlas.

usage: OPENALEX_API_KEY=... python3 refresh/refresh.py <part> [--dry]
  maps       North America + China quantum-chemistry maps, both Top 20 pages, China-US comparison,
             UofT and Stanford networks (their official rosters and OpenAlex matches stay as committed)
  schools-1  first 6 schools of schools/pipeline/schools.json   (MIT ... Chicago)
  schools-2  next 6                                              (Columbia ... USTC)
  schools-3  last 6                                              (Fudan ... SYSU)
  --dry      rebuild from whatever is already in the raw caches, without calling OpenAlex (a local test)

The parts are split so that one run costs about $0.1-0.5 of OpenAlex's $1 free daily budget; the monthly workflow
(.github/workflows/monthly-refresh.yml) runs one part a day. Not refreshed here, because they are hand-made:
department rosters, research summaries of the Top 20 (top20|cn-top20/data/manual), startups.csv, and the
North America company report (na-companies), which mixes OpenAlex counts with curated, dated company facts.

A rebuilt page replaces the old one only when its network still has at least 75% of the old node count, so a run that
loses data (budget used up, OpenAlex outage) leaves the published numbers as they were and fails loudly.
"""
import datetime, glob, json, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DRY = "--dry" in sys.argv
PY = sys.executable
SCHOOLS = list(json.load(open(f"{ROOT}/schools/pipeline/schools.json")))
PARTS = {"maps": None, "schools-1": SCHOOLS[0:6], "schools-2": SCHOOLS[6:12], "schools-3": SCHOOLS[12:]}


def run(args, cwd=ROOT, env=None):
    print("+", " ".join(args), f"(in {os.path.relpath(cwd, ROOT)})", flush=True)
    subprocess.run(args, cwd=cwd, check=True, env={**os.environ, **(env or {})})


def fresh(*patterns):
    """Drop cached OpenAlex downloads so the scripts fetch them again (no-op in --dry and on a fresh CI checkout)."""
    if DRY: return
    for p in patterns:
        for f in glob.glob(os.path.join(ROOT, p)):
            shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)


def nodes(path):
    """Size of a page's data: nodes of every network json in a site/data folder (0 when none)."""
    n = 0
    for fn in glob.glob(f"{path}/*.json"):
        try: d = json.load(open(fn))
        except Exception: continue
        if isinstance(d, dict) and isinstance(d.get("nodes"), list): n += len(d["nodes"])
    return n


def guarded(site_data, build):
    """Run build(); if the rebuilt site_data folder shrank below 75% of its nodes, put the old one back and fail."""
    keep = site_data + ".before-refresh"
    shutil.rmtree(keep, ignore_errors=True)
    if os.path.isdir(site_data): shutil.copytree(site_data, keep)
    before = nodes(site_data)
    build()
    after = nodes(site_data)
    print(f"  {os.path.relpath(site_data, ROOT)}: {before} -> {after} nodes", flush=True)
    if before and after < 0.75 * before:
        shutil.rmtree(site_data); shutil.move(keep, site_data)
        raise SystemExit(f"{site_data}: only {after} of {before} nodes after the refresh; kept the old data")
    shutil.rmtree(keep, ignore_errors=True)


def roster_works(folder, industry):
    """UofT / Stanford: keep the committed roster -> OpenAlex matches, re-download each person's works."""
    d = f"{ROOT}/{folder}"
    fresh(f"{folder}/data/raw/openalex/works", f"{folder}/data/raw/openalex/industry")
    if not DRY:
        code = ("import csv, sys; from concurrent.futures import ThreadPoolExecutor; sys.argv = sys.argv[:1]\n"
                "from openalex_fetch import works\n"
                "ids = sorted({r['openalex_id'] for r in csv.DictReader(open('data/processed/matches.csv')) if r['openalex_id']})\n"
                "list(ThreadPoolExecutor(4).map(works, ids)); print('works', len(ids))")
        run([PY, "-c", code], cwd=d, env={"PYTHONPATH": f"{d}/scripts"})
        if industry: run([PY, "scripts/openalex_industry.py"], cwd=d)
    guarded(f"{d}/site/data", lambda: run([PY, "scripts/build_graph.py"], cwd=d))


def maps():
    for m in ("na-quantum-chem-map", "cn-quantum-chem-map"):
        fresh(f"{m}/data/raw/works_*.jsonl", f"{m}/data/raw/authors", f"{m}/data/raw/institutions")
        if not DRY: run([PY, "scripts/fetch_corpus.py"], cwd=f"{ROOT}/{m}")
        guarded(f"{ROOT}/{m}/site/data", lambda m=m: run([PY, "scripts/build_graph.py"], cwd=f"{ROOT}/{m}"))
    run([PY, "analysis/build_atlas_data.py"])
    roster_works("uoft", industry=True)
    roster_works("stanford", industry=False)
    roster_works("waterloo", industry=False)
    roster_works("udem", industry=False)
    roster_works("mcmaster", industry=False)


def schools(slugs):
    p = f"{ROOT}/schools/pipeline"
    for s in slugs:
        fresh(f"schools/pipeline/raw/{s}")
        def build(s=s):
            if not DRY: run([PY, "fetch.py", s], cwd=p)
            run([PY, "build_graph.py", s], cwd=p)
            run([PY, "make_site.py", s], cwd=p)
        guarded(f"{ROOT}/schools/{s}/site/data", build)


def stamp():
    """Move the 'snapshot / fetched in <year> 年 <month> 月' notes to this month (the English dictionary has
    patterns for these sentences, so only the numbers change)."""
    t = datetime.date.today()
    for fn in ("index.html", "compare/site/index.html"):
        f = f"{ROOT}/{fn}"; s = open(f, encoding="utf-8").read()
        s2 = re.sub(r"20\d\d 年 \d{1,2} 月", f"{t.year} 年 {t.month} 月", s)
        s2 = re.sub(r"截至 20\d\d 年的平均被引", f"截至 {t.year} 年的平均被引", s2)
        if s2 != s: open(f, "w", encoding="utf-8").write(s2)
    u = f"{ROOT}/refresh/updated.json"
    d = json.load(open(u)) if os.path.exists(u) else {}
    d[PART] = t.isoformat()
    json.dump(d, open(u, "w"), indent=1, sort_keys=True); open(u, "a").write("\n")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1 or args[0] not in PARTS: raise SystemExit(__doc__)
    PART = args[0]
    if not DRY and not os.environ.get("OPENALEX_API_KEY"): raise SystemExit("set OPENALEX_API_KEY (never commit it)")
    maps() if PART == "maps" else schools(PARTS[PART])
    stamp()
    print("refreshed", PART, flush=True)
