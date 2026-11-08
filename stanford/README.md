# Stanford 数学 · 物理 · 应用物理 · 化学 研究网络

把斯坦福大学数学系、物理系、应用物理系、化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 17 张专题子网。姊妹项目：[UofT 版本](../uoft/)（同一套方法）。

**在线浏览**：Settings → Pages 选择 GitHub Actions 或 `main` 分支部署 `site/`。本地预览：

```bash
cd site && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 规模

- 名单：137 位在职教授（数学 41、物理 51、应用物理 20、化学 25；跨系聘任按一人计，页面上显示"跨聘"）
- OpenAlex 匹配 136 个作者档案，约 3.7 万篇论文

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 3844 | 12312 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 113 | 370 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| **研究相似网** | 132 | 420 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 337 | 1440 | 只保留跨系（数学×物理×应用物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **数学系子网** | 128 | 448 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **物理系子网** | 148 | 800 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| **应用物理系子网** | 120 | 359 | 应用物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| **化学系子网** | 159 | 516 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **方向子网：理论物理：高能 · 量子引力 · 量子信息** | 62 | 249 | 院系官网标注为「Stanford Leinweber Institute for Theoretical Physics / Theoretical Astrophysics and Cosmology」方向的教授，他们的共同主题与合作/相似关系。 |
| **方向子网：天体物理与宇宙学** | 45 | 231 | 院系官网标注为「Theoretical Astrophysics and Cosmology / Experimental and Observational Astrophysics and Cosmology」方向的教授，他们的共同主题与合作/相似关系。 |
| **方向子网：凝聚态 · 原子分子光学** | 78 | 267 | 院系官网标注为「Experimental Condensed Matter Physics / Atomic, Molecular and Optical Physics」方向的教授，他们的共同主题与合作/相似关系。 |
| **方向子网：化学生物学与有机化学** | 118 | 350 | 院系官网标注为「Chemistry-Biology Interface / Organic Chemistry」方向的教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理化学 · 理论化学 · 材料与催化** | 125 | 377 | 院系官网标注为「Physical Chemistry / Theoretical Chemistry / Materials Chemistry / Catalysis / Inorganic Chemistry」方向的教授，他们的共同主题与合作/相似关系。 |
| **方向子网：数学：几何 · 拓扑 · 分析** | 46 | 124 | 数学系官网标注为 Geometry / Topology / Analysis / Symplectic / Partial Differential 等方向的教授。 |
| **方向子网：数学：数论 · 代数 · 表示论 · 组合** | 30 | 87 | 数学系官网标注为 Number Theory / Algebra / Representation / Combinatorics 等方向的教授。 |
| **方向子网：数学：概率 · 应用与计算数学** | 55 | 134 | 数学系官网标注为 Probability / Applied / Computational / Numerical 等方向的教授。 |
| **研究主题地图** | 301 | 2139 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **创新创业网** | 278 | 660 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位（如 IBM、Google、Genentech），按教授统计合写篇数，见 `data/processed/industry_links.csv`。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条都附公开来源与原文摘录（目前主要来自维基百科，另有 Crunchbase）。只收录明确写着 founder / co-founder 的条目；"研究催生了某公司"、仅任董事或顾问的不收。这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。OpenAlex 不含专利，PatentsView / Google Patents 需要额外的 API key 或云账号。

## 数据流程

```
院系官网教师名单 ──► scripts/roster_stanford.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                          ▼
              scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_stanford.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**：mathematics.stanford.edu（Faculty & Lecturers）、physics.stanford.edu（Faculty）、appliedphysics.stanford.edu（Faculty 区块）、chemistry.stanford.edu（Faculty），抓取于 2026-11-08。去除荣休、讲师、兼职（adjunct）、访问学者、纯礼节性（courtesy）聘任；数学系列出的 Szegő 助理教授保留。尚未入职的（如 "Joining 2027"）也保留并在 `note` 列标注。
- **作者匹配**：OpenAlex 作者检索（限定 Stanford / SLAC / Stanford Medicine），按姓名、研究领域、当前机构打分；OpenAlex 尚未关联 Stanford 的新教师走不限机构的严格匹配，在 `matches.csv` 的 `match_note` 标注。两位教授（Sasha Philippov、Xiaodong Xu）的 OpenAlex 档案被拆分，自动匹配到了碎片，已手工指定主档案。
- **大型合作**：超过 100 位作者的论文（粒子物理、宇宙学巡天等）单独记为"大型合作"浅色边，不计入合写强度。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- **方向子网**：依据院系官网给每位教授标注的研究方向（物理、化学、数学系各自的分类）。
- 数据均来自公开来源；OpenAlex 数据为 CC0。

## 目录

```
scripts/            抓取与构建脚本
data/raw/           原始抓取结果（院系名单页、OpenAlex 缓存）
data/manual/        人工整理并附来源的数据（教授创办的公司）
data/processed/     名单、匹配表、教授表、合作边、相似边、主题表、产业合作表（CSV）
site/               交互式可视化（sigma.js + graphology，已内置，无需 CDN）
```
