# 伊利诺伊大学厄巴纳-香槟分校（UIUC）数学 · 物理 · 化学 研究网络

把 UIUC 数学系、物理系、化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 24 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：191 位在职教授（数学 65、物理 75、化学 51；Makri、Luthey-Schulten、Phillips 三人在物理和化学两系都有任命，按一人计，页面上显示"跨聘"）。含物理系 10 位、化学系 9 位研究教授（Research Professor）和教学序列教授；不含荣休、兼职、讲师和其他院系的 faculty affiliates。
- OpenAlex 匹配 189 个作者档案，约 3.2 万篇论文（不计勘误、撤稿和 dataset 类条目，例如晶体结构数据库里的晶体结构存档）。未匹配的 2 位：Wei Wei（精算方向，OpenAlex 里只有同名的其他人）、Frank Quan（新入职，没有可靠档案）。
- 产业合写企业 258 家；教授创办的公司 11 家（8 位教授）。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2853 | 8605 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 140 | 297 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| **研究相似网** | 181 | 575 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 293 | 921 | 只保留跨系（数学×物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **数学系子网** | 124 | 477 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **物理系子网** | 198 | 945 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| **化学系子网** | 273 | 1018 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **方向子网：量子信息科学（IQUIST 方向）** | 76 | 326 | 物理系官网研究方向含 Quantum Information Science 的教授，加上前三大研究主题含量子信息的数学系教授。 |
| **方向子网：凝聚态理论** | 54 | 194 | 物理系官网标注 Condensed Matter Physics (theoretical) 的教授。 |
| **方向子网：凝聚态实验** | 46 | 152 | 物理系官网标注 Condensed Matter Physics (experimental) 的教授。 |
| **方向子网：原子分子与光学物理** | 37 | 94 | 物理系官网标注 Atomic, Molecular, and Optical Physics 的教授。 |
| **方向子网：天体物理 · 相对论 · 宇宙学** | 40 | 158 | 物理系官网标注 Astrophysics / Relativity / Cosmology 的教授。 |
| **方向子网：高能物理与核物理** | 47 | 211 | 物理系官网标注 High Energy Physics 或 Nuclear Physics（理论与实验）的教授。 |
| **方向子网：生物物理** | 30 | 80 | 物理系官网标注 Biological Physics 的教授（含化学系跨聘）。 |
| **方向子网：物理教育研究** | 12 | 24 | 物理系官网标注 Physics Education 的教授。 |
| **方向子网：有机化学** | 73 | 187 | 化学系官网 Organic Chemistry 方向教师页列出的教授。 |
| **方向子网：无机化学** | 41 | 111 | 化学系官网 Inorganic Chemistry 方向教师页列出的教授。 |
| **方向子网：物理化学 · 理论化学** | 62 | 135 | 化学系官网 Physical Chemistry 方向教师页列出的教授。 |
| **方向子网：分析化学** | 69 | 176 | 化学系官网 Analytical Chemistry 方向教师页列出的教授。 |
| **方向子网：化学生物学** | 71 | 164 | 化学系官网 Chemical Biology 方向教师页列出的教授。 |
| **方向子网：材料化学** | 126 | 385 | 化学系官网 Materials Chemistry 方向教师页列出的教授。 |
| **方向子网：数学：代数 · 数论 · 几何 · 拓扑** | 40 | 132 | 数学系中，主要研究子领域（OpenAlex）为 Algebra and Number Theory 或 Geometry and Topology 的教授。 |
| **方向子网：数学：分析 · 数学物理 · 应用数学 · 概率 · 组合** | 92 | 275 | 数学系中，主要研究子领域（OpenAlex）不是代数/数论/几何/拓扑的教授：分析与偏微分方程、数学物理、应用与计算数学、概率、组合。 |
| **研究主题地图** | 302 | 1730 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **创新创业网** | 256 | 444 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`），不计作者 ≥100 人的大型合作论文（例如事件视界望远镜论文里的 Google 署名）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条都附公开来源与原文摘录：REVOLUTION Medicines、Sfunga（现 Elion Therapeutics）、cystetic Medicines（Burke），Vanquish Oncology（Hergenrother），ChemSensing 及其后继公司、Iridescent Sensors（Suslick），Mobius Scientific（Sligar），Radius Health（Katzenellenbogen），Xerion Advanced Battery（Braun），NanoSi Advanced Technology（Nayfeh），Inprentus（Abbamonte）。只收来源里明确写着 founder / co-founder 的条目。化学系的 startups 页面还列了 Semprius（Nuzzo）、Protasis（Sweedler）等"由其研究产生"的公司，Autonomic Materials 也与 Moore 有关，但来源没写 founder，所以没有收入。这份名单**并不完整**。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单与研究方向页 ──► data/raw/roster/*.txt ──► scripts/roster_uiuc.py ──► data/processed/roster.csv
OpenAlex UIUC 候选作者（列表下载）◄── scripts/openalex_candidates.py ──► data/raw/openalex/candidates.json（不入库）
OpenAlex 匹配 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                           ▼
          scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_uiuc.py
python3 scripts/openalex_candidates.py   # 约 60 次列表请求，代替逐人搜索，省额度
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：数学系 https://math.illinois.edu/directory/faculty （Faculty 标签页）；物理系 https://physics.illinois.edu/people/directory/faculty （Department Faculty 与同页的研究教授，研究方向取自该页）；化学系 https://chemistry.illinois.edu/directory/faculty-by-type （Faculty、Joint Appointments、教学教授、Research Faculty），研究方向取自六个方向教师页（Organic、Inorganic、Physical、Analytical、Chemical Biology、Materials 的 Primary 名单；研究教授按其所在 Other 名单归类，Katzenellenbogen、Zimmerman 两位不在任何方向页上，按其研究归入有机化学）。数学系网页没有方向标注，数学方向子网按 OpenAlex 主要子领域分组。
- **作者匹配**：先一次性下载最后机构为 UIUC、研究主题涉及数学/物理/化学的全部 OpenAlex 作者（约 5800 人），在本地按姓名、学科、作品数打分匹配，只对没把握的人单独检索。10 位教授做了人工指定（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来），多为常见姓名被匹配到同名他人。Qian Chen 的 OpenAlex 档案混有同名作者，论文数可能偏高。
- **大型合作**：OpenAlex 每篇论文最多返回 100 位作者，所以作者数 ≥100 的论文（ATLAS、PHENIX、CMB 实验等）单独记为"大型合作"浅色边，不计入合写强度。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
