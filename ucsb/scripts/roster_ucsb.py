"""Turn the UCSB department listings into data/processed/roster.csv.

ucsb.edu blocks automated fetching from the build environment, so the listings were read in a browser on
2026-11-10 and saved as pipe-separated text in data/raw/roster/roster_part*.txt:
    CODE|name|position|research areas (physics: the department's own research-area tags)
Codes: MA Mathematics, PH Physics, CH Chemistry & Biochemistry.
Sources (only the "Faculty" groups; lecturers, adjunct, affiliated faculty from other departments,
emeriti, researchers and students are left out; teaching professors / Lecturers SOE are kept):
  https://www.math.ucsb.edu/people   (group "Faculty")
  https://www.physics.ucsb.edu/people/faculty
  https://www.chem.ucsb.edu/people   (group "Faculty")
"""
import csv, glob, re, unicodedata, collections
DEPT = {"MA": "Mathematics", "PH": "Physics", "CH": "Chemistry & Biochemistry"}
URL = {"MA": "https://www.math.ucsb.edu/people", "PH": "https://www.physics.ucsb.edu/people/faculty",
       "CH": "https://www.chem.ucsb.edu/people"}
PROFILE = {"MA": "https://www.math.ucsb.edu/people/", "PH": "https://www.physics.ucsb.edu/people/", "CH": "https://www.chem.ucsb.edu/people/"}
PRIMARY = {"frank brown": "CH", "joan emma shea": "CH", "david morrison": "MA"}  # listed by two departments
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = n.split(); return " ".join(p) if len(p) == 3 and p[1] == "emma" else f"{p[0]} {p[-1]}"
def slug(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", n.replace(".", "")).strip("-")
people = {}
for fn in sorted(glob.glob("data/raw/roster/roster_part*.txt")):
    for line in open(fn, encoding="utf8"):
        if not line.strip(): continue
        code, name, title, areas = (line.rstrip("\n").split("|") + [""] * 4)[:4]
        k = key(name)
        if k in people:
            people[k]["codes"].add(code)
            if areas and code == "PH": people[k]["areas"] = (people[k]["areas"] + "; " + areas).strip("; ")
            continue
        people[k] = dict(name=name.strip(), code=code, codes={code}, title=title.strip(), areas=areas.strip(), slug=slug(name))
out = []
for k, p in people.items():
    c = PRIMARY.get(k, p["code"])
    out.append(dict(name=p["name"], dept=DEPT[c], campus="Santa Barbara", title=p["title"] or "Professor",
                    all_depts="/".join(sorted(DEPT[x] for x in p["codes"])), areas=p["areas"],
                    url=PROFILE[c] + p["slug"], source=URL[c], note=""))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
