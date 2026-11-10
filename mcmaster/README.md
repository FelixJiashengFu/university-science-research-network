# 麦克马斯特大学 数学 · 物理 · 化学 研究网络

把麦克马斯特大学（McMaster University，汉密尔顿）理学院数学与统计系、物理与天文系、化学与化学生物系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 22 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：92 位在职教授（数学 34、物理与天文 29、化学 29；Hari Kunduri 在数学、物理两系任职，按一人计，页面上显示"跨聘"）。数学与统计系另有 7 位统计/精算方向的教授未纳入（见下文"范围说明"）。
- OpenAlex 匹配 87 个作者档案，约 1.07 万篇论文。未匹配的 5 位都是教学序列教师（Erin Clements、Christopher McLean、Miranda Schmidt、Anthony Chibba、Avik Ghoshdastidar），OpenAlex 里没有可靠档案。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 1320 | 3126 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 58 | 79 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| 研究相似网 | 79 | 111 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 125 | 247 | 只保留跨系（数学×物理与天文×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学与统计系子网 | 74 | 152 | 数学与统计系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理与天文系子网 | 86 | 216 | 物理与天文系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学与化学生物系子网 | 94 | 214 | 化学与化学生物系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：理论物理（与 Perimeter 研究所联署） | 12 | 21 | 至少 5 篇论文同时署名 Perimeter Institute 的教授（OpenAlex 作者机构）；McMaster 多位理论物理教授是 Perimeter 的 associate faculty。 |
| 方向子网：天体物理与宇宙学（Origins 研究所方向） | 16 | 44 | 主要研究子领域（OpenAlex）为 Astronomy and Astrophysics 的教授：星系、星团、系外行星、星际介质与数值模拟。 |
| 方向子网：高能理论 · 引力 · 核天体物理 | 9 | 14 | 主要研究子领域为 Nuclear and High Energy Physics 的教授（数学系、物理系都有），含有效场论、宇宙学、黑洞与高维引力、核天体物理实验。 |
| 方向子网：凝聚态 · 量子材料 · 固体化学（Brockhouse 研究所方向） | 31 | 90 | 物理、化学两系中主要子领域为凝聚态、电子/光学/磁性材料或材料化学的教授：中子与 μSR 散射、NMR、量子磁性、热电与固态无机材料。 |
| 方向子网：软物质 · 高分子 · 生物物理 | 39 | 82 | 软物质与生物物理方向（按研究主题人工归类）：高分子薄膜与流变、膜与蛋白生物物理、生命起源与进化理论、DNA 纳米技术与高分子化学。 |
| 方向子网：医学物理 · 放射化学 · 核医学 | 12 | 15 | 主要两个子领域中含 Radiation 或 Radiology/Nuclear Medicine 的教授：放射剂量与成像、PET 放射性药物、靶向放射治疗（McMaster 核反应堆与回旋加速器）。 |
| 方向子网：量子理论 · 原子分子光学 · 理论与计算化学 | 16 | 25 | 主要子领域为 Atomic and Molecular Physics, and Optics 或 Physical and Theoretical Chemistry 的教授：冷原子、强场物理、量子多体数值方法、电子结构理论与化学机器学习。 |
| 方向子网：合成化学：有机 · 无机 · 主族 · 金属有机 | 28 | 58 | 化学系中主要子领域为 Organic Chemistry 或 Inorganic Chemistry 的教授。 |
| 方向子网：化学生物 · 生物分析 · 生物材料 | 19 | 34 | 化学系中主要子领域属于分子生物学、生物医学工程、生物材料、结构生物学或临床生化的教授。 |
| 方向子网：能源材料 · 表界面 · 环境化学 | 12 | 13 | 化学系中研究电池/能源材料（固体 NMR）、表面与低维材料、光子学材料、大气与环境化学、暴露科学的教授。 |
| 方向子网：数学：代数 · 几何 · 拓扑 · 数理逻辑 | 20 | 41 | 数学系中主要子领域为 Geometry and Topology 或 Algebra and Number Theory 的教授（含模型论与 o-极小结构）。 |
| 方向子网：数学：分析 · 偏微分方程 · 计算流体与变分 | 16 | 23 | 数学系中主要子领域为 Applied Mathematics、Computational Mechanics、Mechanics of Materials 或 Statistical and Nonlinear Physics 的教授，排除数学生物方向。 |
| 方向子网：数学生物 · 传染病建模 · 生态动力学 | 16 | 28 | 数学系官网研究方向标注 Mathematical Biology 的教授，以及与他们研究主题最接近的物理系进化理论学者。 |
| 方向子网：概率 · 金融数学 · 机器学习理论 | 9 | 15 | 数学系中研究概率论、金融数学与机器学习理论的教授（官网方向 Financial Mathematics，或主要子领域为数学物理/概率/金融/人工智能）。 |
| 研究主题地图 | 134 | 297 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| 创新创业网 | 102 | 126 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：麦克马斯特的数学与统计是同一个系。为与 UofT、Waterloo 只取数学系的做法一致，去掉了以统计学、精算为主的 7 位教授（Abdallah、Balakrishnan、Canty、Childs、Davies、Jeganathan、McNicholas，见 `scripts/roster_mcmaster.py` 的 `STATS`）；概率论（Feng、Forman）和金融数学（Grasselli、Pirvu）保留。
- **物理**：取物理与天文系 Current Faculty 名单（含医学物理方向的教授）；兼职（adjunct）、荣休、博士后、教学助理不纳入。
- **化学**：取化学与化学生物系 Full-time Faculty 名单（含教学序列）；Associate / Adjunct Faculty（Todd Hoare、Yingfu Li、Jakob Magolan 等主聘在其他院系的教授）不纳入。
- **研究所**：Brockhouse 材料研究所、Origins 研究所没有公开、可机读的成员名单，相应子网按 OpenAlex 主要子领域划分，标题里的研究所名只表示方向。Perimeter 研究所在 OpenAlex 里有独立机构记录（I183974707），按教授本人在论文上的署名统计联署篇数。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条附公开来源与原文摘录：MesoMat（Dalnoki-Veress，2017，可穿戴导电纱线）、Tessella Biosciences（Moran-Mirabal，3D 生物打印墨水）。只收明确写着 founder / co-founder 的条目，这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/roster.txt ──► scripts/roster_mcmaster.py ──► data/processed/roster.csv
OpenAlex：McMaster 作者池 + 检索兜底 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                           ▼
                     scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_mcmaster.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：math.mcmaster.ca/people/faculty/、physics.mcmaster.ca/people/current-faculty/、chemistry.mcmaster.ca/people/full-time-faculty/。mcmaster.ca 拒绝云端自动抓取，名单是在浏览器里读出后存成 `data/raw/roster/roster.txt`（院系页面没写研究方向的教授，`areas` 留空，研究主题完全来自 OpenAlex）。
- **作者匹配**：先用 3 次廉价的列表查询拉下所有署名过 McMaster、主题含数学/物理/化学的 OpenAlex 作者（约 9,300 个档案，`data/raw/openalex/pool.json`，不入库），在本地按姓名、研究领域、当前机构打分；池里找不到的人才单独检索。OpenAlex 常把一个人拆成多个档案，14 位教授做了人工指定（`scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来）。Suzanne Lapi 近年从阿拉巴马大学伯明翰分校（UAB）加入 McMaster，OpenAlex 里仍挂在 UAB，手工指定。
- **作者档案污染**：OpenAlex 把一位同名的英国文学学者并进了 Robert Cockcroft 的档案，`build_graph.py` 的 `keep_work` 只保留他的天文学与教学研究论文。
- **合作**：两位教授同时出现在一篇论文的作者列表中即算合写；>100 作者的论文算"大型合作"，单独着色，避免大型天文/核物理合作把网络连成一团；>60 作者的论文不保存完整作者列表。
- **研究相似**：教授的论文主题（OpenAlex primary topic）分布做 TF-IDF 加权后算余弦相似度，每人保留最相近的 6 位（相似度 ≥0.2）。
- **方向子网**：大多按 OpenAlex 的主要子领域自动划分；"软物质 · 高分子 · 生物物理"和"能源材料 · 表界面 · 环境化学"两张按教授的研究主题人工归类（`build_graph.py` 的 `GROUPS`）。
- OpenAlex 数据会随时间更新，计数为 2026-11-10 的快照；全站每月自动刷新时会重新下载论文并重建网络（`refresh/refresh.py`）。
