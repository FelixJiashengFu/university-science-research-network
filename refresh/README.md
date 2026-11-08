# 每月自动更新

`.github/workflows/monthly-refresh.yml` 每月 1–4 日自动重抓 OpenAlex、重建页面并发布，一天跑一部分。每部分只用 OpenAlex 每日 1 美元免费额度的一小部分，额度在 UTC 0 点重置：

| 日期（UTC 05:00，多伦多冬令时 0:00） | 部分 | 内容 |
| --- | --- | --- |
| 1 日 | `maps` | 北美 / 中国量化地图、两个 Top 20、中美对比、UofT、Stanford |
| 2 日 | `schools-1` | MIT、Harvard、Caltech、Berkeley、Princeton、Chicago |
| 3 日 | `schools-2` | Columbia、Yale、Cornell、清华、北大、中科大 |
| 4 日 | `schools-3` | 复旦、上交、浙大、南大、武大、中山 |

MolAstria 在 5 日把新版本复制过去（它的 `atlas-sync.yml`）。

## 第一次使用：放 API key

key 只放在 GitHub 的仓库密钥里，不写进任何文件。

1. 打开仓库 → Settings → Secrets and variables → Actions → New repository secret。
2. Name 填 `OPENALEX_API_KEY`，Secret 粘贴你的 OpenAlex key，保存。
3. 想马上试一次：Actions → Monthly data refresh → Run workflow，part 填 `schools-3` 之类。

## 会自动更新的

论文、被引、h 指数、合作关系，以及由它们算出的网络、排名、对比图和页面上的数字；页脚的“数据快照”月份。各校按论文推断的教师名单也会跟着变（新教师进来，离开的出去）。

## 不会自动更新的（手工维护）

- 院系官网教师名单（UofT、Stanford 和用官网名单的学校）：沿用已提交的名单和 OpenAlex 匹配。新学年要手动重抓。
- Top 20 的研究综述（`top20|cn-top20/data/manual/profiles.json`）：排名变化后，新进入前 20 的人暂时没有综述，要补写。
- 教授创业公司（`data/manual/startups.csv`）。
- 北美 / 中国产业报告（`na-companies/` 等）：公司资料是人工核实、带日期的，不在这里重跑。
- 年份范围：中美对比的趋势图截至 2024 年，各校语料是 2019–2025 年；跨年后要手动往后挪。

## 安全阀

重建后某个页面的网络节点少于原来的 75%（额度用完、OpenAlex 故障），这一部分就保留旧数据，工作流失败。GitHub 会给仓库主人发邮件。下个月照常重跑。

本地运行：`OPENALEX_API_KEY=... python3 refresh/refresh.py <part>`（会清掉该部分的本地缓存重新下载）；`--dry` 只用现有缓存重建，不调用 OpenAlex 的付费接口。
