"""
@deps
provides: function:load_uploaded_recipe, function:load_config_or_problems, function:uploaded_recipe_report, function:validate_data_analysis_recipe, function:checker_problems, function:checker_advices, const:SHOWN_ADVICES, function:home_advice_entries, function:validate_advice_entries, function:engine_load_problems, function:checker_catalogs, function:validate_data_analysis_recipe_data, function:find_data_analysis_recipes, function:read_data_analysis_recipe_header, function:resolve_contact, function:rejected_recipe_text (GATE-GAP-1), class:DataAnalysisRecipeProblem
consumes: libs/utils/src/utils/config_loader.py, libs/utils/src/utils/recipe_loader.py (load_recipe), libs/utils/src/utils/recipe_loader.py (check_recipe_file), libs/utils/src/utils/recipe_tiers.py (tier3_steps: the lookup `materialize_tier3` uses; the tier-3 steps count as read), libs/utils/src/utils/recipe_graph.py (build_graph: the graph the checker's column checks need, J08), libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/actions/base.py (ACTION_SCHEMAS), libs/viz_factory/src/viz_factory/arguments.py (argument_catalog), app/modules/engine_registry.py (engine_tables: the `engine` field of every action and component, D-0238), app/modules/orchestrator.py
consumed_by: app/tests/test_upload_load_never_exits.py, app/tests/test_upload_recipe_check.py, app/tests/test_data_analysis_recipe_validator.py, app/tests/test_data_analysis_recipe_data_check.py, app/tests/test_retest_data_analysis_recipes.py, app/handlers/blueprint_handlers.py (_handle_validate, BP-VALIDATE-1/VALIDATE-UI-1), app/src/bootloader.py (HOME load gate, ADR-094)
doc: .claude/tasks/tasks.md (BP-VALIDATE-1, VALIDATE-UI-1), .claude/rules/rules_data_engine.md#3, .claude/knowledge/architecture_decisions.md#ADR-094
@end_deps

Data analysis recipe validator (headless, no Shiny).

`validate_data_analysis_recipe` loads the recipe through the real engine path (ConfigManager,
SystemExit caught per ADR-094) and checks every table and join is in a shape
the engine accepts (tiered: tier1 and tier2 as keys, each a mapping with steps, via the same reader the engine uses —
DataWrangler.tier_steps), plus the id == file name rule (ADR-092). `validate_data_analysis_recipe_data`
goes further: it reads the real data and checks it against the declared contract.

Both are wired into the BLUEPRINT "Validate" action (`_handle_validate`, BP-VALIDATE-1 /
VALIDATE-UI-1 / issue #53). History, because both halves were independently "wired" and then
turned out not to be: the data-contract half was written and tested on 2026-05-xx but never
called from the running app until VALIDATE-UI-1 (2026-11-08) fixed that. This function
(`validate_data_analysis_recipe`, the structure/engine-load half) was written for HOME's load
gate (ADR-094) and this docstring then *claimed* it was also wired into Validate — it was not:
Validate only ran a separate hand-rolled static script that never touches ConfigManager, so a
recipe with `id:` != file name or a flat wrangling list could PASS Validate and still fail to
load in HOME. Actually wired in by issue #53 (2026-11-10) — found via Eve's own manual testing,
not caught by re-reading this docstring, which is exactly why it was wrong.

Lives in the app layer on purpose: only this layer may combine utils (ConfigManager) and
transformer (DataWrangler); the libraries stay isolated (ADR-011/016).

Works on any data analysis recipe path, including a temporary upload. It returns every problem found
instead of stopping at the first one, and reports a missing include as a problem.
"""
import difflib
import io
from contextlib import redirect_stderr
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Union

import polars as pl
import yaml
from transformer.data_wrangler import DataWrangler
from utils.step_migration import old_action_hint, removed_action_catalog
from app.modules.engine_registry import engine_tables
from utils.config_loader import ConfigManager
from utils.fix_text import with_fix
from utils.recipe_graph import RecipeGraph, RecipeGraphError, build_graph
from utils.recipe_loader import check_recipe_file, load_recipe
from utils.recipe_tiers import tier3_steps

# What the recipe checker must have looked at before a recipe is accepted (its `coverage`): the form of the file, every
# step against the action registry, every plot layer against the component registry, every step and layer against the engine of its block,
# and the columns of every table (the checks that need the recipe graph, J08).
REQUIRED_COVERAGE = frozenset({"structure", "actions", "components", "engines", "columns"})
# Advices that tell the author what a choice does to the result (a float join key, a join of a table with itself, a position step after an unfixed row order).
# The other advices (missing descriptions and the like) are for the author's own review and stay out of HOME's panel.
SHOWN_ADVICES = frozenset({"J12", "J13", "ST13", "ST14", "ST15"})

# Sections whose entries (dataset id -> spec) may carry tier1 and tier2 (D-0250).
_SCHEMA_SECTIONS = ("data_schemas", "additional_datasets_schemas")


@dataclass(frozen=True)
class DataAnalysisRecipeProblem:
    """One problem found in a data analysis recipe: which file, where in it, what is wrong, how to fix."""

    data_analysis_recipe: str
    location: str
    problem: str
    tip: Optional[str] = None

    def __str__(self) -> str:
        return with_fix(f"{self.data_analysis_recipe}: {self.location}: {self.problem}", self.tip or "", label="Tip")

    def text(self) -> str:
        """The problem and its tip as one sentence, the way HOME's gate notes show it (`utils.fix_text.with_fix`)."""
        return with_fix(self.problem, self.tip or "")


def find_data_analysis_recipes(directory: Union[str, Path]) -> list[Path]:
    """Return the data analysis recipe files (*.yaml) directly inside directory, sorted by name.

    Sub-folders hold the included fragments of a data analysis recipe, not data analysis recipes of their own.
    """
    return sorted(Path(directory).glob("*.yaml"))


def _tiered_bodies(raw: dict) -> Iterator[tuple[str, object]]:
    """Yield (location, body) for every table and every join of a data analysis recipe: the places whose `tier1` and
    `tier2` (each a mapping with `steps`, D-0250) the engine runs."""
    for section in _SCHEMA_SECTIONS:
        entries = raw.get(section)
        if not isinstance(entries, dict):
            continue
        for ds_id, spec in entries.items():
            yield f"{section}.{ds_id}", spec
    if "metadata_schema" in raw:
        yield "metadata_schema", raw["metadata_schema"]
    assemblies = raw.get("joins")
    if isinstance(assemblies, dict):
        for assembly_id, spec in assemblies.items():
            yield f"joins.{assembly_id}", spec


def count_steps_written(node: object) -> int:
    """How many steps are written in a piece of a recipe, wherever they are: the items of a list that are mappings with
    an `action`. It does not know the tiers, on purpose: it is the count the readers of the tiers are held against
    (`engine_load_problems`, `validate_data_analysis_recipe_data`), so a reader that looks in the wrong place cannot
    hide the steps it did not read (D-0050)."""
    if isinstance(node, dict):
        return sum(count_steps_written(value) for value in node.values())
    if isinstance(node, list):
        return sum(1 for item in node if isinstance(item, dict) and "action" in item) + sum(count_steps_written(item) for item in node)
    return 0


def unread_steps_problem(name: str, location: str, written: int, read: int) -> Optional["DataAnalysisRecipeProblem"]:
    """The problem to report when the check read fewer steps than the recipe writes, else None.

    A check that finds steps in the text of the recipe and runs none of them has checked nothing; saying nothing then
    would pass a recipe that was never looked at (the `retest_bad_select_column` recipe passed the load gate for that reason
    when the readers still looked for `wrangling`). It is a fault of the app, never a pass."""
    if written == read:
        return None
    return DataAnalysisRecipeProblem(
        name, location,
        f"the check read {read} of the {written} steps written here, so {written - read} step(s) were not checked",
        "This is a fault of the app, not of the data analysis recipe: report it. A recipe is never accepted on a partial check.")


def _load_error_text(stderr_text: str, exc: BaseException) -> str:
    """Prefer the first [FATAL] line printed by ConfigManager; fall back to the exception."""
    for line in stderr_text.splitlines():
        if line.startswith("[FATAL]"):
            return f"cannot load data analysis recipe: {line.removeprefix('[FATAL]').strip()}"
    return f"cannot load data analysis recipe (YAML or include error): {exc}"


def checker_catalogs() -> dict:
    """The registries as plain data for `check_recipe`: the actions with their form schema, the plot components, the
    arguments each accepts, what each is to plotnine (exact, modified, own) and the themes. The one place that builds them, used by HOME's gate, Blueprint's validate
    action and the gallery check (DEC03: one checker, one set of catalogues). Built here because only the app layer
    may read two libraries."""
    import transformer.actions  # noqa: F401  (importing it registers the actions)
    import viz_factory  # noqa: F401  (importing it registers the plot components)
    from transformer.actions.base import ACTION_SCHEMAS
    from viz_factory.arguments import argument_catalog
    from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS

    arguments = argument_catalog()
    components = set(PLOT_COMPONENTS)
    return {
        "actions": dict(ACTION_SCHEMAS),
        "components": components,
        "component_arguments": {name: (None if arguments.get(name) is None else set(arguments[name])) for name in components},
        "component_kinds": {name: COMPONENT_SCHEMAS[name]["plotnine"] for name in components},
        "themes": {name for name in components if name.startswith("theme_")},
        "old_action_names": removed_action_catalog(),
        **engine_tables(),
    }


FRAGMENT_TOOL = "assets/scripts/migrate_recipe_engine_keys.py"
FRAGMENT_TIERS = ("tier1", "tier2")   # tier3 is a plot's: Blueprint never authors it (ADR-082 section 4)


def fragment_tiers(raw) -> dict[str, list]:
    """The steps of an uploaded fragment, by place (D-0250): `{"steps": [...]}` for a tier file (`steps:` and an optional
    `data_engine:`), or `{"tier1": [...], "tier2": [...]}` for the tiers of a table written as their own keys
    (`tier1: {steps: [...]}`). Empty when the file holds neither.

    Only these shapes are read. A `wrangling` key, a tier written as a list or a `steps` that is not a list are old shapes and
    are not read (no shim): `fragment_old_shape` names what is wrong, so the user is told instead of getting fewer steps."""
    if not isinstance(raw, dict):
        return {}
    found: dict[str, list] = {}
    if isinstance(raw.get("steps"), list):
        found["steps"] = raw["steps"]
    for tier in FRAGMENT_TIERS:
        held = raw.get(tier)
        if isinstance(held, dict) and isinstance(held.get("steps"), list):
            found[tier] = held["steps"]
    return found


def fragment_old_shape(raw) -> Optional[str]:
    """Why an uploaded fragment is in an old shape (it holds a `wrangling` key, or a tier as a list), or None."""
    if not isinstance(raw, dict):
        return None
    if "wrangling" in raw:
        return "'wrangling' is not a key any more: a tier file is `steps: [...]`, the tiers of a table are `tier1: {steps: [...]}`"
    listed = [t for t in FRAGMENT_TIERS if isinstance(raw.get(t), list)]
    if listed:
        return f"{', '.join(listed)} written as a list: a tier is a mapping with its steps (`{listed[0]}: {{steps: [...]}}`)"
    return None


def _fragment_report(raw) -> list[str]:
    """One line per problem of the steps of an upload that is a fragment (a tier file, or the tiers of a table), each step
    against its action schema."""
    from utils.ui_schema import step_problems
    located = [(place, i, s) for place, steps in fragment_tiers(raw).items() for i, s in enumerate(steps, start=1)]
    if not located:
        old = fragment_old_shape(raw)
        if old:
            return [f"[UP02] {old}. Rewrite the file with {FRAGMENT_TOOL}"]
        return ["[UP01] the file has no steps and no data_schemas: nothing to import"]
    actions = checker_catalogs()["actions"]
    lines = []
    for tier, i, step in located:
        where = f"{tier}[{i}]"
        if not isinstance(step, dict) or not isinstance(step.get("action"), str):
            lines.append(f"[ST01] {where}: a step is a mapping with an action")
            continue
        name = step["action"]
        if name not in actions or not isinstance(actions[name], dict):
            hint = old_action_hint(name)
            lines.append(f"[ST02] {where} ({name}): {name!r} is not a registered action" + (f". {hint}" if hint else ""))
            continue
        flat = {**{k: v for k, v in step.items() if k != "params"}, **(step.get("params") or {})}
        for p in step_problems(name, flat, actions[name]):
            lines.append(with_fix(f"[{p.code}] {where} ({name}): {p.message}", p.fix))
    return lines


class _TolerantLoader(yaml.SafeLoader):
    """Reads the shape of a file without resolving `!include` (the tag becomes None)."""


_TolerantLoader.add_multi_constructor("!", lambda loader, suffix, node: None)


def load_uploaded_recipe(path: Union[str, Path]) -> tuple[Optional[dict], list[str]]:
    """Load an uploaded file; return (content, []) or (None, problems). Never raises, `SystemExit` included.

    Blueprint reports and never blocks (rules_data_analysis_recipe_structure.md 11a/11b): ConfigManager ends the
    program on a contradictory file, and a SystemExit inside a Shiny effect freezes the session without a message.
    A whole recipe (it has `data_schemas`) goes through the same capture as
    `engine_load_problems`. A plain wrangling fragment cannot pass ConfigManager (it has no `analysis_groups`), so
    it is read as YAML. Problems are lines in the form of `uploaded_recipe_report`."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, [f"[LOAD] the file cannot be read: {exc}"]
    try:
        shape = yaml.load(text, Loader=_TolerantLoader)
    except yaml.YAMLError as exc:
        return None, [f"[LOAD] the file is not valid YAML: {exc}"]
    if not isinstance(shape, dict) or not shape:
        return None, ["[LOAD] the file is empty or its root is not a mapping: nothing to import"]
    if "data_schemas" not in shape:
        return _load_fragment(path)
    cfg, problems = load_config_or_problems(path)
    if cfg is None:
        return None, problems
    raw = cfg.raw_config
    if not isinstance(raw, dict):
        return None, ["[LOAD] the file root is not a mapping: nothing to import"]
    return raw, []


def _load_fragment(path: Path) -> tuple[Optional[dict], list[str]]:
    """Read a wrangling fragment with the strict recipe reader (`load_recipe`, not `load_strict`).

    `load_strict` only refuses a repeated key and has no `!include`. `load_recipe` is the reader the recipe checker
    uses: it also refuses a repeated key (T10), says "quote it" for an unquoted `on:` (T07, which a bare YAML load
    turns into the key True), and reads `!include` inside the project. A problem it reports means the file is not
    imported, so the user never gets a silent choice between two values."""
    from utils.recipe_loader import load_recipe
    try:
        raw, found = load_recipe(path, include_root=path.parent)
    except Exception as exc:
        return None, [f"[LOAD] the file cannot be read: {exc}"]
    if found:
        return None, [with_fix(f"[LOAD] [{p.code}] {p.path + ': ' if p.path else ''}{p.message}", p.fix) for p in found]
    return raw, []


def load_config_or_problems(path: Union[str, Path]):
    """`ConfigManager(path)` that never ends the program: returns (the ConfigManager, []) or (None, problems).

    ConfigManager calls `sys.exit` on a contradictory file; SystemExit is not an `Exception`, so an `except Exception`
    in a Shiny effect does not stop it and the session freezes without a message. Every place of the app that opens
    a recipe a user can edit or upload goes through this helper (BP-UPLOAD-EXIT-1)."""
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            return ConfigManager(str(path)), []
    except (Exception, SystemExit) as exc:
        return None, [f"[LOAD] {_load_error_text(captured.getvalue(), exc)}"]


def uploaded_recipe_report(raw, profile: str = "build") -> list[str]:
    """One line per problem of an uploaded file (a dictionary), empty when it passes.

    A whole recipe (it has `data_schemas`) goes through the strict checker in the given profile; anything else is a
    wrangling fragment, whose steps are checked one by one with the same step check the checker uses (`step_problems`).
    Blueprint reports and never blocks (rules_data_analysis_recipe_structure.md 11a; profiles: recipe_format_spec.md
    DEC18, line 110), so this only returns text; the caller decides what to show."""
    from utils.recipe_check import check_recipe
    try:
        if not (isinstance(raw, dict) and "data_schemas" in raw):
            if isinstance(raw, dict) or raw is None:
                return _fragment_report(raw)
        result = check_recipe(raw, profile, catalogs=checker_catalogs(), graph=_graph_of(raw))
    except Exception as exc:
        return [f"[CHECK] the recipe could not be checked: {exc}"]
    return [with_fix(f"[{p.code}] {p.path + ': ' if p.path else ''}{p.message}", p.fix) for p in result.errors]


def _graph_of(raw) -> Optional[RecipeGraph]:
    """The recipe graph the checker's column checks need (J08), or None when the recipe cannot be drawn as a graph.

    None is not a silent skip: a recipe the graph refuses (an unknown ingredient, a plot with no table, a cycle, a repeated id) also
    carries an error of the checker itself (J04, PS02, X1, S01, J05 ...), and a recipe checked without the columns is never accepted
    (`REQUIRED_COVERAGE`)."""
    if not isinstance(raw, dict):
        return None
    try:
        return build_graph(raw)
    except RecipeGraphError:
        return None


def _check_file(path: Path, profile: str):
    """`check_recipe_file` with the recipe graph, so that the column checks run in the app as they do in the tests."""
    raw, _ = load_recipe(path)
    return check_recipe_file(path, profile, catalogs=checker_catalogs(), graph=_graph_of(raw))


# The exceptions that a recipe of a wrong shape can make the check raise (a value of the wrong kind where it reads text, a mapping or a list).
# Any other exception is not a fact about the recipe.
_SHAPE_EXCEPTIONS = (TypeError, KeyError, AttributeError, ValueError, IndexError)


def _check_failed_problem(path: Path, exc: BaseException) -> DataAnalysisRecipeProblem:
    """The one problem for a recipe that the check itself failed on: the recipe is refused, never accepted on an exception.

    The same form as `uploaded_recipe_report` ("[CHECK] ..."); it names the recipe and gives the exception. Only an exception that a
    recipe of a wrong shape can cause says that the shape of the recipe is the cause; any other (an import that failed, a file the
    check could not read) says that the check could not run, which is a fault of the app or of its installation."""
    if isinstance(exc, _SHAPE_EXCEPTIONS):
        return DataAnalysisRecipeProblem(
            path.name, "check",
            f"[CHECK] the recipe {path.name} could not be checked: the check itself failed on the shape of this recipe ({type(exc).__name__}: {exc}); the recipe is not accepted",
            "Look for a value of the wrong kind (a list where text is expected, a mapping where a list is expected). If the recipe looks right, this is a fault of the app: report it.")
    return DataAnalysisRecipeProblem(
        path.name, "check",
        f"[CHECK] the recipe {path.name} could not be checked: the check could not run ({type(exc).__name__}: {exc}); the recipe is not accepted",
        "This is a fault of the app or of its installation, not of the recipe: report it.")


def checker_problems(path: Path, profile: str = "run") -> list[DataAnalysisRecipeProblem]:
    """The errors of the strict recipe checker (format 1) for the file, as problems of this module.

    An advice of the checker is not a problem here: it does not stop a recipe. When the checker could not look at the
    actions or the plot components, that is a problem of its own: a recipe is never accepted on a partial check."""
    try:
        result = _check_file(path, profile)
    except Exception as exc:
        return [_check_failed_problem(path, exc)]
    problems = [DataAnalysisRecipeProblem(path.name, p.path or "recipe", f"[{p.code}] {p.message}", p.fix or None)
                for p in result.errors]
    missing = REQUIRED_COVERAGE - result.coverage
    if missing and not problems:
        problems.append(DataAnalysisRecipeProblem(
            path.name, "check", "the recipe check did not cover: " + ", ".join(sorted(missing)),
            "This is a fault of the app, not of the data analysis recipe: report it."))
    return problems


def checker_advices(path: Path, profile: str = "run") -> list[DataAnalysisRecipeProblem]:
    """The advices of the strict recipe checker for the file, as problems of this module; they never stop a recipe.

    An advice says what a choice of the recipe means (a float join key, a join of a table with itself on the same key).
    HOME's recipe choice panel and Blueprint's Validate list them next to the problems; neither refuses the recipe for one."""
    path = Path(path)
    if not path.is_file():
        return []
    try:
        result = _check_file(path, profile)
    except Exception as exc:
        return [_check_failed_problem(path, exc)]
    return [DataAnalysisRecipeProblem(path.name, p.path or "recipe", f"[{p.code}] {p.message}", p.fix or None)
            for p in result.advices if p.code in SHOWN_ADVICES]


def home_advice_entries(advices: dict) -> list[tuple[str, list[str]]]:
    """What HOME's recipe choice panel lists as advice: (recipe name, advice texts), sorted by name, recipes without text left out."""
    return [(name, list(texts)) for name, texts in sorted(advices.items()) if texts]


def validate_advice_entries(advice_problems: list[dict]) -> list[tuple[str, str]]:
    """What Blueprint's Validate lists as advice: (heading, text) per advice, the text being the problem and its tip as one
    sentence (`utils.fix_text.with_fix`, the same as HOME and the command line). Advice never changes PASS or FAIL."""
    return [("Advice: " + p["location"], with_fix(p["problem"], p.get("tip") or "")) for p in advice_problems]


def validate_data_analysis_recipe(path: Union[str, Path], profile: str = "run") -> list[DataAnalysisRecipeProblem]:
    """Return all problems of the data analysis recipe at path (empty list when it is valid).

    First the strict checker of recipe format 1 (`check_recipe`: form, keys, steps against the action registry, plot
    layers against the component registry); a recipe it refuses is not handed to the engine. Then the engine's own
    load (`engine_load_problems`), which finds what only loading shows."""
    path = Path(path)
    if not path.is_file():
        return [DataAnalysisRecipeProblem(path.name, "file", f"data analysis recipe file not found: {path}")]
    try:
        return checker_problems(path, profile) or engine_load_problems(path)
    except Exception as exc:  # the one guard of the gate: a check that raises refuses the recipe, never accepts it
        return [_check_failed_problem(path, exc)]


def engine_load_problems(path: Union[str, Path]) -> list[DataAnalysisRecipeProblem]:
    """What only the engine's own load shows: a missing include, a step list the engine cannot resolve, an id that
    differs from the file name. The second half of `validate_data_analysis_recipe`; it never ends the program."""
    path = Path(path)
    name = path.name
    if not path.is_file():
        return [DataAnalysisRecipeProblem(name, "file", f"data analysis recipe file not found: {path}")]
    # ConfigManager ends the program (SystemExit) and prints a FATAL block to stderr on a
    # contradictory data analysis recipe (ADR-077). A validator used from the app must not do that:
    # catch it and keep the FATAL line as the problem text.
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            raw = ConfigManager(str(path)).raw_config
    except (Exception, SystemExit) as exc:
        return [DataAnalysisRecipeProblem(name, "load", _load_error_text(captured.getvalue(), exc))]
    if not isinstance(raw, dict):
        return [DataAnalysisRecipeProblem(name, "load", "data analysis recipe root is not a mapping")]

    problems: list[DataAnalysisRecipeProblem] = []
    # The file name is the data analysis recipe id (selector, cache, sessions, export). The id: key of the
    # file is the root-key marker of a data analysis recipe and is shown in the audit panel, so it must say the same.
    file_id = raw.get("id")
    if file_id is not None and str(file_id) != path.stem:
        problems.append(DataAnalysisRecipeProblem(
            name, "id", f"id '{file_id}' differs from the file name '{path.stem}'.",
            f"Set 'id: {path.stem}', or rename the file to '{file_id}.yaml'; the file name without .yaml is the data analysis recipe id."))
    read = 0
    block_problems = False
    for location, body in _tiered_bodies(raw):
        seen: set[str] = set()
        for tier in ("tier1", "tier2"):
            try:
                read += len(DataWrangler.tier_steps(body, tier))
            except Exception as exc:
                message = str(exc)
                block_problems = True
                # the same message for both tiers (an old container): report it once
                if message in seen:
                    continue
                seen.add(message)
                problems.append(DataAnalysisRecipeProblem(name, f"{location}.{tier}", message, getattr(exc, "tip", None)))
    # The tier-3 steps of the plots: read by the one lookup `DataOrchestrator.materialize_tier3` uses (`utils.recipe_tiers.tier3_steps`),
    # per plot entry as the groups write them (a plot id written twice is then counted twice as written and once as read: refused).
    plot_written = 0
    for group in (raw.get("analysis_groups") or {}).values() if isinstance(raw.get("analysis_groups"), dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        for plot_id, entry in (plots or {}).items() if isinstance(plots, dict) else []:
            if not isinstance(entry, dict):
                continue
            plot_written += count_steps_written(entry)
            read += len(tier3_steps(raw, plot_id))
    if not block_problems:
        # Written: everything in the recipe except `analysis_groups` and `plots` (ConfigManager keeps a flat copy of the plot entries
        # under `plots`: counting it would count every plot step twice) plus the whole of each plot entry, so that a step list the
        # engine does not read in a plot (anywhere but `tier3.steps`) is written and never read, and the count refuses it.
        written = count_steps_written({key: value for key, value in raw.items() if key not in ("analysis_groups", "plots")}) + plot_written
        unread = unread_steps_problem(name, "recipe", written, read)
        if unread is not None:
            problems.append(unread)
    return problems


def _declared_columns(fields) -> list[str]:
    """Column names declared by an input_fields / output_fields block (dict form only)."""
    return list(fields) if isinstance(fields, dict) else []


def validate_data_analysis_recipe_data(path: Union[str, Path], raw_data_dir: Union[str, Path],
                           data_lookup: str = "data_analysis_recipe_paths",
                           imports_dir: Union[str, Path, None] = None) -> list[DataAnalysisRecipeProblem]:
    """Read every dataset of the data analysis recipe and check its declared fields against the real columns.

    Unlike validate_data_analysis_recipe this reads the data files (issue #18). For each data schema it
    builds the dataset the way the app does (input contract, tier-1 wrangling) and reports:
      - a dataset that cannot be loaded (missing file, missing input column, value that does not
        fit its type), with the engine's message and tip;
      - a wrangling step that cannot run on the declared types.
    """
    from app.modules.orchestrator import DataOrchestrator

    path = Path(path)
    name = path.name
    captured = io.StringIO()
    try:
        with redirect_stderr(captured):
            raw = ConfigManager(str(path)).raw_config
    except (Exception, SystemExit) as exc:
        return [DataAnalysisRecipeProblem(name, "load", _load_error_text(captured.getvalue(), exc))]

    orchestrator = DataOrchestrator(path.parent, Path(raw_data_dir), data_lookup=data_lookup, imports_dir=imports_dir)
    schemas: list[tuple[str, str, dict]] = []
    for section in _SCHEMA_SECTIONS:
        entries = raw.get(section)
        if isinstance(entries, dict):
            schemas += [(f"{section}.{ds_id}", ds_id, spec) for ds_id, spec in entries.items() if isinstance(spec, dict)]
    if isinstance(raw.get("metadata_schema"), dict):
        schemas.append(("metadata_schema", "metadata_schema", raw["metadata_schema"]))

    problems: list[DataAnalysisRecipeProblem] = []
    for location, ds_id, spec in schemas:
        try:
            frame = orchestrator.prepare_ingredient(ds_id, spec, recipe_id=path.stem, recipe=raw)
            columns = frame.collect_schema().names()
        except Exception as exc:
            problems.append(DataAnalysisRecipeProblem(name, location, f"dataset cannot be loaded: {exc}", getattr(exc, "tip", None)))
            continue
        # The steps this check runs are the tier-1 steps the engine reads (the same reader as `prepare_ingredient`): every step
        # written in the table, apart from its tier 2 (run when a plot reads the table), must have been among them (D-0050).
        written = count_steps_written({key: value for key, value in spec.items() if key != "tier2"})
        unread = unread_steps_problem(name, location, written, len(DataWrangler.tier_steps(spec, "tier1")))
        if unread is not None:
            problems.append(unread)
            continue
        # WHY: collect_schema() only plans the query. A step whose input type does not fit (a text step on a
        # column declared categorical) fails when the plan runs, so run it on one row (issue #71). Every Polars error
        # of that run is a problem of the recipe or of its data and is reported (D-0050): a step that fails on the
        # values (a text cast to a number) would otherwise pass this check and fail when the recipe is built.
        try:
            frame.head(1).collect()
        except (pl.exceptions.SchemaError, pl.exceptions.ColumnNotFoundError) as exc:
            problems.append(DataAnalysisRecipeProblem(
                name, location, f"wrangling cannot run on this dataset: {exc}",
                "Suggestion: compare the declared type of the column with what the wrangling step expects (a text step needs a String column, not a Categorical one)."))
        except pl.exceptions.PolarsError as exc:
            problems.append(DataAnalysisRecipeProblem(
                name, location, f"wrangling cannot run on this dataset: {exc}",
                "Suggestion: look at the wrangling step that the message names and at the values of the column it reads, then change the step or correct the data."))
    return problems


def read_data_analysis_recipe_header(path: Union[str, Path]) -> Optional[dict]:
    """Read just the `id:`/`info:` keys of a data analysis recipe, tolerant of a broken body.

    HOME's load gate (ADR-094) rejects a data analysis recipe whose structure or data fails
    validation — but the rejection message still needs to show *who to contact*, and the
    `info.contact` convention (data_analysis_recipe_info.py) lives in the same file as the
    broken part. A plain `yaml.safe_load` (no `!include` resolution, no ConfigManager, no
    engine involvement) reads what it can; a YAML file broken badly enough that even this
    fails returns None rather than raising — the caller falls back to the deployment contact.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    return {"id": raw.get("id"), "info": raw.get("info") if isinstance(raw.get("info"), dict) else {}}


def resolve_contact(info: Optional[dict], deployment_contact: Optional[str]) -> Optional[str]:
    """Two-tier contact resolution (ADR-094): the data analysis recipe's own `info.contact`,
    else the deployment's own contact, else None (never a fabricated placeholder)."""
    if info:
        recipe_contact = info.get("contact")
        if recipe_contact:
            return str(recipe_contact)
    return deployment_contact or None


def _clean_contact(value) -> Optional[str]:
    """A contact that is empty after strip counts as absent."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def export_contact_record(info: Optional[dict], deployment_contact: Optional[str]) -> dict:
    """Contact and its origin for the export bundle (D-0208): whose contact it is is stated, never guessed.

    The values are cleaned first (a contact of only spaces is absent, the written text is stripped) and then given to
    resolve_contact(), which keeps its own behaviour. When neither tier names a contact the value is None.
    """
    recipe_contact = _clean_contact((info or {}).get("contact"))
    cleaned_info = {"contact": recipe_contact} if recipe_contact else {}
    contact = resolve_contact(cleaned_info, _clean_contact(deployment_contact))
    if contact is None:
        return {"contact": None, "contact_source": None}
    source = "recipe (info.contact)" if recipe_contact else "deployment (branding.contact)"
    return {"contact": contact, "contact_source": source}


def export_contact_readme_line(record: dict) -> str:
    """The one plain README line for the contact record (whitespace runs, newlines included, become one space)."""
    if record.get("contact") is None:
        return "Contact          : the recipe names no contact (info.contact is empty) and the deployment names none"
    text = " ".join(str(record["contact"]).split())
    return f"Contact          : {text} (from the {record['contact_source']})"


def rejected_recipe_text(name: str, record: dict) -> str:
    """What HOME says when the recipe it was showing no longer passes the gate (GATE-GAP-1): which one, why, who to ask.

    `record` is an entry of `bootloader.rejected_data_analysis_recipes`. At most three problems are listed."""
    problems = [str(p) for p in record.get("problems", [])]
    shown = "; ".join(problems[:3]) or "see Validate in Blueprint"
    more = f" (and {len(problems) - 3} more)" if len(problems) > 3 else ""
    contact = record.get("contact") or "not configured for this deployment"
    return (f"The data analysis recipe '{name}' failed its checks after its files changed, so HOME does not use it. "
            f"Problems: {shown}{more}. Open it in Blueprint, fix it and save; HOME takes it back when it passes. "
            f"Contact: {contact}.")
