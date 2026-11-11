# Experiment: does an agent reach for a GoF pattern, and when?

> The protocol as fixed before the runs, 2026-10-29. A first batch of 24 runs on T1 and T2 (`runs/2026-10-29/`) found two defects in the design; T3 and a wider allowlist were added the same day and all three tasks were rerun (`runs/2026-10-29-b/`). Each folder's `RESULTS.md` has the outcome.

## Baseline

`baseline/`, a .NET 10 solution: `Shop` (class library) and `Shop.Tests` (xUnit). One file of production code:

```csharp
public enum CustomerType { Regular, Loyal }

public record OrderLine(string Sku, decimal UnitPrice, int Quantity);

public record Order(CustomerType Customer, IReadOnlyList<OrderLine> Lines);

public static class PriceCalculator
{
    public static decimal Total(Order order)
    {
        var subtotal = order.Lines.Sum(l => l.UnitPrice * l.Quantity);
        var discount = order.Customer switch
        {
            CustomerType.Loyal => subtotal * 0.05m,
            _ => 0m
        };
        return subtotal - discount;
    }
}
```

Two tests: a regular customer pays 250, a loyal one 237.50. Checked 2026-10-29: `dotnet test` passes 2 of 2; with the loyal rate mutated to 6% one test fails (expected 237.50, actual 235.00); restored, 2 of 2 again.

Why this shape: a `switch` on a type code is the textbook trigger for Strategy ("replace conditional with polymorphism"), so the pattern is a live option in both tasks. Only the forces differ.

## Tasks

- **T1, looks like Strategy, is data.** A new customer type with its own discount, more types announced. Designed as the case where the pattern pays off; the first batch showed it does not: the types differ only by a rate, so a rate table is the better answer and the skill's own rules say so. Kept, because "looks like a pattern case, is a table" is a result in itself.
- **T2, the pattern does not pay off.** One threshold rule on top of the customer discount, temporary.
- **T3, the pattern pays off.** Two new types whose rules have different shapes (flat, capped, tiered), a receipt line per type, and more types announced.

T3 is checked as a positive control before any run (the step T1 skipped). Without a pattern the simplest correct answer is two parallel `switch` expressions over four types, one for the amount and one for the receipt line, so every monthly type edits both. A parameter table no longer fits: it needs a rate, an optional cap, an optional threshold and an optional second rate, a bag of optional fields. With a pattern each type's amount and receipt line live in one unit. Every "Use a pattern when" rule of the skill points to the pattern; none of its "Do not" rules applies. This makes the pattern the defensible answer, not the only correct one: four-arm switches still work, and the article says so.

Outcome classes for T3, fixed before the runs: (A) parallel switches or inline branches; (B) a parameter table; (C) Strategy as functions (a delegate or `Func<>` per type in a table or record); (D) Strategy as classes (an interface or base class with one implementation per type). C and D count as "used the pattern"; C is Norvig's invisible pattern.

## Prompts (verbatim, sent as the single first message)

Variants: (a) the ticket as a person would write it; (b) (a) plus the pattern's name; (c) (a) plus the forces, without a pattern name; (d) exactly (a), with the skill installed.

### T1

**(a) and (d)**

```text
Add a new customer type, Employee, with a 20% discount. Sales plans to add another customer type with its own discount about once a month; partners and students are next. Keep the tests passing and add a test for the new type.
```

**(b)**

```text
Add a new customer type, Employee, with a 20% discount. Sales plans to add another customer type with its own discount about once a month; partners and students are next. Keep the tests passing and add a test for the new type. Use the Strategy pattern.
```

**(c)**

```text
Add a new customer type, Employee, with a 20% discount. Sales plans to add another customer type with its own discount about once a month; partners and students are next. Keep the tests passing and add a test for the new type. Adding a customer type must not require changing the code of the existing discounts, and each discount must be testable on its own.
```

**(e)**

```text
/gof-patterns Add a new customer type, Employee, with a 20% discount. Sales plans to add another customer type with its own discount about once a month; partners and students are next. Keep the tests passing and add a test for the new type.
```

**(f)**

```text
Add a new customer type, Employee, with a 20% discount. Sales plans to add another customer type with its own discount about once a month; partners and students are next. Keep the tests passing and add a test for the new type. Use the gof-patterns skill.
```

### T2

**(a) and (d)**

```text
Orders with a subtotal of 1,000 or more get an extra 3% off the amount left after the customer discount. Keep the tests passing and add a test for the new rule.
```

**(b)**

```text
Orders with a subtotal of 1,000 or more get an extra 3% off the amount left after the customer discount. Keep the tests passing and add a test for the new rule. Use the Strategy pattern.
```

**(c)**

```text
Orders with a subtotal of 1,000 or more get an extra 3% off the amount left after the customer discount. Keep the tests passing and add a test for the new rule. This is a promotion for this quarter only; it will be removed at the end of December, so keep the change small and easy to delete.
```

**(e)**

```text
/gof-patterns Orders with a subtotal of 1,000 or more get an extra 3% off the amount left after the customer discount. Keep the tests passing and add a test for the new rule.
```

**(f)**

```text
Orders with a subtotal of 1,000 or more get an extra 3% off the amount left after the customer discount. Keep the tests passing and add a test for the new rule. Use the gof-patterns skill.
```

### T3

**(a) and (d)**

```text
Add two new customer types. Student: 10% off, but never more than 30 per order. Partner: 10% off when the subtotal is up to 1,000, and 15% off the whole order when it is above 1,000. Every customer's discount must also appear on the receipt as one line, for example "Loyal: 5% off" or "Student: 10% off, max 30". Sales plans to add another customer type with its own discount rule about once a month. Keep the tests passing and add tests for the new behavior.
```

**(b)**

```text
Add two new customer types. Student: 10% off, but never more than 30 per order. Partner: 10% off when the subtotal is up to 1,000, and 15% off the whole order when it is above 1,000. Every customer's discount must also appear on the receipt as one line, for example "Loyal: 5% off" or "Student: 10% off, max 30". Sales plans to add another customer type with its own discount rule about once a month. Keep the tests passing and add tests for the new behavior. Use the Strategy pattern.
```

**(c)**

```text
Add two new customer types. Student: 10% off, but never more than 30 per order. Partner: 10% off when the subtotal is up to 1,000, and 15% off the whole order when it is above 1,000. Every customer's discount must also appear on the receipt as one line, for example "Loyal: 5% off" or "Student: 10% off, max 30". Sales plans to add another customer type with its own discount rule about once a month. Keep the tests passing and add tests for the new behavior. Adding a customer type must not require changing the code of the existing discounts, and each discount rule must be testable on its own.
```

**(e)**

```text
/gof-patterns Add two new customer types. Student: 10% off, but never more than 30 per order. Partner: 10% off when the subtotal is up to 1,000, and 15% off the whole order when it is above 1,000. Every customer's discount must also appear on the receipt as one line, for example "Loyal: 5% off" or "Student: 10% off, max 30". Sales plans to add another customer type with its own discount rule about once a month. Keep the tests passing and add tests for the new behavior.
```

**(f)**

```text
Add two new customer types. Student: 10% off, but never more than 30 per order. Partner: 10% off when the subtotal is up to 1,000, and 15% off the whole order when it is above 1,000. Every customer's discount must also appear on the receipt as one line, for example "Loyal: 5% off" or "Student: 10% off, max 30". Sales plans to add another customer type with its own discount rule about once a month. Keep the tests passing and add tests for the new behavior. Use the gof-patterns skill.
```

T2 (b) deliberately asks for a pattern the task does not need. It measures obedience, not judgment, and the article says so.

## Run protocol

- 4 variants x 3 tasks x 3 repetitions = 36 runs (second batch; the first batch of 24 on T1 and T2 is kept as a pilot), all on one day, one model (the Claude Code default that day, version recorded), in interleaved order (T1a, T1b, T1c, T1d, T2a, ..., T3d, then the next repetition) so a mid-day change hits every variant alike.
- Each run starts from a fresh copy of `baseline/` at a fixed commit, in a clean Claude Code configuration: no global CLAUDE.md, no plugins, no hooks, no memory. Variant (d) adds only `skills/gof-patterns/` to that configuration.
- Non-interactive, one message, no follow-up. The agent may edit files and run `dotnet build` and `dotnet test`.
- The skill is frozen before the first run; its SHA-256 goes into the results.
- The skill was written by the same person who wrote T1 and T2, with both tasks in view: its "third case" rule matches T1 and its "temporary change" rule matches T2. Kept as is; the article states this next to the (d) results, so (d) reads as "a skill that encodes the right signals", not as a blind test of skills in general.

### Run setup (checked 2026-10-29 with two Haiku probes, about 0.003 USD in all, Claude Code 2.1.310)

Each run, from the run's own fresh directory (a git repo with the baseline committed; for (d) the commit also holds `.claude/skills/gof-patterns/SKILL.md`, so the skill never shows in the diff):

```bash
env -i HOME="$HOME" PATH="$PATH" USER="$USER" TERM=dumb claude -p "<prompt>" --setting-sources project --strict-mcp-config --no-chrome --no-session-persistence --permission-mode acceptEdits --permission-prompts none --allowedTools "Bash(dotnet build:*)" "Bash(dotnet test:*)" "Bash(git ls-files:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(find:*)" "Bash(grep:*)" "Bash(head:*)" "Bash(tail:*)" --output-format stream-json --verbose > transcript.jsonl
```

What the probes showed (from the `system/init` event and the debug log):

- `--setting-sources project` drops the user settings: none of the 8 installed plugins (ponytail, superpowers and the rest) is enabled, 0 plugin hooks are registered, and 0 user skills load. What remains is Claude Code's own: 3 built-in plugins and its bundled skills (`simplify`, `code-review`, `verify` and others). Those are part of any default install, so they stay in every variant and the init event's skill list goes into the results.
- The project skill is listed only where it was copied: init showed `gof-patterns` as the one project skill.
- No CLAUDE.md is found (the debug log searched 7 ancestor directories, 0 found), and the probe model answered NONE when asked for user-level instructions. The second half is the model's own report, not a file check.
- Auto-memory points at a per-path directory that does not exist, so a new directory per run means no memory.
- `env -i` matters: launched from inside a Claude Code session, the child inherits that session's variables (for example `CLAUDE_EFFORT=high`). Runs go from a plain shell or with `env -i`; the model and effort are then the defaults, read from the init event.
- A skill load appears in the transcript as a `tool_use` named `Skill` with input `{"skill": "gof-patterns"}`, which a script can count. The probe asked for the skill by name; whether (d) loads it from its description alone is the thing the experiment measures.
- First batch: with only `dotnet build` and `dotnet test` allowed, every run's first exploration command (`git ls-files && cat …`) was denied and 11 of 24 agents then never ran the tests themselves, so the second batch also allows read-only commands (`git ls-files/status/diff/log`, `ls`, `cat`, `find`, `grep`, `head`, `tail`). Write commands stay denied. Checked on run 1 of the second batch (T1a): the agent's opening `git ls-files && cat $(…)` is still refused (the `$(…)` substitution is not covered by an allowlist entry), but it then ran plain `git ls-files` and `dotnet test 2>&1 | tail` and both were allowed. One run is one sample; the batch table records per run whether the agent ran the tests itself.
- `dotnet test` ran non-interactively under these flags with no permission denial. Per `claude --help` (not yet seen in a run), any other command is refused without a prompt and listed in the result's `permission_denials`, which is recorded.
- Not checked: an actual file edit under `acceptEdits` in print mode (the probe was told not to edit). The first real run shows it; if it fails, the run is discarded and the setup fixed before the rest. (It worked: every run's edits were applied.)

## Third batch: how the skill gets loaded (2026-10-31)

In the second batch (d) relies on Claude loading the skill from its description, and in T2 it never did (0 of 3). The third batch asks what a user can do about that, with the skill file unchanged (same SHA-256):

- (e) invokes the skill explicitly: `/gof-patterns` at the start of the message, followed by the (a) ticket. In print mode Claude Code loads the first skill named this way, with the rest of the line as its arguments.
- (f) is the (a) ticket plus one sentence asking for the skill by name, without a slash: "Use the gof-patterns skill." Whether Claude then loads it is its own call.

2 variants x 3 tasks x 3 repetitions = 18 runs, same baseline, script, isolation, allowlist, model and Claude Code version (2.1.310) as the second batch, in interleaved order, into `runs/2026-10-31-c/`: `run-experiment.sh runs/2026-10-31-c <work-root> 1 18 "e f"`. Both variants have the skill installed, as (d) does.

How a load shows in the transcript, checked on 2026-10-31 with two Haiku probes (about 0.004 USD): an explicit `/gof-patterns` invocation leaves no `Skill` tool call and no other marker in the stream-json output, yet the model quoted the skill's "Before you finish" line verbatim with no file or tool access; the same question without the slash got "NONE". So `skill_loads` counts only loads Claude makes itself (a `Skill` tool call). For (e) the skill is loaded by the invocation, and the column reads 0 unless Claude also calls the tool.

## What is recorded per run

| Field | How |
|---|---|
| Tests pass | exit code of `dotnet test` after the run, captured without a pipe |
| New types | `class`, `interface`, `record`, `enum` declarations added in the diff |
| Files added, lines added and removed | `git diff --numstat` against the baseline commit |
| Pattern used | read by hand from the diff: none, Strategy, other (named) |
| Skill loaded (d only) | from the run transcript |
| Model, version, effort | from the run transcript (init event) |
| Skills available | init event's skill list |
| Permission denials | result event's `permission_denials` |

Raw diffs and transcripts are kept; the table is derived from them. The diff and test columns come from the diff and the test log alone, so they work for any agent; the model, skill-load, cost, denial and agent-ran-tests columns read the Claude Code transcript. A declaration count from the diff is naive (it counts a nested record the same as a new file); the hand-read "pattern used" column is the check on it.

## What would change the thesis

- If (a) in T2 regularly produces a pattern, the over-engineering claim stands for the current model and the review section carries the article.
- If (a) never over-builds in T2, Anthropic's "Overeagerness" note (Opus 4.5 and 4.6) is out of date for this model, and the article says so; the thesis then rests on the prompt and review halves.
- If (a) in T3 picks C or D, the agent reaches for the pattern when it pays without being told; if it picks A or B, naming the forces or the pattern is what gets it there, and that is the prompt half of the thesis.
- If (d) never loads the skill, the skill section becomes "a skill that never fires does nothing", and that is the result.
