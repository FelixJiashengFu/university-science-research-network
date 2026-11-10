# 密歇根大学（Ann Arbor）数学 · 物理 · 化学 研究网络

把密歇根大学文理学院（LSA）数学系、物理系、化学系在职教授的研究领域、论文、合作关系、校外研究机构、产业合作与创业活动编织成一张主网，并拆出 22 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：153 位在职 tenured / tenure-track 教授（数学 55、物理 51、化学 47；Dominika Zgid 物理与化学双聘，按一人计）。
- OpenAlex 匹配 151 个作者档案，约 2.8 万篇论文（去掉勘误、撤稿、审稿意见和数据集条目后）。未匹配的是数学系 Charlotte Chan 与 Patrick Lutz（OpenAlex 里找不到可靠档案，同名候选都是化学家或医生）。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2487 | 7143 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 117 | 223 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| 研究相似网 | 143 | 408 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 262 | 679 | 只保留跨系（数学×物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学系子网 | 137 | 471 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理系子网 | 150 | 601 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学系子网 | 213 | 768 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：数学：代数 · 代数几何 · 数论 · 组合 | 41 | 156 | 按院系官网标注的研究方向含「Algebra / Number Theory / Combinatorics」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：数学：几何 · 拓扑 · 分析 · 偏微分方程 | 49 | 148 | 按院系官网标注的研究方向含「Geometry and Topology / Analysis / Differential Equations / Logic」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：数学：概率 · 数学物理 · 金融数学 | 28 | 51 | 按院系官网标注的研究方向含「Probability / Mathematical Physics / Financial」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：数学：应用数学 · 数学生物 · 科学计算 | 56 | 102 | 按院系官网标注的研究方向含「Applied Mathematics / Mathematical Biology / Scientific Computing / Computer Science」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：物理：粒子物理 · 核物理 | 43 | 192 | 按院系官网标注的研究方向含「Elementary Particle / Nuclear」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：物理：宇宙学 · 天体物理 | 28 | 92 | 按院系官网标注的研究方向含「Cosmology」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：物理：凝聚态 · 原子分子光学 | 77 | 262 | 按院系官网标注的研究方向含「Condensed Matter / Atomic, Molecular」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：物理：生物物理 · 复杂系统 | 22 | 37 | 按院系官网标注的研究方向含「Biological Physics / Complex Systems」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：化学：有机 · 合成 · 催化 | 147 | 500 | 按院系官网标注的研究方向含「Organic Chemistry / Synthesis / Catalysis」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：化学：化学生物学 · 生物大分子 | 119 | 350 | 按院系官网标注的研究方向含「Chemical Biology / Biomacromolecular」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：化学：物理化学 · 理论计算 · 成像与光谱 | 159 | 444 | 按院系官网标注的研究方向含「Physical Chemistry / Theory & Computation / Imaging / Photochemistry」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：化学：无机 · 材料 · 能源与环境 | 154 | 484 | 按院系官网标注的研究方向含「Inorganic / Materials / Energy / Nanochemistry」的教授，他们的共同主题与合作/相似关系。 |
| 方向子网：化学：分析化学 | 51 | 102 | 按院系官网标注的研究方向含「Analytical」的教授，他们的共同主题与合作/相似关系。 |
| 研究主题地图 | 285 | 1335 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| 研究机构网 | 298 | 953 | 教授与校外研究机构、国家实验室、医院和资助机构的联系（OpenAlex 机构类型 nonprofit / facility / government / healthcare）：同一机构与该教授合写 ≥3 篇、且至少连到 2 位教授才显示；另含教授之间的合写关系。 |
| 创新创业网 | 241 | 391 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司，以及公开资料称为其实验室衍生的公司（逐条附来源与原文摘录，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：数学系官网 "Faculty - Tenured, Tenure Track" 名单。讲师（Lecturers）、博士后、研究科学家、荣休教授不在范围内。统计系是独立的系，不纳入（与其他学校只取数学系一致）。
- **物理**：物理系官网 Faculty 名单（含工学院核工程系的 Sara Pozzi，官网列在物理系教师中）。
- **化学**：化学系官网 Faculty 名单去掉 Lecturer 后的 47 人。
- 方向子网按院系官网给每位教授打的研究方向标签划分（数学的 Algebra / Analysis…，物理的 Experimental/Theoretical Condensed Matter…，化学的 Analytical / Inorganic / Organic / Physical / Chemical Biology / Materials / Theory & Computation 等），一位教授可同时属于多个方向子网。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **校外研究机构**：OpenAlex 类型为 nonprofit / facility / government / healthcare 的机构（国家实验室、医院、研究所等）单独成"研究机构网"。
- **教授创办的公司**：`data/manual/startups.csv`，每条都附公开来源与原文摘录：Heliotrope Technologies（Delia Milliron）、MONSTR Sense Technologies（Steven Cundiff）、k-Space Associates（Roy Clarke，1992）。只收明确写着 founder / co-founder 的条目，这份名单**并不完整**，欢迎按同样格式补充。Ryan Bailey 与 Genalyte 的关系公开资料只写 "helped launch"，暂不收录。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/{math,physics,chemistry}.txt ──► scripts/roster_umich.py ──► data/processed/roster.csv
OpenAlex 作者池 + 检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                          ▼
         scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_umich.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：lsa.umich.edu 的 math/people/faculty.html、physics/people/faculty.html、chem/people/faculty.html。该站拒绝云端自动抓取，名单是在浏览器里读出后存成 `data/raw/roster/*.txt`（只保留姓名、职称、研究方向）。Roy Clarke 仍列在物理系 Faculty 页面上，但学校董事会文件显示他已于 2026 年 5 月荣休，这里按官网名单保留。
- **作者匹配**：先用一次低成本的 OpenAlex 列表查询取回"最近机构 = 密歇根大学、研究领域含数学/物理/化学"的约 6,000 个作者档案（`authors/_pool.json`，不提交），在本地按姓名、研究领域打分；本地找不到的再调用检索。5 位教授做了人工指定（含化学系 Wenjing Wang：自动匹配曾误配到一位同姓 ATLAS 物理学家）（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来）。
- **大型合作**：OpenAlex 每篇论文最多返回 100 个作者，所以作者数 = 100 实际表示"100 位及以上"。这类论文（ATLAS、DUNE 等）单独记为"大型合作"浅色边，不计入合写强度（`BIG_COLLAB = 99`），也不计入产业合写与校外机构统计（否则几千人合作里的一家公司会被算成产业合作）。
- **数据集条目**：OpenAlex 的 `dataset` 类型（如蛋白质结构库的结构存档，一人可多达数百条）不算论文，已排除。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
