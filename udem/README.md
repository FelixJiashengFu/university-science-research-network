# 蒙特利尔大学（Université de Montréal）数学 · 物理 · 化学 研究网络

把蒙特利尔大学数学与统计系（DMS）、物理系、化学系教授的研究领域、论文、合作关系、校外研究机构与产业合作编织成一张主网，并拆出专题子网。姊妹项目：[UofT](../uoft/)、[Stanford](../stanford/)（同一套方法）。

**在线浏览**：GitHub Pages 发布在 `/udem/`。本地预览：

```bash
cd site && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 规模

- 名单：96 位教授（数学与统计 34、物理 28、化学 34）
- OpenAlex 全部匹配（96/96），约 1.75 万篇论文

共 22 张网络，清单（节点数、边数）见 `site/data/index.json`，页面左上角可切换。包括：主网（教授 · 主题 · 学科层级 · 论文 · 企业 · 全部关系）、合作网、研究相似网、交叉学科网、三个系子网、11 张方向子网（数学 3、物理 4、化学 4）、研究主题地图、**研究机构网**（与 Mila、CRM、医院、国家实验室等校外机构的合写）、**创新创业网**。

## 名单来源（重要）

| 系 | 来源 | 读取日期 |
|---|---|---|
| 数学与统计 | https://dms.umontreal.ca/fr/repertoire-departement/professeurs（含统计、精算、机器学习方向） | 2026-11-09 |
| 化学 | https://chimie.umontreal.ca/fr/repertoire-departement/professeurs | 2026-11-09 |
| 物理 | **院系官网无法读取**（浏览器报证书错误，robots.txt 拒绝抓取），`data/manual/physics_faculty.csv` 按公开资料整理 28 位教授，并逐一用 OpenAlex 核对（当前单位为 UdeM、近年有论文）。**未经院系官网核对**，可能漏掉新入职教授或含已荣休者。 | 2026-11-10 |

UdeM 院系网站拒绝自动抓取，数学、化学名单在浏览器里读取后存为 `data/raw/roster/*.psv`（姓名 | 职级 | 研究专长 | 主页标识）。只收"Professeurs"页面（不含 associés / honoraires / 讲师）。

## 创新创业板块

- **产业合写**：论文作者机构中 OpenAlex 类型为 `company` 的单位，按教授统计合写篇数，见 `data/processed/industry_links.csv`。创新创业网保留 ≥2 篇，主网保留 ≥3 篇。
- **教授创办 / 实验室衍生的公司**：`data/manual/startups.csv`，每条附来源与原文摘录。role = `co-founder` 的是来源明确写着联合创办（Pierre Thibault · Epitopea）；`lab spin-off` 的是来源只说"出自某教授实验室"，没有写明创办人（Affinité Instruments、Anasens），页面上用不同颜色区分。名单**并不完整**，欢迎按同样格式补充。
- **研究机构网**：OpenAlex 类型为 nonprofit / facility / government / healthcare 的合写机构（≥3 篇且连到 ≥2 位教授）。
- 专利暂未纳入。

## 数据流程与重跑

```bash
pip install networkx scipy numpy
export OPENALEX_API_KEY=...        # 切勿提交到仓库
python3 scripts/roster_udem.py     # data/raw/roster/*.psv + data/manual/physics_faculty.csv → data/processed/roster.csv
python3 scripts/openalex_fetch.py --works
python3 scripts/build_graph.py     # → site/data/*.json, data/processed/*.csv
```

## 方法与局限

- **作者匹配**：OpenAlex 作者检索（限定 Université de Montréal），按姓名、研究领域、当前机构打分；三位自动匹配失败的（Octavian Cornea、Robert G. Owens、Madison Mooney）在 `scripts/openalex_fetch.py` 的 OVERRIDE 中手工指定。Dirk Douwes-Schultz 在 OpenAlex 中尚无 UdeM 单位（新入职），走不限机构的严格匹配。
- **大型合作**：超过 100 位作者的论文（ATLAS、JWST 等）记为"大型合作"浅色边，不计入合写强度。Jean-François Arguin 的论文多为 ATLAS 合作论文。
- **研究主题**：OpenAlex Topic 体系，每篇论文取 primary topic；研究相似 = 主题分布的 TF-IDF 余弦相似度。
- **方向子网**：数学、化学按官网列出的研究专长关键词分组；物理按整理名单中的研究方向分组。
- 数据均来自公开来源；OpenAlex 数据为 CC0。
