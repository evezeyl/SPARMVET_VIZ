"""Build the mapping table for the configuration rename (ADR-091) from the rules file.

Read-only in this form: it finds every token and every tracked path that contains a retired
word (persona, manifest, recipe, profile), proposes the new name from
assets/scripts/rename_vocabulary_rules.yaml, and writes a Markdown table that Eve reviews
before any file is changed. Tokens whose new name depends on the context are marked
CONTEXT; tokens that still contain a retired word after the rules are marked UNMAPPED and
must be zero before the table is approved.

The audit exclusions of assets/scripts/audit_old_words.py (history, the two AI agent files)
are respected.

Examples:
  .venv/bin/python assets/scripts/rename_vocabulary.py --out .claude/tasks/config_rename_mapping.md
  .venv/bin/python assets/scripts/rename_vocabulary.py --unmapped
"""

import argparse
import importlib.util
import io
import re
import subprocess
import sys
import tokenize
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
RULES = HERE / "rename_vocabulary_rules.yaml"
_spec = importlib.util.spec_from_file_location("audit_old_words", HERE / "audit_old_words.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)

TOKEN = re.compile(r"[A-Za-z0-9_\-]*(?:persona|manifest|recipe|profile|connector_(?:config|path|template|cache)|sparmvet_connector|local_connector)[A-Za-z0-9_\-]*", re.I)
RETIRED = re.compile(r"persona(?!l)|manifest|recipe|profile|connector_(?:config|path|template|cache)|sparmvet_connector", re.I)
CONTEXT = "STEPS_OR_RECIPE_BY_CONTEXT"


def camel(snake: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in snake.split("_") if p)


def forms(old: str, new: str):
    """The pair in snake, Camel and UPPER spelling."""
    yield old, new
    if "_" in old or True:
        yield camel(old), camel(new) if new != CONTEXT else CONTEXT
    yield old.upper(), new.upper() if new != CONTEXT else CONTEXT


def load_pairs():
    rules = yaml.safe_load(RULES.read_text())
    pairs = []
    for old, new in rules["pairs"]:
        pairs.extend(forms(old, new))
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs, rules


def _substitute(text: str, pairs) -> str:
    """Apply all pairs in ONE pass (longest first), so a new name is never rewritten again."""
    table = dict(pairs)
    rx = re.compile("|".join(re.escape(o) for o, _ in pairs))
    return rx.sub(lambda m: table[m.group(0)], text)


def transform(token: str, pairs, keep):
    """Return (new_token, status) with status auto, CONTEXT, keep or UNMAPPED."""
    marks = {}
    masked = token
    for i, k in enumerate(keep):
        for m in list(re.finditer(re.escape(k), masked, re.I)):
            tag = f"\x00{len(marks)}\x00"
            marks[tag] = m.group(0)
            masked = masked.replace(m.group(0), tag, 1)
    out = _substitute(masked, pairs)
    for tag, val in marks.items():
        out = out.replace(tag, val)
    if out == token:
        return out, "keep"
    if "REMOVE_" in out:
        return out, "REMOVE"
    if CONTEXT in out:
        return out, "CONTEXT"
    leftover = out
    for val in marks.values():
        leftover = leftover.replace(val, "")
    # the new term contains the word recipe on purpose
    leftover = re.sub(r"data_analysis_recipe|DataAnalysisRecipe|DATA_ANALYSIS_RECIPE", "", leftover)
    return out, ("UNMAPPED" if RETIRED.search(leftover) else "auto")


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    return [f for f in out.split("\n") if f and not audit.is_excluded(f) and f != "tree.txt"]


def new_path(path: str, pairs, keep, rules):
    p = path
    for old, new in rules["paths"].items():
        if old == "drop_suffix":
            continue
        if p.startswith(old + "/") or p == old:
            p = new + p[len(old):]
    parts = p.split("/")
    out = []
    for seg in parts:
        seg2, _ = transform(seg, pairs, keep)
        out.append(seg2)
    p = "/".join(out)
    if p.startswith("config/app_features/") and p.endswith("_template.yaml"):
        p = p[: -len("_template.yaml")] + ".yaml"
    # deployment files: the folder already says deployment, so the suffix is dropped
    if p.startswith("config/deployment/"):
        p = p.replace("_deployment_template.yaml", "_template.yaml").replace("_deployment.yaml", ".yaml")
    return p


def subset_pairs(pairs, words):
    """Keep only the pairs whose old spelling contains one of the requested words."""
    words = [w.lower() for w in words]
    return [(o, n) for o, n in pairs if any(w in o.lower() for w in words)]


def rewrite_python_identifiers(path: str, pairs, keep, dry_run: bool):
    """Rename NAME tokens (identifiers, attributes, keyword arguments, import names) only.

    Strings, comments and docstrings are not touched: file formats, configuration keys and
    messages change in their own phases. Returns the number of tokens renamed.
    """
    src = Path(path).read_text(encoding="utf-8")
    lines = src.split("\n")
    edits = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.NAME and RETIRED.search(tok.string):
                new, status = transform(tok.string, pairs, keep)
                if status in ("auto", "CONTEXT") and new != tok.string and CONTEXT not in new:
                    edits.append((tok.start, tok.end, new))
    except tokenize.TokenError as exc:
        raise SystemExit(f"cannot tokenize {path}: {exc}")
    for (sr, sc), (er, ec), new in sorted(edits, reverse=True):
        assert sr == er, f"multi-line name token in {path}"
        line = lines[sr - 1]
        lines[sr - 1] = line[:sc] + new + line[ec:]
    if edits and not dry_run:
        Path(path).write_text("\n".join(lines), encoding="utf-8")
    return len(edits)


def move_files(paths, pairs, keep, rules, dry_run: bool):
    """git mv every path whose new name (from the pairs) differs."""
    moved = []
    for f in paths:
        new = new_path_subset(f, pairs, keep, rules)
        if new != f:
            moved.append((f, new))
            if not dry_run:
                Path(new).parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "mv", f, new], check=True)
    return moved


def new_path_subset(path: str, pairs, keep, rules):
    if path in (rules.get("paths_exact") or {}):
        return rules["paths_exact"][path]
    parts = path.split("/")
    out = "/".join(transform(seg, pairs, keep)[0] if RETIRED.search(seg) else seg for seg in parts)
    if out.startswith("config/deployment/"):
        out = out.replace("_deployment_template.yaml", "_template.yaml").replace("_deployment.yaml", ".yaml")
    return out


TEXT_EXT = {".py", ".yaml", ".yml", ".sh", ".toml", ".css", ".md", ".qmd", ".mmd", ".txt",
            ".json", ".timer", ".service", ".scss"}
# generated or handled elsewhere: the file map is regenerated, settings.json has its own cleanup task
TEXT_SKIP = {"tree.txt", ".claude/settings.json", "CLAUDE.md",
             "app/modules/renamed_keys.py"}
ID_TOKEN = re.compile(r"[A-Za-z0-9_]+(?:[-./][A-Za-z0-9_]+)*")


def _prose_rules(rules, words):
    out = []
    for w in words:
        for rx, new in rules.get("prose", {}).get(w, []):
            out.append((re.compile(rx), new))
    return out


def rewrite_text(path: str, words, pairs, keep, prose, dry_run: bool):
    """Rename ids by the pairs (snake, Camel, UPPER, paths) and plain words by the prose rules."""
    src = Path(path).read_text(encoding="utf-8")
    word_rx = re.compile("|".join(words), re.I) if words else RETIRED
    multi = [(rx, n) for rx, n in prose if " " in n or "-" in rx.pattern]
    single = [(rx, n) for rx, n in prose if (rx, n) not in multi]
    out = src
    for rx, new in multi:
        out = rx.sub(new, out)

    def fix_token(m):
        tok = m.group(0)
        if not word_rx.search(tok):
            return tok
        has_sep = any(c in tok for c in "_-./") or (tok != tok.lower() and tok != tok.upper() and tok[1:] != tok[1:].lower())
        if not has_sep and tok.lower() in {w.lower() for w in words} | {w.lower() + "s" for w in words}:
            return tok  # a plain word: prose rules decide
        new, status = transform(tok, pairs, keep)
        return new if status in ("auto",) else tok

    out = ID_TOKEN.sub(fix_token, out)
    for rx, new in single:
        out = rx.sub(new, out)
    out = re.sub(r"\b([Aa]) (app features|App features)", lambda m: ("An" if m.group(1) == "A" else "an") + " " + m.group(2), out)
    changed = out != src
    if changed and not dry_run:
        Path(path).write_text(out, encoding="utf-8")
    return changed


# ---- context-aware rewriting (code versus prose) -------------------------------------------
_SEP_ID = re.compile(r"(?<![A-Za-z0-9_])(--)?[A-Za-z0-9_]+(?:[-./][A-Za-z0-9_]+)*")
_CAMEL = re.compile(r"[a-z][A-Z]")


PROTECT_PHRASES = []
RULES_PROTECT = [str(p) for p in (yaml.safe_load(RULES.read_text()).get("protect_phrases") or [])]


def _plain_case(part: str):
    """lower, Title or UPPER of a plain word part, or None for mixed case."""
    if part.islower():
        return "lower"
    if part.isupper():
        return "upper"
    if part[:1].isupper() and part[1:].islower():
        return "title"
    return None


def fix_span(seg: str, ctx: str, words, pairs, keep, forms, whole_string: bool = False) -> str:
    """Rename retired words inside one span. ctx is 'code' or 'prose'."""
    word_rx = re.compile("|".join(map(re.escape, words)), re.I)
    protected = {}
    for i, phrase in enumerate(PROTECT_PHRASES):
        for m0 in list(re.finditer(re.escape(phrase), seg, re.I)):
            tag = f"\x01{i}_{len(protected)}\x01"
            protected[tag] = m0.group(0)
            seg = seg.replace(m0.group(0), tag, 1)

    def repl(m):
        tok = m.group(0)
        if not word_rx.search(tok):
            return tok
        core = tok[2:] if tok.startswith("--") else tok
        flag = tok.startswith("--")
        # ids with underscore, dot, slash or CamelCase: the pairs decide, in every context
        if any(c in core for c in "_./") or _CAMEL.search(core):
            new, status = transform(core, pairs, keep)
            return ("--" if flag else "") + (new if status == "auto" else core)
        if "-" in core:
            as_snake, status0 = transform(core.replace("-", "_"), pairs, keep)
            if status0 == "auto" and as_snake != core.replace("-", "_"):
                return ("--" if flag else "") + as_snake.replace("_", "-")
        parts = core.split("-")
        eff = "code" if len(parts) >= 3 else ctx  # error codes and ids such as manifest-file-missing
        out = []
        for i, part in enumerate(parts):
            base = part[:-1] if part.lower().endswith("s") and part[:-1].lower() in words else part
            plural = base != part
            if base.lower() not in words:
                out.append(part)
                continue
            case = _plain_case(base)
            f = forms[base.lower()]
            if case is None:
                out.append(part)
                continue
            if eff == "code" or flag or (whole_string and case == "lower"):
                snake = f.get("snake_pl", f["snake"] + "s") if plural else f["snake"]
                if case == "upper":
                    snake = snake.upper()
                elif case == "title":
                    snake = "".join(p.capitalize() for p in snake.split("_"))
                out.append(snake.replace("_", "-") if (flag or len(parts) > 1) else snake)
            else:
                prose = f.get("prose_pl", f["prose"] + "s") if plural else f["prose"]
                title = f.get("title_pl", f["title"] + "s") if plural else f["title"]
                if case == "upper":
                    word = prose.upper()
                elif case == "title":
                    prev = seg[max(0, m.start() - 40):m.start()].rstrip().split(" ")[-1:]
                    word = title if prev and prev[0][:1].isupper() and prev[0] not in ("The", "A", "An") else prose[:1].upper() + prose[1:]
                else:
                    word = prose
                out.append(word)
        return ("--" if flag else "") + "-".join(out) if eff == "code" or flag else "-".join(out)

    out = _SEP_ID.sub(repl, seg)
    for tag, val in protected.items():
        out = out.replace(tag, val)
    return out


def _split_backticks(text: str):
    """Yield (segment, in_code_span) for inline code spans in a prose text."""
    pos = 0
    for m in re.finditer(r"`[^`\n]+`", text):
        if m.start() > pos:
            yield text[pos:m.start()], False
        yield m.group(0), True
        pos = m.end()
    if pos < len(text):
        yield text[pos:], False


def _yaml_like_line(line: str, fix):
    """Comment part is prose; the code part is code unless a value holds several words."""
    code, hash_, comment = line, "", ""
    m = re.search(r"(^|\s)#", line)
    if m:
        code, comment = line[:m.start() + len(m.group(1))], line[m.start() + len(m.group(1)):]
    km = re.match(r"^(\s*-?\s*[\"']?)([A-Za-z0-9_.\-/]+)([\"']?\s*:)(.*)$", code)
    if km:
        pre, key, post, val = km.groups()
        val_ctx = "prose" if re.search(r"[A-Za-z]+\s+[A-Za-z]+", val.strip().strip("\"'")) else "code"
        code = pre + fix(key, "code", True) + post + fix(val, val_ctx)
    else:
        ctx = "prose" if re.search(r"[A-Za-z]+\s+[A-Za-z]+", code.strip()) else "code"
        code = fix(code, ctx)
    return code + (fix(comment, "prose") if comment else "")


def _recipe_forms(path: str, forms: dict, rules: dict):
    """Forms for the bare word recipe in this file: the noun of its area, steps for keys."""
    nouns = rules["nouns"]
    chosen = "steps"
    for entry in rules.get("recipe_nouns", []):
        if path.startswith(entry["prefix"]):
            chosen = entry["noun"]
            break
    return {**forms, "recipe": nouns[chosen]}, nouns["steps"]


def _apply_phrases(text: str, rules: dict) -> str:
    for rx, repl in rules.get("recipe_phrases", []):
        lower_literal = re.sub(r"^(\\b|\(\?:)+", "", rx)[:1].islower()

        def cb(m, repl=repl, lower_literal=lower_literal):
            out = m.expand(repl)
            return out[:1].upper() + out[1:] if lower_literal and m.group(0)[:1].isupper() else out
        text = re.sub(rx, cb, text, flags=re.I)
    return text


def rewrite_context(path: str, words, pairs, keep, forms, dry_run: bool, rules: dict | None = None) -> bool:
    src = Path(path).read_text(encoding="utf-8")
    suffix = Path(path).suffix
    words = [w.lower() for w in words]
    PROTECT_PHRASES[:] = RULES_PROTECT + (["data analysis recipe", "data-analysis-recipe"] if "recipe" in words else [])
    key_forms = forms
    if "recipe" in words and rules:
        forms, steps_noun = _recipe_forms(path, forms, rules)
        key_forms = {**forms, "recipe": steps_noun}
    phrase = (lambda s: _apply_phrases(s, rules)) if ("recipe" in words and rules) else (lambda s: s)

    def fix(seg, ctx, whole=False):
        seg = phrase(seg) if ctx == "prose" or " " in seg else seg
        # a whole string or a key that is the bare word is a key: always steps
        use = key_forms if whole else forms
        return fix_span(seg, ctx, words, pairs, keep, use, whole)
    if suffix == ".py":
        out = _rewrite_py(src, fix)
    elif suffix in (".md", ".qmd", ".txt", ".mmd"):
        out = _rewrite_markdown(src, fix)
    else:
        out = "\n".join(_yaml_like_line(l, fix) for l in src.split("\n"))
    if out != src and not dry_run:
        Path(path).write_text(out, encoding="utf-8")
    return out != src


def _rewrite_markdown(src: str, fix) -> str:
    out, fenced = [], False
    for line in src.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        if fenced:
            out.append(_yaml_like_line(line, fix))
            continue
        pieces = []
        for seg, is_code in _split_backticks(line):
            pieces.append(fix(seg, "code", True) if is_code else fix(seg, "prose"))
        out.append("".join(pieces))
    return "\n".join(out)


def _rewrite_py(src: str, fix) -> str:
    lines = src.split("\n")
    edits = []
    fstring_depth = 0
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        text = tok.string
        if tok.type == tokenize.COMMENT:
            new = fix(text, "prose")
        elif tok.type == tokenize.STRING:
            body = text.lstrip("rbfuRBFU")
            inner = body.strip("\"'")
            multiline = "\n" in text
            if multiline:
                # embedded YAML or a docstring: key lines are code, sentences are prose
                new = "\n".join(_yaml_like_line(l, fix) for l in text.split("\n"))
            else:
                ctx = "prose" if re.search(r"\s", inner.strip()) else "code"
                new = fix(text, ctx, whole=(ctx == "code"))
        elif tok.type == getattr(tokenize, "FSTRING_MIDDLE", -1):
            new = fix(text, "prose" if re.search(r"\s", text.strip()) else "code")
        elif tok.type == tokenize.NAME:
            new = fix(text, "code")
        else:
            continue
        if new != text:
            edits.append((tok.start, tok.end, new))
    for (sr, sc), (er, ec), new in sorted(edits, reverse=True):
        if sr == er:
            lines[sr - 1] = lines[sr - 1][:sc] + new + lines[sr - 1][ec:]
        else:  # multi-line token: rewrite the covered range as one text
            first, last = lines[sr - 1], lines[er - 1]
            joined = first[:sc] + new + last[ec:]
            lines[sr - 1:er] = joined.split("\n")
    return "\n".join(lines)


def cmd_apply(args) -> int:
    pairs_all, rules = load_pairs()
    keep = [k.lower() for k in rules["keep_substrings"]]
    pairs = subset_pairs(pairs_all, args.words)
    files = [f for f in tracked_files() if f.endswith(".py")]
    total = 0
    if args.what in ("moves", "all"):
        all_files = tracked_files() if args.ext == "all" else files
        py_with_word = [f for f in all_files if any(w in f.lower() for w in args.words)]
        for old, new in move_files(py_with_word, pairs, keep, rules, args.dry_run):
            print(f"move  {old} -> {new}")
        if not args.dry_run:
            files = [f for f in tracked_files() if f.endswith(".py")]
    if args.what in ("identifiers", "all"):
        for f in files:
            if not Path(f).exists():
                continue
            n = rewrite_python_identifiers(f, pairs, keep, args.dry_run)
            if n:
                total += n
                print(f"{n:>4}  {f}")
        print(f"identifier tokens {'to rename' if args.dry_run else 'renamed'}: {total}")
    if args.what == "context":
        forms = rules.get("forms", {})
        n_files = 0
        for f in tracked_files():
            if f in TEXT_SKIP or Path(f).suffix not in TEXT_EXT:
                continue
            try:
                if rewrite_context(f, args.words, pairs, keep, forms, args.dry_run, rules):
                    n_files += 1
                    print(f"context  {f}")
            except (UnicodeDecodeError, tokenize.TokenError, IndentationError) as exc:
                print(f"skip {f}: {exc}")
        print(f"context files {'to change' if args.dry_run else 'changed'}: {n_files}")
    if args.what == "text":
        rules_prose = _prose_rules(rules, args.words)
        n_files = 0
        for f in tracked_files():
            if f in TEXT_SKIP or Path(f).suffix not in TEXT_EXT:
                continue
            if any(f.startswith(p) for w in args.words for p in rules.get("prose_skip_paths", {}).get(w, [])):
                continue
            try:
                if rewrite_text(f, args.words, pairs, keep, rules_prose, args.dry_run):
                    n_files += 1
                    print(f"text  {f}")
            except UnicodeDecodeError:
                continue
        print(f"text files {'to change' if args.dry_run else 'changed'}: {n_files}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", metavar="PATH", help="write the Markdown mapping table here")
    ap.add_argument("--unmapped", action="store_true", help="print only the UNMAPPED tokens and exit 1 if any")
    ap.add_argument("--apply", choices=["identifiers", "moves", "text", "context", "all"],
                    help="change files: rename Python identifiers and/or git mv Python files")
    ap.add_argument("--words", nargs="+", default=[], help="with --apply: retired words to rename, e.g. persona")
    ap.add_argument("--ext", choices=["py", "all"], default="py", help="with --apply moves: which files to move")
    ap.add_argument("--dry-run", action="store_true", help="with --apply: only print what would change")
    args = ap.parse_args()

    if args.apply:
        args.what = args.apply
        if not args.words:
            ap.error("--apply needs --words")
        return cmd_apply(args)

    pairs, rules = load_pairs()
    keep = [k.lower() for k in rules["keep_substrings"]]
    files = tracked_files()

    count: Counter = Counter()
    where: dict = defaultdict(Counter)
    for f in files:
        try:
            text = Path(f).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            text = ""
        for tok in TOKEN.findall(text):
            count[tok] += 1
            where[tok][f] += 1

    rows = []
    for tok, n in count.items():
        new, status = transform(tok, pairs, keep)
        if status == "keep" and new == tok:
            pass
        rows.append((tok, n, new, status))
    unmapped = sorted(r for r in rows if r[3] == "UNMAPPED")

    path_rows = []
    for f in files:
        if RETIRED.search(f):
            np_ = new_path(f, pairs, keep, rules)
            path_rows.append((f, np_, "auto" if np_ != f else "keep"))

    if args.unmapped:
        for r in unmapped:
            print(f"{r[1]:>5}  {r[0]}  ->  {r[2]}")
        print(f"{len(unmapped)} unmapped")
        return 1 if unmapped else 0

    by_status = Counter(r[3] for r in rows)
    lines = ["# Rename mapping table (generated)", "",
             "Generated by `assets/scripts/rename_vocabulary.py` from `assets/scripts/rename_vocabulary_rules.yaml`.",
             "Eve approves the rules and this table before any file is changed (task CONFIG-MAPPING-1).", "",
             f"- distinct tokens: {len(rows)}   occurrences: {sum(count.values())}",
             f"- by status: " + ", ".join(f"{k} {v}" for k, v in sorted(by_status.items())),
             f"- tracked paths to rename: {sum(1 for p in path_rows if p[2] == 'auto')} of {len(path_rows)} paths containing a retired word", "",
             "Status: `auto` the rules decide; `CONTEXT` the bare word `recipe` or `recipes`, decided by the area it is in (see below); `keep` a domain term; `UNMAPPED` needs a rule.", ""]
    lines += ["## Tokens that need a decision by context", "",
              "| token | count | main places |", "|---|---|---|"]
    for tok, n, new, st in sorted((r for r in rows if r[3] == "CONTEXT"), key=lambda r: -r[1]):
        places = ", ".join(f"{k.split('/')[0]}/{k.split('/')[1] if '/' in k else ''}:{v}" for k, v in where[tok].most_common(3))
        lines.append(f"| `{tok}` | {n} | {places} |")
    lines += ["", "## Unmapped", ""]
    lines += [f"- `{r[0]}` ({r[1]}) -> `{r[2]}`" for r in unmapped] or ["none"]
    lines += ["", "## Tokens (all)", "", "| old | count | new | status |", "|---|---|---|---|"]
    for tok, n, new, st in sorted(rows, key=lambda r: (-r[1], r[0])):
        lines.append(f"| `{tok}` | {n} | `{new}` | {st} |")
    lines += ["", "## Paths", "", "| old path | new path | status |", "|---|---|---|"]
    for old, new, st in sorted(path_rows):
        lines.append(f"| `{old}` | `{new}` | {st} |")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
        print(f"wrote {args.out}: {len(rows)} tokens, {len(unmapped)} unmapped, {len(path_rows)} paths")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
