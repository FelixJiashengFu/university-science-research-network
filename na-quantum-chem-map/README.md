# 北美量子化学与计算化学合作地图

美国和加拿大高校里做量子化学、计算化学理论与方法的教授（课题组负责人），按学校的真实经纬度铺在北美地图上。点是教授，线是两位教授共同发表的论文，点开教授可以看到他的主要论文（按被引排序）、近期论文和网内合作者。

| | |
|---|---|
| 教授 | 1,044（美国 950，加拿大 94） |
| 学校 | 277 |
| 合作线 | 4,244（权重 = 共同论文数） |
| 论文语料 | 165,638 篇（2000–2026） |

打开 `site/index.html`（需要本地 HTTP 服务：`python3 -m http.server` 后访问 `/na-quantum-chem-map/site/`），或通过仓库的 GitHub Pages。

## 方法

1. **论文语料**（`scripts/fetch_corpus.py`）：OpenAlex 中 2000 年以来、至少一位作者单位在美国或加拿大的论文，取以下五个查询的并集：
   - 主主题：Advanced Chemical Physics Studies、Spectroscopy and Quantum Chemical Studies、Advanced Physical and Chemical Molecular Interactions、Machine Learning in Materials Science
   - 概念：Ab initio quantum chemistry methods、Quantum chemistry、Relativistic quantum chemistry、TDDFT、Coupled cluster
   - 概念：Density functional theory
   - 概念：Molecular dynamics
   - 期刊：J. Chem. Theory Comput.、J. Chem. Phys.、J. Comput. Chem.、WIREs Comput. Mol. Sci.、Int. J. Quantum Chem.、Theor. Chem. Acc.
2. **识别教授**（`scripts/build_graph.py`）。没有一份全北美的院系名单可用，所以按发表记录推断课题组负责人：
   - 语料中至少 10 篇论文，2021 年后仍有发表；
   - 多作者论文里末位（通讯）作者比例 ≥ 30%；
   - 按近年加权的主要单位是美加高校（OpenAlex 类型 education；国家实验室与大学双挂时取大学；“University of California System”这类系统级机构跳过）；
   - 相关论文占其 2000 年以来全部论文 ≥ 25%，或占比 ≥ 8% 且有 ≥ 20 篇核心理论论文（理论期刊 / 量子化学概念 / 化学物理主题）；
   - 论文标题中带理论/方法词（calculation、simulation、ab initio、DFT、model、method…）的比例 ≥ 25%，用来去掉做实验的化学物理课题组。被去掉的 132 人列在 `data/processed/excluded_experimental.csv`，可人工捞回。
3. **位置**：教授落在所属学校的 OpenAlex 坐标；同校教授按向日葵排布围绕学校展开，放大地图后可分开。
4. **研究方向**：每篇论文按主主题 / 命中的查询归到 6 个方向之一，教授取论文最多的方向。
5. **合作线**：两位入选教授在语料中共同发表的论文数（作者数 > 60 的大合作论文不计）。
6. **主要论文**：该教授在语料中被引最多的 10 篇 + 最近 4 篇，链接到 DOI。

底图来自 Natural Earth 1:50m（公有领域），由 `scripts/build_basemap.py` 生成 `site/data/basemap.json`。

## 重跑

```bash
export OPENALEX_API_KEY=...          # 只放环境变量，不要提交
cd na-quantum-chem-map
python3 scripts/fetch_corpus.py      # 约 830 次列表请求，≈ $0.08
python3 scripts/build_graph.py       # 作者 / 机构单条查询免费，结果缓存在 data/raw/
# 底图：把 Natural Earth 三个 geojson 放进 data/raw/ne/ 后
python3 scripts/build_basemap.py
```

`data/raw/` 体积约 200 MB，不入库。

## 局限

- 名单是按论文推断的，不是院系官网名单：会混入少数资深研究员、博士后或研究科学家，也会漏掉论文少、刚入职或在 OpenAlex 里被拆成多个作者档案的教授。
- 分子动力学和 DFT 两个概念覆盖面很广，偏生物模拟和计算材料的课题组占比较高；“反应动力学与速率理论”方向只有在主主题明确时才会被归类，所以人数偏少。
- 机构以 OpenAlex 的“最后已知单位”为准，最近换校的教授可能仍显示在旧学校。
- 合作线只统计语料内的论文，即量子化学 / 计算化学方向的合作，不含其他领域的合写。
