# University Science Research Network

把大学数学、物理、化学教授的研究领域、论文、合作关系与产业合作编织成一张主网，并拆出专题子网，可交互浏览。

| 学校 | 目录 | 规模 |
|---|---|---|
| 多伦多大学（三校区） | [`uoft/`](uoft/) | 298 位教授 · 主网 6,274 节点 / 24,618 边 · 12 张网络 |
| 斯坦福大学 | [`stanford/`](stanford/) | 136 位教授 · 主网 3,844 节点 / 12,312 边 · 18 张网络 |
| 美国 + 加拿大：量子化学 / 计算化学 | [`na-quantum-chem-map/`](na-quantum-chem-map/) | 1,044 位教授 · 277 所学校 · 4,244 条合作线 · 真实地图 |

**在线浏览**：仓库 Settings → Pages → Source 选 *GitHub Actions*，`.github/workflows/pages.yml` 会把顶层入口页和各子项目的 `site/` 一起发布。

**本地浏览**：

```bash
python3 -m http.server 8000   # 在仓库根目录
# 打开 http://localhost:8000/ ，或直接 uoft/site/、stanford/site/
```

两个子项目使用同一套方法：院系公开教师名单 → OpenAlex 作者匹配 → 论文、主题、合作者、企业合作 → networkx 构建网络并预计算布局 → sigma.js 交互页面。重跑步骤、方法与局限分别见 [`uoft/README.md`](uoft/README.md) 和 [`stanford/README.md`](stanford/README.md)。OpenAlex API key 只通过环境变量 `OPENALEX_API_KEY` 读取，仓库里不含任何密钥。
