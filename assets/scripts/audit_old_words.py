"""Count the retired configuration words (ADR-091) in file paths and file contents.

Why it exists: the rename of persona, manifest, the old meanings of recipe and the
deployment "profile" must leave no old word in a live file. This audit prints a count per
word and per area so that every rename commit can show the count going down, and the final
screening can prove it reached zero outside the marked exclusions.

By default only files tracked by git are scanned. Use --include-untracked for files git
does not track yet and --include-ignored for git-ignored working files (tmp/, tmpAI/,
issue-drafts/, generated folders). The last screening of the rename uses both.

Exit code with --check: 0 when no word is found outside the exclusions, 1 otherwise.

Examples:
  .venv/bin/python assets/scripts/audit_old_words.py
  .venv/bin/python assets/scripts/audit_old_words.py --include-untracked --include-ignored --check
  .venv/bin/python assets/scripts/audit_old_words.py --word persona --list
  .venv/bin/python assets/scripts/audit_old_words.py --json tmpAI/rename/audit_now.json
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Retired words. Each regex is matched case-insensitively against path and content.
# "recipe" is counted as a whole and reviewed by meaning in the mapping table; only the
# bare word is retired, the full name data_analysis_recipe is the new term and is not counted.
WORDS = {
    "persona": r"persona(?!l)",
    "manifest": r"manifest",
    "recipe": r"(?<!data_analysis_)(?<!data analysis )(?<!data-analysis-)(?<!DataAnalysis)recipe",
    "profile": r"profile",
    "app features template": r"ui/templates|(?:developer|qa|pipeline-[a-z-]+|project-independent|demo-vetinst|web-demo)_template",
    "connector (deployment file)": r"connector_(?:config|path|template|cache)|sparmvet_connector|local_connector",
}

# History and the two AI agent files keep the old words on purpose (ADR-091 point 7).
# A path matches an exclusion when it starts with the prefix or equals the file.
EXCLUDED_PREFIXES = (
    ".git/",
    ".venv/",
    "docs/_freeze/",
    ".claude/logs/",
    ".claude/tasks/archives/",
    ".claude/baselines/",
    ".claude/conversations/",
    ".claude/knowledge/architecture_decisions.md",
    ".claude/tasks/config_rename_strategy.md",
    "assets/scripts/audit_old_words.py",
    "app/modules/renamed_keys.py",
    "libs/utils/src/utils/legacy_keys.py",
    "assets/scripts/migrate_config_vocabulary.py",
    "app/tests/test_legacy_formats.py",
    "app/tests/test_audit_old_words.py",
    "app/tests/test_rename_context.py",
    "app/tests/test_dead_config_keys.py",
    "app/tests/test_shipped_deployments.py",
    "app/tests/test_bootloader_launch.py",
    "assets/scripts/rename_vocabulary.py",
    "assets/scripts/rename_vocabulary_rules.yaml",
    "assets/scripts/inventory_config_keys.py",
    ".claude/tasks/config_rename_mapping.md",
    ".claude/tasks/config_rename_inventory.md",
    ".claude/tasks/config_rename_review.md",
)
# Words allowed only in specific files (the AI agent role files may say persona).
MAX_FILE_BYTES = 2_000_000

# Phrases that keep a retired word on purpose (ADR-091): another meaning, or another tool's term.
# They are removed from a line before it is counted. A line can also carry the marker
# audit:allow-old-word (for a tombstone that names a removed setting).
ALLOWED_PHRASES = {
    "manifest": [r"vendor[ _-]manifest", r"manifest\.json"],
    "profile": [r"(?:AMR|Plasmid|amr|plasmid)[ _]?[Pp]rofile\w*", r"Flavor Profile", r"[Rr]esistance profile",
                r"profiler", r"null-profile", r"distribution profiles", r"EVE_\w*Profile\w*"],
}
ALLOW_MARKER = "audit:allow-old-word"


def git_files(include_untracked: bool, include_ignored: bool) -> list[str]:
    """List files to scan: tracked, optionally untracked and ignored."""
    def run(args):
        out = subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
        return [line for line in out.split("\n") if line]

    files = set(run(["ls-files"]))
    if include_untracked:
        files |= set(run(["ls-files", "--others", "--exclude-standard"]))
    if include_ignored:
        files |= set(run(["ls-files", "--others", "--ignored", "--exclude-standard"]))
    return sorted(f for f in files if Path(f).is_file())


def is_excluded(path: str) -> bool:
    return any(path == p or path.startswith(p) for p in EXCLUDED_PREFIXES)


def area_of(path: str) -> str:
    parts = Path(path).parts
    if parts[0] in ("app", "libs") and len(parts) > 1:
        return f"{parts[0]}/{parts[1]}"
    if parts[0] in (".claude", "config", "assets", "docs") and len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def _masked(word: str, text: str) -> str:
    for rx in ALLOWED_PHRASES.get(word, []):
        text = re.sub(rx, " ", text, flags=re.I)
    return text


def scan(files: list[str], words: dict[str, re.Pattern], show_excluded: bool):
    """Return counters keyed by (word, where, area) plus line hits for --list."""
    counts: Counter = Counter()
    hits: list[tuple[str, str, str, int, str]] = []
    skipped_binary = 0
    for path in files:
        if is_excluded(path) and not show_excluded:
            continue
        for word, rx in words.items():
            n = len(rx.findall(_masked(word, path)))
            if n:
                counts[(word, "path", area_of(path))] += n
                hits.append((word, "path", path, 0, path))
        try:
            p = Path(path)
            if p.stat().st_size > MAX_FILE_BYTES:
                skipped_binary += 1
                continue
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped_binary += 1
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            if ALLOW_MARKER in line:
                continue
            for word, rx in words.items():
                n = len(rx.findall(_masked(word, line)))
                if n:
                    counts[(word, "content", area_of(path))] += n
                    hits.append((word, "content", path, lineno, line.strip()[:140]))
    return counts, hits, skipped_binary


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--include-untracked", action="store_true",
                    help="also scan files git does not track yet")
    ap.add_argument("--include-ignored", action="store_true",
                    help="also scan git-ignored working files (tmp/, tmpAI/, issue-drafts/ ...)")
    ap.add_argument("--word", choices=sorted(WORDS), action="append",
                    help="limit to one word (repeatable); default all")
    ap.add_argument("--list", action="store_true", help="print every hit (path:line: text)")
    ap.add_argument("--show-excluded", action="store_true",
                    help="count the excluded history files too (to see their size)")
    ap.add_argument("--json", metavar="PATH", help="write the counts to a JSON file")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when any word is found outside the exclusions")
    args = ap.parse_args()

    chosen = {w: re.compile(WORDS[w], re.IGNORECASE) for w in (args.word or WORDS)}
    files = git_files(args.include_untracked, args.include_ignored)
    counts, hits, skipped = scan(files, chosen, args.show_excluded)

    by_word: dict[str, Counter] = defaultdict(Counter)
    for (word, where, area), n in counts.items():
        by_word[word][where] += n
    print(f"files scanned: {len(files)}   skipped (binary or large): {skipped}")
    print(f"{'word':<10}{'in paths':>10}{'in content':>12}")
    for w in chosen:
        print(f"{w:<10}{by_word[w]['path']:>10}{by_word[w]['content']:>12}")
    print("\nby area (content + paths):")
    area_totals: Counter = Counter()
    for (word, where, area), n in counts.items():
        area_totals[(area, word)] += n
    for (area, word), n in sorted(area_totals.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {n:>6}  {word:<9} {area}")

    if args.list:
        print()
        for word, where, path, lineno, text in hits:
            loc = f"{path}:{lineno}" if lineno else path
            print(f"[{word}] {where}: {loc}: {text}")
    if args.json:
        out = {f"{w}|{wh}|{a}": n for (w, wh, a), n in sorted(counts.items())}
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(out, indent=2) + "\n")
    if args.check and counts:
        print("\nCHECK FAILED: retired words remain outside the exclusions.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
