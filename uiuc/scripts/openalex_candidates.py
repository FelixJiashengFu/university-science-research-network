"""Download every OpenAlex author whose last known institution is UIUC and who has topics in
Mathematics (26), Physics & Astronomy (31) or Chemistry (16). List requests only (cheap), so roster
names can be matched locally instead of one paid search per professor.
Output: data/raw/openalex/candidates.json
"""
import json, os, sys, time, urllib.parse, urllib.request
KEY = os.environ["OPENALEX_API_KEY"]; INST = "I157725225"
def get(params):
    url = "https://api.openalex.org/authors?" + urllib.parse.urlencode(params)
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "User-Agent": "uiuc-science-research-network/0.1"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print("retry", e, file=sys.stderr); time.sleep(2 ** a)
    raise SystemExit("failed " + url)
out = {}
for f in ("26", "31", "16"):
    cursor = "*"
    while cursor:
        r = get({"filter": f"last_known_institutions.id:{INST},topics.field.id:fields/{f},works_count:>3", "per_page": 200, "cursor": cursor,
                 "select": "id,display_name,display_name_alternatives,works_count,cited_by_count,summary_stats,topics,last_known_institutions,orcid"})
        for a in r["results"]: out[a["id"].split("/")[-1]] = a
        cursor = r["meta"].get("next_cursor")
        if not r["results"]: break
    print(f, len(out))
json.dump(out, open("data/raw/openalex/candidates.json", "w"))
