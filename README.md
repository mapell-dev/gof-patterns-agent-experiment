# Does a coding agent reach for a GoF pattern, and when?

The experiment behind the article "<title, link added at publication>". One small C# solution, three tasks, four ways of asking, three repetitions: 36 Claude Code runs, plus a 24-run pilot. Every diff, transcript and test log is here.

## The question

Given a `switch` on a customer type, the textbook trigger for Strategy, does the agent pick the structure the task needs? And what changes when the prompt names the pattern, states the design forces instead, or a design-patterns skill is installed?

- **T1** adds a customer type that differs only by its rate. It looks like a Strategy case and is a table.
- **T2** adds a temporary threshold rule. No pattern pays off.
- **T3** adds two types whose rules have different shapes (capped, tiered), a receipt line per type, and more types announced. Here the pattern pays off.

Variants: (a) the plain ticket, (b) (a) plus "Use the Strategy pattern.", (c) (a) plus the forces without a pattern name, (d) exactly (a) with the skill in `skills/gof-patterns/` installed. The prompts, verbatim, are in [EXPERIMENT.md](EXPERIMENT.md).

## Result (36 runs, `runs/2026-10-29-b/`)

| Task | (a) plain | (b) "Use the Strategy pattern" | (c) forces, no name | (d) plain + skill |
|---|---|---|---|---|
| T1 rate only | rate table 3/3 | Strategy (classes) 3/3 | Strategy (classes) 3/3 | `switch` 2, table 1; skill loaded 3/3 |
| T2 temporary rule | inline, 3 lines, 3/3 | Strategy (classes) 3/3 | inline 3/3, marked temporary | inline 3/3; skill loaded 0/3 |
| T3 different rule shapes | Strategy (classes) 3/3 | Strategy (classes) 3/3 | Strategy (classes) 3/3 | Strategy as `Func` in a record 3/3; skill loaded 3/3 |

Claude Code 2.1.310, model `claude-opus-5-5` in every run, default effort. All 60 runs ended with the tests green. Details, line counts and caveats: [runs/2026-10-29-b/RESULTS.md](runs/2026-10-29-b/RESULTS.md); the pilot and the two design defects it found: [runs/2026-10-29/RESULTS.md](runs/2026-10-29/RESULTS.md).

Read it with its limits: one model, three small tasks, three repetitions per cell. The skill was written by the same person as the tasks, knowing T1 and T2, so (d) shows what a skill that encodes the right signals does, not how skills do in general. In 10 of 36 runs the agent did not run the tests itself because some shell commands were refused; the script ran them after every run.

## Layout

```text
EXPERIMENT.md         protocol, tasks, prompts (verbatim), run setup, outcome classes
baseline/             the .NET 10 solution every run starts from
skills/gof-patterns/  the skill installed in variant (d)
run-experiment.sh     runs the experiment
tabulate.py           builds table.md and results.tsv from the run folders
runs/<batch>/NN-<task><variant>-r<rep>/
  prompt.txt  transcript.jsonl  diff.patch  numstat.txt  name-status.txt  test.log  meta.txt
```

The "pattern used" column is classified by hand from the diffs; `tabulate.py` only counts.

## Run it yourself

Needs Claude Code, the .NET 10 SDK, Python 3, Perl and git. The runs use your Claude Code login; the 36-run batch cost 9.07 USD at list price.

```bash
./run-experiment.sh runs/mine /tmp/gof-work 1 36
python3 tabulate.py runs/mine > runs/mine/table.md
```

Run numbers 1 to 36 follow the interleaved order (repetition, then task, then variant); a finished run is skipped, so a stopped batch resumes. Each run gets a fresh git copy of `baseline/`, starts Claude Code under `env -i` with only project settings (no user plugins, skills, hooks or CLAUDE.md), and is killed after 20 minutes. `CLAUDE_BIN` overrides which `claude` is used.

The only change to the script since the runs: the `claude` path was hard-coded, now it is looked up on `PATH`.

## License

MIT, see [LICENSE](LICENSE).
