# 滑铁卢大学 数学 · 物理 · 化学 研究网络

把滑铁卢大学数学学院三个数学系（纯数学、应用数学、组合与优化）和理学院物理与天文系、化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 23 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：178 位在职教授（纯数学 27、应用数学 31、组合与优化 33、物理与天文 43、化学 44；20 人在范围内跨系聘任，按一人计，页面上显示"跨聘"）。
- OpenAlex 匹配 167 个作者档案，约 1.9 万篇论文。未匹配的 11 位多为教学序列教授或刚入职、OpenAlex 里没有可靠档案的老师。
- 量子计算研究所（IQC）：29 位成员（20 位 faculty + 9 位 associates），单独成网。
- Perimeter 理论物理研究所：按论文署名统计，27 位教授有 ≥5 篇论文同时署名 Perimeter。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2185 | 5885 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 125 | 184 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| **研究相似网** | 155 | 438 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 307 | 871 | 只保留跨系（纯数学×应用数学×组合与优化×物理与天文×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **纯数学系子网** | 40 | 129 | 纯数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **应用数学系子网** | 86 | 203 | 应用数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **组合与优化系子网** | 62 | 224 | 组合与优化系教授、他们共同的研究主题与内部合作/相似关系。 |
| **物理与天文系子网** | 116 | 370 | 物理与天文系教授、他们共同的研究主题与内部合作/相似关系。 |
| **化学系子网** | 160 | 435 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **方向子网：量子信息与量子计算（IQC 成员）** | 75 | 267 | 量子计算研究所（IQC）官网列出的 faculty 与 associates，横跨纯数学、应用数学、组合与优化、物理与化学。 |
| **方向子网：理论物理（与 Perimeter 研究所联署）** | 72 | 230 | 至少 5 篇论文同时署名 Perimeter Institute 的教授（OpenAlex 作者机构）。 |
| **方向子网：天体物理与宇宙学** | 21 | 73 | 主要研究子领域（OpenAlex）为 Astronomy and Astrophysics 的教授。 |
| **方向子网：凝聚态 · 原子分子光学 · 软物质** | 89 | 285 | 物理与天文、化学两系中，主要子领域为凝聚态、原子分子光学或材料物理的教授。 |
| **方向子网：有机化学 · 生物化学 · 生物分析** | 51 | 93 | 化学系官网标注为 Organic Chemistry / Biochemistry / Bioanalytical Chemistry 方向的教授。 |
| **方向子网：物理化学 · 理论化学 · 无机与纳米材料** | 106 | 253 | 化学系官网标注为 Physical / Theoretical / Inorganic / Polymer / Analytical Chemistry 或 Nanotechnology 方向的教授。 |
| **方向子网：纯数学：代数 · 数论 · 几何 · 拓扑** | 35 | 110 | 纯数学系官网研究方向含 algebra / number theory / geometry / topology / Lie / representation 的教授。 |
| **方向子网：纯数学：分析 · 算子代数 · 逻辑 · 动力系统** | 13 | 25 | 纯数学系官网研究方向含 analysis / operator / logic / model theory / probability / dynamical 的教授。 |
| **方向子网：应用数学：数学生物与医学 · 动力系统 · 控制** | 41 | 93 | 应用数学系官网标注 Mathematical Biology / Dynamical Systems / Control 方向的教授。 |
| **方向子网：应用数学：流体力学 · 科学计算 · 数值分析** | 31 | 61 | 应用数学系官网标注 Fluid Mechanics / Scientific Computing / Numerical 方向的教授。 |
| **方向子网：应用数学：数学物理 · 量子信息 · 机器学习** | 20 | 44 | 应用数学系官网标注 Mathematical Physics / Quantum Information / Machine Learning 方向的教授。 |
| **方向子网：组合与优化：组合 · 图论** | 38 | 134 | 组合与优化系中，主要子领域（OpenAlex）为 Discrete Mathematics and Combinatorics 或 Computational Theory 的教授。 |
| **方向子网：组合与优化：连续优化 · 运筹 · 密码学 · 量子** | 22 | 55 | 组合与优化系中，主要子领域不属于组合/图论的教授（数值优化、运筹、密码学、量子计算等）。 |
| **研究主题地图** | 237 | 775 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **创新创业网** | 222 | 300 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：滑铁卢的数学学院有五个系。这里取纯数学、应用数学、组合与优化三个系；统计与精算系和计算机科学学院不在范围内（与 UofT、Stanford 版本只取数学系一致）。
- **跨系聘任**：只合并这五个系之间的跨聘（如 Mosca 在组合与优化、应用数学、物理三系）。外院（电子与计算机工程、光学视觉学院等）挂在物理系的跨聘教师不纳入。
- **IQC 与 Perimeter**：IQC 不是独立聘任单位，成员都挂在各系，名单来自 IQC 官网 Our people 页的 Faculty 与 Associates of IQC 两组（`data/manual/iqc_members.csv`）。Perimeter 在 OpenAlex 里有独立机构记录（I183974707），按教授本人在论文上的署名统计联署篇数。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条都附公开来源与原文摘录：evolutionQ（Mosca、Lütkenhaus、Jao）、softwareQ（Mosca）、Quantum Benchmark（Emerson，2021 年被 Keysight 收购）、Open Quantum Design（Senko、Islam、Melko，非营利）。只收明确写着 founder / co-founder 的条目，这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/roster_part*.txt ──► scripts/roster_waterloo.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/{startups,iqc_members}.csv ─┐
                                          ▼
                     scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_waterloo.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-09 读取）：uwaterloo.ca 各系教师页——纯数学 faculty-members、应用数学 faculty-members 与 cross-appointed、组合与优化 our-people/faculty、物理与天文 contacts（Professors、Cross-appointed faculty 两组）、化学 our-people/professors。uwaterloo.ca 拒绝云端自动抓取，名单是在浏览器里读出后存成 `data/raw/roster/roster_part*.txt`。不含荣休、兼职（adjunct）、博士后。教学序列（Teaching Stream）教授保留。Pok Man Tam 2027 年 1 月到任，已列入并在 `note` 标注。Robert Mann 未出现在物理系 Professors 分组中，但应用数学系跨聘名单把他列为物理与天文系教授，因此手工补入。
- **作者匹配**：OpenAlex 作者检索（限定 Waterloo / Perimeter），按姓名、研究领域、当前机构打分。OpenAlex 常把一个人拆成多个档案，12 位教授做了人工指定（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来）；Russell Thompson、Karen Cummings 的候选档案都是同名的其他人，不匹配。
- **大型合作**：超过 100 位作者的论文单独记为"大型合作"浅色边，不计入合写强度。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- **方向子网**：数学与化学按院系官网标注的研究方向；物理系与组合与优化系官网没有方向标注，按每位教授论文的主要 OpenAlex 子领域分组。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
