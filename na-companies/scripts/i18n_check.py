"""List visible Chinese strings in site/index.html that the atlas English dictionary (../i18n/en.json, plus this build's
data/processed/i18n_en_additions.json) cannot translate. Matching: exact text, then digits replaced by {0}, {1}, ...
Usage: python3 scripts/i18n_check.py [--merge]   (--merge writes the additions into ../i18n/en.json)"""
import json, os, re, sys
from html.parser import HTMLParser
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CJK = re.compile(r"[㐀-鿿]")
NUM = re.compile(r"\d[\d,.]*\d|\d")

def templ(s):
    nums = []
    def f(m): nums.append(m.group(0)); return "{%d}" % (len(nums) - 1)
    return NUM.sub(f, s), nums

class P(HTMLParser):
    def __init__(self): super().__init__(); self.skip = 0; self.out = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1
        for k, v in attrs:
            if k in ("placeholder", "aria-label", "title", "alt") and v and CJK.search(v): self.out.append(v.strip())
    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip -= 1
    def handle_data(self, d):
        if not self.skip and CJK.search(d): self.out.append(re.sub(r"\s+", " ", d).strip())

def main():
    en = json.load(open(os.path.join(R, "..", "i18n", "en.json"), encoding="utf-8"))
    addp = os.path.join(R, "data", "processed", "i18n_en_additions.json")
    add = json.load(open(addp, encoding="utf-8")) if os.path.exists(addp) else {}
    full = {}
    for k, v in add.items():
        full[k] = v
        tk, nk = templ(k); tv, nv = templ(v)
        if nk and nk == nv: full[tk] = tv
    D = {**en, **full}
    p = P(); p.feed(open(os.path.join(R, "site", "index.html"), encoding="utf-8").read())
    def tr(x):
        x = x.strip()
        if x in D: return D[x]
        t, n = templ(x)
        if t in D:
            out = D[t]
            for i, v in enumerate(n): out = out.replace("{%d}" % i, v)
            return out
        if not CJK.search(x): return x
        m = re.fullmatch(r"(.+)（(FY\d{4})）", x)
        if m and tr(m.group(1)): return f"{tr(m.group(1))} ({m.group(2)})"
        if " · " in x:
            parts = [tr(y) for y in x.split(" · ")]
            if all(parts): return " · ".join(parts)
        return None
    STD = {"图 {0}": "Fig. {0}", "{0} 篇": "{0} papers", "{0} 家": "{0} companies"}
    for k, v in STD.items(): D.setdefault(k, v)
    miss = []
    for s in dict.fromkeys(p.out):
        if s in D: continue
        v = tr(s)
        if v is not None: full[s] = v; continue  # stored concretely so no host templating is needed
        miss.append(s)
    print(len(set(p.out)), "strings,", len(miss), "missing")
    for s in miss: print(repr(s))
    if "--merge" in sys.argv:
        new = {k: v for k, v in full.items() if en.get(k) != v}
        en.update(full)
        json.dump(en, open(os.path.join(R, "..", "i18n", "en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        print("merged", len(new), "entries")

if __name__ == "__main__": main()
