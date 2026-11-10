# 宾夕法尼亚大学 数学 · 物理 · 化学 研究网络

把宾夕法尼亚大学文理学院（SAS）数学系、物理与天文系、化学系教授的研究领域、论文、合作关系、产业合作与创业活动编织成一张主网，并拆出 19 张专题子网。姊妹项目：[`uoft/`](../uoft/)、[`stanford/`](../stanford/)、[`waterloo/`](../waterloo/) 等，方法相同。

本地预览：在仓库根目录 `python3 -m http.server 8000`，打开 http://localhost:8000/upenn/site/ 。

## 规模

- 名单：105 位在职教授（数学 28、物理与天文 40、化学 37）。Ron Donagi 是数学系教授、物理系兼聘，按一人计。
- OpenAlex 匹配 103 个作者档案，约 2.3 万篇论文（不含 dataset 类条目，如 PNNL 数据仓库的存档记录）。Kai Chen、Yuting Zhou 两位新任助理教授在 OpenAlex 里只有同名的其他人，暂不匹配。

## 网络一览

| 网络 | 节点 | 边 | 内容 |
|---|---|---|---|
| **主网：教授 · 主题 · 学科 · 论文 · 全部关系** | 2069 | 6127 | 所有已匹配教授；每人主要研究主题及被多人共享的主题；主题→子领域→领域的学科层级；全部网内合作论文与每人被引最多的 5 篇论文；合写 ≥3 篇的企业与教授创办的公司；合写、大型合作、研究相似、产业合作、创办等全部关系。 |
| 合作网 | 86 | 191 | 只看教授之间真实合写的论文（不足 100 作者的论文为深色边，≥100 作者的大型合作论文为浅色边）。 |
| 研究相似网 | 98 | 261 | 按研究主题分布（TF-IDF 余弦相似度）连接每位教授最相近的同行，不要求合写过论文。 |
| 交叉学科网 | 205 | 624 | 只保留跨系（数学×物理与天文×化学）的合作、相似关系，以及被至少两个系的教授共同研究的主题。 |
| 数学系子网 | 63 | 187 | 数学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 物理与天文系子网 | 138 | 500 | 物理与天文系教授、他们共同的研究主题与内部合作/相似关系。 |
| 化学系子网 | 223 | 739 | 化学系教授、他们共同的研究主题与内部合作/相似关系。 |
| 方向子网：数学物理 · 弦论 · 高能理论 | 21 | 59 | 数学系与物理系之间最强的桥：研究方向含 string theory / mathematical physics 的数学家，加上物理系高能理论组。 |
| 方向子网：天体物理与宇宙学（含粒子宇宙学中心） | 29 | 138 | 物理与天文系天体物理与宇宙学组，包括宾大粒子宇宙学中心（Penn Center for Particle Cosmology）的成员。 |
| 方向子网：高能实验（ATLAS · 中微子） | 13 | 42 | 物理与天文系高能实验组：ATLAS 实验与中微子实验。他们的大型合作论文（≥100 作者）只记为浅色的大型合作边。 |
| 方向子网：凝聚态 · 光子学 · 纳米 | 91 | 290 | 物理系凝聚态理论与实验组，加上化学系标注 Nanoscale Science 的教授。 |
| 方向子网：软物质与生物物理（软物质与生命物质中心） | 96 | 256 | 物理系软物质与生物物理组（Center for Soft and Living Matter 一带），加上化学系标注 Biophysical Chemistry 的教授。 |
| 方向子网：化学生物学 · 生物化学 | 81 | 211 | 化学系官网 Focus Area 含 Chemical Biology / Biological 的教授。 |
| 方向子网：有机合成 · 催化 · 无机化学 | 156 | 436 | 化学系官网 Focus Area 含 Organic / Chemical Catalysis / Inorganic 的教授。 |
| 方向子网：物理化学 · 理论与模拟 · 光谱 | 74 | 167 | 化学系官网 Focus Area 含 Chemical Physics and Physical Chemistry / Theory Simulation and Modeling / Laser Chemistry and Spectroscopy 的教授。 |
| 方向子网：材料化学 · 能源 · 纳米 | 96 | 254 | 化学系官网 Focus Area 含 Materials Chemistry / Energy Research / Nanoscale Science 的教授（与 LRSM、Vagelos 能源研究所相关）。 |
| 方向子网：数学：代数 · 数论 · 代数几何 · 拓扑 | 48 | 149 | 数学系官网研究方向含 algebra / number theory / Galois / geometry / topology / K-theory / combinatorics 的教授。 |
| 方向子网：数学：分析 · 偏微分方程 · 概率 · 应用数学 | 33 | 65 | 数学系官网研究方向含 analysis / PDE / probability / applied / differential geometry 的教授。 |
| 研究主题地图 | 237 | 1143 | 研究主题之间的关联：两个主题被同一位教授（≥2 篇论文）研究时相连，按学科领域着色。 |
| 创新创业网 | 152 | 276 | 教授与企业的联系：① 与企业作者合写过 ≥2 篇论文的公司（OpenAlex 机构类型 = company）；② 教授创办/联合创办的公司（逐条附公开来源，见 data/manual/startups.csv）；③ 教授之间的合写关系。 |

每张网都用 Louvain 算法划分研究社群，可在页面上切换"按研究社群"着色。

## 范围说明

- **数学**：数学系 Standing Faculty 页的在职教授（荣休教授不计）。页面上的"关联教师"（统计系、计算机系、物理系、生物系、机械系老师）和讲师、博士后不纳入；他们在本系的身份已由各自的系代表（例如 Cvetič、Heckman、Kamien 在物理系）。
- **物理与天文**：Standing Faculty 页上的教授。主聘在本范围外的兼聘教师（Bassett 生物工程、Engheta 电子系统工程、Janmey 生理学、Karp 放射学）和兼职教授 Stephens 不纳入。
- **化学**：化学系 Faculty 页上的教授，含在化学系挂名的生物化学与生物物理系、电子系统工程系等老师（de la Fuente、Kathy Fange Liu、Vinogradov、Kagan）以及 Professor of Practice Huryn；讲师和兼职教授（Marmorstein）不纳入。
- **研究方向**：数学系、化学系用官网写明的研究方向 / Focus Area。物理系官网没有逐人标方向，`physics_standing.txt` 里的方向是按系里的研究组（天体物理与宇宙学、高能理论、高能实验、凝聚态理论/实验、软物质、生物物理）结合公开资料和 OpenAlex 主题标注的，属于整理结果，不是官网原文。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数（`data/processed/industry_links.csv`）。创新创业网保留 ≥2 篇的联系，主网保留 ≥3 篇的。
- **教授创办的公司**：`data/manual/startups.csv`，每条附公开来源与原文摘录：Graphene Frontiers（A.T. Charlie Johnson，2011）、Peptaris（César de la Fuente）。只收明确写着 founder / co-founder 的条目，这份名单**并不完整**，欢迎按同样格式补充。
- **专利**：暂未纳入。

## 数据流程

```
院系官网教师名单（浏览器读取）──► data/raw/roster/*.txt ──► scripts/roster_upenn.py ──► data/processed/roster.csv
OpenAlex 作者候选池 + 检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv, data/raw/openalex/works/*.jsonl
data/manual/startups.csv ─┐
                           ▼
          scripts/build_graph.py ──► site/data/*.json（含预计算布局）, data/processed/*.csv
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_upenn.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限

- **名单来源**（2026-11-10 读取）：math.upenn.edu/people/standing-faculty、physics.upenn.edu/people/standing-faculty、chem.upenn.edu/people/faculty。upenn.edu 拒绝云端自动抓取（robots.txt 与代理），名单是在浏览器里读出后存成 `data/raw/roster/*.txt`。
- **作者匹配**：先用一次列表查询取出"最近机构为宾大、论文 >15 篇、主题含数学/物理/化学"的 2029 个 OpenAlex 作者作为候选池，在本地按姓名、研究领域打分匹配；池里没有的再按姓名检索。OpenAlex 常把一个人拆成多个档案或匹配到同名者，5 位教授做了人工指定（`scripts/openalex_fetch.py` 的 `OVERRIDE`：Christianson、Aimin Liu、Hartmann、Tong、Jain；第一个 id 为主档案，其余碎片的论文合并进来）。
- **大型合作**：OpenAlex 每篇论文最多返回 100 个作者，所以作者数 ≥100 的论文（ATLAS 等）一律算"大型合作"，只连浅色边，不计入合写网，避免高能实验组把网络撑成一团。这类论文也不计入产业合写：署名里出现某家公司（如 SDSS 论文里的 Microsoft）不等于教授和这家公司有合作项目。
- **剔除的条目**：OpenAlex 里类型为 dataset（如美国能源部 PNNL 数据仓库的 EMSL 项目存档）、erratum、retraction、paratext、peer-review 的条目不算论文。不剔除时，921 条 PNNL 存档记录（每条列满 100 位"作者"，其中有 Christianson 和 Genentech 的人，UCLA 的 Eisenberg 名下也是同一批）会被算成 Christianson 与 Genentech 合写 921 篇。
- **研究主题**：每篇论文的 OpenAlex primary topic；相似度为主题分布的 TF-IDF 余弦。
