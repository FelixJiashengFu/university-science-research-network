# 中国量子化学与计算化学合作地图

中国内地、香港、澳门高校与中科院等研究所中做量子化学、计算化学理论与方法的课题组负责人，按单位真实经纬度铺在中国地图上。点是教授，线是共同发表的论文；点开教授看主要论文、近期论文和网内合作者。方法、阈值与 [`../na-quantum-chem-map/`](../na-quantum-chem-map/) 完全相同，便于中美对比。

| | |
|---|---|
| 教授 | 513 |
| 单位 | 201 |
| 合作线 | 927 |
| 论文语料 | 140,923 篇（2000–2026） |

## 与北美版的差异
- 语料限定作者单位国家为 CN / HK / MO；台湾地区高校不在统计范围内（底图按中国地图惯例绘制）。
- 中科院各研究所（OpenAlex 类型 facility / government）与高校同样计为“当前单位”；同时挂靠国科大与某研究所时取研究所。
- 单位中文名来自人工整理的 `data/manual/inst_zh.tsv`。
- `data/manual/inst_fix.tsv`：OpenAlex“最后已知单位”明显错误时的人工更正（附说明）。

## 重跑
```bash
export OPENALEX_API_KEY=...                       # 只放环境变量
python3 scripts/fetch_corpus.py                   # 约 700 次列表请求，≈ $0.07；COUNTRIES 环境变量可改国家
python3 scripts/build_graph.py                    # 作者 / 机构单条查询免费，缓存在 data/raw/
python3 scripts/build_basemap.py                  # 需先把 Natural Earth geojson 放进 data/raw/ne/
```

## 局限
OpenAlex 对中文姓名的作者消歧较弱：同名学者被合并会让“语料论文占比”偏低而被过滤，一人被拆成多个档案也会漏掉，所以中国 PI 数很可能被低估，部分学者的单位也可能是旧单位。
