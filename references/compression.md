# Compression playbook: levers, measured yields, and the accounting behind them

## The gap ledger (do this before touching anything)

1. **Measure the overflow** in mm from `measure_layout.py` (content beyond the
   last allowed body page, or the last column's shortfall if you are filling).
   Convert: 1 line ≈ 3.67 mm at 9 pt spconf.
2. **Measure the stock**: words in the sections you are allowed to condense ÷
   ~10 words per full line = lines of prose.
3. **Ratio = overflow lines ÷ stock lines.** Prose condensation of already-
   edited text yields 12 – 16 % per pass; dense setup paragraphs give ~5 %,
   discussion and conclusion 15 – 20 %. Above ~20 % you will start deleting
   argument. Tell the author *now*, with the layout levers below and their
   measured yields, and let them choose.
4. Every number you consider deleting: is it *derivable* from numbers already
   on the page (then it can go) or an *independent fact* or a *link in a causal
   chain* (then it stays)? A "6.7× more steps" deleted once severed "more
   tracklets → more optimizer steps → higher dispersion" and had to come back.

## Layout levers, in order of yield ÷ risk (measured on an 8 → 5 page job)

| lever | yield | risk / rule |
|---|---|---|
| Table body `\small`→`\caption`→`\scriptsize` on the tabular only | ~1–2 lines per table | caption must stay 9 pt (kit); return width via `\tabcolsep` so the table still fills the column |
| booktabs rule seps (`\tightrules`) | 2–4 mm per short table | `\arraystretch` is usually already at the floor — measure before touching it |
| Caption `\vskip` 10 pt → 3 pt (override `\@makecaption`) | ~1 line per float | matches corpus caption spacing |
| Float separations `\floatsep`/`\textfloatsep` 6/5 pt | small | keep ≥ 5 pt |
| Section skips reduced | ~1 line per 3 headings | do not go below the corpus's visible heading spacing |
| Display-equation skips (`\abovedisplayskip` etc. 4/4/2/2 pt) | stock→4 pt saves 4.4 mm over five equations; 4→3 pt 3.2 mm; 3→2 pt 7.4 mm; →0 pt 14.8 mm | at 4 pt the white between text ink and equation ink is 1.42 pt against 1.24 – 1.95 pt in accepted papers — **already level; do not go tighter** |
| `\parskip 0pt plus 1.5pt` | absorbs `\flushbottom` stretch quietly | — |
| Group several floats into one column (declare at one insertion point) | frees the column they used to split | re-measure every column bottom after moving a float |
| Prose condensation | 12 – 16 % per pass | see Phase B rules |

Do **not**: change `\textwidth`/margins, drop below 9 pt in captions or body,
trim `\vskip 2em` above the title (every accepted paper keeps it), or delete
figure/table content.

## `\flushbottom` and why freed lines have to have a destination

spconf sets `\flushbottom`. A line freed on page 1 pulls every later line up
by one; the last body page then has one line of slack, which is absorbed by
stretching inter-paragraph glue — or, if a section heading and two lines fit,
by pulling the next section up onto that page. Two consequences:

- Freeing lines on the body pages is counter-productive when the problem is a
  half-empty *last* page: it moves the ethics statement up and makes the
  reference column emptier.
- To add a line somewhere (a fuller conclusion, a caption qualifier) on a full
  page, free a line *on that same page* first, then spend it there.

## Short last lines ("runts")

`find_runts.py` lists every paragraph and caption whose last line holds ≤2
words. With W words on that line and ~N per full line, removing k words leaves
a new last line of ≈ N + W − k words:

- k = 2–3 → 8–9 words (80–90 % full): optimal
- k ≥ 5 → ≤6 words: you made a new half-empty tail
- k < 1 → the runt survives

Preferred sources of the 2–3 words, because they cost no information:
1. a "colon + restating clause" (`…below theirs: averaging is not generically
   beneficial.`) — it repeats the numbers beside it, adds a colon, and is
   usually exactly a 3-word tail;
2. a doubled verb or phrase inside one sentence (`is correct at … , is correct
   at every rank …`);
3. a standalone one-sentence paragraph that repeats the previous sentence —
   fold it into that paragraph.

## Captions

- n-gram (5-gram) overlap with the body: a shared sentence is deleted from the
  caption, never from the body.
- Key-style legends (`ℓ: manual labels; †: external model; ‡: as reported in
  [n]`) are a compression device, not an AI tell — keep them.
- Every comparison table repeats the scope qualifier its superlatives depend
  on. "Among backbones of comparable scale" in the prose does not protect a
  table that reads as unrestricted; the qualifier goes in the caption, and it
  must admit your own row (an "≤86M" bound is about the *backbone*; check
  which quantity your parameter count reports before deciding the bound is
  violated).

## Filling the last page

1. Measure the corpus last-column gap first (accepted: 0.1 – 9.0 mm). Target
   under 10 mm; 1–2 mm is achievable.
2. Main lever: bibliography `\itemsep`. In the preamble:
   ```latex
   \let\spconfthebibliography\thebibliography
   \def\thebibliography#1{\spconfthebibliography{#1}%
     \setlength{\itemsep}{2.2pt plus .5pt}\setlength{\parsep}{0pt}}
   ```
   Bisect: a 34 mm gap over 25 entry gaps suggests 3.8 pt arithmetically, but
   3 pt already overflowed to a sixth page in one case and 2.2 pt landed at a
   1.2 mm gap — the arithmetic over-estimates because the left column's
   stretch pushes lines into the right one. Rebuild and count pages each step.
3. A fuller compliance statement (what the authors did, not what a licence
   says) is legitimate page-5 content.
4. **Not** a lever: expanding `and others` author lists (IEEE requires et al.
   past six authors), adding uncited references, or letting one body line
   spill onto page 5.

## Punctuation

Measure first (`corpus_baseline.py` prints densities). Then:

- `independent clause; independent clause` in body prose → two sentences.
- A colon must be explained by the *whole* clause before it, not by its last
  noun; otherwise rewrite as two statements.
- Keep caption keys' semicolons. Keep colons that introduce displays.
- Abbreviation periods (`Fig.`, `No align.`) are consistent or absent — never
  both forms of the same word in one figure.

## Title-block line

A second affiliation line costs one body line *in each column* of page 1 and
ripples to the end. See `author-block.md` for the recipe that adds an
affiliation at zero body cost.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
