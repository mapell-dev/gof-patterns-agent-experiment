# Does a coding agent reach for a GoF pattern, and when?

The experiment behind the article [GoF patterns when the agent writes the code](https://mapell.dev/articles/gof-patterns-when-the-agent-writes-the-code). One small C# solution, three tasks, four ways of asking, three repetitions: 36 Claude Code runs, plus a 24-run pilot before them and an 18-run third batch after. Every diff, transcript and test log is here.

The owner designed the experiment. An AI assistant in the owner's Claude Code session set up and executed the runs, drafted the skill and classified the outcomes, at the owner's instruction.

## The question

Given a `switch` on a customer type, the textbook trigger for Strategy, does the agent pick the structure the task needs? And what changes when the prompt names the pattern, states the design forces instead, or a design-patterns skill is installed?

- **T1** adds a customer type that differs only by its rate. It looks like a Strategy case and is a table.
- **T2** adds a temporary threshold rule. No pattern pays off.
- **T3** adds two types whose rules have different shapes (capped, tiered), a receipt line per type, and more types announced. Here a pattern is defensible.

Variants: (a) the plain ticket, (b) (a) plus "Use the Strategy pattern.", (c) (a) plus the forces without a pattern name, (d) exactly (a) with the skill in `skills/gof-patterns/` installed. The prompts, verbatim, are in [EXPERIMENT.md](EXPERIMENT.md).

## Result (36 runs, `runs/2026-10-29-b/`)

| Task | (a) plain | (b) "Use the Strategy pattern" | (c) forces, no name | (d) plain + skill |
|---|---|---|---|---|
| T1 rate only | rate table 3/3 | Strategy (classes) 3/3 | Strategy (classes) 3/3 | `switch` 2, table 1; skill loaded 3/3 |
| T2 temporary rule | inline, 3 lines, 3/3 | Strategy (classes) 3/3 | inline 3/3, marked temporary | inline 3/3; skill loaded 0/3 |
| T3 different rule shapes | Strategy (classes) 3/3 | Strategy (classes) 3/3 | Strategy (classes) 3/3 | Strategy as `Func` in a record 3/3; skill loaded 3/3 |

Claude Code 2.1.310, model `claude-opus-5-5` in every run, default effort. All 78 runs (pilot, second and third batch) ended with the tests green. Details, line counts and caveats: [runs/2026-10-29-b/RESULTS.md](runs/2026-10-29-b/RESULTS.md); the pilot and the two design defects it found: [runs/2026-10-29/RESULTS.md](runs/2026-10-29/RESULTS.md).

Read it with its limits: one model, three small tasks, three repetitions per cell. The skill was drafted by the AI assistant and accepted by the owner, knowing T1 and T2, so (d) shows what a skill that encodes the right signals does, not how skills do in general. In 10 of 36 runs the agent never ran the tests itself. Each of those runs had two or more shell commands refused, but so did some runs that did run the tests, and every run had at least one refusal, so the table does not show the refusals as the cause. The script ran the tests after every run.

## Third batch (18 runs, `runs/2026-10-31-c/`)

In (d) Claude loaded the skill on its own in T1 and T3 but never in T2. The third batch asks what a user can do about that, with the skill file unchanged: (e) invokes it explicitly, `/gof-patterns` followed by the (a) ticket; (f) is the (a) ticket plus "Use the gof-patterns skill."

| Task | (e) explicit invocation | (f) asked by name |
|---|---|---|
| T1 rate only | `switch` 3/3 | rate table 3/3 |
| T2 temporary rule | inline 3/3 | inline 3/3 |
| T3 different rule shapes | Strategy as `Func` in a record 3/3 | Strategy (classes) 2/3, `Func` in a record 1/3 |

In (f) Claude loaded the skill in 9 of 9 runs. An explicit invocation leaves no marker in the transcript, so for (e) the load is not counted. Details: [runs/2026-10-31-c/RESULTS.md](runs/2026-10-31-c/RESULTS.md).

## Layout

```text
EXPERIMENT.md         protocol, tasks, prompts (verbatim), run setup, outcome classes
baseline/             the .NET 10 solution every run starts from
skills/gof-patterns/  the skill installed in variants (d), (e) and (f)
run-experiment.sh     runs the experiment
tabulate.py           builds table.md and results.tsv from the run folders
runs/<batch>/NN-<task><variant>-r<rep>/
  prompt.txt  transcript.jsonl  diff.patch  numstat.txt  name-status.txt  test.log  meta.txt
```

The "pattern used" column is read from the diffs, not computed: the AI assistant classified each run, and the owner did not review the classification run by run. `tabulate.py` only counts.

## Run it yourself

Needs Claude Code, the .NET 10 SDK, Python 3, Perl and git. The runs use your Claude Code login; the 36-run batch cost 9.07 USD at list price, the third batch 3.37 USD.

```bash
./run-experiment.sh runs/mine /tmp/gof-work 1 36
python3 tabulate.py runs/mine > runs/mine/table.md
```

Run numbers 1 to 36 follow the interleaved order (repetition, then task, then variant); a finished run is skipped, so a stopped batch resumes. A fifth argument selects the variants (default `"a b c d"`); the third batch is `./run-experiment.sh runs/mine-c /tmp/gof-work-c 1 18 "e f"`. Each run gets a fresh git copy of `baseline/`, starts Claude Code under `env -i` with only project settings (no user plugins, skills, hooks or CLAUDE.md), and is killed after 20 minutes. `CLAUDE_BIN` overrides which `claude` is used.

Changes to the script since the 36 runs: the `claude` path was hard-coded, now it is looked up on `PATH`; the variants became a fifth argument for the third batch; and the output path is made absolute, after a relative one made the third batch skip its test step (the tests were re-run afterwards, see that batch's RESULTS.md).

## License

MIT, see [LICENSE](LICENSE).
