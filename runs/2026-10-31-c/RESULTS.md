# Third batch: how the skill gets loaded (2026-10-31)

18 runs: tasks T1 to T3, variants (e) and (f), 3 repetitions, interleaved. Same baseline, script, isolation and allowlist as the second batch; `claude-opus-5-5` in Claude Code 2.1.310 in every run (from each transcript's init event); the skill file unchanged (`skill.sha256`). List cost 3.37 USD (0.13 to 0.37 per run). Prompts: `prompts/`, built from EXPERIMENT.md.

- (e) `/gof-patterns` followed by the (a) ticket: explicit invocation.
- (f) the (a) ticket plus "Use the gof-patterns skill.": asking by name, no slash.

## Skill loading

- (f): Claude loaded the skill itself (one `Skill` tool call) in 9 of 9 runs, including all three T2 runs. In the second batch (d) loaded it in T1 3/3, T2 0/3, T3 3/3.
- (e): the invocation loads the skill, and no marker appears in the transcript (see EXPERIMENT.md, Third batch), so `skill_loads` reads 0 by design.

## Pattern used (classified by hand)

Classified from each diff's added declarations and how `Total` uses them, with the second batch's outcome classes for T3. Classified by the AI assistant that ran the batch; not reviewed run by run by the owner.

| Task | (e) explicit invocation | (f) asked by name |
|---|---|---|
| T1 | `switch` 3/3, 0 new types; lines 22, 14, 15 | rate table 3/3, 0 new types; lines 15, 14, 20 |
| T2 | inline 3/3, 0 new types; lines 19, 14, 18 | inline 3/3, 0 new types; lines 18, 14, 18 |
| T3 | C (Strategy as `Func` in a record) 3/3; 2, 1, 2 new types; lines 64, 56, 63 | D (Strategy as classes) 2/3, 6 new types each, lines 100, 97; C 1/3, 2 new types, 65 lines |

Against the second batch:

- T1: same decision as (a) and (d) in all six runs (no Strategy, no new types). (e) used a `switch` like most (d) runs, (f) a table like (a).
- T2: with the skill loaded in all six runs, the structure is the same as (a): an inline change, no new types. No run marks the rule as temporary; the plain ticket does not say it is, so the skill's "temporary change" rule has nothing to match.
- T3: (e) matches (d), Strategy as a `Func` in a record in 3 of 3. (f) loaded the same skill and built classes in 2 of 3, like (a).

## Unmapped customer types (T1 and T3)

Code that fails for a customer type with no rule (a throw or a dictionary indexer): T1 (e) 2 of 3 (runs 01, 13; run 07 keeps `_ => 0m`), T1 (f) 1 of 3 (run 14; runs 02 and 08 keep a no-discount fallback), T3 (e) and (f) 6 of 6.

## Test step

The batch was started with a relative output path. The script runs `dotnet test` after changing into each run's work directory, so the redirect to `test.log` could not open, the test step did not run, and `meta.txt` recorded `test_rc=1` for all 18 runs. The work directories were untouched afterwards: for each run the staged diff against the baseline commit was re-taken and compared byte for byte with the recorded `diff.patch` (all 18 identical), then `dotnet test` was run there and `test.log` and `test_rc` written; each `meta.txt` carries a `test_rerun=` line saying so. All 18 pass. The script now makes the output path absolute.
