"""Turn the department directory snapshots into data/processed/roster.csv.

Sources (read 2026-11-10 in a browser; the sites are Algolia-driven and refuse automated fetching from the cloud):
  Mathematics  https://math.utexas.edu/directory       (filter: Tenure-Track/Tenured Faculty)
  Physics      https://physics.utexas.edu/directory    (filter: Tenure-Track/Tenured Faculty)
  Chemistry    https://chemistry.utexas.edu/directory  (filter: Tenure-Track/Tenured Faculty)
Each snapshot line in data/raw/roster/*.psv is: name|rank|[position ...]|F:fields of interest (as listed).
Emeriti and retired faculty are kept in the snapshot but left out of the network (active faculty only, as for UdeM/Waterloo).
Many physics entries list no "fields of interest"; data/manual/areas_supplement.csv fills those in (and a few chemistry ones) from the
faculty's public research descriptions (marked area_source=manual).
"""
import csv, os
SRC = {"math": ("Mathematics", "https://math.utexas.edu/directory"),
       "physics": ("Physics", "https://physics.utexas.edu/directory"),
       "chemistry": ("Chemistry", "https://chemistry.utexas.edu/directory")}
manual = {r["name"]: r for r in csv.DictReader(open("data/manual/areas_supplement.csv", encoding="utf-8"))}
rows, skipped = [], []
for f, (dept, src) in SRC.items():
    for line in open(f"data/raw/roster/{f}.psv", encoding="utf-8"):
        p = [x.strip() for x in line.rstrip("\n").split("|") if x.strip()]
        if len(p) < 2: continue
        name, rank = p[0], p[1]
        if "Emerit" in rank or "Retired" in rank:
            skipped.append(name); continue
        areas = next((x[2:] for x in p if x.startswith("F:")), "")
        positions = "; ".join(x for x in p[2:] if not x.startswith("F:"))
        area_src = "directory" if areas else ""
        if name in manual and manual[name]["dept"] == dept:
            areas = "; ".join(a for a in [areas, manual[name]["areas"]] if a); area_src = "manual" if not area_src else "directory+manual"
        rows.append(dict(name=name, dept=dept, campus="Austin", title=rank, all_depts=dept, areas=areas.replace(", ", "; "),
                         area_source=area_src, positions=positions, url=src, source=src, note=""))
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/roster.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows;", len(skipped), "emeriti/retired skipped")
