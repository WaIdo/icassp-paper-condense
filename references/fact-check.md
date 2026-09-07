# Fact-checking a condensed paper: what actually breaks, and how not to break it further

A full fact-check of one 4+1 page paper — 554 checkable assertions, each
checked against the experiment archive, flagged ones re-checked by three
independent readers — produced a result that runs against intuition: **every
numeric claim held. The claims that broke had no number in them.** Spend the
verification budget accordingly.

## Which sentences break

| pattern | why it breaks | example shape |
|---|---|---|
| **Instruction written as achieved effect** | the prompt/config *says* X; the paper reports X as done. The shipped data can falsify it in a minute | "the prompt permits an unknown value *and prevents unsupported guesses*" — the first half is the instruction, the second is a measurement nobody made |
| **Universal over cited works** | "These approaches all depend on A, B or C" is falsifiable by one cited paper that escapes all three; often your own related-work draft already names it | soften the quantifier, or restrict the domain ("in video", "on tracklets") if that is actually the boundary |
| **Superlative without its scope in the table** | the prose says "among comparable backbones"; the table caption says nothing; the reviewer checks the table | repeat the qualifier in *every* comparison table's caption |
| **"Both / Neither / All + generalisation"** | reads as one statement, is really two; if one subject fails, the sentence is false and contradicts the sentence before it | "δ is 0.4 on A and 0.7 on B … *Both* transfer across datasets" — λ did, δ did not |
| **Ratio carried across a definition boundary** | "6.7× more tracklets, so 6.7× more steps" — but dense sampling turns tracklet *length* into steps too; measured ratio was 38× | verify the multiplier on the quantity being claimed, from logs (batch count × epochs, or wall-clock per epoch) |
| **Temporal adverb read as measurement time** | "removing X *before* consolidation costs 3.2" — meant "X acts during training, which precedes merging"; reads as "measured on unmerged replicas", where the same A/B was not significant | say what was measured: "the consolidated model trained without X loses 3.2" |
| **Legend that looks like a definition** | a figure legend `r<s, J_rs<δ` describes the toy drawing; readers cite it as the selection rule; the code's rule (agglomeration against a cluster union) differs | make the legend state the paper's actual rule (`c_r≠c_s`) if the drawn marks satisfy it |
| **Template statements with false premises** | the kit's example ethics sentence presumes open-access data and a licence that speaks to ethics | write what the authors did |
| **Competitor attribute markers from your own notes** | a "uses manual labels" dagger inherited from an early note | evidence order: the cited paper's own table > a third-party summary table > your notes; take the *newest* note; a two-valued symbol ("not reported/used") cannot overturn several consistent records |

Numbers still get checked — but by script (`diff_numbers.py`, re-running the
figure generator, re-running the pseudo-label builder) rather than by reading.

## Evidence order, and its exception

| rank | source | caveat |
|---|---|---|
| 1 | run logs and shipped data files | re-run the shipped script; if it reproduces the paper's number bit-for-bit, the reproduction pipeline is trusted for the rest |
| 2 | the cited paper's own tables | a **two-valued symbol** in an authoritative table ("‘–’: results/attributes not reported/used") has lower evidential value than five consistent internal records — rank by *whether the evidence is a unique reading*, not only by source authority |
| 3 | third-party summary tables | transcribe cell-by-cell **by column name, not position**; their column order will differ from yours; they also get venues wrong (a workshop paper listed as the main conference — page-number magnitude settles it: main-track pages run to thousands, workshop volumes to hundreds) |
| 4 | your own notes | prefer the newest; a claim that appears only in a README written after the paper is not corroboration |

## Over-correction

Three edits in one audit had to be reverted, and all three pointed the same
way: they weakened the authors' own claims. That is a bias, not a coincidence
— a verifier's stance ("would this get caught?") never asks "is this being
undersold?". Principle:

> Deleting a claim that holds is the same error as writing one that does not.

Before changing a statement's meaning, answer four questions in writing:

1. **Which quantity is the sentence wrong about?** Whole model vs backbone;
   optimizer steps vs tracklets; measurement time vs mechanism time. If you
   can only say "it feels imprecise", do not change it.
2. **Is the evidence a unique reading?** Pull the source's own legend/definition
   and read it, not the cell.
3. **Does the evidence outrank what it contradicts?** (table above)
4. **Does the change make the claim more accurate, or only weaker?** Only
   weaker → leave it.

Then run the check from the author's side: *if I make this change, what does
the paper lose?* In the audited case the three reverts recovered a three-way
contrast with two competitors, the venue-standard scale label, and a sentence
that had been correct all along.

## "I cannot verify it" ≠ "it is wrong"

Items whose evidence is not local — a competitor's PDF not on disk, per-seed
checkpoints not shipped, a caption-data snapshot that cannot be matched to the
original run — go into the report under **Could not verify locally**, with
*what to check, against what, and what to change if it disagrees*. They do
not become edits. Two reproductions disagreeing at the third decimal with no
way to tell which snapshot is authoritative is a note to the author, not a
change to the paper.

## Aggregating a large parallel check

If you fan the check out over many workers and some die (rate limits, session
caps), the aggregation rule must distinguish *checked-and-clean* from
*never-adjudicated*. A rule like "keep if ≥2 of 3 verifiers object" silently
classifies a claim whose three verifiers all died as "cleared". Report the
un-adjudicated count explicitly; the surviving list is a lower bound.

---

<!-- SPDX-License-Identifier: MIT -->
Part of [icassp-paper-condense](https://github.com/WaIdo/icassp-paper-condense) · MIT © 2026 WaIdo (github.com/WaIdo)
