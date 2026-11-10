"""Turn the University of Michigan (Ann Arbor) department listings into data/processed/roster.csv.

lsa.umich.edu cannot be reached from the build environment, so the listings were read in a browser on
2026-11-10 and saved as pipe-separated text in data/raw/roster/{math,physics,chemistry}.txt:
    name|title|research areas
Scope: tenured and tenure-track faculty. Mathematics' page is already "Tenured, Tenure Track";
for Chemistry the Lecturers on the faculty page are left out to match.
Sources:
  https://lsa.umich.edu/math/people/faculty.html
  https://lsa.umich.edu/physics/people/faculty.html
  https://lsa.umich.edu/chem/people/faculty.html
"""
import csv, re, collections, unicodedata
SRC = {"math": ("Mathematics", "https://lsa.umich.edu/math/people/faculty.html"),
       "physics": ("Physics", "https://lsa.umich.edu/physics/people/faculty.html"),
       "chemistry": ("Chemistry", "https://lsa.umich.edu/chem/people/faculty.html")}
TITLE = {"P": "Professor", "AssocP": "Associate Professor", "AsstP": "Assistant Professor", "Lect": "Lecturer"}
# Physics page abbreviations (expanded) and Chemistry division codes (as tagged on the department page)
PHYS = [("Th ", "Theoretical "), ("Exp ", "Experimental "), ("HEP", "Elementary Particle Physics"), ("CMP", "Condensed Matter Physics"),
        ("Nuc", "Nuclear and Subatomic Physics"), ("AMO", "Atomic, Molecular & Optical"), ("Cosmo/Astro", "Cosmology and Astrophysics")]
CHEM = {"An": "Analytical Chemistry", "In": "Inorganic Chemistry", "Or": "Organic Chemistry", "Ph": "Physical Chemistry",
        "CB": "Chemical Biology", "Ma": "Materials Chemistry", "Th": "Theory & Computation", "Bm": "Biomacromolecular Chemistry",
        "Ca": "Catalysis", "Sy": "Synthesis", "En": "Energy & Environmental Chemistry", "Im": "Imaging & Spectroscopy",
        "Pc": "Photochemistry", "Nn": "Macromolecular Nanochemistry", "Ed": "Chemistry Education"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\(.*?\)", " ", n); n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = [x for x in n.split() if x not in ("iii", "jr")]; return f"{p[0]} {p[-1]}"
people = {}
for f, (dept, url) in SRC.items():
    for line in open(f"data/raw/roster/{f}.txt", encoding="utf8"):
        if not line.strip(): continue
        name, t, areas = (line.rstrip("\n").split("|") + [""] * 3)[:3]
        if t == "Lect": continue
        if f == "physics":
            for a, b in PHYS: areas = areas.replace(a, b)
        if f == "chemistry": areas = "; ".join(CHEM[c] for c in areas.split())
        areas = areas.replace(",", "; ")
        k = key(name)
        if k in people:
            people[k]["depts"].add(dept); people[k]["areas"] += "; " + areas; continue
        people[k] = dict(name=re.sub(r"\s*\(.*?\)", "", name).strip(), dept=dept, depts={dept}, title=TITLE.get(t, t), areas=areas, url=url)
out = [dict(name=p["name"], dept=p["dept"], campus="Ann Arbor", title=p["title"], all_depts="/".join(sorted(p["depts"])),
            areas=p["areas"], url=p["url"], source=p["url"], note="") for p in people.values()]
with open("data/processed/roster.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
