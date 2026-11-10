"""Turn the University of Alberta department listings into data/processed/roster.csv.

ualberta.ca refuses the build environment's proxy, so the listings were read on 2026-11-10 through a
web reader and saved as pipe-separated text in data/raw/roster/roster_*.txt:
    CODE|name|title|research areas|note
Codes: MA Mathematical & Statistical Sciences (math faculty only), PH Physics, CH Chemistry.
Sources:
  https://www.ualberta.ca/en/mathematical-and-statistical-sciences/people/academic-staff.html
  https://www.ualberta.ca/en/mathematical-and-statistical-sciences/research/research-areas.html
  https://www.ualberta.ca/en/physics/people/faculty.html
  https://www.ualberta.ca/en/chemistry/people/faculty.html
Scope: professors only (lecturers, faculty service officers and staff left out). In Mathematical &
Statistical Sciences, faculty whose listed research is statistics only are left out, like the UofT build.
"""
import csv, glob, collections
DEPT = {"MA": "Mathematics", "PH": "Physics", "CH": "Chemistry"}
URL = {"MA": "https://www.ualberta.ca/en/mathematical-and-statistical-sciences/people/academic-staff.html",
       "PH": "https://www.ualberta.ca/en/physics/people/faculty.html",
       "CH": "https://www.ualberta.ca/en/chemistry/people/faculty.html"}
out = []
for fn in sorted(glob.glob("data/raw/roster/roster_*.txt")):
    for line in open(fn, encoding="utf8"):
        if not line.strip(): continue
        code, name, title, areas, note = (line.rstrip("\n").split("|") + [""] * 5)[:5]
        out.append(dict(name=name.strip(), dept=DEPT[code], campus="Edmonton", title=title.strip() or "Professor",
                        all_depts=DEPT[code], areas=areas.strip(), url=URL[code], source=URL[code], note=note.strip()))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out))
