"""Turn the department directory snapshots into data/processed/roster.csv.

Sources (read 2026-11-09 in a browser, the sites refuse automated fetching):
  Mathématiques et statistique  https://dms.umontreal.ca/fr/repertoire-departement/professeurs
  Chimie                        https://chimie.umontreal.ca/fr/repertoire-departement/professeurs
Each snapshot line in data/raw/roster/*.psv is: name|rank|expertises (; separated)|profile slug
Physics: physique.umontreal.ca could not be read (certificate error in the browser, robots.txt refuses fetchers),
so data/manual/physics_faculty.csv lists physics professors compiled from public information and checked against
OpenAlex (current UdeM affiliation, active 2023+). It is NOT checked against the department directory.
"""
import csv, os
SRC = {"mathematiques": ("Mathematics", "https://dms.umontreal.ca/fr/repertoire-departement/professeurs"),
       "chimie": ("Chemistry", "https://chimie.umontreal.ca/fr/repertoire-departement/professeurs")}
rows = []
for f, (dept, src) in SRC.items():
    for line in open(f"data/raw/roster/{f}.psv", encoding="utf-8"):
        p = line.rstrip("\n").split("|")
        if len(p) < 3: continue
        name, rank, areas = p[0], p[1], p[2]
        slug = p[3] if len(p) > 3 else ""
        url = f"{src}/portrait/{slug}" if slug else src
        rows.append(dict(name=name, dept=dept, campus="Montréal", title=f"Professeur·e {rank}", all_depts=dept,
                         areas=areas, url=url, source=src, note=""))
for r in csv.DictReader(open("data/manual/physics_faculty.csv", encoding="utf-8")):
    rows.append(dict(name=r["name"], dept="Physics", campus="Montréal", title="Professeur·e", all_depts="Physics", areas=r["areas"],
                     url="https://physique.umontreal.ca/repertoire-departement/professeurs/", source="整理自公开资料（未经院系名单核对）",
                     note="物理系名单未经院系官网核对"))
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/roster.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
