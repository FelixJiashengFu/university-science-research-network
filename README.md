# University Science Research Network

把大学数学、物理、化学教授的研究领域、论文、合作关系与产业合作编织成一张主网，并拆出专题子网，可交互浏览。

| # | 部分 | 目录 | 规模 |
|---|---|---|---|
| 01 | 多伦多大学（三校区）数理化研究网络 | [`uoft/`](uoft/) | 298 位教授 · 12 张网络 |
| 02 | 斯坦福大学数理化研究网络 | [`stanford/`](stanford/) | 136 位教授 · 18 张网络 |
| 02b | 滑铁卢大学数理化研究网络 | [`waterloo/`](waterloo/) | 167 位教授 · 24 张网络 |
| 02c | 蒙特利尔大学（UdeM）数理化研究网络 | [`udem/`](udem/) | 96 位教授 · 22 张网络（物理系名单未经官网核对） |
| 02d | 麦克马斯特大学数理化研究网络 | [`mcmaster/`](mcmaster/) | 87 位教授 · 23 张网络 |
| 02e | 阿尔伯塔大学数理化研究网络 | [`ualberta/`](ualberta/) | 119 位教授 · 23 张网络 |
| 03 | 北美量子化学 / 计算化学合作地图 | [`na-quantum-chem-map/`](na-quantum-chem-map/) | 1,044 位教授 · 277 所学校 · 4,244 条合作线 |
| 04 | 北美 Top 20 学者深度档案 | [`top20/`](top20/) | 20 份档案 + 个人合作网络 |
| 05 | 中国量子化学 / 计算化学合作地图 | [`cn-quantum-chem-map/`](cn-quantum-chem-map/) | 513 位教授 · 201 个单位 · 927 条合作线 |
| 06 | 中美细分领域对比 | [`compare/`](compare/) | 17 张统计图 · 6 张对比表 |
| 07 | 中美量化 / 计算化学产业报告 | [`na-companies/`](na-companies/) | 164 家企业（北美 113 + 中国 51）· 57 张统计图 |

顶层 `index.html` 是统一入口，`assets/`（`site.css` 设计变量、`nav.js` 全站导航、`charts.js` 图表组件）被所有页面共用；数据生成脚本在 [`analysis/`](analysis/) 与各子目录的 `scripts/`。

**在线浏览**：仓库 Settings → Pages → Source 选 *GitHub Actions*，`.github/workflows/pages.yml` 会把顶层入口页、`assets/` 和各子项目的 `site/` 一起发布。

**本地浏览**：

```bash
./build_site.sh                       # 组装成与线上相同的 _site/ 目录
python3 -m http.server 8000 -d _site  # 打开 http://localhost:8000/
```

这些子项目使用同一套方法：院系公开教师名单 → OpenAlex 作者匹配 → 论文、主题、合作者、企业合作 → networkx 构建网络并预计算布局 → sigma.js 交互页面。重跑步骤、方法与局限分别见 [`uoft/README.md`](uoft/README.md)、[`stanford/README.md`](stanford/README.md)、[`waterloo/README.md`](waterloo/README.md)、[`udem/README.md`](udem/README.md) 和 [`mcmaster/README.md`](mcmaster/README.md)、[`ualberta/README.md`](ualberta/README.md)。OpenAlex API key 只通过环境变量 `OPENALEX_API_KEY` 读取，仓库里不含任何密钥。
