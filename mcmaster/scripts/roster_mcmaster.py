"""Turn the McMaster department listings into data/processed/roster.csv.

mcmaster.ca refuses automated fetching from the build environment, so the three faculty pages were read in a
browser on 2026-11-10 and saved as pipe-separated text in data/raw/roster/roster.txt:
    CODE|name|position|research areas (as listed on the department page; blank when the page lists none)
Codes: MA Mathematics & Statistics, PH Physics & Astronomy, CH Chemistry & Chemical Biology.
Sources:
  https://math.mcmaster.ca/people/faculty/
  https://physics.mcmaster.ca/people/current-faculty/
  https://chemistry.mcmaster.ca/people/full-time-faculty/
Statisticians and actuaries of the Department of Mathematics & Statistics are left out (STATS below), like the
statistics departments at UofT and Waterloo; probability and financial mathematics stay in.
"""
import csv, re, unicodedata, collections
DEPT = {"MA": "Mathematics", "PH": "Physics & Astronomy", "CH": "Chemistry"}
URL = {"MA": "https://math.mcmaster.ca/people/faculty/",
       "PH": "https://physics.mcmaster.ca/people/current-faculty/",
       "CH": "https://chemistry.mcmaster.ca/people/full-time-faculty/"}
STATS = {"Anas Abdallah", "N. Balakrishnan", "Angelo Canty", "Aaron Childs", "Katherine Davies",
         "Pratheepa Jeganathan", "Paul McNicholas"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = n.split(); return f"{p[0]} {p[-1]}"
people = {}
for line in open("data/raw/roster/roster.txt", encoding="utf8"):
    if not line.strip(): continue
    code, name, title, areas = (line.rstrip("\n").split("|") + [""] * 4)[:4]
    if name in STATS: continue
    k = key(name)
    if k in people:
        people[k]["codes"].add(code); continue
    people[k] = dict(name=name.strip(), code=code, codes={code}, title=title.strip(), areas=areas.strip())
out = []
for p in people.values():
    note = "teaching stream" if re.search(r"Teaching|Lecturer", p["title"]) else ""
    out.append(dict(name=p["name"], dept=DEPT[p["code"]], campus="Hamilton", title=p["title"] or "Professor",
                    all_depts="/".join(sorted(DEPT[c] for c in p["codes"])), areas=p["areas"], url=URL[p["code"]],
                    source=URL[p["code"]], note=note))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
