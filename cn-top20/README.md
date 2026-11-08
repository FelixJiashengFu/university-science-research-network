# 中国量子化学 / 计算化学 Top 20

Same ranking formula as `top20/` (40% corpus citations, 20% h-index, 20% corpus papers, 20% network degree, each as a percentile), applied to the 513 PIs of `cn-quantum-chem-map/`.

- `site/` — the page (`index.html`) and generated `data/top20.json`
- `data/manual/profiles.json` — hand-written research summaries; `inst`/`where` override the OpenAlex institution where it is wrong
- Built by `analysis/build_atlas_data.py` (needs the raw corpora, see `cn-quantum-chem-map/`).

OpenAlex disambiguates Chinese names poorly: profiles #4 (Jun Li), #12 (Jing Ma) and #18 (John Z. H. Zhang) are flagged on the page as possibly merged or split.
