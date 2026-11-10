"""Turn the Waterloo department listings into data/processed/roster.csv.

uwaterloo.ca blocks automated fetching from the build environment, so the listings were read in a
browser on 2026-11-09 and saved as pipe-separated text in data/raw/roster/roster_part*.txt:
    CODE|name|position|research areas
Codes: PM Pure Mathematics, AM Applied Mathematics, CO Combinatorics & Optimization,
       PH Physics & Astronomy, CH Chemistry; AMx / PHx = that department's cross-appointed list.
Sources:
  https://uwaterloo.ca/pure-mathematics/department-members/faculty-members
  https://uwaterloo.ca/applied-mathematics/department-members/faculty-members (+ /cross-appointed)
  https://uwaterloo.ca/combinatorics-and-optimization/our-people/faculty
  https://uwaterloo.ca/physics-astronomy/contacts (group: Professors, Cross-appointed faculty)
  https://uwaterloo.ca/chemistry/our-people/professors
"""
import csv, glob, re, unicodedata, collections
DEPT = {"PM": "Pure Mathematics", "AM": "Applied Mathematics", "CO": "Combinatorics & Optimization",
        "PH": "Physics & Astronomy", "CH": "Chemistry"}
URL = {"PM": "https://uwaterloo.ca/pure-mathematics/department-members/faculty-members",
       "AM": "https://uwaterloo.ca/applied-mathematics/department-members/faculty-members",
       "CO": "https://uwaterloo.ca/combinatorics-and-optimization/our-people/faculty",
       "PH": "https://uwaterloo.ca/physics-astronomy/contacts",
       "CH": "https://uwaterloo.ca/chemistry/our-people/professors"}
# cross-appointment text -> in-scope department code
XMAP = [("Pure Math", "PM"), ("Applied Math", "AM"), ("Combinatorics", "CO"), ("Physics", "PH"), ("Chemistry", "CH")]
ALIAS = {"rowan yeats": "karen yeats", "german sciaini": "german sciaini"}  # same person listed under two names
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = n.split(); k = f"{p[0]} {p[-1]}"
    return ALIAS.get(k, k)
people, cross = {}, collections.defaultdict(set)
for fn in sorted(glob.glob("data/raw/roster/roster_part*.txt")):
    for line in open(fn, encoding="utf8"):
        if not line.strip(): continue
        code, name, title, areas = (line.rstrip("\n").split("|") + [""] * 4)[:4]
        if code.endswith("x"):  # cross-appointed list of department code[:-1]; areas/title name the home dept
            home = [c for t, c in XMAP if t.lower() in (areas + " " + title).lower()]
            if home: cross[key(name)] |= {code[:-1], home[0]}
            continue
        k = key(name)
        if k in people:
            people[k]["codes"].add(code)
            if areas and areas not in people[k]["areas"]: people[k]["areas"] += "; " + areas
            continue
        people[k] = dict(name=name.strip(), code=code, codes={code}, title=title.strip(), areas=areas.strip().replace(", ", "; "))
for k, cs in cross.items():
    if k in people: people[k]["codes"] |= cs
out = []
for p in people.values():
    note = "arriving 2027" if p["name"] == "Pok Man Tam" else ""
    out.append(dict(name=p["name"], dept=DEPT[p["code"]], campus="Waterloo", title=p["title"] or "Professor",
                    all_depts="/".join(sorted(DEPT[c] for c in p["codes"])), areas=p["areas"], url=URL[p["code"]],
                    source=URL[p["code"]], note=note))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
