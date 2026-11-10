"""Turn the UIUC department listings into data/processed/roster.csv.

Department pages were read on 2026-11-10 and saved as pipe-separated text in data/raw/roster/:
  math.txt       Name|Title                      https://math.illinois.edu/directory/faculty (Faculty tab)
  physics.txt    Name|Title|research areas       https://physics.illinois.edu/people/directory/faculty
                 (Department Faculty > Faculty, plus the research professors listed on the same page)
  chemistry.txt  Name|Title                      https://chemistry.illinois.edu/directory/faculty-by-type
                 (Faculty, Joint Appointments, teaching professors, Research Faculty)
  chem_areas.txt Area|names                      https://chemistry.illinois.edu/research/<area>/<area>-faculty
Not included: emeriti, adjunct, lecturers/instructors, postdocs, and faculty affiliates from other departments.
"""
import csv, re, unicodedata, collections
URL = {"Mathematics": "https://math.illinois.edu/directory/faculty",
       "Physics": "https://physics.illinois.edu/people/directory/faculty",
       "Chemistry": "https://chemistry.illinois.edu/directory/faculty-by-type"}
FILES = [("Mathematics", "math.txt"), ("Physics", "physics.txt"), ("Chemistry", "chemistry.txt")]
# people listed by two in-scope departments: home department
HOME = {"nancy makri": "Chemistry", "zan schulten": "Chemistry", "philip phillips": "Physics"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\(.*?\)", " ", n); n = re.sub(r"\b[a-z]\.?\s", " ", n + " ").replace("-", " ")
    p = n.split(); return f"{p[0]} {p[-1]}".replace("zaida", "zan")
areas = collections.defaultdict(list)
for line in open("data/raw/roster/chem_areas.txt", encoding="utf8"):
    a, names = line.rstrip("\n").split("|")
    for n in names.split(";"): areas[key(n.strip())].append(a if a == "Chemical Biology" else a + " Chemistry")
people = {}
for dept, fn in FILES:
    for line in open("data/raw/roster/" + fn, encoding="utf8"):
        if not line.strip(): continue
        name, title, ar = (line.rstrip("\n").split("|") + [""] * 3)[:3]
        k = key(name)
        if dept == "Chemistry" and k in areas: ar = "; ".join(areas[k])
        if k in people:
            p = people[k]; p["depts"].add(dept)
            if ar: p["areas"] = "; ".join(x for x in dict.fromkeys((p["areas"] + "; " + ar).split("; ")) if x)
            if HOME.get(k) == dept: p.update(dept=dept, title=title)
            continue
        people[k] = dict(name=re.sub(r"\s+", " ", name.replace("Zaida (Zan)", "Zan")).strip(), dept=dept, depts={dept}, title=title.strip(), areas=ar.strip())
out = []
for p in people.values():
    rt = "research professor" if "Research" in p["title"] else ""
    out.append(dict(name=p["name"], dept=p["dept"], campus="Urbana-Champaign", title=p["title"], all_depts="/".join(sorted(p["depts"])),
                    areas=p["areas"], url=URL[p["dept"]], source=URL[p["dept"]], note=rt))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
