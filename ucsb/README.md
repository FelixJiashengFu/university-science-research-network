# 加州大学圣塔芭芭拉分校（UCSB）数学 · 物理 · 化学 研究网络

把 UCSB 数学系、物理系、化学与生物化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 20 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：132 位在职教授（数学 32、物理 59、化学与生物化学 41；David Morrison 数学/物理、Frank Brown 与 Joan-Emma Shea 化学/物理三系跨聘，按一人计）。
- OpenAlex 匹配 131 个作者档案，约 2.5 万篇论文（不含 OpenAlex 里的 dataset 记录，如 PDB / 晶体结构存档）。未匹配的 1 位（Stephanie Pazos，教学序列）在 OpenAlex 里没有可靠档案。
- Kavli 理论物理研究所（KITP）：OpenAlex 机构 I4405259940，按教授本人在论文上的署名统计联署篇数，≥5 篇的单独成网。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2052 | 5992 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 101 | 198 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| **研究相似网** | 128 | 339 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 234 | 736 | 只保留跨系（数学×物理×化学与生物化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **数学系子网** | 72 | 191 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **物理系子网** | 158 | 682 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| **化学与生物化学系子网** | 208 | 673 | 化学与生物化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| **方向子网：理论物理（与 KITP 联署）** | 63 | 210 | 至少 5 篇论文同时署名 Kavli 理论物理研究所（KITP）的教授（OpenAlex 作者机构）。KITP 设在 UCSB，常驻成员也在物理系任教。 |
| **方向子网：量子信息 · 量子计算 · 拓扑量子物质** | 66 | 246 | 至少 6 篇论文的主主题（OpenAlex）属于量子计算、量子信息、量子输运、拓扑材料或量子多体的教授，横跨数学、物理、化学（含 Microsoft Station Q、Google 量子 AI 相关团队）。 |
| **方向子网：高能理论 · 引力 · 数学物理** | 29 | 102 | 物理系官网标注 High Energy Theory / Gravity & Relativity / Mathematical Physics 方向的教授。 |
| **方向子网：高能实验物理** | 14 | 47 | 物理系官网标注 High Energy Experimental Physics 方向的教授（CMS、LZ、DUNE 等大型合作的论文为浅色边）。 |
| **方向子网：天体物理与宇宙学** | 25 | 91 | 物理系官网标注 Astrophysics & Cosmology 方向的教授。 |
| **方向子网：凝聚态理论** | 32 | 90 | 物理系官网标注 Condensed Matter Theory 方向的教授。 |
| **方向子网：凝聚态实验 · 原子分子光学** | 45 | 126 | 物理系官网标注 Condensed Matter Experimental Physics 或 Atomic, Molecular, and Optical Physics 方向的教授。 |
| **方向子网：软物质与生命物理** | 60 | 160 | 物理系官网标注 Physics of Soft and Living Matter 方向的教授（含物理、化学两系跨聘）。 |
| **方向子网：化学：有机合成 · 生物化学 · 化学生物学** | 122 | 329 | 化学与生物化学系中，主要子领域（OpenAlex）为有机化学、生物化学、分子/结构生物学、生物物理、生物材料等的教授。 |
| **方向子网：化学：材料 · 高分子 · 无机 · 物理与理论化学** | 93 | 215 | 化学与生物化学系中，主要子领域不属于有机/生物方向的教授（材料化学、高分子、无机、催化、物理与理论化学等）。 |
| **方向子网：数学：代数 · 数论 · 几何 · 拓扑** | 16 | 36 | 数学系中，主要子领域（OpenAlex）为代数与数论、几何与拓扑或离散数学的教授。 |
| **方向子网：数学：分析 · 偏微分方程 · 应用与计算数学** | 58 | 141 | 数学系中，主要子领域不属于代数/几何/拓扑的教授（分析、偏微分方程、数值与计算数学、数学物理、金融数学、机器学习等）。 |
| **研究主题地图** | 231 | 1311 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **创新创业网** | 192 | 328 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **只取三个系的 Faculty 分组**：数学系 people 页的 Faculty（不含 Lecturers、来自其他系的 Affiliated Faculty）；物理系 faculty 页（去掉 Adjunct Professor Andy Howell 与 Affiliated Faculty Ousmane Kodio）；化学与生物化学系 people 页的 Faculty（不含 Lecturer / Continuing Lecturer，以及 Affiliated 分组的 Adjunct / Research Professor）。教学序列教授（Teaching Professor、Lecturer SOE）保留。
- 统计与应用概率系、材料系、化工系不在范围内（与其他学校只取数学、物理、化学系一致）；化学系名单里挂名的化工、材料系教授（Mukherjee、Bates、Segalman）保留，归化学与生物化学系。
- 物理系各方向子网直接用物理系官网给每位教授打的研究方向标签；化学与数学的方向子网按 OpenAlex 主要子领域划分。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。Google（Martinis、Devoret 的量子 AI 合作）、Microsoft（Station Q：Nayak、Wang 等）都在其中。
- **教授创办 / 发明技术的公司**：`data/manual/startups.csv`，每条附公开来源：Qolab（Martinis，联合创办）、Quantum Circuits Inc.（Devoret，联合创办）、SP2 Quantum（Young）、Nutromics（Plaxco）、Spero Renewables（Abu-Omar）、Olaplex（Hawker，技术发明人）。后四条来自 UCSB 技术与产业联盟（TIA）创业公司数据库的 "Inventor/Founder" 一栏，那一栏不区分创办人和发明人，`role` 列如实标注。这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/roster_part*.txt ──► scripts/roster_ucsb.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                          ▼
     scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_ucsb.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：https://www.math.ucsb.edu/people 、https://www.physics.ucsb.edu/people/faculty 、https://www.chem.ucsb.edu/people 。ucsb.edu 拒绝云端自动抓取，名单是在浏览器里读出后存成 `data/raw/roster/roster_part*.txt`。
- **作者匹配**：OpenAlex 作者检索（限定 UCSB / KITP），按姓名、研究领域、当前机构打分。4 位做了人工指定（`scripts/openalex_fetch.py` 的 `OVERRIDE`）：Xu Yang、Yang Yang、Tom Pettus 的自动结果是同名的其他人；Zheng Liu 在 OpenAlex 里的论文大多被并进了一个同名大档案，只能取到 1 篇，网络里他的分量明显偏小。
- **高能实验**：Campagnari、Incandela、Richman、Stuart 等人的 CMS 论文数以千计、作者上千，>100 作者的论文只记为"大型合作"浅色边，作者列表 >60 人的论文不展开作者。
- 主题、子领域、领域均为 OpenAlex 自动分类，可能有误；"研究相似"是统计意义上的相近，不代表真实合作。
