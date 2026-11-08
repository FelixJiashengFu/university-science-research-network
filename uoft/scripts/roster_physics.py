"""Scrape UofT Physics (St. George) faculty directory -> data/raw/roster_physics_utsg.json"""
import re, json, html, subprocess
rows = []
for page in range(1, 6):
    url = f"https://www.physics.utoronto.ca/members/?m_type=faculty&page={page}"
    h = subprocess.run(["curl", "-sL", "-m", "40", url], capture_output=True, text=True).stdout
    items = h.split('<li class="hover:bg-slate-50">')[1:]
    if not items: break
    for it in items:
        m = re.search(r'href="(/members/[^"]+)">\s*(.*?)\s*</a>', it, re.S)
        if not m: continue
        divs = [html.unescape(re.sub(r'<[^>]+>', '', d)).strip() for d in re.findall(r'<div class="[^"]*(?:text-secondary|hidden md:block)[^"]*">(.*?)</div>', it, re.S)]
        email = re.search(r'mailto:([^"]+)', it)
        rows.append({"name": html.unescape(m.group(2)).strip(), "url": "https://www.physics.utoronto.ca" + m.group(1),
                     "info": [d for d in divs if d], "email": email.group(1) if email else None})
    print(page, len(rows))
json.dump(rows, open("data/raw/roster_physics_utsg.json", "w"), indent=1, ensure_ascii=False)
