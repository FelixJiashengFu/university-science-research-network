#!/bin/bash
# Assemble the published site into _site/ (same layout as GitHub Pages). Used by .github/workflows/pages.yml.
set -e
cd "$(dirname "$0")"
rm -rf _site && mkdir -p _site
cp index.html _site/ && cp -r assets _site/assets && mkdir -p _site/schools && cp schools/index.html _site/schools/ && (cp schools/stats.json _site/schools/ 2>/dev/null || true)
# English dictionary for hosts that translate the atlas (MolAstria's i18n.js): i18n/en.json → assets/i18n-en.js
python3 i18n/build_js.py
for d in uoft stanford waterloo udem mcmaster ualberta umich ucsb na-quantum-chem-map cn-quantum-chem-map top20 cn-top20 compare na-companies; do
  mkdir -p "_site/$d" && cp -r "$d/site/." "_site/$d/"
done
for d in schools/*/site; do [ -d "$d" ] || continue; s=$(basename "$(dirname "$d")"); mkdir -p "_site/schools/$s" && cp -r "$d/." "_site/schools/$s/"; done
rm -rf _site/schools/pipeline
echo "site assembled in _site/"
