#!/bin/bash
# Runs the GoF experiment as EXPERIMENT.md "Run protocol" and "Run setup" describe.
# Usage: run-experiment.sh <out-dir> <work-root> <first> <last>   (run numbers 1..36, interleaved order)
set -u
here=$(cd "$(dirname "$0")" && pwd)
out=$1; work_root=$2; first=$3; last=$4
claude_bin=${CLAUDE_BIN:-$(command -v claude)}
mkdir -p "$out" "$work_root"

# Prompts come verbatim from EXPERIMENT.md, never retyped.
python3 - "$here/EXPERIMENT.md" "$out/prompts" <<'EOF' || { echo "PROMPT EXTRACTION FAILED"; exit 1; }
import re, sys, pathlib
text = pathlib.Path(sys.argv[1]).read_text()
dest = pathlib.Path(sys.argv[2]); dest.mkdir(exist_ok=True)
for task in ("T1", "T2", "T3"):
    sect = text.split(f"### {task}\n", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    blocks = re.findall(r"\*\*\((.)\)(?: and \((.)\))?\*\*\s*```text\n(.*?)\n```", sect, re.S)
    got = {}
    for v1, v2, body in blocks:
        for v in (v1, v2):
            if v: got[v] = body
    assert sorted(got) == ["a", "b", "c", "d"], (task, sorted(got))
    for v, body in got.items():
        (dest / f"{task}{v}.txt").write_text(body)
EOF

skill_sha=$(shasum -a 256 "$here/skills/gof-patterns/SKILL.md" | cut -d' ' -f1)
[ -f "$out/skill.sha256" ] || echo "$skill_sha" > "$out/skill.sha256"
[ "$(cat "$out/skill.sha256")" = "$skill_sha" ] || { echo "SKILL CHANGED SINCE FIRST RUN"; exit 1; }

# Interleaved order: repetition, then task, then variant.
order=()
for rep in 1 2 3; do for task in T1 T2 T3; do for v in a b c d; do order+=("$task $v $rep"); done; done; done

for ((n = first; n <= last; n++)); do
  read -r task v rep <<<"${order[n-1]}"
  id=$(printf '%02d-%s%s-r%s' "$n" "$task" "$v" "$rep")
  dir="$out/$id"; wd="$work_root/$id"
  if [ -e "$dir/meta.txt" ]; then echo "$id already done, skipped"; continue; fi
  rm -rf "$wd"; mkdir -p "$dir" "$wd"
  cp -R "$here/baseline/." "$wd/"
  if [ "$v" = d ]; then mkdir -p "$wd/.claude/skills"; cp -R "$here/skills/gof-patterns" "$wd/.claude/skills/"; fi
  git -C "$wd" init -q
  printf 'bin/\nobj/\n' > "$wd/.git/info/exclude"
  git -C "$wd" add -A
  git -C "$wd" -c user.name=baseline -c user.email=baseline@example.invalid commit -q -m baseline
  base=$(git -C "$wd" rev-parse HEAD)
  cp "$out/prompts/$task$v.txt" "$dir/prompt.txt"
  prompt=$(cat "$dir/prompt.txt")

  echo "$(date -u +%FT%TZ) start $id"
  start=$(date -u +%FT%TZ)
  # perl alarm: a hung run is killed after 20 minutes instead of blocking the rest.
  (cd "$wd" && env -i HOME="$HOME" PATH="$PATH" USER="$USER" TERM=dumb \
    perl -e 'alarm shift; exec @ARGV' 1200 \
    "$claude_bin" -p "$prompt" --setting-sources project --strict-mcp-config --no-chrome \
      --no-session-persistence --permission-mode acceptEdits --permission-prompts none \
      --allowedTools "Bash(dotnet build:*)" "Bash(dotnet test:*)" "Bash(git ls-files:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(find:*)" "Bash(grep:*)" "Bash(head:*)" "Bash(tail:*)" \
      --output-format stream-json --verbose) >"$dir/transcript.jsonl" 2>"$dir/stderr.txt"
  claude_rc=$?
  end=$(date -u +%FT%TZ)

  git -C "$wd" add -A
  git -C "$wd" diff --cached "$base" >"$dir/diff.patch"
  git -C "$wd" diff --cached --numstat "$base" >"$dir/numstat.txt"
  git -C "$wd" diff --cached --name-status "$base" >"$dir/name-status.txt"
  (cd "$wd" && dotnet test >"$dir/test.log" 2>&1)
  test_rc=$?

  printf 'id=%s\ntask=%s\nvariant=%s\nrep=%s\nstart=%s\nend=%s\nclaude_rc=%s\ntest_rc=%s\nbase=%s\nskill_sha256=%s\n' \
    "$id" "$task" "$v" "$rep" "$start" "$end" "$claude_rc" "$test_rc" "$base" "$skill_sha" >"$dir/meta.txt"
  echo "$(date -u +%FT%TZ) done $id claude_rc=$claude_rc test_rc=$test_rc"
done
