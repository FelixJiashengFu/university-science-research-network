"""Turn the Penn department listings into data/processed/roster.csv.

upenn.edu blocks automated fetching from the build environment (robots.txt / proxy), so the listings were read
in a browser on 2026-11-10 and saved as pipe-separated text in data/raw/roster/*.txt:
    CODE|name|position|research areas
Codes: MA Mathematics, PH Physics & Astronomy, CH Chemistry; PHx = physics secondary appointment of a
mathematics professor (merged into that person, not a second node).
Sources:
  https://www.math.upenn.edu/people/standing-faculty   (emeriti left out)
  https://www.physics.upenn.edu/people/standing-faculty (adjuncts and faculty whose primary appointment is
      outside the three departments — Bioengineering, ESE, Physiology, Radiology — left out)
  https://www.chem.upenn.edu/people/faculty            (lecturers and adjuncts left out; areas = the page's "Focus Area")
Physics lists no research areas; the areas in physics_standing.txt are the department's research groups
(astro/cosmology, HEP theory/experiment, condensed matter theory/experiment, soft matter, biological physics)
assigned from each person's public research description and checked against OpenAlex.
"""
import csv, glob, re, unicodedata, collections
DEPT = {"MA": "Mathematics", "PH": "Physics & Astronomy", "CH": "Chemistry"}
URL = {"MA": "https://www.math.upenn.edu/people/standing-faculty",
       "PH": "https://www.physics.upenn.edu/people/standing-faculty",
       "CH": "https://www.chem.upenn.edu/people/faculty"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = n.split(); return f"{p[0]} {p[-1]}"
people, cross = {}, collections.defaultdict(set)
for fn in sorted(glob.glob("data/raw/roster/*.txt")):
    for line in open(fn, encoding="utf8"):
        if not line.strip(): continue
        code, name, title, areas = (line.rstrip("\n").split("|") + [""] * 4)[:4]
        if code.endswith("x"): cross[key(name)].add(code[:-1]); continue
        people[key(name)] = dict(name=name.strip(), code=code, codes={code}, title=title.strip(), areas=areas.strip().replace(", ", "; "))
for k, cs in cross.items():
    if k in people: people[k]["codes"] |= cs
out = [dict(name=p["name"], dept=DEPT[p["code"]], campus="Philadelphia", title=p["title"] or "Professor",
            all_depts="/".join(sorted(DEPT[c] for c in p["codes"])), areas=p["areas"], url=URL[p["code"]],
            source=URL[p["code"]], note="") for p in people.values()]
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
