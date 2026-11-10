# 加州大学洛杉矶分校（UCLA）数学 · 物理 · 化学 研究网络

把 UCLA 数学系、物理与天文系、化学与生物化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 24 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：187 位在职教师（数学 42、物理与天文 57、化学与生物化学 88；不含荣休教授、讲师与博士后）。
- OpenAlex 匹配 181 个作者档案，约 3.6 万篇论文（去掉 PDB 结构数据集等 dataset 记录后）。未匹配的 6 位（Maya Pathuri、Frank Ow、Johnny W. Pang、Hung V. Pham、Sining Wang、Richard L. Weiss）多为教学序列教师，OpenAlex 里没有可靠档案。
- 加州纳米系统研究所（CNSI）：按论文署名统计，34 位教授有 ≥5 篇论文同时署名 CNSI，单独成网。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 3899 | 11951 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 144 | 398 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| 研究相似网 | 172 | 449 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 309 | 995 | 只保留跨系（数学×物理与天文×化学与生物化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学系子网 | 134 | 388 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理与天文系子网 | 147 | 607 | 物理与天文系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学与生物化学系子网 | 381 | 1667 | 化学与生物化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：加州纳米系统研究所（CNSI）联署 | 274 | 996 | 至少 5 篇论文同时署名 California NanoSystems Institute 的教授（OpenAlex 作者机构），横跨化学、物理与数学。 |
| 方向子网：量子科学：量子信息 · 量子材料 · 量子化学 | 196 | 700 | 三系中至少 8 篇论文的 OpenAlex 主题属于量子信息 / 量子计算、拓扑与超导等量子材料、冷原子与原子物理、量子化学光谱的教授。 |
| 方向子网：天文与天体物理 | 30 | 150 | 物理与天文系官网研究组为 Astronomy 的教授。 |
| 方向子网：理论粒子物理 · 弦论 · 数学物理（含 Bhaumik 理论物理所） | 23 | 64 | 物理与天文系官网研究组为 Theoretical Elementary Particles、QCD 与核理论或理论与数学物理的教授。 |
| 方向子网：实验粒子物理 · 天体粒子 · 加速器 | 26 | 85 | 物理与天文系官网研究组为 Experimental Particle Physics、Astroparticle、实验 QCD 或 Accelerator Physics 的教授。 |
| 方向子网：凝聚态物理 | 42 | 119 | 物理与天文系官网研究组为 Condensed Matter 的教授。 |
| 方向子网：原子分子光学 · 等离子体 | 31 | 81 | 物理与天文系官网研究组为 AMO 或 Plasma 的教授。 |
| 方向子网：生物物理 · 神经物理 · 软物质 | 127 | 321 | 物理与天文系研究组为 Biophysics / Neurophysics，或化学与生物化学系标注 Biophysics 的教授。 |
| 方向子网：有机化学 · 化学生物学 | 232 | 841 | 化学与生物化学系官网标注 Organic / Chemical Biology / Synthesis 方向的教授。 |
| 方向子网：生物化学 · 分子与结构生物学 | 115 | 315 | 化学与生物化学系官网标注 Biochemistry / Molecular and Structural Biology 方向的教授。 |
| 方向子网：无机化学 · 材料与纳米科学 | 169 | 571 | 化学与生物化学系官网标注 Inorganic / Materials / Nanoscience 方向的教授。 |
| 方向子网：物理化学 · 分析化学 | 174 | 488 | 化学与生物化学系官网标注 Physical / Analytical 方向的教授。 |
| 方向子网：理论与计算化学 | 110 | 270 | 化学与生物化学系官网标注 Theory / Computation 方向的教授。 |
| 方向子网：数学：代数 · 数论 · 几何 · 拓扑 · 组合 · 逻辑 | 35 | 111 | 数学系中，主要研究子领域（OpenAlex）为代数与数论、几何与拓扑、离散数学与组合或计算理论的教授。 |
| 方向子网：数学：分析 · 偏微分方程 · 概率 · 数学物理 | 35 | 71 | 数学系中，主要研究子领域（OpenAlex）为数学物理、应用数学（多为偏微分方程与分析）或统计与概率的教授。 |
| 方向子网：数学：应用与计算数学 · 数据科学 · 图像与网络 | 49 | 116 | 数学系中，主要研究子领域（OpenAlex）属于计算力学、人工智能、计算机视觉、信号处理、金融、非线性物理、生物等应用方向的教授。 |
| 研究主题地图 | 341 | 1911 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **创新创业网** | 284 | 589 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：取数学系 ladder faculty 名单（https://www.math.ucla.edu/people/ladder）中的在职教授。挂在数学系、但主聘在电子工程、计算机、统计或地球行星空间科学系的 7 位（Dolecek、Fletcher、Ker-Chau Li、Newman、Ostrovsky、Sahai、Vandenberghe）不纳入；数学与计算医学、社会学、统计、机械航天双聘的（Chou、Roper、Porter、Montúfar、Bertozzi）纳入。官网名单里没有 Rowan Killip、Monica Visan 等人，因此也没有收录。
- **物理与天文**：取 https://www.pa.ucla.edu/faculty.html 的在职教授（含 Distinguished Research Professor D'Hoker 与教学教授 Samani），研究组按该页标注（Astronomy、TEP、实验粒子、凝聚态、AMO、等离子体、加速器、生物物理）。
- **化学与生物化学**：取系目录 https://www.chemistry.ucla.edu/directory/department/faculty 全部 5 页（88 人，去掉主聘在微生物、免疫与分子遗传系的 Hong Zhou）。目录不显示职称，页面上统一显示为 Faculty，带 Instructional 标签的显示为 Teaching faculty。部分资深教授（如 Levine、Reisler）同时出现在 2023 年的荣休名单里，以现行目录为准保留。
- **CNSI**：California NanoSystems Institute 在 OpenAlex 里有独立机构记录（I142207940），按教授本人在论文上的署名统计联署篇数。
- **量子科学子网**：UCLA 有跨院系的 Center for Quantum Science and Engineering，但没有可读取的成员名单，因此按论文主题筛选（至少 8 篇论文主题属于量子信息、量子材料、冷原子与原子物理或量子化学光谱）。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。合作最多的企业有 RadiaBeam、Merck、ExxonMobil、Amgen、Pfizer、HRL、Northrop Grumman 等。
- **教授创办的公司**：`data/manual/startups.csv`，14 条，每条都附公开来源与原文摘录：Kaner（Nanotech Energy、SuperMetalix、Polycera、Hydrophilix/SILQ）、Jung（Aragon Pharmaceuticals、Pelage、Athos Therapeutics）、Yi Tang（Hexagon Bio）、Narang（Aliro Quantum）、Rosenzweig（RadiaBeam）、Duan（Nanosys，科学联合创始人）、Andrews（FemSync）、Garg（ElectraTect）、Deming（Amicrobe）。只收明确写着 founder / co-founder 的条目；Eisenberg（ADRx）、Putterman（Tribogenics）等找不到明确"创办"表述的没有收录。这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单 ──► data/raw/roster/{math,physics,chem_raw}.txt ──► scripts/roster_ucla.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                           ▼
          scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_ucla.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py     # 主网布局约 5 分钟
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：上面三个院系官网页面。云端无法直接访问 ucla.edu，名单经网页抓取工具读出后存成 `data/raw/roster/*.txt`。
- **作者匹配**：OpenAlex 作者检索（限定 UCLA，I161318765），按姓名、研究领域、当前机构打分。12 位做了人工指定（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来），例如 Bachtis、Stuart Brown 的检索结果只命中 1 篇的碎片档案，Yu Huang、Paul S. Weiss、Young Dae Yoon 被自动匹配到了同名或相近名字的其他人。Hung V. Pham、Sining Wang 的候选档案都是同名的其他人，不匹配。
- **论文**：每人全部 OpenAlex works，去掉勘误、撤稿、同行评议记录与 dataset（Eisenberg 等人名下有大量 PDB 结构数据集，会把 Genentech 等误算成合作企业）。>60 作者的论文不记录作者名单；≥100 作者的算"大型合作"（OpenAlex 每篇最多返回 100 个作者，100 即表示被截断；CMS、IceCube 等），在合作网中用浅色边。
- **方向子网**：物理与化学按院系官网标注的研究组；数学系官网不列研究方向，数学的三张方向子网按每人论文最多的 OpenAlex 子领域划分，属近似。
- 研究相似度：每人论文主题的 TF-IDF 余弦相似度，取最相近的 6 位（阈值 0.2）。
