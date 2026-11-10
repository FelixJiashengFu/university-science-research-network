# 麦吉尔大学（McGill）数学 · 物理 · 化学 研究网络

把麦吉尔大学理学院数学与统计系、物理系、化学系教授的研究领域、论文、合作关系、校外研究机构、产业合作与创业活动编织成一张主网，并拆出 21 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：在仓库根目录 `python3 -m http.server 8000`，打开 http://localhost:8000/mcgill/site/ 。

## 规模

- 名单：123 位在职教授与讲师（数学与统计 49、物理 38、化学 36；Siwick、Wiseman 为物理/化学跨聘，按一人计）。
- OpenAlex 匹配 117 个作者档案，约 2.0 万篇论文。未匹配的 6 位都是教学序列讲师：其中 3 位 OpenAlex 里没有档案，Kiwon Lee、Armel Kelome、Sam Sewall 的候选档案是同名的其他人（或混入了其他人的论文），因此不匹配。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2322 | 6464 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 100 | 203 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| **研究相似网** | 109 | 245 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 160 | 328 | 只保留跨系（数学×物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **数学与统计系子网** | 108 | 306 | 数学与统计系教授、他们共同的研究主题与内部合作/相似关系。 |
| **物理系子网** | 113 | 405 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| **化学系子网** | 167 | 572 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **方向子网：数学：代数 · 数论 · 几何 · 拓扑 · 逻辑** | 19 | 47 | 数学与统计系官网研究方向含 Algebra / Number Theory / Geometry / Topology / Geometric Group Theory / Logic 的教授。 |
| **方向子网：数学：分析 · 偏微分方程 · 数学物理** | 27 | 60 | 数学与统计系官网研究方向含 Analysis / Partial Differential Equations / Mathematical Physics 的教授。 |
| **方向子网：数学：应用数学 · 数值分析 · 数学生物 · 优化与机器学习** | 20 | 41 | 数学与统计系官网研究方向含 Applied Mathematics / Numerical Analysis / Mathematical Biology 的教授，以及 Canada CIFAR AI Chair 教授。 |
| **方向子网：数学：概率 · 离散数学 · 组合** | 12 | 19 | 数学与统计系官网研究方向含 Probability / Discrete Mathematics 的教授。 |
| **方向子网：数学：统计** | 40 | 93 | 数学与统计系官网研究方向含 Statistics 的教授。 |
| **方向子网：物理：天体物理 · 宇宙学 · 粒子天体物理** | 29 | 129 | 物理系官网按领域分组中属于 Astrophysics / Particle Astrophysics 的教授。 |
| **方向子网：物理：凝聚态（实验与理论）· 生物物理 · 非线性** | 60 | 143 | 物理系官网按领域分组中属于 Experimental / Theoretical Condensed Matter、Biophysics、Non Linear Dynamics 的教授。 |
| **方向子网：物理：高能物理 · 核物理（实验与理论）** | 27 | 99 | 物理系官网按领域分组中属于 Experimental / Theoretical High Energy、Experimental / Theoretical Nuclear 的教授。 |
| **方向子网：Trottier 空间研究所（论文联署）** | 31 | 127 | 至少 5 篇论文同时署名 Trottier Space Institute at McGill 的教授（OpenAlex 作者机构）。 |
| **方向子网：化学：有机合成 · 化学生物学 · 药物与核酸** | 136 | 435 | 化学系教授中，论文最多的两个子领域（OpenAlex）含有机化学、生物化学、分子生物学、药物发现等的教授（化学系官网没有按方向的名单）。 |
| **方向子网：化学：材料 · 高分子 · 催化 · 电化学与绿色化学** | 103 | 303 | 化学系教授中，论文最多的两个子领域（OpenAlex）含材料化学、高分子、无机化学、催化、电化学、可持续能源等的教授。 |
| **方向子网：化学：物理化学 · 理论计算 · 分析与大气化学** | 26 | 42 | 化学系教授中，论文最多的两个子领域（OpenAlex）含物理与理论化学、光谱、分析化学、大气与环境化学等的教授。 |
| **研究主题地图** | 230 | 861 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **研究机构网** | 388 | 1550 | 教授与校外研究机构、国家实验室、医院和资助机构的联系（OpenAlex 机构类型 nonprofit / facility / government / healthcare）：同一机构与该教授合写 ≥3 篇、且至少连到 2 位教授才显示；另含教授之间的合写关系。 |
| **创新创业网** | 172 | 285 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司，以及公开资料称为其实验室衍生的公司（逐条附来源与原文摘录，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：McGill 的数学与统计是同一个系，这里整系纳入（含统计方向教授），在方向子网里再拆出"统计"。
- **不纳入**：荣休、退休、兼职（adjunct）教授与 associate members；Vetta 在计算机学院的跨聘不计。
- **大型合作**：作者数 ≥100 的论文（OpenAlex 一篇最多列 100 位作者，100 即被截断）算作大型合作，只画浅色边、不进主网论文层；ATLAS、ZEUS、CHIME 等实验合作论文因此不会淹没真正的小组合作。
- **Trottier 空间研究所**：OpenAlex 机构 I4405269957，按教授本人在论文上的署名统计联署篇数（≥5 篇进子网）。Mila（I4210164802）同样统计，但只有 2 位教授 ≥2 篇，未单独成网，在教授详情中显示。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条附公开来源与原文摘录：Nanoacademic Technologies（Hong Guo，2007 年 McGill 衍生）、Molecular Forecaster（Moitessier）、CataLum Technologies 与 ACSYNAM（Chao-Jun Li）、Anomera（Mark Andrews）。只收明确写着 founder / co-founder 的条目，名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/*.txt ──► scripts/roster_mcgill.py ──► data/processed/roster.csv
OpenAlex 候选作者池 + 逐名检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                           ▼
          scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_mcgill.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：www.mcgill.ca/mathstat/people/faculty（3 页）、www.physics.mcgill.ca/people/faculty-a.html（研究领域取自 faculty-f.html）、www.mcgill.ca/chemistry/faculty（Professors 与 Faculty Lecturers 两组）。mcgill.ca 拒绝云端自动抓取，名单在浏览器里读出后存为 `data/raw/roster/*.txt`。化学系没有按方向的教师名单，化学方向子网按每人论文最多的两个 OpenAlex 子领域划分。
- **作者匹配**：先用一次分页查询取回"最后机构为 McGill、研究领域含数学/物理/化学"的约 1,800 个作者作候选池，在本地按姓名、领域、机构打分；池中没有的再逐名检索。OpenAlex 常把一个人拆成多个档案，`scripts/openalex_fetch.py` 的 `OVERRIDE` 做了人工指定（第一个 id 为主档案，其余碎片的论文合并进来）。Hong Guo 的 McGill 论文大多落在与其他同名学者混在一起的档案里，因此改为按"署名 Hong Guo 且机构为 McGill、领域属物理/材料/化学/工程"的作者条目收集（`RAWNAME`）。
- **合作关系**只统计本名单内教授之间的合写；研究相似度按 OpenAlex 主题分布的 TF-IDF 余弦相似度。
