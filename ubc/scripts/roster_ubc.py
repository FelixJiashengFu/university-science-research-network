"""Turn the department pages read in the browser (data/raw/roster/*.txt) into data/processed/roster.csv.

Vancouver: Mathematics (directory "Faculty" tab, associate members left out), Physics & Astronomy ("Faculty" table of
Researchers & Instructors; the honorary professor left out), Chemistry (research + teaching faculty).
Okanagan: Mathematics and Physics from the Department of Mathematics, Physics and Statistics, and Chemistry.
A person listed by two departments (e.g. Sarah Burke: Physics & Chemistry) is kept once per department here;
build_graph.py merges the two rows into one node and records both departments.
"""
import csv, collections, os, re
R = "data/raw/roster"

def rows(fn):
    for line in open(f"{R}/{fn}", encoding="utf-8"):
        line = line.rstrip("\n")
        if line and not line.startswith("#"): yield line.split("|")

def areas(fn):
    out = collections.defaultdict(list)
    for area, names in rows(fn):
        for n in names.split(","): out[n.strip()].append(area)
    return out

def surname(name): return name.split(",")[0].strip()

out = []
A = areas("math_vancouver_fields.txt")
for name, uid in rows("math_vancouver.txt"):
    if "[AM]" in name: continue
    last, first = [x.strip() for x in name.split(",", 1)]
    out.append(dict(name=f"{first} {last}", dept="Mathematics", campus="Vancouver", title="", areas="; ".join(A.get(last, [])),
                    url=f"https://www.math.ubc.ca/user/{uid}", source="https://www.math.ubc.ca/about-our-department/directory", note=""))
A = areas("phas_vancouver_areas.txt")
for first, last, pos, slug in rows("phas_vancouver.txt"):
    if pos.startswith("Honorary"): continue
    out.append(dict(name=f"{first} {last}", dept="Physics & Astronomy", campus="Vancouver", title=pos, areas="; ".join(A.get(last, [])),
                    url=f"https://phas.ubc.ca/users/{slug}", source="https://phas.ubc.ca/researchers", note=""))
A = areas("chem_vancouver_areas.txt")
for grp, name, slug in rows("chem_vancouver.txt"):
    last, first = [x.strip() for x in name.split(",", 1)]
    out.append(dict(name=f"{first} {last}", dept="Chemistry", campus="Vancouver", title=grp, areas="; ".join(A.get(last, [])),
                    url=f"https://www.chem.ubc.ca/{slug}", source="https://www.chem.ubc.ca/faculty", note=""))
for dept, name, title, ar, slug in rows("okanagan.txt"):
    base = "https://chemistry.ok.ubc.ca/about/contact/" if dept == "Chemistry" else "https://mps.ok.ubc.ca/about/contact/"
    out.append(dict(name=name, dept={"Physics": "Physics & Astronomy"}.get(dept, dept), campus="Okanagan", title=title, areas=ar,
                    url=f"{base}{slug}/", source=base, note=""))
# clean display names: "James (Jimmy) Feng" -> keep; "Jaclyn (Jackie) Stewart" -> keep (norm() drops brackets for matching)
by = collections.defaultdict(list)
for r in out: by[r["name"]].append(r)
for r in out: r["all_depts"] = "/".join(sorted({x["dept"] for x in by[r["name"]]}))
os.makedirs("data/processed", exist_ok=True)
cols = ["name", "dept", "campus", "title", "all_depts", "areas", "url", "source", "note"]
with open("data/processed/roster.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
print(len(out), "rows,", len(by), "people;", dict(collections.Counter((r["campus"], r["dept"]) for r in out)))
print("in two departments:", [n for n, v in by.items() if len(v) > 1])
