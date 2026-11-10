# 得克萨斯大学奥斯汀分校（UT Austin）数学 · 物理 · 化学 研究网络

把 UT Austin 自然科学学院数学系、物理系、化学系在职教授的研究领域、论文、合作关系、校外研究机构与产业合作编织成一张主网，并拆出专题子网。姊妹项目：[UofT](../uoft/)、[Stanford](../stanford/)、[UdeM](../udem/)（同一套方法）。

**在线浏览**：GitHub Pages 发布在 `/utaustin/`。本地预览：

```bash
cd site && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 规模

- 名单：133 位在职教授（数学 45、物理 53、化学 35；Chelikowsky 物理/化学双聘，合并为一人）
- OpenAlex 匹配 131/133，约 2.4 万篇论文（不含 OpenAlex 中的数据集条目，如 PDB 结构）
- 共 23 张网络，清单（节点数、边数）见 `site/data/index.json`：主网（教授 · 主题 · 学科层级 · 论文 · 企业 · 全部关系）、合作网、研究相似网、交叉学科网、三个系子网、12 张方向子网（数学 3、物理 5、化学 4）、**Oden 计算工程与科学研究所子网**、研究主题地图、研究机构网、**创新创业网**。

## 名单来源

| 系 | 来源 | 读取日期 |
|---|---|---|
| 数学 | https://math.utexas.edu/directory（Tenure-Track/Tenured Faculty） | 2026-11-10 |
| 物理 | https://physics.utexas.edu/directory（同上） | 2026-11-10 |
| 化学 | https://chemistry.utexas.edu/directory（同上） | 2026-11-10 |

目录由 Algolia 在浏览器端渲染，云端无法直接抓取，在浏览器里读取后存为 `data/raw/roster/*.psv`（姓名 | 职级 | 职务 | F:研究方向）。快照里含 16 位荣休/退休教授，网络只收在职教授。Professional-track（教学岗）、博士后不收。

研究方向取目录里的 "Fields of Interest"。物理系多数教授目录里没有填写，`data/manual/areas_supplement.csv` 按教授公开的研究介绍补充（另含化学系 5 人），只用于方向子网分组。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数，见 `data/processed/industry_links.csv`。创新创业网保留 ≥2 篇，主网保留 ≥3 篇。
- **教授创办 / 实验室衍生的公司**：`data/manual/startups.csv`，每条附来源与原文摘录：Jonathan Sessler 联合创办 Pharmacyclics、Anionics；TAU Systems 从 UT Austin 分拆（Hegelich 团队研制原型，他任 CEO）；Focused Energy 由 Markus Roth 与 Todd Ditmire 发起（Ditmire 任 CTO）。只收来源写明的，**名单并不完整**，欢迎按同样格式补充。
- 专利暂未纳入。

## 数据流程与重跑

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # 切勿提交到仓库
python3 scripts/roster_utaustin.py # data/raw/roster/*.psv + data/manual/areas_supplement.csv → data/processed/roster.csv
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py     # → site/data/*.json, data/processed/*.csv（约 10 分钟）
```

为节省 OpenAlex 额度，候选作者来自**一次批量列表查询**（所有曾在 UT Austin 署名、>10 篇、含数理化主题的作者，约 90 页 × $0.0001），缓存在 `data/raw/openalex/pool.jsonl`（47 MB，未提交）；只有池里找不到的才逐个检索。

## 方法与局限

- **作者匹配**：按姓名、研究领域、当前机构打分。6 人在 `scripts/openalex_fetch.py` 的 OVERRIDE 中手工指定（自动结果错配或缺失：James A. M. Álvarez、Thomas Chen、Nick Hunter-Jones、Jason Shear、Peter Mueller、Dmitry Eremin）。Oscar Gonzalez、Griffin Wang 在 OpenAlex 里找不到可靠档案，暂未纳入网络。
- **大型合作**：OpenAlex 每篇论文最多返回 100 位作者，因此作者数 ≥100 的论文（ATLAS、LIGO、ALICE 等）一律记为"大型合作"浅色边，不计入合写强度，也不计入企业合作和校外研究机构合作（否则 ATLAS 一篇论文就会带进上百个机构）。Andeen、Onyisi、Christina Markert、Deepa Thomas、Hsin-Yu Chen 的论文多为此类。
- **研究主题**：OpenAlex Topic 体系，每篇论文取 primary topic；研究相似 = 主题分布的 TF-IDF 余弦相似度。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
