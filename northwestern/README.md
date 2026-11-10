# 西北大学 数学 · 物理 · 化学 研究网络

把西北大学（Northwestern University）Weinberg 文理学院数学系、物理与天文系、化学系，以及 McCormick 工程学院工程科学与应用数学系（ESAM）教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 19 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/)，方法相同。

本地预览：`cd site && python3 -m http.server 8000`，打开 http://localhost:8000 。

## 规模

- 名单：143 位在职教授（数学 33、物理与天文 46、化学 54、ESAM 10）。化学系名单里的联合/礼节性聘任（Dravid、Haile、Hersam、Luijten、Rogers、Rosenzweig、Shilatifard、Hao Zhang）保留；在 ESAM 有礼节性聘任的 Motter、Tchekhovskoy、Kovács、Gingrich、Luijten 按一人计，页面显示"跨聘"。
- OpenAlex 匹配 135 个作者档案，约 3.8 万篇论文（不含勘误、撤稿、同行评审记录与数据集条目）。未匹配的多为教学序列教授或 OpenAlex 里没有可靠档案的老师（Katie Gesmundo、Carine Nemr、Aaron Peterson、Derek Nelson、Tianlong Zu），以及只从邮箱得知姓氏、无法唯一确定的 3 位数学系教学序列老师。
- 国家实验室联署：OpenAlex 按教授本人在论文上的署名统计 Argonne（I1282105669）与 Fermilab（I1314696892）篇数；Argonne ≥5 篇的教授单独成网，Fermilab 不足 4 人未成网，但在教授详情里标注。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 4302 | 13779 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 104 | 416 | 只看教授之间真实合写的论文（作者少于 100 人的论文为深色边，大型合作论文为浅色边）。 |
| 研究相似网 | 127 | 384 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 305 | 1245 | 只保留跨系（数学×工程科学与应用数学×物理与天文×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学系子网 | 54 | 169 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 工程科学与应用数学系子网 | 41 | 82 | 工程科学与应用数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理与天文系子网 | 143 | 551 | 物理与天文系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学系子网 | 360 | 1856 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：与阿贡国家实验室（Argonne）联署 | 243 | 1069 | 至少 5 篇论文同时署名 Argonne National Laboratory 的教授（OpenAlex 作者机构）。 |
| 方向子网：天体物理与宇宙学（CIERA） | 29 | 149 | 主要研究子领域（OpenAlex）为 Astronomy and Astrophysics 的教授，大多属于 CIERA 跨学科天体物理研究中心。 |
| 方向子网：粒子物理 · 核物理 · 精密测量 | 22 | 70 | 物理与天文系中，主要子领域为 Nuclear and High Energy Physics 的教授（含 LHC/CMS、中微子、暗物质与精密测量）。 |
| 方向子网：凝聚态 · 原子分子光学 · 量子 | 132 | 363 | 物理与天文、化学两系中，主要子领域为凝聚态、原子分子光学或电子/光学/磁性材料的教授。 |
| 方向子网：复杂系统 · 网络 · 生物物理 | 63 | 134 | 工程科学与应用数学系全体，加上主要子领域含统计与非线性物理、生物物理的教授（对应 NICO 西北复杂系统研究所）。 |
| 方向子网：材料化学 · 纳米科学（IIN） | 133 | 395 | 化学系中，主要子领域为材料化学、聚合物、生物材料、纳米与电子材料的教授（与国际纳米技术研究所 IIN 高度重合）。 |
| 方向子网：有机化学 · 化学生物学 · 生物化学 | 141 | 393 | 化学系中，主要子领域为有机化学、生物化学、分子/细胞生物学、药物发现或光谱的教授。 |
| 方向子网：物理化学 · 无机 · 催化与能源 | 107 | 318 | 化学系中，主要子领域为物理与理论化学、无机、分析、电化学、催化或能源的教授。 |
| 方向子网：数学：代数 · 数论 · 几何 · 拓扑 · 数学物理 | 29 | 89 | 数学系官网研究方向含 algebra / number theory / geometry / topology / Lie / representation / mathematical physics 的教授。 |
| 方向子网：数学：分析 · 概率 · 动力系统 · 偏微分方程 | 24 | 47 | 数学系官网研究方向含 analysis / probability / dynamical / ergodic / PDE / statistics 的教授。 |
| 研究主题地图 | 297 | 2132 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| 创新创业网 | 302 | 677 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，30 条，每条附公开来源与原文摘录（Mirkin、Kelley、Sargent、Mrksich、Meade、Rogers、Hersam、Dichtel、Farha、Gianneschi、Silverman、Kanatzidis 等）。只收明确写着 founder / co-founder 的条目；Stupp（Amphix Bio）、Hupp（NuMat）、Marks（Polyera）等只查到"发明人/顾问"表述，未收。名单**并不完整**。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/*.txt ──► scripts/roster_northwestern.py ──► data/processed/roster.csv
OpenAlex 作者列表/检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                          ▼
         scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_northwestern.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：physics.northwestern.edu core-faculty 与 instructional-faculty、chemistry.northwestern.edu people/faculty（core faculty）、mccormick.northwestern.edu applied-math people/faculty、math.northwestern.edu people/faculty。northwestern.edu 拒绝云端自动抓取，物理、化学名单在浏览器里读出；数学系页面浏览器打不开，只拿到文字版（职称、方向、邮箱，没有姓名），**姓名按邮箱补全，未在院系官网核对**。不含荣休、兼职（adjunct）、博士后，数学系 Boas 助理教授（博士后性质）与讲师不含。ESAM 只收本系教授与上述数理化教授，其他院系的礼节性聘任不含。Pieter van Dokkum 2027 年 1 月到任，已列入并标注。
- **作者匹配**：先用一次列表调用取回最近机构为西北大学、论文 ≥10 篇的全部 OpenAlex 作者（约 1.3 万），按姓名、研究领域、当前机构本地打分，未命中再检索（比逐个检索省约九成调用）。7 位教授做了人工指定（见 `scripts/openalex_fetch.py` 的 `OVERRIDE`：同名错配或档案被拆分，第一个 id 为主档案，其余碎片的论文合并进来）。
- **大型合作**：OpenAlex 每篇论文最多返回 100 位作者，因此作者数 ≥100 的论文都记为"大型合作"浅色边，不计入合写强度（CMS 等实验合作论文不会被当成普通合写）。
- **数据集条目**：OpenAlex 把 PDB、PNNL 数据仓库等的数据集也算作作品，个别生化教授名下有数百条，会把论文数和企业合写数撑大（例如被误记为与 Genentech 合写 921 篇），因此 `type = dataset` 一律剔除。
- **研究主题**：OpenAlex Topic 体系（Topic → Subfield → Field → Domain），每篇论文取 primary topic。
- **方向子网**：数学按院系官网标注的研究方向；物理、化学、ESAM 官网没有逐人方向标注，按每位教授论文的主要 OpenAlex 子领域分组；CIERA、NICO、IIN 只是对应关系的说明，不是这些研究所的官方名单。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
