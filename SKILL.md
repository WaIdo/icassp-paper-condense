---
name: icassp-paper-condense
description: "Fit a LaTeX manuscript to an ICASSP/spconf page budget through measured layout changes."
---

# ICASSP paper condensation

Use the user's target year and official submission kit to establish the page budget, typography, and allowed final-page content. The bundled measurements describe a particular accepted-paper corpus; they are evidence, not universal venue requirements.

Default to layout changes that preserve the author's words, numerical results, citations, and figure/table content. A request to change layout does not authorize changing scientific claims. If the user explicitly requests prose compression, that authorization takes precedence over the references' layout-only examples; preserve meaning and evidence and verify any changed numbers or claims.

## Work and completion

Build the original manuscript and retain a baseline PDF. Measure the overflow and choose applicable layout changes. Apply safe local edits without repeated approval, rebuild, inspect affected pages, and fix resulting layout or citation problems. Batch related edits and validate their effects; do not rerun the full audit after each trivial change.

Use the bundled `verify_all.sh` for the final manuscript when its toolchain is applicable. Locate it in this installed skill's scripts directory; use its documented arguments. Inspect its output rather than equating command completion with success. Finish when the requested page budget and relevant quality checks pass. If the authorized changes cannot close the gap, report measured remaining space and the decision needed; do not stop automatically at the end of an intermediate phase.

Ask only about changes to claims, ambiguous factual corrections, or other decisions outside the user's existing authorization. Never fabricate results, delete evidence to satisfy layout, or shrink figures until labels become unreadable.

## Load references by operation

- Venue requirements and template behavior: [rules](references/rules.md).
- Comparing page geometry with the bundled corpus: [measurements](references/measurements.md).
- Choosing and measuring layout adjustments: [compression](references/compression.md).
- Adding authors or affiliations: [author block](references/author-block.md).
- Auditing claims affected by the change: [fact checking](references/fact-check.md).
- Diagnosing LaTeX, BibTeX, path, or float failures: [pitfalls](references/pitfalls.md).

## License and attribution

MIT — see `LICENSE`. Copyright (c) 2026 WaIdo (github.com/WaIdo).
Source: https://github.com/WaIdo/icassp-paper-condense

Preserve copyright notices and SPDX headers when copying or editing the skill. The IEEE/ICASSP paper kit and source papers retain their own licensing terms.
