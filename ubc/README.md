# 不列颠哥伦比亚大学（UBC）数学 · 物理 · 化学 研究网络

把 UBC 两个校区数学、物理（与天文）、化学教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 28 张专题子网。温哥华校区：数学系、物理与天文系、化学系；奥卡纳根（Kelowna）校区：数学、物理与统计系里的数学和物理教授，以及化学系。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/) 等，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：230 位在职教授。温哥华：数学 77、物理与天文 65、化学 53；奥卡纳根：数学 11、物理 9、化学 17。Sarah Burke（物理与天文 / 化学）、Ido Levin（数学 / 化学）两系跨聘，按一人计。
- OpenAlex 匹配 218 个作者档案，约 2.7 万篇论文（27,207 篇，不含勘误、撤稿、数据集等）。未匹配的 12 位多为教学序列讲师、刚入职或 OpenAlex 里没有可靠档案的老师（Michael Hormel、Rose Viande、Simin Bagheri Najmi、Amali Jambuge、Anka Lekhi、Laura Stirchak、Jay Wickenden、Edward Butz、Sylvie Desjardins、Yas Yamin、Robert Godin、Summer Li）。
- Stewart Blusson 量子物质研究所（QMI）：官网 Investigators 名单中 20 位属于这三个系的教授，单独成网（`data/manual/qmi_investigators.csv`）。
- TRIUMF（加拿大国家粒子加速器实验室，OpenAlex 机构 I1304378839）：按教授本人在论文上的署名统计联署篇数，≥5 篇的 8 位单独成网。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2684 | 7389 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| **合作网** | 173 | 261 | 只看教授之间真实合写的论文（作者少于 100 人的论文为深色边，≥100 作者的大型合作论文为浅色边）。 |
| **研究相似网** | 209 | 584 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| **交叉学科网** | 330 | 864 | 只保留跨系（数学×物理与天文×化学，两个校区合计）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| **数学系子网** | 172 | 571 | 数学系教授（温哥华 + 奥卡纳根两个校区）、他们共同的研究主题与内部合作/相似关系。 |
| **物理与天文系子网** | 178 | 703 | 物理与天文系教授（温哥华 + 奥卡纳根两个校区）、他们共同的研究主题与内部合作/相似关系。 |
| **化学系子网** | 224 | 741 | 化学系教授（温哥华 + 奥卡纳根两个校区）、他们共同的研究主题与内部合作/相似关系。 |
| **温哥华校区子网** | 512 | 1954 | 温哥华校区数学、物理与天文、化学三系教授，他们共同的研究主题与合作/相似关系。 |
| **奥卡纳根校区子网** | 65 | 104 | 奥卡纳根校区数学、物理与天文、化学三系教授，他们共同的研究主题与合作/相似关系。 |
| **方向子网：数学：代数 · 代数几何 · 数论 · 拓扑** | 32 | 128 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Algebra and Algebraic Geometry / Number Theory / Topology / number theory」等的数学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：数学：调和分析 · 偏微分方程 · 微分几何 · 数学物理** | 37 | 85 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Harmonic Analysis / Partial Differential Equations / Differential Geometry / Mathematical Physics」等的数学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：数学：概率 · 离散数学 · 组合** | 22 | 52 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Probability / Discrete Mathematics / Combinatori / graph theory」等的数学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：数学：数学生物 · 非线性动力学与应用偏微分方程** | 39 | 71 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Mathematical Biology / Nonlinear Dynamics / ecology」等的数学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：数学：流体 · 科学计算 · 信息数学与优化** | 50 | 113 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Fluids / Scientific Computing / Mathematics of Information / optimization」等的数学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：天文 · 天体物理 · 宇宙学** | 29 | 117 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Astronomy & Astrophysics / Astrophysics / cosmology」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：凝聚态 · 量子材料** | 52 | 196 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Condensed Matter / superconductor」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：原子分子光学 · 量子信息** | 25 | 55 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Atomic, Molecular & Optical / Quantum Information」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：粒子与核物理** | 28 | 101 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Particle & Nuclear」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：理论物理 · 引力** | 54 | 190 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Theoretical Physics / General relativity」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：物理：应用物理 · 生物物理 · 医学物理** | 56 | 111 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Applied Physics / Biophysics / Medical」等的物理与天文系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：化学：有机 · 合成 · 催化** | 95 | 297 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Organic Chemistry / Chemical Synthesis / Catalytic Processes / catalysis」等的化学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：化学：无机 · 材料与高分子 · 界面与表面** | 88 | 227 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Inorganic Chemistry / Materials & Polymer / Interfacial and Surface / Main-group」等的化学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：化学：物理与理论化学 · 化学物理 · 分子光谱** | 86 | 210 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Physical & Theoretical / Chemical Physics / Molecular Spectroscopy / Computational」等的化学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：化学：生物与药物化学 · 分析 · 环境 · 核化学** | 70 | 156 | 院系官网列出的研究方向（温哥华：研究领域页面；奥卡纳根：个人主页研究兴趣）含「Biological & Medicinal / Analytical Chemistry / Environmental Chemistry / Nuclear and Radiochemistry」等的化学系教授，他们的共同主题与合作/相似关系。 |
| **方向子网：量子材料（Blusson 量子物质研究所 QMI 研究员）** | 66 | 210 | Stewart Blusson 量子物质研究所（QMI）官网 Investigators 名单中、属于物理与天文系和化学系的教授（data/manual/qmi_investigators.csv）。 |
| **方向子网：粒子 · 核 · 加速器（与 TRIUMF 联署）** | 32 | 65 | 至少 5 篇论文同时署名 TRIUMF（加拿大国家粒子加速器实验室，位于温哥华校区）的教授（OpenAlex 作者机构）。 |
| **研究主题地图** | 286 | 1169 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| **研究机构网** | 416 | 1197 | 教授与校外研究机构、国家实验室、医院和资助机构的联系（OpenAlex 机构类型 nonprofit / facility / government / healthcare）：同一机构与该教授合写 ≥3 篇、且至少连到 2 位教授才显示；另含教授之间的合写关系。 |
| **创新创业网** | 287 | 400 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司，以及公开资料称为其实验室衍生的公司（逐条附来源与原文摘录，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，页面上可切换"按院系 / 按校区 / 按研究社群"着色，也可以按院系、校区筛选。

## 范围说明

- **温哥华数学系**：系 Directory 的 Faculty 分组，去掉标为 Associate Member 的 9 位（他们的正式聘任在计算机、地球海洋大气、机械工程、细胞生理等其他系，或在奥卡纳根校区）。教学序列（Lecturer、Professor of Teaching）保留。
- **温哥华物理与天文系**：Researchers & Instructors 页的 Faculty 表，去掉荣誉教授 Sun Kwok；Douglas Scott 在表里出现两次（同一电话、两个档案页），按一人计。Adjunct、Associate Member、博士后、荣休不纳入。
- **温哥华化学系**：Research & Teaching Faculty 页的 Research Faculty 与 Teaching Faculty 两组；Sessional、Emeritus、Adjunct/Affiliate/Associate 不纳入。
- **奥卡纳根**：数学、物理与统计系（原 CMPS 拆分后的新系）目录里的在职教师，只取数学和物理方向；统计 / 数据科学教师（Jeff Andrews、W. John Braun、Xiaoping Shi、John R.J. Thompson、Irene Vrbik、Lengyi Han）按统一口径不纳入。化学系取在职教师（含 3 位休假中的教授）。两系的荣休、兼职（adjunct）、荣誉合作者、Sessional 讲师和博士后都不纳入。
- **方向子网**：温哥华三系按院系官网的研究领域页面（数学系 research-topics 各页的 Faculty 表、物理系 research-areas 各页列出的教师、化学系 faculty 目录的研究方向筛选），奥卡纳根按目录个人页的研究兴趣（`data/raw/roster/okanagan.txt` 里是简写）。一个人可以出现在多个方向子网。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办 / 实验室衍生的公司**：`data/manual/startups.csv`，每条附公开来源与原文摘录：Telescope Innovations（Jason Hein，创办人兼 CTO）、Boreal Genomics（Andre Marziali，2007 年创办）、TIR Systems（Lorne Whitehead，创办）、Miru Smart Technologies、Sora Fuel、CURA、Carbonyx（Curtis Berlinguette，创办 / 联合创办）、ScopeSys（源自 Sabrina Leslie 的研究，标为实验室衍生）。只收公开资料明确写着 founder / co-founder 或"源自某教授研究"的条目。Whitehead 主页说他还"帮助创办"了另外六家公司（Brightside、CLEARink 等），措辞不是创办人，未收录。这份名单**并不完整**，欢迎按同样格式补充。
- **研究机构网**：OpenAlex 机构类型为 nonprofit / facility / government / healthcare 的校外单位（TRIUMF、国家实验室、医院、资助机构等）。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/*.txt ──► scripts/roster_ubc.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/{startups,qmi_investigators}.csv ─┐
                                               ▼
                     scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_ubc.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py      # 自动以 PYTHONHASHSEED=0 重新启动，同样的数据重建结果完全一致
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：https://www.math.ubc.ca/about-our-department/directory 、https://phas.ubc.ca/researchers 、https://www.chem.ubc.ca/faculty 、https://mps.ok.ubc.ca/about/contact/ 、https://chemistry.ok.ubc.ca/about/contact/ ，QMI 名单 https://qmi.ubc.ca/people/investigators/ 。ubc.ca 拒绝云端直接抓取，名单是在浏览器里读出后存成 `data/raw/roster/*.txt`。
- **作者匹配**：OpenAlex 作者检索（限定 UBC 温哥华 I141945490、UBC 奥卡纳根 I4405260628、TRIUMF），按姓名、研究领域、当前机构打分。OpenAlex 常把一个人拆成多个档案，或把同名的人并进一个档案，以下做了人工处理（`scripts/openalex_fetch.py` 的 `OVERRIDE` / `NONE` / `WORK_FILTER`）：Scott Oser、Xianfu (Shawn) Wang、Liam Watson、Yue-Xian Li、Keqin Liu、Rodolfo Brandão 合并了碎片档案；Hongbin Li 的档案混入了多位同名学者，只保留署名 UBC 的论文；John Hopkinson 的档案混入了 19 世纪的同名工程师和医生，只保留 1995 年后的物理论文；Jingyi Chen 只取署名 UBC 的小档案（大档案混了他人），论文数偏少；Robert Godin、Edward Butz、Michael Hormel、Sylvie Desjardins 的候选档案无法确认是本人，未匹配。
- **大型合作**：OpenAlex 每篇论文最多列 100 位作者，所以 ≥100 作者的论文（ATLAS、Belle II、Planck、LIGO 等）一律记为"大型合作"浅色边，不计入合写强度，也不计入产业合写和校外研究机构联系（否则对撞机、宇宙学合作里的上百家单位都会算成某位教授的合作方）。
- **论文类型**：勘误（erratum）、撤稿声明、目录页（paratext）、同行评审意见、补充材料和数据集（dataset）不计入。UBC 的 1,461 条数据集记录里有 1,195 条是剑桥晶体数据中心（CCDC）的晶体结构存档，MacLachlan、Schafer 等化学教授每人上百条，计入会虚增论文数。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。主题、子领域、领域均为自动分类，可能有误；"研究相似"是统计意义上的相近，不代表真实合作。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
