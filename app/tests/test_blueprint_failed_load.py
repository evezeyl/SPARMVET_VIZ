"""GATE-GAP-1 part B: Blueprint never shows the previous recipe, silently, after a recipe failed to load.

Three places used to only print (`sync_blueprint_mapper`, the TubeMap highlight of `_do_load_component`,
`_do_refresh_blueprint`) and one of them then said "Blueprint: x (53 component(s))" as a success. Now each says which recipe
could not be opened and why, and the stale map, YAML view and component stores are cleared by one function
(`blank_blueprint_view`). The save of a failing recipe is never blocked (Blueprint is where it is fixed).

The tests run the real bodies of the closures of `define_server` (cut out by `ast`, run with recording stand-ins for the
Shiny pieces): `define_server` needs a session, and the bodies are what decides what the user sees.
"""
import ast
from collections import deque
from pathlib import Path

import pytest
import yaml

from app.handlers import blueprint_handlers
from app.tests.tiny_recipe import tiny_recipe

SOURCE = Path(blueprint_handlers.__file__)
PREVIOUS = "PREVIOUS-RECIPE"


class Val:
    def __init__(self, v):
        self.v = v

    def get(self):
        return self.v

    def set(self, v):
        self.v = v


class Ui:
    def __init__(self):
        self.notifications = []
        self.selects = []

    def notification_show(self, message, **kwargs):
        self.notifications.append((kwargs.get("type"), str(message)))

    def update_select(self, *args, **kwargs):
        self.selects.append((args, kwargs))


class Isolate:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeReactive:
    isolate = staticmethod(lambda: Isolate())


def _closure(tree, name):
    define = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == name)
    fn.decorator_list = []
    return fn


class Harness:
    """The names the closures use, as recording stand-ins, and the real closures compiled against them."""

    def __init__(self):
        self.ui = Ui()
        self.includes_map = Val({"prev/rel.yaml": "/prev/rel.yaml"})
        self.component_ctx_map = Val({"prev/rel.yaml": {"role": "wrangling"}})
        self.schema_registry = Val({"PREV": 1})
        self.groups_refresh = Val(0)
        self.ws = type("WS", (), {
            "active_tubemap_mermaid": Val(PREVIOUS), "active_raw_yaml": Val(PREVIOUS),
            "active_component_info": Val({"schema_id": "PREV"}), "logic_stack": Val(["PREV NODE"]),
            "active_lineage_chain": Val([{"rel": "prev"}]), "inline_errors": Val({}),
            "active_upstream": Val([]), "active_downstream": Val([]), "active_fields": Val({}),
            "active_data_analysis_recipe_path": Val(""), "active_component_path": Val(""),
        })()
        self.input = {}
        ns = dict(vars(blueprint_handlers))
        ns.update(
            ui=self.ui, reactive=FakeReactive, wrangle_studio=self.ws, includes_map=self.includes_map,
            component_ctx_map=self.component_ctx_map, schema_registry=self.schema_registry,
            _groups_refresh=self.groups_refresh, input=self.input,
            safe_input=lambda i, k, d=None: i.get(k, d),
            _parse_logic_to_nodes=lambda wrangling, source: [{"action": "n"}],
            _read_bp_draft=lambda *a, **k: None, _draft_dir=None, undo_stack=deque(), _draft_save_time=Val(""),
            _last_load_failure={"key": None},
        )
        ns["input"] = type("In", (), {"stored_data_analysis_recipe_selector": lambda s: self.input.get("stored_data_analysis_recipe_selector")})()
        self.raw_input = self.input
        self.ns = ns
        tree = ast.parse(SOURCE.read_text())
        for name in ("_fail_load", "_do_refresh_blueprint", "_update_dataset_pipelines", "sync_blueprint_mapper", "_do_load_component"):
            fn = _closure(tree, name)
            exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), name, "exec"), ns)
        # sync_blueprint_mapper reads the inputs through safe_input(input, ...): a plain dict
        self.sync_input = self.raw_input

    def seed_previous(self):
        self.ui.notifications.clear()
        self.includes_map.set({"prev/rel.yaml": "/prev/rel.yaml"})
        self.component_ctx_map.set({"prev/rel.yaml": {"role": "wrangling"}})
        self.schema_registry.set({"PREV": 1})
        self.ws.active_tubemap_mermaid.set(PREVIOUS)
        self.ws.active_raw_yaml.set(PREVIOUS)
        self.ws.active_lineage_chain.set([{"rel": "prev"}])
        self.ns["_last_load_failure"]["key"] = None

    def run_sync(self, path):
        self.ns["input"] = self.raw_input
        self.raw_input.update({"sidebar_nav": "Wrangle Studio", "stored_data_analysis_recipe_selector": path})
        self.ns["sync_blueprint_mapper"]()

    def run_update(self, path):
        self.raw_input["stored_data_analysis_recipe_selector"] = path
        self.ns["input"] = type("In", (), {"stored_data_analysis_recipe_selector": lambda s: path})()
        self.ns["_update_dataset_pipelines"]()

    def assert_nothing_of_the_previous_recipe_is_left(self):
        assert self.ws.active_tubemap_mermaid.get() != PREVIOUS
        assert self.ws.active_raw_yaml.get() != PREVIOUS
        assert self.includes_map.get() == {} and self.component_ctx_map.get() == {} and self.schema_registry.get() == {}
        assert self.ws.active_lineage_chain.get() == []

    def warnings(self):
        return [m for t, m in self.ui.notifications if t == "warning"]

    def successes(self):
        return [m for t, m in self.ui.notifications if t == "message"]


@pytest.fixture()
def harness(monkeypatch):
    h = Harness()
    # module-level helpers (_show_load_problems) use the module's own `ui`
    monkeypatch.setattr(blueprint_handlers, "ui", h.ui)
    return h


def _recipe_with_include(folder: Path, name: str, fragment_exists: bool) -> Path:
    recipe = tiny_recipe(name)
    spec = recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]
    recipe["analysis_groups"]["g"]["plots"]["p"]["spec"] = "__INC__"
    text = yaml.safe_dump(recipe, sort_keys=False).replace("__INC__", f"!include '{name}/spec_p.yaml'")
    path = folder / f"{name}.yaml"
    path.write_text(text)
    if fragment_exists:
        (folder / name).mkdir(exist_ok=True)
        (folder / name / "spec_p.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
    return path


def _broken_recipes(tmp_path):
    syntax = tmp_path / "yaml_syntax.yaml"
    syntax.write_text("id: yaml_syntax\ninfo: [unclosed\n  - : :\n")
    missing = _recipe_with_include(tmp_path, "missing_include", fragment_exists=False)
    return {"yaml_syntax": syntax, "missing_include": missing}


KINDS = ["yaml_syntax", "missing_include"]


@pytest.mark.parametrize("kind", KINDS)
def test_refresh_says_the_recipe_cannot_be_opened_and_clears_the_previous_one(harness, tmp_path, kind):
    path = _broken_recipes(tmp_path)[kind]

    result = harness.ns["_do_refresh_blueprint"](str(path))

    assert result is None
    assert any(path.name in w for w in harness.warnings()), harness.ui.notifications
    harness.assert_nothing_of_the_previous_recipe_is_left()


@pytest.mark.parametrize("kind", KINDS)
def test_selecting_a_failing_recipe_gives_no_success_message(harness, tmp_path, kind):
    """The old text was 'Blueprint: x (53 component(s))' as type message, for a recipe that could not be read."""
    path = _broken_recipes(tmp_path)[kind]

    harness.run_update(str(path))

    assert harness.successes() == [], harness.ui.notifications
    assert any(path.name in w for w in harness.warnings())
    harness.assert_nothing_of_the_previous_recipe_is_left()


@pytest.mark.parametrize("kind", KINDS)
def test_the_tubemap_sync_says_so_and_clears_the_stale_map_and_yaml_view(harness, tmp_path, kind):
    path = _broken_recipes(tmp_path)[kind]

    harness.run_sync(str(path))

    assert any(path.name in w for w in harness.warnings()), harness.ui.notifications
    harness.assert_nothing_of_the_previous_recipe_is_left()


@pytest.mark.parametrize("kind", KINDS)
def test_loading_a_component_of_a_failing_recipe_does_not_say_loaded(harness, tmp_path, kind):
    """The TubeMap highlight failed, was printed, and 'Loaded x (N step(s))' followed: the component is new, the map is old."""
    path = _broken_recipes(tmp_path)[kind]
    fragment = tmp_path / "some_fragment.yaml"
    fragment.write_text(yaml.safe_dump({"tier1": [{"action": "polars_fill_null"}]}))
    harness.ns["load_fields_file"] = lambda p: []

    harness.ns["_do_load_component"](str(path), "frag/some_fragment.yaml", {"frag/some_fragment.yaml": str(fragment)}, {})

    assert not any("Loaded" in m for m in harness.successes()), harness.ui.notifications
    assert any(path.name in w for w in harness.warnings()), harness.ui.notifications
    assert harness.ws.active_tubemap_mermaid.get() != PREVIOUS


def test_the_same_failure_is_told_once_not_once_per_effect(harness, tmp_path):
    """Selecting a recipe fires both the refresh and the sync effect: one recipe, one problem, one message."""
    path = _broken_recipes(tmp_path)["yaml_syntax"]

    harness.run_update(str(path))
    harness.run_sync(str(path))

    assert len(harness.warnings()) == 1, harness.ui.notifications


def test_a_failure_is_told_again_after_a_good_recipe_was_opened(harness, tmp_path):
    broken = _broken_recipes(tmp_path)["yaml_syntax"]
    good = _recipe_with_include(tmp_path, "good", fragment_exists=True)

    harness.run_update(str(broken))
    harness.run_update(str(good))
    harness.ui.notifications.clear()
    harness.run_update(str(broken))

    assert len(harness.warnings()) == 1


def test_control_a_recipe_that_loads_still_gets_its_success_message_and_its_map(harness, tmp_path):
    good = _recipe_with_include(tmp_path, "good", fragment_exists=True)

    harness.run_update(str(good))
    harness.run_sync(str(good))

    assert harness.warnings() == []
    assert any("Blueprint: good.yaml" in m for m in harness.successes())
    assert harness.ws.active_tubemap_mermaid.get() != PREVIOUS and harness.ws.active_tubemap_mermaid.get() != ""
    assert harness.includes_map.get() != {}


def test_blank_view_clears_every_store_it_names():
    stores = {name: Val("x") for name in ("includes", "ctx", "registry")}
    ws = type("WS", (), {"active_tubemap_mermaid": Val("x"), "active_raw_yaml": Val("x"), "active_lineage_chain": Val(["x"]),
                         "logic_stack": Val(["node"])})()

    blueprint_handlers.blank_blueprint_view(ws, stores["includes"], stores["ctx"], stores["registry"])

    assert [stores["includes"].get(), stores["ctx"].get(), stores["registry"].get()] == [{}, {}, {}]
    assert (ws.active_tubemap_mermaid.get(), ws.active_raw_yaml.get(), ws.active_lineage_chain.get(),
            ws.logic_stack.get()) == ("", "", [], [])


def test_blank_view_can_keep_the_component_that_was_just_loaded():
    ws = type("WS", (), {"active_tubemap_mermaid": Val("x"), "active_raw_yaml": Val("component text"),
                         "active_lineage_chain": Val([]), "logic_stack": Val(["node"])})()

    blueprint_handlers.blank_blueprint_view(ws, Val({}), Val({}), Val({}), keep_component=True)

    assert ws.active_raw_yaml.get() == "component text" and ws.logic_stack.get() == ["node"]
    assert ws.active_tubemap_mermaid.get() == ""


# --- after a save (part A, Blueprint side): the author is told, the save is never blocked -------------------------

def test_after_a_save_the_author_is_told_when_home_will_not_use_the_recipe(harness):
    class FakeBootloader:
        rejected_data_analysis_recipes = {"x": {"problems": ["[ST02] unknown action 'polars_fill_nulll'"], "contact": None}}
        available_data_analysis_recipes = {}

        def recheck_changed_data_analysis_recipes(self):
            return ["x"]

    told = blueprint_handlers.tell_save_outcome(FakeBootloader(), harness.ui.notification_show)

    assert told == ["x"]
    assert any("x" in w and "HOME" in w and "polars_fill_nulll" in w for w in harness.warnings()), harness.ui.notifications


def test_after_a_save_that_repairs_the_recipe_the_author_hears_it_is_back(harness):
    class FakeBootloader:
        rejected_data_analysis_recipes = {"x": {"problems": ["p"], "contact": None}}
        available_data_analysis_recipes = {}

        def recheck_changed_data_analysis_recipes(self):
            self.rejected_data_analysis_recipes, self.available_data_analysis_recipes = {}, {"x": "/p/x.yaml"}
            return ["x"]

    blueprint_handlers.tell_save_outcome(FakeBootloader(), harness.ui.notification_show)

    assert any("x" in m and "HOME" in m for m in harness.successes()), harness.ui.notifications


def test_after_a_save_of_a_recipe_that_stays_good_nothing_is_said(harness):
    class FakeBootloader:
        rejected_data_analysis_recipes = {}
        available_data_analysis_recipes = {"x": "/p/x.yaml"}

        def recheck_changed_data_analysis_recipes(self):
            return ["x"]

    blueprint_handlers.tell_save_outcome(FakeBootloader(), harness.ui.notification_show)

    assert harness.ui.notifications == []


def test_after_a_save_that_changed_no_recipe_nothing_is_said(harness):
    class FakeBootloader:
        rejected_data_analysis_recipes = {}
        available_data_analysis_recipes = {}

        def recheck_changed_data_analysis_recipes(self):
            return []

    assert blueprint_handlers.tell_save_outcome(FakeBootloader(), harness.ui.notification_show) == []
    assert harness.ui.notifications == []


def test_every_blueprint_writer_of_a_recipe_file_re_checks_after_it_wrote():
    """The three writers (a step, a branch, the info block) each call the re-check; none blocks the write."""
    tree = ast.parse(SOURCE.read_text())
    define = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    callers = {fn.name for fn in ast.walk(define) if isinstance(fn, ast.FunctionDef)
               and any(isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_tell_save_outcome" for c in ast.walk(fn))}
    assert {"_write_branch_plan", "_handle_data_analysis_recipe_save_internal", "_handle_meta_save"} <= callers, callers


@pytest.mark.parametrize("kind", KINDS)
def test_after_a_failed_load_the_component_list_is_emptied_and_says_so(harness, tmp_path, kind):
    """Pinned as built (GATE-GAP-1, nothing new decided): the list of components of the previous recipe is replaced by
    "No components found". Still possible in Blueprint after a failed load: pick another recipe, press Validate (it reads the
    file and lists the problems with their fix), download the recipe bundle. Not possible: see or edit the failing file
    inside Blueprint (the map, the YAML view and the steps are empty): a fix list is Eve's open choice."""
    path = _broken_recipes(tmp_path)[kind]

    harness.ns["_do_refresh_blueprint"](str(path))

    selects = [kw.get("choices") for _args, kw in harness.ui.selects]
    assert ["No components found"] in selects, selects
    assert harness.groups_refresh.get() > 0  # the lists that depend on the recipe redraw
