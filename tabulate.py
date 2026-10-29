"""Builds the results table from the raw run folders (EXPERIMENT.md, "What is recorded per run").

Usage: python3 tabulate.py <out-dir>   -> prints a Markdown table, writes results.tsv beside the runs.
Reads only meta.txt, transcript.jsonl, diff.patch, name-status.txt, numstat.txt and test.log.
"Pattern used" is not computed here; it is read by hand from each diff.
"""
import json, pathlib, re, sys

DECL = re.compile(r"\b(class|interface|record|enum|struct)\s+([A-Za-z_]\w*)")


def meta(d):
    return dict(l.split("=", 1) for l in (d / "meta.txt").read_text().splitlines() if "=" in l)


def transcript(d):
    info = {"model": "", "version": "", "skill_listed": False, "skill_loads": 0, "cost": "", "turns": "", "denials": "", "result": "", "agent_tests": False}
    dotnet_calls = set()
    for line in (d / "transcript.jsonl").read_text().splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("type") == "system" and m.get("subtype") == "init":
            info["model"], info["version"] = m.get("model", ""), m.get("claude_code_version", "")
            info["skill_listed"] = "gof-patterns" in (m.get("skills") or [])
        elif m.get("type") == "assistant":
            for c in m["message"]["content"]:
                if c.get("type") == "tool_use" and c["name"] == "Skill" and c["input"].get("skill") == "gof-patterns":
                    info["skill_loads"] += 1
                if c.get("type") == "tool_use" and c["name"] == "Bash" and "dotnet test" in c["input"].get("command", ""):
                    dotnet_calls.add(c["id"])
        elif m.get("type") == "result":
            info["cost"] = round(m.get("total_cost_usd") or 0, 2)
            info["turns"] = m.get("num_turns")
            info["denials"] = len(m.get("permission_denials") or [])
            info["result"] = m.get("subtype")
            denied = {x["tool_use_id"] for x in m.get("permission_denials") or []}
            info["agent_tests"] = bool(dotnet_calls - denied)
    return info


def diff_stats(d):
    added_files = [l.split("\t", 1)[1] for l in (d / "name-status.txt").read_text().splitlines() if l.startswith("A\t")]
    plus = minus = 0
    for l in (d / "numstat.txt").read_text().splitlines():
        a, r, _ = l.split("\t", 2)
        plus += int(a) if a.isdigit() else 0
        minus += int(r) if r.isdigit() else 0
    # A declaration counts as new only if no removed line declared the same name (an edited enum is not new).
    added, removed, current = {}, set(), ""
    for l in (d / "diff.patch").read_text().splitlines():
        if l.startswith("+++ "):
            current = l[6:] if l.startswith("+++ b/") else ""
        elif l.startswith("--- "):
            continue
        elif l[:1] in "+-" and current.endswith(".cs") and not l[1:].lstrip().startswith(("//", "*")):
            for kind, name in DECL.findall(l):
                if l[0] == "+":
                    added[f"{kind} {name}"] = current
                else:
                    removed.add(f"{kind} {name}")
    new = {k: f for k, f in added.items() if k not in removed}
    prod = [k for k, f in new.items() if "Tests" not in f]
    test = [k for k, f in new.items() if "Tests" in f]
    return added_files, plus, minus, prod, test


def tests(d):
    t = (d / "test.log").read_text()
    m = re.search(r"Passed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+)", t) or re.search(r"Failed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+)", t)
    return (m.group(2), m.group(1)) if m else ("?", "?")


def main(out):
    rows = []
    for d in sorted(p for p in pathlib.Path(out).iterdir() if (p / "meta.txt").exists()):
        mt, tr = meta(d), transcript(d)
        added, plus, minus, prod, test = diff_stats(d)
        passed, failed = tests(d)
        rows.append({
            "run": mt["id"], "task": mt["task"], "var": mt["variant"], "rep": mt["rep"],
            "claude_rc": mt["claude_rc"], "test_rc": mt["test_rc"], "passed": passed, "failed": failed,
            "new_prod_types": len(prod), "prod_types": ", ".join(prod), "new_test_types": len(test),
            "files_added": len(added), "lines_+": plus, "lines_-": minus,
            "skill_listed": tr["skill_listed"], "skill_loads": tr["skill_loads"],
            "model": tr["model"], "version": tr["version"], "turns": tr["turns"], "cost_usd": tr["cost"],
            "denials": tr["denials"], "agent_ran_tests": tr["agent_tests"], "result": tr["result"],
        })
    if not rows:
        sys.exit("no finished runs found")
    cols = list(rows[0])
    (pathlib.Path(out) / "results.tsv").write_text("\n".join(["\t".join(cols)] + ["\t".join(str(r[c]) for c in cols) for r in rows]) + "\n")
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join(str(r[c]) for c in cols) + " |")


if __name__ == "__main__":
    main(sys.argv[1])
