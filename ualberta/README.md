# 阿尔伯塔大学 数学 · 物理 · 化学 研究网络

把阿尔伯塔大学（University of Alberta，埃德蒙顿）理学院数学与统计科学系（数学方向）、物理系、化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 22 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`waterloo/`](../waterloo/)、[`udem/`](../udem/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：120 位在职教授（数学 39、物理 47、化学 34）。
- OpenAlex 匹配 119 个作者档案，约 2.25 万篇论文。未匹配的 1 位是 Michelle Michelle（OpenAlex 里同名记录都是其他人）。
- 物理系在阿尔伯塔包含地球物理与空间物理，因此单独做了"地球物理 · 空间物理 · 等离子体"子网。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 4115 | 13117 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 93 | 169 | 只看教授之间真实合写的论文（≤100 作者的论文为深色边，大型合作论文为浅色边）。 |
| 研究相似网 | 111 | 269 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 171 | 354 | 只保留跨系（数学×物理×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学系子网 | 78 | 220 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理系子网 | 130 | 456 | 物理系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学系子网 | 158 | 513 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：纳米技术（与国家纳米技术研究所联署） | 36 | 80 | 至少 3 篇论文同时署名 National Institute for Nanotechnology（NRC 纳米技术研究中心，位于校内）的教授，横跨物理与化学。 |
| 方向子网：糖科学（与 Alberta Glycomics Centre 联署） | 18 | 45 | 至少 3 篇论文同时署名 Alberta Glycomics Centre 的教授，或化学系官网标注糖化学/糖组学方向的教授。 |
| 方向子网：数学物理 · 引力 · 量子场论（数学 × 物理） | 28 | 55 | 数学系与物理系中，官网研究方向含 mathematical physics / string / relativity / gravity / quantum field / conformal 的教授。 |
| 方向子网：粒子物理 · 中微子 · 暗物质 | 23 | 88 | 物理系官网研究方向含 particle / neutrino / dark matter / gauge 的教授（含 ATLAS、MoEDAL、SNO+、DEAP、IceCube 等大型合作）。 |
| 方向子网：天体物理 · 宇宙学 · 引力 | 29 | 100 | 物理系官网研究方向含 astro / cosmology / neutron star / black hole / stellar / galaxy / gravity 的教授。 |
| 方向子网：凝聚态 · 量子物质 · 纳米与生物物理 | 39 | 110 | 物理系官网研究方向含 condensed matter / superconductivity / quantum gases / nano / optomechanics / biophysics 的教授。 |
| 方向子网：地球物理 · 空间物理 · 等离子体 | 44 | 127 | 物理系官网研究方向含 geophysics / seismic / mantle / tectonics / planetary / space / plasma / magnetosphere 的教授（阿尔伯塔物理系包含地球物理与空间物理）。 |
| 方向子网：有机化学 · 化学生物学 | 96 | 313 | 化学系官网研究方向为有机合成、天然产物、化学生物学、糖化学的教授。 |
| 方向子网：分析化学 · 质谱 · 环境与大气 | 22 | 34 | 化学系官网研究方向为分析化学、质谱、电化学分析、环境与大气化学的教授。 |
| 方向子网：物理化学 · 理论计算 · 无机与材料 | 94 | 269 | 化学系官网研究方向为物理化学、理论与计算化学、无机、催化与材料的教授。 |
| 方向子网：数学：代数 · 数论 · 代数几何 | 17 | 59 | 数学系官网研究方向含 algebra / number theory / algebraic geometry / Galois / Lie / representation / quadratic forms 的教授。 |
| 方向子网：数学：分析 · 几何分析 · 最优传输 · 逼近 | 17 | 32 | 数学系官网研究方向含 analysis / functional / operator / convex geometry / harmonic / approximation / wavelet / optimal transport 的教授。 |
| 方向子网：数学：微分方程 · 动力系统 · 数学生物 · 流体 | 23 | 49 | 数学系官网研究方向含 differential equations / dynamical systems / mathematical biology / epidemiology / fluid 的教授。 |
| 方向子网：数学：概率 · 随机分析 · 数理金融 | 18 | 42 | 数学系官网研究方向含 probability / stochastic / mathematical finance / filtering 的教授。 |
| 研究主题地图 | 210 | 812 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| 创新创业网 | 183 | 268 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：阿尔伯塔的数学与统计在同一个系。这里只取数学方向（含概率与数理金融）的教授；官网研究方向只写统计的教授（如统计推断、函数型数据、神经影像统计）不纳入，与 UofT 只取数学系一致。讲师（Lecturer）、Faculty Service Officer 和行政人员不纳入。Michael Kouritzin 与 Gerda de Vries 只出现在系里的研究方向页、没出现在读到的教师表里，仍列入并在页面上标注。
- **物理**：物理系教师表中的全部教授，包括地球物理与空间物理方向；Andy Kale 是 Faculty Service Officer（CARISMA 项目经理），不纳入。Yangyang Shen 2026 年到任，已列入并标注。
- **化学**：化学系 Faculty 表中的全部教授。兼职（adjunct）、荣休、教学人员（teaching staff）列在单独页面，不纳入。
- **研究机构**：国家纳米技术研究所（National Institute for Nanotechnology，NRC 纳米技术研究中心，位于校内，OpenAlex I40752897）和 Alberta Glycomics Centre（I4210159304）在 OpenAlex 里有独立机构记录，按教授本人在论文上的署名统计联署篇数，各做一张子网。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。合写最多的是 Atomic Energy of Canada、DSM、Amgen、IBM、Canadian Light Source 等。
- **教授创办的公司**：`data/manual/startups.csv`，每条附公开来源与原文摘录：Applied Quantum Materials（Veinot，联合创始人）、48Hour Discovery（Derda，创始人）。只收来源里明确写着 founder / co-founder 的条目：例如 Quantum Silicon 是 Wolkow 团队的校办衍生公司，但读到的来源只写他担任 CTO，没有写"创始人"，因此未收录。这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（网页阅读器读取）──► data/raw/roster/roster_*.txt ──► scripts/roster_ualberta.py ──► data/processed/roster.csv
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                          ▼
           scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_ualberta.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：ualberta.ca 的数学与统计科学系 Academic Staff 页与 Research Areas 页、物理系 Faculty 页、化学系 Faculty 页。ualberta.ca 拒绝云端直接抓取，名单经网页阅读器读出；这些页面较长，后半部分（数学 R–Z、物理 Rastgoo 之后、化学 Mar 之后）由阅读器的摘要给出，而不是逐字页面文本，**名字可信，但个别人可能遗漏**。研究方向关键词为对官网描述的简写。
- **作者匹配**：OpenAlex 作者检索（限定 University of Alberta），按姓名、研究领域、当前机构打分。OpenAlex 常把一个人拆成多个档案，10 位教授做了人工指定（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`，第一个 id 为主档案，其余碎片的论文合并进来）。Steven Robertson 指定为粒子物理大型合作档案（BaBar / Belle II 等）。
- **大型合作**：超过 100 位作者的论文（ATLAS、MoEDAL、IceCube、SNO+ 等）单独记为"大型合作"浅色边，不计入合写强度。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- **方向子网**：按院系官网写的研究方向关键词分组；纳米所与糖组学中心子网按论文署名。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
