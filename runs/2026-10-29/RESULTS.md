# Results, 2026-10-29

24 runs per `../../EXPERIMENT.md`. The script is `run-experiment.sh`, the table builder `tabulate.py` (both at the repository root). Model `claude-opus-5-5`, Claude Code 2.1.310, default effort, skill SHA-256 `a588e536…c867`. Every run ended with `claude` exit 0 and `dotnet test` green (run by the script after the agent finished). Total list cost 5.59 USD, 0.13 to 0.42 per run, on the subscription.

Raw material per run: `NN-<task><variant>-r<rep>/` (prompt, transcript, diff, numstat, test log, meta). The full table, built from those files only, is `table.md` / `results.tsv`.

## Pattern used (read by hand from each diff)

| Task | (a) plain | (b) "Use the Strategy pattern" | (c) forces, no name | (d) plain + skill |
|---|---|---|---|---|
| T1 new customer type | 0/3: rate table `Dictionary<CustomerType, decimal>` (3/3) | 3/3 Strategy (interface + classes) | 3/3 Strategy (interface + classes, 2 to 4 new files) | 0/3: table (1) or `switch` in a `DiscountRate` method (2); skill loaded 3/3 |
| T2 temporary threshold | 0/3: one inline expression | 3/3 Strategy | 0/3: inline, and all 3 mark the rule and its tests "TEMPORARY Q4 promotion, remove at end of December" | 0/3: inline; skill loaded 0/3 |

Lines added (production + tests): T1a 22 to 24, T1d 14 to 22, T1b 42 to 45, T1c 58 to 94; T2 a/c/d 13 to 20, T2b 42 to 47.

What the T1d agents said about the choice (run 12): each type so far is only a percentage, and a list of percentages handles that without new classes. That is the skill's "more types than behavior" rule.

## What this means against "What would change the thesis"

- The plain ticket never over-built: 0 of 6 (a) runs added a type. Under the protocol the article says Anthropic's "Overeagerness" note (Opus 4.5 and 4.6) did not show up for this model on these tasks.
- Naming the pattern always produced it, including in T2 where it does not pay off (3/3): obedience, as planned.
- Stating the forces without a name produced Strategy in T1 (3/3) and nothing in T2 (3/3).
- The skill loaded from its description in every T1 run and in no T2 run, and it did not change the outcome against (a).

## Two problems found in the run, both mine

1. **T1 does not need a pattern.** Discounts that differ only by a rate are data, so a table is the better answer, and the skill's own rules say so. T1 was meant to be "the pattern pays off" and it is not. The experiment as run has no task where Strategy is the right answer, so it cannot show an agent *missing* a pattern it needed. Fixing it means a third task whose variants differ in behavior (for example a student discount capped at an amount, a partner discount tiered by subtotal), with its own 12 runs (about 3 USD list).
2. **The shell allowlist was narrower than the protocol meant.** Only `dotnet build` and `dotnet test` were allowed. Every run's first move, `git ls-files && cat …`, was denied (1 to 4 denials per run). In 11 of 24 runs the agent then never ran `dotnet test` itself; two T1d agents said in their final message that the shell was blocked. (The first version of this file said 12; a per-run count from the transcripts, now the `agent_ran_tests` column, gives 11.) The protocol says the agent may run the tests, so these 11 runs deviate from it. The outcome does not follow the deviation: every cell is 3/3 or 0/3 whether or not the agent ran tests (for example T1a ran tests in r1 and r3, not in r2, and all three wrote the same table). Correctness is unaffected because the script ran the tests afterwards. A rerun would allow read-only commands too (`git`, `ls`, `cat`, `find`, `grep`).

## Table column caveats

- "new_prod_types" counts declarations whose name was not on a removed line, skipping comment lines. The first version counted the edited `enum CustomerType` line and the words "enum value" in comments; both were fixed before this table was built.
- "passed" is the script's own `dotnet test` after the run, not the agent's.
