"""Write schools/<slug>/site/index.html from the Stanford page template, copy vendor libs, update schools/stats.json.
usage: python3 make_site.py <slug> [<slug> ...]"""
import json, os, shutil, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../..")
CFG = json.load(open(f"{HERE}/schools.json"))
T = open(f"{ROOT}/stanford/site/index.html", encoding="utf-8").read()
statf = f"{HERE}/../stats.json"
stats = json.load(open(statf)) if os.path.exists(statf) else {}
for slug in sys.argv[1:]:
    c = CFG[slug]; d = f"{HERE}/../{slug}/site"
    idx = json.load(open(f"{d}/data/index.json")); profs = json.load(open(f"{d}/data/profs.json"))
    nd = {k: sum(1 for p in profs.values() if p["dept"] == k) for k in ("Mathematics", "Physics", "Chemistry")}
    s = T
    R = [("<title>Stanford 数理化研究网络</title>", f"<title>{c['zh']} 数理化研究网络</title>"),
         ("<h1>斯坦福大学 · 数学 / 物理 / 应用物理 / 化学 研究网络</h1>", f"<h1>{c['zh']} · 数学 / 物理 / 化学 研究网络</h1>"),
         ("<div class=\"sub\">数学系 · 物理系 · 应用物理系 · 化学系　数据：院系官网 + OpenAlex + 公开创业资料</div>",
          f"<div class=\"sub\">{c['en']} · 数学 {nd['Mathematics']} · 物理 {nd['Physics']} · 化学 {nd['Chemistry']} 位（按论文推断）　数据：OpenAlex</div>"),
         ('const DEPT = {Mathematics:["数学","#3b82f6"], Physics:["物理","#ef4444"], "Applied Physics":["应用物理","#a855f7"], Chemistry:["化学","#10b981"]};',
          'const DEPT = {Mathematics:["数学","#3b82f6"], Physics:["物理","#ef4444"], Chemistry:["化学","#10b981"]};'),
         ("数据来源：斯坦福各院系公开教师名单、OpenAlex（CC0）、维基百科等公开创业资料。作者匹配为自动完成，可能存在误差，详见仓库 README。",
          f"数据来源：OpenAlex（CC0）。教师名单按 2019–2025 年本校署名论文推断（论文数、末位作者比例、h 指数、最近机构），会混入资深研究员、漏掉论文少的教授；方法见仓库 schools/README.md。"),
         ('<script src="../assets/nav.js" data-root=".." defer></script>', '<script src="../../assets/nav.js" data-root="../.." defer></script>'),
         ("院系主页", "主页")]
    for a, b in R:
        assert a in s, a; s = s.replace(a, b)
    open(f"{d}/index.html", "w", encoding="utf-8").write(s)
    shutil.copytree(f"{ROOT}/stanford/site/vendor", f"{d}/vendor", dirs_exist_ok=True)
    main = next(n for n in idx if n["id"] == "main")
    stats[slug] = [len(profs), sum(p["n_works"] for p in profs.values()), len(idx), main["nodes"]]
    print(slug, stats[slug])
json.dump(stats, open(statf, "w"), indent=1)
