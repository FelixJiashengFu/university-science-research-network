# 北美量子化学与计算化学产业报告（na-companies）

美国与加拿大的量子化学 / 计算化学企业分析：113 家精选企业（软件商、量子计算、AI/物理驱动药物与材料发现、药企/化工/科技巨头的计算化学部门），外加 OpenAlex 论文语料中出现的全部约 785 家北美企业。页面含 29 张统计图、交易与预测表、可搜索的企业名录。

## 文件
- `site/index.html`：报告页面（引用 `../assets/site.css` 与 `../assets/nav.js`，图表为内联 SVG，无外部 JS 依赖）
- `data/manual/companies.csv`：精选企业名录。`funding_conf`：A 财报/官方，B 媒体/数据库，C 本报告估计
- `data/manual/market.json`：交易、上市公司收入、第三方预测（带来源 URL）以及本报告情景假设
- `data/processed/`：`corpus_companies.csv`（全部企业论文足迹）、`company_university_links.csv`、`professor_company_links.csv`（链接到 na-quantum-chem-map 的教授）、`summary.json`
- `scripts/fetch_openalex_companies.py`：拉取有北美企业作者的论文（需环境变量 `OPENALEX_API_KEY`，切勿提交）
- `scripts/build_report.py`：生成全部表格与页面

## 重建
```
export OPENALEX_API_KEY=...            # 仅放环境变量
python3 scripts/fetch_openalex_companies.py   # 约 40 次列表请求，成本 < $0.01
cp ../na-quantum-chem-map/data/processed/professors.csv data/raw/
cp ../na-quantum-chem-map/site/data/basemap.json data/raw/
python3 scripts/build_report.py
```

## 局限
- 精选名录不可能穷尽所有公司；长尾见论文足迹表。
- 私营公司融资额口径不一（是否含政府资金、加元/美元），已用可信度标记。员工数为约数。
- 预测部分严格区分「第三方预测」「公司指引」「本报告估计/情景」，不构成投资建议。
