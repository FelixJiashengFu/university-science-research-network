#!/bin/bash
# Assemble the published site into _site/ (same layout as GitHub Pages). Used by .github/workflows/pages.yml.
set -e
cd "$(dirname "$0")"
rm -rf _site && mkdir -p _site
cp index.html _site/ && cp -r assets _site/assets && cp -r schools _site/schools
for d in uoft stanford na-quantum-chem-map cn-quantum-chem-map top20 cn-top20 compare na-companies; do
  mkdir -p "_site/$d" && cp -r "$d/site/." "_site/$d/"
done
echo "site assembled in _site/"
