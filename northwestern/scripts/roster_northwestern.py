"""Turn the Northwestern department listings into data/processed/roster.csv.

The department sites refuse automated fetching from the build environment (proxy / robots.txt), so the
listings were read in a browser on 2026-11-10 and saved as pipe-separated text in data/raw/roster/*.txt:
    CODE|name|title[|research area|email id]
Codes: MA Mathematics, AM Engineering Sciences & Applied Mathematics (ESAM), PH Physics & Astronomy,
       CH Chemistry; AMx = faculty of another in-scope department with a courtesy appointment in ESAM.
Sources:
  https://math.northwestern.edu/people/faculty/             (professorial + instructional faculty; Boas
                                                             assistant professors / lecturers are postdoc-type
                                                             or teaching-only posts and are left out)
  https://www.mccormick.northwestern.edu/applied-math/people/faculty/   (ESAM; courtesy faculty from outside
                                                             math/physics/chemistry and adjuncts left out)
  https://physics.northwestern.edu/people/faculty/core-faculty/ and /instructional-faculty/
  https://chemistry.northwestern.edu/people/faculty/        (core faculty, incl. joint/courtesy appointments)
The math page text gives each entry's title, field and e-mail but its name headings did not come through,
so names were filled in from the e-mail ids; names starting with "?" are resolved by surname against
OpenAlex Northwestern authors in openalex_fetch.py.
"""
import csv, glob, re, unicodedata, collections
DEPT = {"MA": "Mathematics", "AM": "Applied Mathematics (ESAM)", "PH": "Physics & Astronomy", "CH": "Chemistry"}
URL = {"MA": "https://math.northwestern.edu/people/faculty/",
       "AM": "https://www.mccormick.northwestern.edu/applied-math/people/faculty/",
       "PH": "https://physics.northwestern.edu/people/faculty/core-faculty/",
       "CH": "https://chemistry.northwestern.edu/people/faculty/"}
def key(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\(.*?\)", " ", n); n = re.sub(r"\b[a-z]\.\s*", "", n).replace("-", " ")
    p = n.split(); return f"{p[0]} {p[-1]}"
people, cross = {}, collections.defaultdict(set)
for fn in sorted(glob.glob("data/raw/roster/*.txt")):
    for line in open(fn, encoding="utf8"):
        if not line.strip(): continue
        code, name, title, areas, email = (line.rstrip("\n").split("|") + [""] * 5)[:5]
        if code.endswith("x"): cross[key(name)].add(code[:-1]); continue
        k = key(name)
        if k in people: people[k]["codes"].add(code); continue
        people[k] = dict(name=name.strip(), code=code, codes={code}, title=title.strip(), areas=areas.strip().replace(", ", "; "), email=email)
for k, cs in cross.items():
    if k in people: people[k]["codes"] |= cs
    else: print("cross-listed but not on a home roster:", k)
out = []
for p in people.values():
    note = []
    if p["name"] == "Pieter van Dokkum": note.append("arriving 2027-01")
    if "Joint Professor" in p["title"] or "Courtesy" in p["title"]: note.append("joint/courtesy appointment in Chemistry")
    if p["name"].startswith("?"): note.append("name resolved from e-mail id " + p["email"])
    out.append(dict(name=p["name"], dept=DEPT[p["code"]], campus="Evanston", title=p["title"] or "Professor",
                    all_depts="/".join(sorted(DEPT[c] for c in p["codes"])), areas=p["areas"], url=URL[p["code"]],
                    source=URL[p["code"]], note="; ".join(note)))
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("roster", len(out), collections.Counter(o["dept"] for o in out), "joint", sum("/" in o["all_depts"] for o in out))
