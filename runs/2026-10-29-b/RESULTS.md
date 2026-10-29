# Results, second batch, 2026-10-29

36 runs per `../../EXPERIMENT.md` (T1, T2, T3 x 4 variants x 3 repetitions, interleaved), with the wider read-only allowlist. Model `claude-opus-5-5` in every run, Claude Code 2.1.310, default effort, skill SHA-256 `a588e536…c867` (the same file as the first batch). Every run ended with `claude` exit 0 and the script's own `dotnet test` green. Total list cost 9.07 USD, 0.14 to 0.53 per run, on the subscription.

The first batch (`../2026-10-29/`, 24 runs on T1 and T2) is the pilot. Its T1 and T2 cells came out the same as here.

Raw material per run: `NN-<task><variant>-r<rep>/`. Full table: `table.md` / `results.tsv`, built only from those files.

## Pattern used (classified by hand)

Classified from each diff's added declarations and how `Total` uses them; the T3a and T3d production diffs and the T1d and T2 lines were read in full. T3 uses the outcome classes fixed before the runs: (A) parallel switches or inline branches, (B) parameter table, (C) Strategy as functions, (D) Strategy as classes.

| Task | (a) plain | (b) "Use the Strategy pattern" | (c) forces, no name | (d) plain + skill |
|---|---|---|---|---|
| T1 new type, rate only | 0/3: rate table 3/3 | 3/3 Strategy (classes) | 3/3 Strategy (classes) | 0/3: `switch` 2, table 1; skill loaded 3/3 |
| T2 temporary threshold | 0/3: inline, 3 lines | 3/3 Strategy (classes) | 0/3: inline, all 3 marked temporary | 0/3: inline; skill loaded 0/3 |
| T3 new types, different rule shapes | **D 3/3** | D 3/3 | D 3/3 | **C 3/3**: `record Discount(string ReceiptLine, Func<decimal, decimal> AmountFor)` per type; skill loaded 3/3 |

Lines added (production + tests), per repetition: T3a 100, 123, 109; T3b 123, 121, 116; T3c 210, 150, 159; T3d 64, 70, 77. T1 and T2 as in the pilot (T1a 15 to 22, T1b/c 45 to 74, T2 a/c/d 13 to 22, T2b 43 to 50).

Within D the units differ: T3a r1 and r3 wrote one class per customer type (`StudentDiscount`, `PartnerDiscount`); T3a r2 and T3b r3 wrote one type per rule shape (`PercentOff`, `CappedPercentOff`, `TieredPercentOff`) and mapped types to configured instances.

## Against "What would change the thesis"

- **Over-building, plain ticket:** 0 of 6 (a) runs in T1 and T2 added a type where none was needed (0 of 12 with the pilot). The "Overeagerness" note did not show for this model on these tasks.
- **Pattern when it pays, plain ticket:** T3 (a) picked the pattern 3 of 3 without being told (class D). The agent tells the cases apart by itself here: a table for rate-only T1, one line for temporary T2, an interface for T3.
- **Naming the pattern:** always produced it, including T2 where it does not pay (3/3, obedience).
- **Forces without a name:** Strategy in T1 and T3, nothing in T2. In T1 that is more than the task needed; the forces sentence ("must not require changing the code of the existing discounts") pushed a rate-only change into classes.
- **The skill:** loaded from its description in all T1 and T3 runs, never in T2. It changed nothing in T1 and T2. In T3 it changed the form, not the decision: Strategy as functions instead of classes, 3 of 3, with 64 to 77 lines instead of 100 to 123. That matches its own rule "the language already covers it: a delegate or `Func<>` is a strategy", which is Norvig's invisible pattern.

## Deviations and caveats

- **Agents that never ran the tests themselves: 10 of 36** (04, 05, 08, 11, 16, 18, 19, 24, 30, 31), against 11 of 24 in the pilot. The wider allowlist helped only partly: the opening `git ls-files && cat $(…)`, `git -C <path> …` and some `find` calls are still refused, and after several refusals those agents concluded the shell was blocked and said so in their final message. Outcomes do not follow this: every cell is 3/3 or 0/3 whether the agent ran tests or not (T3c r1 did not, r2 and r3 did, all three class D). Correctness is covered by the script's `dotnet test` after each run. Removing the deviation entirely would need `--permission-mode bypassPermissions` in a sandbox, which this setup does not have.
- **Who wrote what:** the skill was written knowing T1 and T2 (disclosed). T3 was written after the skill, by the same author, knowing the skill; the skill file did not change (same SHA-256 in both batches). So T3 is not a blind test of the skill either.
- **Table columns:** `new_prod_types` counts declarations whose name is not on a removed line, skipping comments; `passed` is the script's `dotnet test`; `agent_ran_tests` is true when a `dotnet test` call by the agent was not denied.
