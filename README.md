# icassp-paper-condense

**English** · [简体中文](README.zh-CN.md)

An agent skill for condensing, typesetting and fact-checking a LaTeX paper to
**ICASSP's 4 + 1 page limit** (spconf template) — by changing typesetting only,
never deleting or rewording your text, figures or tables, and with every edit
verified by measurement rather than by eye.

Works with **Claude Code** and **OpenAI Codex** (both read the same
`SKILL.md` format). The measured venue facts come from seven accepted
ICASSP 2026 papers; the process and the pitfalls come from doing this on a
real submission, including the mistakes.

## What it does

1. **Phase 0** — measures the paper (pages, column bottoms, overflow in mm,
   short last lines, font sizes, citation order) and the venue corpus, writes a
   gap ledger, and stops.
2. **Phase A** — figures, tables and captions only: table font/rule spacing,
   float grouping and numbering order, in-figure typography, caption
   de-duplication and scope qualifiers. Stops for the author's confirmation.
3. **Phase B** — body text, *typesetting only*: microtype, `\looseness`,
   hyphenation and float placement to buy lines without changing a word; then
   filling the last page, and a fact-check. Anything that would need words cut
   is written up as a proposal for you, not applied.
4. After every edit: rebuild, and a seven-gate check that must pass.

Three red lines:

- **Your words are never edited.** Not a paragraph, not a sentence, not "two
  redundant words" — for text the skill may change only *how the same words are
  set*, using microtype, `\looseness`, hyphenation and float placement. On one
  5-page paper, loading microtype alone was worth 32 lines (about a full page)
  without touching a single word. When layout runs out, the skill reports the
  paragraphs and the words it *would* cut, and stops; you decide.
- **Figure and table content is never cut**: no dropping metric columns, no
  removing panels.
- **No over-correction**: a claim made weaker but not more accurate is left
  alone; a factual problem is reported with evidence and a proposed wording,
  not silently rewritten.

## Back up before you start

Everything the skill does is reversible only if there is something to revert to,
and page-limited typesetting is exactly the kind of work where the third attempt
is worse than the first. Snapshot the whole source, not just the PDF:

```bash
git add -A && git commit -m "pre-condensation snapshot"
# not using git? then:
cp -r my-paper my-paper.backup-$(date +%Y%m%d_%H%M%S)
```

Phase 0 of the workflow does this first and refuses to continue without it.
Keep a dated PDF of each stage in `backup/` as well, so `diff_numbers.py`
always has a previous build to compare against.

## Install

### Claude Code

```bash
git clone https://github.com/WaIdo/icassp-paper-condense ~/.claude/skills/icassp-paper-condense
```
or drop the folder into a project's `.claude/skills/`. Claude Code picks it up
from the `name` / `description` in `SKILL.md`.

### Codex

```bash
git clone https://github.com/WaIdo/icassp-paper-condense ~/.codex/skills/icassp-paper-condense
```

### Dependencies

```bash
pip install pymupdf
```
plus poppler (`pdftotext`, `pdfinfo`, `pdffonts`) and a TeX distribution with
`latexmk`. On macOS: `brew install poppler`.

## Scripts

Run from the paper's directory.

| script | purpose |
|---|---|
| `scripts/measure_layout.py main.pdf` | full layout / compliance report (`--json` available) |
| `scripts/find_runts.py main.pdf --main main.tex` | paragraphs and captions ending in ≤2 words |
| `scripts/check_citations.py --main main.tex` | cite ↔ bib ↔ bbl audit, contexts, IEEE et-al rule |
| `scripts/diff_numbers.py old.pdf new.pdf` | numbers lost/gained between two builds |
| `scripts/corpus_baseline.py papers/ICASSP2026/ --also main.pdf` | measure accepted papers, place yours beside them |
| `scripts/verify_all.sh main.tex --backup old.pdf` | rebuild + every gate; non-zero exit on failure |

## Layout

```
SKILL.md                  workflow, red lines, gates, report template
references/
  rules.md                hard vs. soft ICASSP rules; what spconf.sty does
  measurements.md         venue baselines (title block, abstract, tables, refs, punctuation)
  compression.md          levers with measured yields; gap ledger; runt rule; \flushbottom
  author-block.md         add an author / second affiliation at zero body cost
  fact-check.md           which sentences break; evidence order; over-correction
  pitfalls.md             silent failures, each one real
scripts/                  see above
```

## Scope

Written for spconf-based IEEE conferences (ICASSP, ICIP, …) with a hard page
limit and a references-only extra page. The measurement scripts work on any
two-column PDF; the venue numbers in `references/measurements.md` are
ICASSP 2026 and should be re-measured for other venues with
`corpus_baseline.py`.

## License

MIT — see [`LICENSE`](LICENSE). Copyright (c) 2026 WaIdo (github.com/WaIdo).

Every script carries an `SPDX-License-Identifier: MIT` header and every
reference file a one-line footer, so an individual file copied out of the skill
still carries its origin and terms. Please keep them.

Not covered by this licence: the ICASSP paper kit and `spconf.sty`, which are
IEEE/ICASSP's; and any papers you measure with `corpus_baseline.py`. The venue
numbers in `references/measurements.md` are measurements of published papers —
factual observations about page geometry, font sizes and punctuation counts.

If you use this in published work, a link to the repository is appreciated but
not required.
