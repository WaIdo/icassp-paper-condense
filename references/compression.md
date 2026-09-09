# Compression playbook: levers, measured yields, and the accounting behind them

**The author's text is not a lever.** Nothing in this file authorises deleting
or rewording a sentence, a clause or a "redundant" word of the paper. Body text
and caption prose may only be re-*set*, never re-*written*. Where a section
below would once have cut words, it now tells you what to measure and what to
propose to the author instead.

## The gap ledger (do this before touching anything)

1. **Measure the overflow** in mm from `measure_layout.py` (content beyond the
   last allowed body page, or the last column's shortfall if you are filling).
   Convert: 1 line ≈ 3.67 mm at 9 pt spconf.
2. **Add up what layout can still give.** Go down the lever table below, note
   which levers this paper has not used yet, and sum their measured yields.
   That is your budget; you have no other.
3. **Compare.** If layout covers the overflow, say so and proceed. If it does
   not, report the shortfall in lines *now* — before editing anything — and
   list the paragraphs whose text the author could cut, with the lines each
   would buy. Cutting is their decision, not yours.
4. If the author does decide to cut, help them judge each number: is it
   *derivable* from numbers already on the page, or an *independent fact* or a
   *link in a causal chain*? A "6.7× more steps" deleted once severed "more
   tracklets → more optimizer steps → higher dispersion" and had to be put
   back.

## Layout levers, in order of yield ÷ risk (measured on an 8 → 5 page job)

| lever | yield | risk / rule |
|---|---|---|
| Table body `\small`→`\caption`→`\scriptsize` on the tabular only | ~1–2 lines per table | caption must stay 9 pt (kit); return width via `\tabcolsep` so the table still fills the column |
| booktabs rule seps (`\tightrules`) | 2–4 mm per short table | `\arraystretch` is usually already at the floor — measure before touching it |
| Caption `\vskip` 10 pt → 3 pt (override `\@makecaption`) | ~1 line per float | matches corpus caption spacing |
| Float separations `\floatsep`/`\textfloatsep` 6/5 pt | small | keep ≥ 5 pt |
| Section/subsection skips (`\@startsection`) | ~13 pt (4.6 mm) of white per heading; 14 headings = 64 mm ≈ 17 lines of column space, and one page on the paper measured | buys **white, not lines** — the text-line count was 1002 before and after; the corpus floor is 10.5 pt above / 4.3 pt below and going under it is a decision to report, not a default. See the worked case below |
| Display-equation skips (`\abovedisplayskip` etc. 4/4/2/2 pt) | stock→4 pt saves 4.4 mm over five equations; 4→3 pt 3.2 mm; 3→2 pt 7.4 mm; →0 pt 14.8 mm | at 4 pt the white between text ink and equation ink is 1.42 pt against 1.24 – 1.95 pt in accepted papers — **already level; do not go tighter** |
| `\parskip 0pt plus 1.5pt` | absorbs `\flushbottom` stretch quietly | — |
| Group several floats into one column (declare at one insertion point) | frees the column they used to split | re-measure every column bottom after moving a float |
| **microtype** | on one 5-page paper: none = 1034 lines / 6 pages, `protrusion=false` = 1002 / 5, `protrusion+expansion` = 1000 / 5 — loading it at all was worth **32 lines** | protrusion nudges punctuation into the margin; drop to `protrusion=false` if that is unwelcome and keep most of the gain |
| `\looseness=-1` on one paragraph | 0 or 1 line | only works where the paragraph has interword slack; on two already-tight paragraphs it re-broke the lines and saved nothing. Measure, and revert when it pays nothing |
| `\-` or `\hyphenation{}` on a long unbreakable word | often exactly the runt | the cheapest runt fix that changes no word |

Do **not**: change `\textwidth`/margins, drop below 9 pt in captions or body,
trim `\vskip 2em` above the title (every accepted paper keeps it), delete
figure/table content, or delete or reword any of the author's text.

## Section-heading spacing (worked case)

`spconf.sty` redefines only the heading *face*, so the skips are `article`'s,
sized for a 10 pt one-column class and generous in a 9 pt two-column one. They
are set with `\@startsection`; the first brace group is the skip *before* the
heading (negative = suppress the following paragraph indent), the second the
skip *after*:

```latex
\makeatletter
% spconf's \@sect still sets the face; this changes only the skips.
\renewcommand\section{\@startsection{section}{1}{\z@}%
  {-1.8ex \@plus -.3ex \@minus -.2ex}{1.0ex \@plus .1ex}{\normalfont\normalsize\bfseries}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-1.6ex \@plus -.3ex \@minus -.2ex}{0.6ex \@plus .1ex}{\normalfont\normalsize\bfseries}}
\makeatother
```

Measured on one 5-page paper with 14 headings, stock skips versus the above:

| | pages | body text lines | extra white above / below a heading |
|---|---|---|---|
| stock (`-3.5ex/2.3ex`, `-3.25ex/1.5ex`) | **6** | 1002 | 15.12 / 8.20 pt |
| corpus floor (`-2.5ex/1.3ex`, `-2.3ex/0.9ex`) | **6** | 1002 | 11.04 / 5.34 pt |
| shipped (`-1.8ex/1.0ex`, `-1.6ex/0.6ex`) | **5** | 1002 | 7.21 / 3.06 pt |

Read the middle column before the first: **the line count never moves.** This
lever does not shorten the text, it removes vertical white — 13 pt per heading,
64 mm over fourteen of them, which on that paper was the difference between six
pages and five. That also means it cannot fix a runt or a half-empty last page;
it only relocates where the column breaks fall.

How to use it:

1. Measure first (`measure_layout.py` prints `heading spacing`, and
   `corpus_baseline.py` the venue's `head_ab_pt` / `head_be_pt`). The stock
   template already sits *inside* the accepted band, so you are not correcting
   anything — you are spending appearance for a page.
2. Move in steps of ~0.3ex and rebuild each time. The step that matters is
   usually the last one: on that paper, `-2.0ex/1.05ex` was still six pages and
   `-1.8ex/1.0ex` was five, so ~0.2ex per heading was the whole margin.
   Bisect; do not jump straight to a tiny value and assume it was needed.
3. If the result lands below the corpus floor (10.5 pt above, 4.3 pt below),
   `measure_layout.py` flags it. Do not silently accept the flag: state in the
   report how many pages the tightening buys. If the answer is "none" or "it
   would also fit one step looser", back it off.
4. Do **not** tighten `\subsubsection` to zero or set the after-skip to `0ex` —
   the heading then touches its first line and the level structure stops being
   readable. 0.6ex was the floor that still read correctly at 9 pt.
5. This is a preamble change and touches no text, so it is a Phase B lever you
   may apply — unlike anything that would reword a heading.

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
words. Fix them with typesetting first, in this order:

1. **`\-` or a `\hyphenation{}` entry** for the long word sitting at the end of
   the previous line — a runt is often just a word TeX could not break.
2. **`\looseness=-1`** at the start of that paragraph. Measure; revert if it
   buys nothing.
3. **microtype**, if the paper is not already using it — it re-breaks every
   paragraph in the document and clears runts wholesale.

If none of that works, the runt stays and goes in the report as a proposal.
State it in the form the author can act on: with W words on the last line and
~N per full line, removing k words leaves ≈ N + W − k, so **suggest cutting
2–3 words** (5 or more just makes a new half-empty tail), and name the
candidates you would cut and why they cost no information:

1. a "colon + restating clause" (`…below theirs: averaging is not generically
   beneficial.`) — it repeats the numbers beside it;
2. a doubled verb or phrase inside one sentence (`is correct at …, is correct
   at every rank …`);
3. a standalone one-sentence paragraph that repeats the previous sentence.

Quote the paragraph, mark the words, give the line count. Then stop.

## Captions

- n-gram (5-gram) overlap with the body: report the duplicated sentence and
  recommend dropping it from the *caption* rather than the body — but the
  caption is the author's text too, so propose it, do not cut it yourself.
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

Punctuation lives inside sentences, so every item here is a **proposal**, not
an edit you make:

- `independent clause; independent clause` in body prose reads as the "AI feel"
  tell; suggest splitting into two sentences.
- A colon should be explained by the *whole* clause before it, not by its last
  noun.
- Caption keys' semicolons and colons introducing displays are correct — leave
  them out of the report.
- Abbreviation periods (`Fig.`, `No align.`) are consistent or absent — never
  both forms of the same word in one figure.

## Title-block line

A second affiliation line costs one body line *in each column* of page 1 and
ripples to the end. See `author-block.md` for the recipe that adds an
affiliation at zero body cost.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
