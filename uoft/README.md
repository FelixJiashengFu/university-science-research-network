# UofT 数学 · 物理 · 化学 研究网络

把多伦多大学三个校区（St. George / Mississauga / Scarborough）数学、物理、化学教授的研究领域、论文与合作关系编织成一张大网，并拆出专题子网。

**在线浏览**：见仓库根目录 README（GitHub Pages 发布在 `/uoft/`）。本地预览：

```bash
cd site && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 网络一览

| 网络 | 内容 |
|---|---|
| **主网** | 全部已匹配教授 + 被 ≥2 位教授共同研究的 OpenAlex 主题 + 每对合作者被引最多的 3 篇合作论文；边包括合写、大型合作、研究相似、教授↔主题、教授↔论文 |
| 合作网 | 只看教授之间真实合写的论文 |
| 研究相似网 | 按研究主题分布（TF‑IDF 余弦相似度）连接每位教授最相近的同行，不要求合写 |
| 交叉学科网 | 只保留跨系（数学×物理×化学）的合作/相似关系，以及被至少两个系共同研究的主题 |
| 数学 / 物理 / 化学 系子网 | 各系三校区教授及其共同主题 |
| 校区子网 | 每个校区内部的关系 |
| 研究主题地图 | 主题之间的关联（同一位教授在两个主题上都有 ≥2 篇论文即相连），按学科领域着色 |

每个子网都用 Louvain 算法划分了研究社群，可在页面上切换"按研究社群"着色。

## 数据流程

```
院系官网教师名单 ──► scripts/roster_*.py ──► data/processed/roster.csv
                                              │
OpenAlex 作者检索 + 论文 ◄── scripts/openalex_fetch.py ──► data/processed/matches.csv
                                              │                data/raw/openalex/works/*.jsonl
                                              ▼
                               scripts/build_graph.py ──► site/data/*.json（含预计算布局）
                                                          data/processed/*.csv（可直接用 Excel/Gephi 打开）
```

重跑：

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # openalex.org 免费申请，切勿提交到仓库
python3 scripts/roster_physics.py
python3 scripts/roster_parse.py
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py
```

## 方法与局限（请务必读）

- **名单来源**：UofT 物理系成员目录（含跨聘到物理系的化学、CITA 成员）、UTM 数学与计算科学系、UTM 化学与物理科学系、UTSC 物理与环境科学系。去除了荣休、兼职讲师、访问学者等。
- **缺口**：St. George 数学系、St. George 化学系的官网有人机验证，UTSC 数学（CMS 系）教师页需要登录，这三份名单目前不完整，见 `data/processed/roster.csv` 的 `source` 列。
- **作者匹配**：用 OpenAlex 作者检索（限定 UofT 机构），按姓名相似度、研究领域、当前机构打分；新入职、OpenAlex 尚未关联 UofT 的教授走不限机构的严格匹配，在 `matches.csv` 的 `match_note` 中标注。OpenAlex 会把同一人拆成多个 ID 或把同名者合并，个别结果可能有误。
- **大型合作**：超过 100 位作者的论文（如 ATLAS、IceCube）单独记为"大型合作"浅色边，不算入合写强度，以免粒子物理把整张网"粘"成一团。
- **研究主题**：使用 OpenAlex 的 Topic 体系（约 4500 个主题，归属 Subfield → Field → Domain），每篇论文取 primary topic。
- 所有数据均来自公开来源；OpenAlex 数据为 CC0。

## 目录

```
scripts/            抓取与构建脚本
data/raw/           原始抓取结果（名单页、OpenAlex 缓存）
data/processed/     名单、匹配表、教授表、合作边、相似边、主题表（CSV）
site/               交互式可视化（sigma.js + graphology，已内置，无需 CDN）
```
