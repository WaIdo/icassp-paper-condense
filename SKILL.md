---
name: icassp-paper-condense
description: Condense, typeset and fact-check a LaTeX paper to ICASSP's 4-page-plus-references limit (spconf.sty) by changing typesetting only -- never deleting or rewording the author's text, figures or tables -- and verify every edit by measurement. Use this whenever a user wants to shrink, compress, tighten, squeeze, fit, or polish a paper for ICASSP or another IEEE signal-processing venue on the spconf template, mentions a page overflow, an over-long fifth page, a last page that is half empty, one-word last lines, a table that is too wide or too tall, an abstract over 80 mm, adding an author or affiliation without breaking the page count, or asks to check that the paper's numbers, citations and claims still hold after editing -- even if they never say "ICASSP" but the paper is a 4+1-page two-column IEEE conference submission.
---

# ICASSP paper condensation

You are shrinking a finished paper into ICASSP's budget: **4 pages of technical
content, plus an optional 5th page that may hold only references, funding
acknowledgements and the Compliance-with-Ethical-Standards statement.** The
paper is usually already written and already good; your job is to make it fit
and keep it correct, not to rewrite it. Everything below follows from three
facts about this task:

1. **A page-limited paper is a zero-sum layout.** Every line you add is paid
   for by a line somewhere else, and `\flushbottom` means freed lines do not
   sit as white space -- they pull later content upward, sometimes dragging a
   section heading onto the wrong page. So measure before and after every
   edit, and know where each line came from.
2. **Verification, not impression.** "It looks fine" is how a references-free
   PDF gets reported as "five pages". Every claim in your report carries a
   number or a `file:line`.
3. **The author has already made judgment calls.** Deleting a claim that holds
   is as wrong as adding one that doesn't. When you are unsure whether a change
   sharpens or merely weakens, ask.

## Red lines (stop and ask the author before crossing)

- **Never delete or reword the author's text.** Not a paragraph, not a
  sentence, not "two redundant words". For body text you may change only the
  *typesetting* -- how the same words are set on the page. The words are the
  author's argument, and an agent cannot tell a redundant clause from a load-
  bearing one by reading it once. When layout cannot close the gap, list the
  paragraphs and your suggested rewrites in the report and let the author cut.
- **Never cut figure or table content**: no dropping metric columns, no
  removing panels, no shrinking a figure until labels are unreadable. Space
  comes from layout only. If layout runs out, present the gap in mm and the
  options with their costs; the author chooses.
- **Never over-correct.** Before changing any statement, answer: which *quantity*
  is the sentence wrong about, is your evidence a *unique* reading, does it
  outrank what it contradicts, and does the change make the claim *more
  accurate* or only *weaker*? "Only weaker" means leave it. See
  `references/fact-check.md`, section "Over-correction".
- **Never edit twice without rebuilding.** Run `scripts/verify_all.sh` after
  every change.
- **Not verifiable ≠ wrong.** A claim you cannot check locally (source PDF or
  checkpoint missing) goes into a "for the author to confirm" list, not into
  an edit.

## Tools

All scripts need Python 3 with PyMuPDF (`pip install pymupdf`) and poppler
(`pdftotext`, `pdfinfo`, `pdffonts`). Run them from the paper directory.

| script | what it answers |
|---|---|
| `scripts/measure_layout.py main.pdf` | pages, per-column bottoms, last-column gap, log/bibtex counts, references cited/orphaned/`[?]`, first-citation order of refs and floats, what is on page 5, abstract height, title-block geometry, font sizes, page numbers |
| `scripts/find_runts.py main.pdf --main main.tex` | every paragraph and caption whose last line has ≤2 words, with fill %; exit code = count |
| `scripts/check_citations.py --main main.tex` | cite keys ↔ bib entries ↔ bbl items, each key's context, IEEE et-al rule, missing year/pages, duplicates, `%` inside entries |
| `scripts/diff_numbers.py old.pdf new.pdf` | numbers lost or gained on the body pages between two builds |
| `scripts/corpus_baseline.py papers/ICASSP2026/ --also main.pdf` | measure accepted papers from the venue and place yours beside them |
| `scripts/verify_all.sh main.tex --backup old.pdf` | rebuild + all of the above; non-zero exit if any gate fails |

`measure_layout.py --json` gives machine-readable output when you need to
compute with it.

## Workflow

### Phase 0 — baseline (measure only, change nothing)

1. **Back up the whole source, not just the PDF, before touching anything.**
   Everything after this point is reversible only if there is something to
   revert to:
   ```bash
   git add -A && git commit -m "pre-condensation snapshot"   # if the paper is in git
   # or, if it is not:
   cp -r <paper-dir> <paper-dir>.backup-$(date +%Y%m%d_%H%M%S)
   ```
   Then keep a dated PDF of each accepted stage in `backup/`, so
   `diff_numbers.py` always has a previous build to compare against.
2. `measure_layout.py main.pdf` and `find_runts.py`. Note the overflow in mm
   and convert to lines (9 pt spconf: 1 line ≈ 3.67 mm, ≈10 words per full line).
3. If accepted papers from the venue are available, `corpus_baseline.py` them.
   Almost every "is this normal?" question in this task is settled by that
   table, not by memory. If no corpus is available, say so; do not assert
   venue conventions you have not measured.
4. Write the gap ledger (`references/compression.md`, "Gap ledger"): overflow
   lines ÷ words available to condense. Above ~20 % the gap cannot be closed by
   prose alone -- tell the author now, with the layout levers and their
   measured yields, rather than discovering it three hours in.
5. Report and **stop**. Do not enter Phase A without the author's go-ahead.

### Phase A — figures, tables and their captions (nothing in the body)

Work in this order; it is roughly benefit ÷ risk:

1. **Table bodies.** `\small` → `\caption{...}` → `\scriptsize` applied to the
   `tabular` only, so the caption stays at the kit's 9 pt. Return the width you
   freed as `\tabcolsep` so the table still spans the column. The vertical lever
   in short tables is booktabs' `\aboverulesep`/`\belowrulesep`, not
   `\arraystretch`, which is usually already at the content floor. Read actual
   span sizes from the PDF; do not infer sizes from box heights.
2. **Float placement and numbering.** Floats declared at the same point tend to
   land in one column. Numbering follows `\caption` declaration order, not page
   position: if `measure_layout.py` shows figures cited out of order, move the
   float's declaration to just after its first `\ref`, then re-measure all
   column bottoms. One figure with several panels is `Fig. 3(a, b)`, never
   `Figs. 3(a, b)` -- accepted papers contain zero `Figs.`.
3. **Merging and cropping figures.** Two levers that cut no content: several
   small figures declared as one multi-panel figure (each float removed takes
   its caption block and one `\floatsep` with it -- but the merged caption is
   usually longer, so measure the net), and cropping the whitespace inside a
   figure's own bounding box. Both re-arrange the author's figures, so propose
   them; apply only after the author agrees.
4. **In-figure typography.** Pairwise overlap checks miss three things: text
   escaping its own panel (do a containment check), a legend entry that reads
   as a formula but does not match the method (check it against the code --
   legends describe the toy drawing, readers cite them as definitions), and
   abbreviation periods that differ between panels. After any figure rebuild,
   confirm the PDF bounding box is unchanged so the page does not reflow.
5. **Captions.** A caption is the author's text, so the same rule holds: set
   it differently, do not rewrite it. Run an n-gram comparison against the body
   and *report* any sentence that appears in both, recommending it be dropped
   from the caption rather than the body -- then let the author drop it. Fix
   ≤2-word last lines by hyphenation or `\looseness`, not by cutting words.
   The one caption change worth proposing every time: every comparison table's
   caption should carry the same scope qualifier the prose uses ("among
   backbones of comparable scale", "≤ N M parameters"), because reviewers check
   superlatives against the table, not against the paragraph that scoped them.
6. Run `verify_all.sh`, report using the template below, and **stop for the
   author's confirmation**. Say how many mm Phase A saved and how many words
   Phase B will need.

### Phase B — body text, typesetting only (after the author confirms Phase A)

The words do not change in this phase. What changes is how TeX sets them.
These levers are ordered by measured yield; run `verify_all.sh` after each one
and keep it only if it actually bought lines.

1. **microtype.** The single largest lever, and it touches no word. On one
   5-page paper: no microtype = 1034 text lines and 6 pages; `protrusion=false`
   = 1002 lines and 5 pages; `protrusion=true, expansion=true` = 1000 lines.
   Loading it at all was worth 32 lines, about a full page.
   ```latex
   \usepackage[protrusion=true,expansion=true,stretch=20,shrink=20]{microtype}
   ```
   Protrusion pushes punctuation slightly into the margin; if that bothers the
   venue or the author, `protrusion=false` still keeps most of the gain.
2. **`\looseness=-1` at the start of a paragraph** asks TeX for one line fewer
   without changing a word. It works only where the paragraph has interword
   slack: on two already-tight paragraphs it re-broke the lines but saved
   nothing. So try it, measure, and revert it when it does not pay -- a
   `\looseness` that saves no line only makes the spacing worse.
3. **Hyphenation.** A short last line is often a long unbreakable word on the
   line above. `\-` inside that word, or a `\hyphenation{...}` entry in the
   preamble, lets TeX fill the line and can absorb the runt with no rewriting.
4. **Float placement.** Moving a float's declaration changes where text flows
   around it and can remove a runt several paragraphs away. Re-measure every
   column bottom afterwards. The stock float *parameters* (`topnumber` 2,
   `topfraction` .7, `textfraction` .2) also cap how much of a column floats
   may take, and raising them stops figures drifting past their references on
   a float-heavy draft -- but re-measure at the end: on one paper they were
   necessary at 8 pages and, once the paper reached 5, reverting them changed
   nothing. Say so in the report rather than carrying an override you can no
   longer justify.
5. **Section-heading skips.** `spconf.sty` sets only the heading *face*, so the
   skips are `article`'s, sized for a 10 pt one-column class. Tightening them
   with `\@startsection` reclaims ~13 pt of white per heading -- 64 mm over
   fourteen headings, a page on the paper measured -- and changes no word. It
   buys **white, not lines**: the text-line count was identical before and
   after, so it cannot fix a runt. Move in ~0.3ex steps, rebuild each time, and
   stop at the first setting that fits; the stock template already sits inside
   the accepted corpus band, so every step below it is appearance spent for a
   page, and `measure_layout.py` flags a paper that goes under the corpus floor
   (10.5 pt above / 4.3 pt below). Recipe and the measured table:
   `references/compression.md`.
6. **Reference venue names.** Abbreviating them to IEEE style
   (`Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
   Recognition` -> `Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.`) is
   the largest reference-page lever measured here: expanding 24 venue strings
   on a 26-entry bibliography added 18 lines and a page. It touches no author
   prose. Note for the author that IEEE style prescribes the short forms while
   6 of 7 accepted papers print them in full -- both get accepted.
7. **Fill the last page.** Measure the corpus's last-column gap first (accepted
   ICASSP 2026 papers: 0.1–9.0 mm). The lever is the bibliography `\itemsep`,
   tuned by bisection with a full rebuild each step. Do not expand `et al.`
   author lists to fill space -- IEEE style requires et al. past six authors, so
   expanding is a violation, not a trick.
8. **What you may not do here:** delete a sentence, delete "redundant" words,
   merge two paragraphs, shorten a caption's prose, or reword for density.
   Those are text edits. If `find_runts.py` still reports runts, or the gap is
   still open, put them in the report as *proposals* -- quote the paragraph,
   name the two or three words you would cut, say how many lines it buys -- and
   stop. The author decides.
9. **Fact-check what the layout moved**, using `references/fact-check.md`. A
   factual error you find is also reported, not silently rewritten: quote the
   sentence, give the evidence, propose the wording, let the author approve it.
10. `verify_all.sh --backup <phase-A pdf>`. Since no word changed,
   `diff_numbers.py` must report **zero** lost and zero gained numbers. Any
   difference means you edited text without meaning to.

### After every edit

```
verify_all.sh main.tex --backup <previous.pdf>
```
must show: pages ≤ limit · Overfull 0 · undefined 0 · BibTeX warnings 0 ·
conclusion still on the last body page · page 5 holds only references /
acknowledgements / ethics · all column bottoms flush except the last ·
runts 0 · references all cited, none `[?]` · float order ascending · every
lost/gained number explained.

## Report template

```
## Changed
| edit | evidence (measurement or file:line) | yield |

## Gates (verify_all.sh)
pages / Overfull / undefined / last body page / page-5 contents / column
bottoms / runts / citations / numbers-vs-backup

## Remaining gap
X mm ≈ Y lines; Phase B needs ≈ Z words

## Text changes I am proposing (not applied)
(quote the paragraph, the words to cut, and the lines it buys -- the author applies them)

## For the author to decide
(each: current state, options, cost of each -- do not decide for them)

## Could not verify locally
(what to check, against what, and what to change if it disagrees)
```

Report conclusions and evidence, not the process.

## When to stop and ask

1. End of Phase A -- always.
2. Gap ledger above ~20 % of condensable prose.
3. Any edit that changes a claim: dropping a qualifier, softening "all" to
   "most", changing a competitor's attribute marker, rewording what was
   measured.
4. A factual error with more than one defensible fix.

Everything else: finish the phase, then report.

## Reference files

Read these when the situation arises; they hold the measured facts and the
worked reasoning behind the rules above.

| file | read it when |
|---|---|
| `references/rules.md` | you need to know what the kit *requires* versus *suggests*, and what `spconf.sty` actually does |
| `references/measurements.md` | deciding whether something is "normal for the venue": title block, abstract, table fonts, reference spacing, last-page gap, punctuation density |
| `references/compression.md` | choosing a lever and estimating its yield; the gap ledger; the runt rule; `\flushbottom` behaviour |
| `references/author-block.md` | adding an author or a second affiliation without spending a body line |
| `references/fact-check.md` | before touching any sentence's meaning; over-correction; which sentences actually break |
| `references/pitfalls.md` | silent failures: BibTeX skipping entries, `&&` masking exit codes, appending to the wrong file, float numbering, "not reported/used" symbols |

## License and attribution

MIT — see `LICENSE`. Copyright (c) 2026 WaIdo (github.com/WaIdo).
Source: https://github.com/WaIdo/icassp-paper-condense

You may use, modify and redistribute this skill, including inside a paid or
closed product, provided the copyright notice and the licence text travel with
it. That matters here because agents copy single files out of skills: each
script carries an SPDX header and each reference file a one-line footer, so a
file that ends up somewhere else still says where it came from. Keep them when
you edit.

Two things this skill does **not** license, because they are not its to give:
the ICASSP paper kit and `spconf.sty` (IEEE/ICASSP's own terms), and the papers
you point `corpus_baseline.py` at. The venue figures quoted in
`references/measurements.md` are measurements of published work — facts about
page geometry and font sizes, not reproductions of it.

