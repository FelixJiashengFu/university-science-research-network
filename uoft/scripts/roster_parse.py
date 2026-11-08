"""Parse saved directory pages (UTM, UTSC) + physics JSON into data/processed/roster.csv"""
import json, csv, re
R = []
def add(name, dept, campus, title, source, note=""):
    name = re.sub(r",?\s*Ph\.?D\.?$", "", name).strip()
    R.append(dict(name=name, dept=dept, campus=campus, title=title, source=source, note=note))


# Mathematics department directory (all three campuses), read in a regular browser -> data/raw/math_directory.txt
CAMP = {"St. George": "St. George", "UTM": "UTM", "UTSC": "UTSC"}
sec = None
for l in open("data/raw/math_directory.txt"):
    l = l.strip()
    if not l or l.startswith("# "): continue
    if l.startswith("#"): sec = l[1:]; continue
    name, title = l.split("|", 1)
    campus = next((v for k, v in CAMP.items() if f"({k})" in sec), "St. George")
    add(name, "Mathematics", campus, title, "mathematics.utoronto.ca", note="cross-appointed" if "Cross" in sec else "")

# Chemistry department directory -> data/raw/chem_directory.txt
for l in open("data/raw/chem_directory.txt"):
    l = l.strip()
    if not l or l.startswith("#"): continue
    name, title, codes = l.split("|")
    c = codes.split(",")
    campus = "UTSC" if "UTSC" in c else "UTM" if "UTM" in c else "St. George"
    fields = [x for x in c if x not in ("SG", "UTM", "UTSC", "TEN", "TS", "X")]
    add(name, "Chemistry", campus, title, "chemistry.utoronto.ca", note="; ".join((["cross-appointed"] if "X" in c else []) + fields))

# UTM: "Name\nTitle/Position\n<title line>"
for fn, default in [("data/raw/utm_math.txt", "Mathematics"), ("data/raw/utm_cps.txt", None)]:
    L = [l.strip() for l in open(fn) if l.strip()]
    for i, l in enumerate(L):
        if l == "Title/Position":
            name, title = L[i-1], L[i+1]
            if len(name) <= 3 and i >= 2: name = L[i-2]  # initials avatar
            rest = " ".join(L[i+1:i+3])
            if default: dept = default
            elif re.search(r"Chemi", rest): dept = "Chemistry"
            elif re.search(r"Physic|Astro", rest): dept = "Physics"
            else: continue  # earth science etc.
            if re.search(r"Emerit", title): continue
            add(name, dept, "UTM", title, "utm.utoronto.ca")

# UTSC DPES: Name, Discipline, Title
L = [l.strip() for l in open("data/raw/utsc_dpes.txt") if l.strip()]
start = L.index("Apply") + 1
DISC = {"Chemistry", "Physics", "Environmental Science", "Environmental Studies"}
for i in range(start, len(L) - 1):
    if L[i] in DISC or L[i+1] not in DISC or L[i].startswith("Location") or "@" in L[i]: continue
    j = i + 1; ds = []
    while j < len(L) and L[j] in DISC: ds.append(L[j]); j += 1
    sci = [d for d in ds if d in ("Chemistry", "Physics")]
    if sci: add(L[i], sci[0], "UTSC", L[j], "utsc.utoronto.ca/physsci", note="also "+"/".join(ds[1:]) if len(ds) > 1 else "")

# Physics St. George
KEEP = ("Faculty", "Faculty, Teaching Stream", "UTM/UTSC Faculty, Graduate Department of Physics",
        "CITA Non-Budgetary Cross-Appointed Faculty", "UTSG Non-Budgetary Cross-Appointed Faculty",
        "UTM/UTSC Non-Budgetary Cross-Appointed Faculty", "Grant-Funded Contractually Limited Term Appointment")
for p in json.load(open("data/raw/roster_physics_utsg.json")):
    info = p["info"]; cat = next((x for x in info if x in KEEP), None)
    if not cat or any("Emerit" in x or "Retired" in x for x in info): continue
    title = info[0] if info else ""
    home = next((x for x in info[1:] if x.startswith("Department") or "Institute" in x), "Department of Physics")
    campus = "UTM" if "UTM)" in home else "UTSC" if ("UTSC" in home or "Scarborough" in home) else "St. George"
    dept = "Chemistry" if home == "Department of Chemistry" else "Physics"
    add(p["name"], dept, campus, title, "physics.utoronto.ca", note=(cat + "; " + home) if "Cross" in cat or "UTM/UTSC" in cat else "")

seen = {}; out = []
for r in R:
    k = re.sub(r"[^a-z]", "", re.sub(r"\(.*?\)|\b[A-Z]\.\s*", "", r["name"]).lower())
    if k in seen: continue
    seen[k] = 1; out.append(r)
with open("data/processed/roster.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
import collections; print(len(out), collections.Counter((r["campus"], r["dept"]) for r in out))
