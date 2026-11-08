# 20 所大学的数理化研究网络

`schools/index.html` is the hub. UofT (`uoft/`) and Stanford (`stanford/`) use department rosters. The other 18 schools live in `schools/<slug>/` and are built by one generic pipeline in `schools/pipeline/`:

```bash
export OPENALEX_API_KEY=...            # never commit it
cd schools/pipeline
python3 fetch.py mit                   # infer roster + download works  (raw/ is git-ignored)
python3 build_graph.py mit             # 17 networks -> schools/mit/site/data/
python3 make_site.py mit               # page from the Stanford template + schools/stats.json
```

**Rosters.** When `schools/<slug>/data/processed/roster.csv` exists (faculty lists taken from the department websites, same columns as Stanford's), `fetch.py` matches those names to the authors in the school's 2019–2025 corpus locally. It needs no author-search requests. Pinyin spellings, hyphens and swapped family/given order are handled; a match needs the full given name, or an initial plus most papers in the right field. Unmatched names stay in `matches.csv` without an OpenAlex id.

**Roster inference (fallback when no roster file).** These schools do not share a common faculty list, so the roster is inferred from publications (method in `fetch.py`):
- **Corpus.** Works from 2019 to 2025 with an author affiliated to the school and a primary topic in Mathematics, Physics or Chemistry.
- **Who counts.** A person is kept when, on papers carrying the school's affiliation, they meet all of these:

  | Requirement | Physics, Chemistry | Mathematics |
  |---|---|---|
  | Papers | ≥ 10 | ≥ 6 |
  | Papers in 2023–2025 | ≥ 2 | ≥ 2 |
  | Last-author share on papers with ≤ 50 authors | ≥ 30% | not used (alphabetical author order) |
  | h-index | ≥ 12 | ≥ 8 |
  | School among OpenAlex last-known institutions | required | required |

- **Department.** Assigned from the field of most of those papers.
- **Cap.** At most 260 people per school, keeping the highest h-index.

**Limits.** The list will include some senior research scientists. It misses faculty with few papers or with OpenAlex profiles split across several IDs. Chinese names are disambiguated less reliably.

**Research-area sub-networks** use OpenAlex subfields that make up at least 15% of a person's papers, instead of department area lists.
