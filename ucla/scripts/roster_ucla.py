"""Turn the UCLA department listings into data/processed/roster.csv.

The listings were read on 2026-11-10 and saved as text in data/raw/roster/:
  math.txt     MA|name|title|            https://www.math.ucla.edu/people/ladder (ladder faculty, emeriti left out)
  physics.txt  PA|name|title|group|site  https://www.pa.ucla.edu/faculty.html (emeriti left out)
  chem_raw.txt Last, First|specialties|slug  https://www.chemistry.ucla.edu/directory/department/faculty (pages 1-5)
Joint appointments whose home is outside the three departments (EE, CS, Statistics, EPSS) are left out of math;
Hong Zhou (Microbiology, Immunology & Molecular Genetics) is left out of chemistry.
"""
import csv, collections
DEPT = {"MA": "Mathematics", "PA": "Physics & Astronomy", "CH": "Chemistry & Biochemistry"}
URL = {"MA": "https://www.math.ucla.edu/people/ladder", "PA": "https://www.pa.ucla.edu/faculty.html",
       "CH": "https://www.chemistry.ucla.edu/directory/department/faculty"}
out = []
for code, fn in (("MA", "math.txt"), ("PA", "physics.txt")):
    for line in open(f"data/raw/roster/{fn}", encoding="utf8"):
        if not line.strip(): continue
        c, name, title, areas, url = (line.rstrip("\n").split("|") + [""] * 5)[:5]
        out.append(dict(name=name, dept=DEPT[code], campus="Los Angeles", title=title, all_depts=DEPT[code], areas=areas,
                        url=url or URL[code], source=URL[code], note=""))
for line in open("data/raw/roster/chem_raw.txt", encoding="utf8"):
    if not line.strip(): continue
    nm, areas, slug = line.rstrip("\n").split("|")
    last, first = [x.strip() for x in nm.split(",", 1)]
    first = first.replace("(Cindy)", "").strip()
    name = f"{first} {last}"
    instr = "Instructional" in areas
    out.append(dict(name=name, dept=DEPT["CH"], campus="Los Angeles", title="Teaching faculty" if instr else "Faculty",
                    all_depts=DEPT["CH"], areas=areas, url=f"https://www.chemistry.ucla.edu/directory/{slug}/",
                    source=URL["CH"], note="title not shown in the directory"))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out))
