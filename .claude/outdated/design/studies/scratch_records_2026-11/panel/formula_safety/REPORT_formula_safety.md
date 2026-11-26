# Formula safety: how others do it, what Polars can reach, and three ways to keep formulas

Added chapter for `tmpAI/panel/recipe_arguments/REPORT_for_eve.md`. Date: 2026-11-17. Nothing was edited, built or decided.

Labels: **run** means I ran it here. **read** means I read it in a file. **web** means a search result read on 2026-11-17. **memory** means not checked.

## 0. Anything that would change a decided behaviour

- **D-0030** says "formulas only from an allowed list of Polars functions (P9)". D-0064 says the allow-list "as built is accepted for now" and "no time or size limit now".
  - Option (a) below, text plus check, keeps both decisions as they are.
  - Options (b) and (c) keep the allow-list idea. They change how a formula is written in the recipe. I found no ledger line that decides the written form of a formula. Read: `.claude/knowledge/decision_ledger.md:59`, `:93`. The grep showed no other formula-form decision, but I did not read the whole ledger.
  - So (b) or (c) needs a new decision from you (D-0165).
- **Open item, not decided.** The spec marks `Expr.inspect` as refused by name: "PROVISIONAL, an agent's choice under D-0030 on 2026-11-17, to be confirmed by the owner" (`recipe_format_spec.md` section 15; `formula_check.py:104-106`). It waits for you.
- **Two points where the check accepts something that is not safe or not reproducible** (run, details in section 4):
  1. `shuffle()` and `sample(n=3)` pass the check and give a different table on each run. Your own rule is "the same data and recipe give the same result". The earlier report lists this as finding 4 of the scientist. No decision exists on seeds.
  2. A very large allocation is accepted, for example `repeat_by(10**12)` and `str.pad_start(4000000000)`. D-0064 says no size limit now. This is recorded, not new.
- **The check is a net with holes, not a proof.** The code says so itself (`formula_check.py:123-137`). Two holes were already found by people on 2026-11-17: `deserialize` and `inspect`. Section 1 shows that similar tools had similar holes, and they were fixed in later versions.

## 1. How comparable projects keep user expressions safe, and how they failed

Short rule from the sources: a list of what is allowed works better than a list of what is forbidden. A list still has holes. The holes appear where the tool lets text run through Python's own text-formatting or attribute lookup.

**OWASP and CWE-95 (eval injection).**
- The advice is to remove dynamic code execution if you can. Replace it with parsers, mappings or an allow-listed interpreter. If you must use eval, check the input strictly and sandbox it. [web: https://wiki.owasp.org/index.php/Direct_Dynamic_Code_Evaluation_('Eval_Injection') and https://dipsylala.github.io/FlawFixingGuidance/CWE-95, read 2026-11-17]. The search showed mirrors of this text. I did not open the current owasp.org page.
- Your app already follows the "allow-list" part and the "second layer" part (empty builtins, `formula_check.py:386-395`, read).

**Restricted AST evaluators (they parse the text, then walk it).**

| Tool | Real advisories (web, 2026-11-17) |
|---|---|
| asteval | CVE-2025-24359, GHSA-3wwr-3g9f-9gc7. A crafted format string leaves the sandbox. Fixed in 1.0.6. Score 8.4. https://advisories.gitlab.com/pypi/asteval/CVE-2025-24359/ |
| simpleeval | CVE-2026-32640, GHSA-44vg-5wv2-h2hg. Chained attribute lookups on allowed objects reached `os` and `sys`. Fixed in 1.0.5. Scores differ by source (8.7 to 9.8). https://advisories.gitlab.com/pypi/simpleeval/CVE-2026-32640/ |
| RestrictedPython | CVE-2023-41039 (sandbox escape through `format`). CVE-2023-37271 (stack frame escape). CVE-2026-76825 (escape when the policy exposes `string.Formatter`; fix in 8.4). https://cvepremium.circl.lu/vuln/cve-2023-41039 and https://advisories.gitlab.com/pypi/restrictedpython/CVE-2026-76825/ |

**Template sandboxes.**
- Jinja2 sandbox: CVE-2024-56326, GHSA-q2x7-8rv6-6q7h. An indirect reference to `str.format` ran Python code. Fixed in 3.1.5. https://advisories.gitlab.com/pypi/jinja2/CVE-2024-56326/ [web]. Sources disagree on severity (5.4 to 7.8).
- dbt uses Jinja. Its own sandbox status I did not check (memory).

**Dataframe tools that take user text.**
- pandas `query` and `eval`: the pandas documentation now warns that `query()` can run arbitrary code like `eval()`. The CVE for it (CVE-2024-9880) is disputed. https://nvd.nist.gov/vuln/detail/CVE-2024-9880 and https://security.snyk.io/vuln/SNYK-PYTHON-PANDAS-8549481 [web].
- Downstream, applications that pass user or model text to it were hit: CVE-2023-39662 (LlamaIndex) and CVE-2026-25481 (Langroid). In Langroid, an allow-list of DataFrame methods was bypassed by chaining allowed methods to reach the `eval` builtin. Fixed in 0.59.32. https://advisories.gitlab.com/pypi/langroid/CVE-2026-25481/ [web].
- This last case matters for you. It is the same shape as your design: a list of allowed methods on a dataframe object. The lesson is that "allowed method" must also mean "reaches nothing outside the data".
- numexpr: the search did not describe numexpr itself. One report said both engines worked in its test [web, weak]. Treat as not checked.

**Structure-based and small-language tools (not searched, memory).**
- Vega expression language: its own parser, an allow-list of functions, no access to the page's objects. Safe by design, but it is a language someone has to maintain.
- JSON-logic: operators are plain data, no text runs. Lines are long.
- Ibis and Polars SQL context: build expressions from structure or SQL text. The SQL context can read files if the table names allow it. Polars `pl.SQLContext` and `pl.sql_expr` exist at module level (run, section 2); your check refuses both because they are not on `MODULE_FUNCTIONS`.

**What this means in short:** every tool that runs real Python on a text got a real advisory. The tools that never run text as Python (structure forms, own parsers) have no such record in my sources. I did not search for advisories on them.

## 2. What Polars can reach beyond the data (installed Polars 1.40.1, run)

Method: I listed the module names and the `Expr` members and namespaces, then called your own functions `refused_members()` and `_allowed()`. Script: `tmpAI/panel/formula_safety/introspect.py` (scratch).

**At module level (`pl.<name>`).** The app allows 38 names (`MODULE_FUNCTIONS`, `formula_check.py:55-62`). The other 161 callables of `pl` are refused by the check, including all of these:
- Reading files: `read_csv`, `read_parquet`, `read_json`, `read_ndjson`, `read_excel`, `read_ods`, `read_avro`, `read_ipc`, `read_delta`, `read_database`, `read_database_uri`, `read_lines`, `read_clipboard`.
- Scanning files: `scan_csv`, `scan_parquet`, `scan_ndjson`, `scan_ipc`, `scan_delta`, `scan_iceberg`, `scan_lines`, `scan_pyarrow_dataset`.
- SQL: `SQLContext`, `sql`, `sql_expr`.
- Global state: `Config`, `StringCache`, `enable_string_cache`, `thread_pool_size`, `set_random_seed`, `register_extension_type`.
- Writing is not at module level. It is on frames (`write_*`, `sink_*`), and a formula does not reach frames.

**On `Expr` (218 public names).** The check allows 200 in `expr`. It refuses these (read from the output):

| Member | What it does | Reason given by the check |
|---|---|---|
| `deserialize`, `from_json` | build an expression from a file or serialised data | reads outside data |
| `register_plugin` | loads a native library | loads outside |
| `map_batches`, `map_elements`, `pipe`, `rolling_map`, `list.to_struct`, `arr.to_struct`, `name.map`, `name.map_fields` | call a Python function | takes a function |
| `meta` (whole namespace; it also has `serialize`, `write_json`, `show_graph`) | read or write expression structure | refused by name |
| `inspect` | prints the column with a text run through `str.format` | refused by name |
| `ext` | extension namespace | not an expression method |

- Polars says about `register_plugin`: "highly unsafe as this will call the C function loaded" (run, docstring of the installed version).
- Polars documents `deserialize` as reading "a path to a file or a file-like object". The pickle warning for serialised Python functions is from the earlier report, which read the Polars documentation. I did not build a payload.

**Allowed today and worth knowing** (run, names confirmed in `_allowed()`):
- `sample`, `shuffle` (random, not reproducible without a seed).
- `repeat_by`, `reshape` (can allocate a lot).
- `str.json_decode` (can raise `PanicException`, not caught by `except Exception`; this is open item (a) in the spec, `recipe_format_spec.md` around line 806, read).
- `bin.decode`, `hash`.
- `list.eval` and `arr.eval` (allowed; they need `pl.element()`, which is not allowed, so they are mostly unusable).
- `str.json_path_match`, `struct.json_encode`.

**Words found in the documentation of allowed members** (run): `path` in `set_sorted`, `http` in many regex examples, `url` in `str.extract`, `json` in the JSON members. These are examples and descriptions, not file access. I did not read each member's behaviour.

**Which the allow-list names today, in one line:** it names 38 module functions and 200 `Expr` members plus the namespaces `str`, `dt`, `list`, `arr`, `cat`, `struct`, `name`, `bin`. It does not name anything that reads files, loads libraries, runs a Python function, or runs SQL (run on 60 hostile lines, section 4). It does not stop random, large or panicking members.

## 3. The comparison table

Three real formulas from the shipped recipes (read, `config/data_analysis_recipes/pipelines/`):
- **F1** (`1_test_data_ST22_dummy/wrangling/QA_population_zscore.yaml:18`): a z-score.
- **F2** (`2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:38`): multi-resistant flag.
- **F3** (`1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:14`): resistance points with `when`, `then`.

The grep for `expression:` in `config/` finds nothing. The recipes write formulas under `named_exprs:` with `pl.col`. There are 19 such lines in the shipped pipelines (grep, run).

### How each formula looks

**(a) Text plus check (today).**
```
n50_zscore: (pl.col('n50') - pl.col('n50').mean()) / pl.col('n50').std()
is_multi_resistant_bool: pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id') > 1
resistance_points: pl.when(pl.col('value') == 'Susceptible').then(pl.lit(0)).when(pl.col('value').cast(pl.String).str.starts_with('unknown')).then(pl.lit(None)).otherwise(pl.lit(1))
```
3 lines. One line per formula.

**(b) Nested YAML structure.** The names and shapes below are my illustration. They are not a design, only the size.
```
n50_zscore:
  div:
    - sub: [{col: n50}, {mean: {col: n50}}]
    - std: {col: n50}
is_multi_resistant_bool:
  gt:
    - over:
        expr:
          n_unique:
            drop_nulls: {col: predicted_phenotype_clean}
        by: sample_id
    - 1
resistance_points:
  when:
    - if: {eq: [{col: value}, Susceptible]}
      then: 0
    - if: {starts_with: [{cast: [{col: value}, String]}, unknown]}
      then: null
    - else: 1
```
About 22 lines for the three. The earlier report says the scientist found 14 and 17 lines for what is one line of text (`REPORT_for_eve.md` section "The Polars side"), the same order of size.

**(c) Own small language.**
```
n50_zscore: (n50 - mean(n50)) / std(n50)
is_multi_resistant_bool: n_unique(drop_nulls(predicted_phenotype_clean)) over sample_id > 1
resistance_points: if value == 'Susceptible' then 0 elif starts_with(str(value), 'unknown') then null else 1
```
3 lines, a bit shorter than (a). Illustration only. I did not design the grammar.

### Table

| | (a) Text plus check | (b) Structure in YAML | (c) Own parser for a small language |
|---|---|---|---|
| **Safety** | Good if the check holds. Today's check refuses all 60 hostile lines of section 4 except the ones about size and randomness. It is a net with holes (`formula_check.py:123-137`); two holes found on 2026-11-17. Text is run by Python `eval` with empty builtins as a second layer (`:386-395`). The tools in section 1 that run Python on text all got advisories. | Strongest. A name not on the fixed list cannot run, because there is no code that handles it. No text is run. | Strong. Same idea as (b), and it is a smaller surface than Python. The parser itself must be written and tested. A parser bug is possible. |
| **Length to write** | 1 line per formula. | About 5 to 8 lines per formula. Long `when` chains are worst. | 1 line. Slightly shorter than (a). |
| **How it reads in a recipe** | Looks like the Polars and R-style code a data scientist knows. A reviewer can copy it into Polars. | Hard to read at a glance. Nesting hides the order of operations. | Reads like a formula. Differs from Polars; a reviewer must learn it. |
| **Work to build (estimate, not measured)** | Done. Keep testing it on each Polars upgrade (the walk tests do this). | Large. A table of every allowed method with its arguments, a reader, tests, a migration of 19 shipped formulas, and a new help in Blueprint. Many days (guess). | Large. A grammar, a parser, an evaluator, error messages, tests, migration, help. Similar to (b), maybe more. Many days (guess). |
| **Effect on decided points** | Keeps D-0030 and D-0064 as they are. | Keeps the allow-list idea of D-0030. Changes the written form, which needs a new decision (D-0165). Breaks every recipe and bundle that holds text formulas. | Same as (b). A new language also changes the "same data and recipe give the same result" story: a result now depends on the app's own parser version. |
| **What the architect of the earlier report proposed** | | | A fourth way is in that report: keep the text, but read it with `ast` and build the expression by calling registered members only, with no `eval` (about 400 lines, run on 15 formulas, `REPORT_for_eve.md` section "The Polars side"). This keeps the written form of (a) and removes the `eval` call. I did not re-check it. |

I did not test (b) or (c) on the formulas. The formulas are illustrations I wrote by hand.

## 4. Test idea: hostile formulas

Method: `tmpAI/panel/formula_safety/hostile.py` (scratch). I called only `formula_problems()` from `libs/utils/src/utils/formula_check.py`. I did not evaluate any of these. Result for each line: REFUSED or ACCEPTED by today's check.

The test should assert that every line marked "must be refused" is refused. Lines marked ACCEPTED are the gap list.

**Attribute walking**
1. `pl.col('a').__class__`: reach the class. REFUSED (underscore).
2. `pl.col('a').str.__class__.__mro__`: walk the class tree. REFUSED.
3. `pl.Expr.__subclasses__()`: list all classes. REFUSED (`pl.Expr` not allowed).
4. `pl.col('a').__init__.__globals__`: read module globals. REFUSED.
5. `pl.os.system('id')`: reach `os` through `pl`. REFUSED.
6. `pl.sys.modules`: reach loaded modules. REFUSED.

**Dunder access**
7. `().__class__.__bases__[0].__subclasses__()`: classic escape. REFUSED.
8. `pl.__builtins__`: reach builtins. REFUSED.
9. `pl.col('a').__reduce__()`: pickle hook. REFUSED.
10. `pl.__spec__.loader`: reach the module loader. REFUSED.
11. `pl.col('a').__getattribute__('x')`: lookup by name. REFUSED.

**Format strings**
12. `'{0.__class__}'.format(pl)`: format string walks attributes (the shape of the asteval and Jinja advisories). REFUSED (`format` is not an expression method on a string).
13. `pl.col('a').inspect('{0.__init__.__globals__}')`: same trick, on Polars `inspect`. REFUSED (by name).
14. `pl.format('{}', pl.col('a')).__class__`: format then attribute. REFUSED.
15. `f'{pl.__file__}'`: f-string reads a name. REFUSED (JoinedStr).

**Comprehension scopes**
16. `[c for c in ().__class__.__mro__]`: comprehension with attribute walking. REFUSED.
17. `[x for x in (1,2)]`: plain list comprehension. REFUSED.
18. `{k: v for k, v in [(1, 2)]}`: dict comprehension. REFUSED.
19. `(x for x in [1])`: generator. REFUSED.

**Lambda and Python functions**
20. `(lambda: __import__('os'))()`: lambda that imports. REFUSED.
21. `pl.col('a').map_elements(lambda v: v)`: per-row Python function. REFUSED.
22. `pl.col('a').map_batches(print)`: batch Python function. REFUSED.
23. `pl.col('a').pipe(print)`: pipe a function. REFUSED.

**Builtins**
24. `eval('1+1')`: eval. REFUSED.
25. `exec('import os')`: exec. REFUSED.
26. `open('/etc/passwd').read()`: file read. REFUSED.
27. `getattr(pl, 'read_csv')`: reach a function by name. REFUSED.
28. `print(pl)`: print. REFUSED.

**Imports**
29. `__import__('os').system('id')`: import a module. REFUSED.
30. `import os`: statement, not an expression. REFUSED (syntax error).
31. `pl.col('a') if True else __import__('os')`: hide it in a conditional. REFUSED.

**Serialised data**
32. `pl.Expr.deserialize('/tmp/x.json')`: build an expression from a file. REFUSED at the module level.
33. `pl.Expr.from_json('{}')`: build from JSON. REFUSED.
34. `pl.col('a').meta.serialize()`: write the structure. REFUSED.
35. `pl.col('a').str.json_decode(pl.Object)`: Polars raises `PanicException`; code that catches only `Exception` does not catch it. **ACCEPTED** (known open item (a) in the spec).
36. `pl.col('a').bin.decode('hex')`: decode bytes. **ACCEPTED**; harmless by itself (my reading, not tested at run time).

**File paths and SQL**
37. `pl.read_csv('/etc/passwd')`: read a file. REFUSED.
38. `pl.scan_parquet('/etc/shadow').collect()`: scan a file. REFUSED.
39. `pl.read_json('x.json')`: read JSON. REFUSED.
40. `pl.lit('/etc/passwd')`: a path as plain text. **ACCEPTED**; correct, since it is only a text value.
41. `pl.sql_expr('1')`: SQL text. REFUSED.
42. `pl.SQLContext()`: SQL context. REFUSED.

**Plugins and global state**
43. `pl.col('a').register_plugin(lib='/tmp/x.so', symbol='f')`: load a native library. REFUSED.
44. `pl.Config.set_tbl_rows(1)`: change the global setting. REFUSED.
45. `pl.col('a').ext.to('x')`: extension namespace. REFUSED.

**Very large allocations**
46. `pl.col('a').repeat_by(10**12)`: very large list. **ACCEPTED** (D-0064: no size limit now).
47. `pl.lit('a') * 10**9`: very large text. **ACCEPTED**. The check refuses a text constant multiplied (`formula_check.py` `visit_BinOp`), but not a call result.
48. `pl.col('a') ** 99999999`: huge exponent. REFUSED (exponent limit 100).
49. `pl.lit(10**10000)`: huge number built by power. REFUSED.
50. `pl.col('a')` plus `.abs()` 500 times: very deep chain. REFUSED (over 2000 characters).
51. `pl.lit('x'*5000)`: text multiplied. REFUSED.
52. `pl.col('a').cast(pl.String).str.pad_start(4000000000)`: 4 GB of padding. **ACCEPTED**.

**Randomness (not a security problem, a reproducibility one)**
53. `pl.col('a').shuffle()`: random order. **ACCEPTED**.
54. `pl.col('a').sample(n=3)`: random rows. **ACCEPTED**.

**Syntax tricks**
55. `pl.col('a') << 5`: shift operator. REFUSED.
56. `*pl.col('a')`: star expression. REFUSED.
57. `pl.col(*['a'])`: starred argument. REFUSED.
58. `pl.col(**{'name':'a'})`: keyword unpacking. REFUSED.
59. `pl.col('a').list.eval(pl.element())`: inner expression. REFUSED (`pl.element` not allowed, a limit not a danger).
60. `pl.col('a').list.eval(pl.col('a').map_elements(print))`: function hidden inside `eval`. REFUSED.

**Count:** 60 lines. 49 refused. 11 accepted: lines 35, 36, 40, 46, 47, 52, 53, 54. That is 8 lines, not 11. The correct count is: 52 refused, 8 accepted (run; I counted from the output list). Of the 8, only 40 and 36 are fine; 35, 46, 47, 52, 53, 54 are the gap list.

For the test, the "must refuse" group (everything refused above, in groups of attribute walking, dunder, format strings, comprehensions, lambda, builtins, imports, plugins, SQL, file readers) is 52 lines. A "known gaps, must stay visible" group holds 35, 46, 47, 52, 53, 54. That group needs your decision on seeds and size (no decision exists).

The existing test file already tests some of this (`test_formula_reads_no_outside_data.py`, read: file read, `inspect`, math function strings, the walk of every allowed member). I did not check which of my 60 lines it already covers.

## 5. A suggestion for the reader (not a decision)

Facts first. I did not see a hole in the check that I could use. The check is also not a proof; the code says so (`formula_check.py:123-137`).
- **Option (a)** is the cheapest and is decided for now (D-0064). Its weak points are the two classes of danger that signature reading cannot see: members dangerous by effect (`inspect`), and members that panic or allocate.
- The earlier report's fourth way (parse the text, call registered members only, no `eval`) keeps your formulas as they are and removes one risk class: a name the check missed would then have no code to run. That is a middle way between (a) and (c). It is an estimate of about 400 lines from the earlier report. I did not test it.
- (b) and (c) cost most and change what recipe authors write.

What needs your word, because no decision exists: (1) require a seed for `shuffle` and `sample`, or refuse them; (2) confirm or remove `inspect` as refused by name; (3) whether `PanicException` from `json_decode` is a problem for you.

## 6. What I did not check

- Primary advisory texts. I read search results only for the CVEs, never the GitHub advisory pages themselves. Scores and fixed versions differ by source and are quoted as the search showed.
- Vega expression language, JSON-logic, Ibis, Polars SQL context and dbt sandbox: from memory, no search.
- The numexpr claim about `query`: weak, from one search result.
- Whether the walk tests in `libs/utils/tests/test_formula_reads_no_outside_data.py` already cover my 60 lines. I read only the test names.
- Whether any of the 8 accepted lines is run by the app and what it costs at run time (not run; I did not call `evaluate_formula`).
- The reading of the `str.format` danger in `inspect` comes from the spec and code comments; I only confirmed it is refused.
- The size of work for (b) and (c) is a guess.
- The three formulas in forms (b) and (c) are written by me, not tested.
- Whether `scout`, panel or reviewer reports contradict the 2026-11-17 `inspect` fix. I did not read them.
- Polars version: 1.40.1 only. Python 3.14 per the earlier report; I did not check.

Files used (all read-only except my scratch in `tmpAI/panel/formula_safety/`):
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/utils/src/utils/formula_check.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/utils/tests/test_formula_reads_no_outside_data.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/design/recipe_format_spec.md`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/recipe_arguments/REPORT_for_eve.md`
- Scratch scripts: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_safety/introspect.py` and `.../hostile.py`
