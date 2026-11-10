"""Turn the McGill department listings into data/processed/roster.csv.

mcgill.ca blocks automated fetching from the build environment (and asks browsers for a WAF token on
paged listings), so the listings were read in a browser on 2026-11-10 and saved as pipe-separated text:
  data/raw/roster/math.txt       name|title|research areas|profile slug   (Mathematics and Statistics, 3 pages)
  data/raw/roster/physics.txt    name|title|research field                (faculty table + "by field" page)
  data/raw/roster/chemistry.txt  name|title                               (Professors + Faculty Lecturers tables)
Sources:
  https://www.mcgill.ca/mathstat/people/faculty
  https://www.physics.mcgill.ca/people/faculty-a.html  (+ faculty-f.html for the research field)
  https://www.mcgill.ca/chemistry/faculty
Left out: emeriti, retired, adjunct professors and associate members. Siwick and Wiseman hold joint
appointments in Physics and Chemistry and are counted once; Vetta's joint appointment is in Computer Science.
"""
import csv, collections, re, unicodedata

SRC = {"Mathematics": "https://www.mcgill.ca/mathstat/people/faculty",
       "Physics": "https://www.physics.mcgill.ca/people/faculty-a.html",
       "Chemistry": "https://www.mcgill.ca/chemistry/faculty"}
JOINT = {"brad siwick": "bradley siwick"}  # same person, two spellings

def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    p = re.sub(r"[^a-z ]", " ", n).split(); k = f"{p[0]} {p[-1]}"
    return JOINT.get(k, k)

people = {}
def add(dept, name, title, areas="", url=""):
    k = key(name)
    if k in people:
        people[k]["depts"].add(dept)
        if areas and areas not in people[k]["areas"]: people[k]["areas"] = "; ".join(x for x in (people[k]["areas"], areas) if x)
        return
    people[k] = dict(name=name, dept=dept, depts={dept}, title=title, areas=areas, url=url or SRC[dept])

for line in open("data/raw/roster/math.txt", encoding="utf8"):
    if line.strip():
        n, t, a, s = line.rstrip("\n").split("|")
        add("Mathematics", n, t, a.replace(", ", "; "), f"https://www.mcgill.ca/mathstat/{s}")
for line in open("data/raw/roster/physics.txt", encoding="utf8"):
    if line.strip():
        n, t, a = line.rstrip("\n").split("|"); add("Physics", n, t, a)
for line in open("data/raw/roster/chemistry.txt", encoding="utf8"):
    if line.strip():
        n, t = line.rstrip("\n").split("|"); add("Chemistry", n, t)

out = []
for p in people.values():
    note = "joint appointment with Computer Science" if "Computer Science" in p["title"] else ""
    out.append(dict(name=p["name"], dept=p["dept"], campus="Montréal", title=p["title"],
                    all_depts="/".join(sorted(p["depts"])), areas=p["areas"], url=p["url"], source=SRC[p["dept"]], note=note))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
