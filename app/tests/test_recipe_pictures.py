"""The picture check of all recipes (`assets/scripts/recipe_pictures.py`) detects what it must detect.

Small temporary recipes, not the shipped ones. A recipe is written, its pictures are stored with `--write`, a change is made,
and `--check` must pass or fail. A changed figure title and a changed theme must be seen; a plot missing from the new run, and a plot
that errors, must be reported and fail the check. The comparison itself is proved able to fail in `test_the_comparison_can_fail`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_recipe_pictures.py -q
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# imported now: the tests change the working folder (a recipe's data path is relative to it), `PYTHONPATH=.` must not matter then
import app.modules.cache_keys  # noqa: F401
import app.modules.data_analysis_recipe_validator  # noqa: F401
import app.modules.orchestrator  # noqa: F401
import utils.config_loader  # noqa: F401
import viz_factory.viz_factory  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]


def _load_script():
    spec = importlib.util.spec_from_file_location("recipe_pictures", ROOT / "assets" / "scripts" / "recipe_pictures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rp = _load_script()

PLOT = """      {name}:
        label: {name}
        spec:
          target_dataset: C
          title: {title}
          theme: {theme}
          mapping: {{x: group}}
          layers:
            - name: geom_bar
              params: {{}}
"""


class Project:
    """A tiny recipe with a data file in a temporary folder, and the commands of the tool on it."""

    def __init__(self, root: Path):
        self.root = root
        self.recipes = root / "recipes"
        self.recipes.mkdir()
        self.data = root / "data" / "T.tsv"
        self.data.parent.mkdir()
        self.data.write_text("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\n")
        self.stored = root / "stored"
        self.write_recipe({"p": ("Hello", "theme_gray")})

    def write_recipe(self, plots: dict, layer: str = "geom_bar") -> None:
        body = "".join(PLOT.format(name=n, title=t, theme=th) for n, (t, th) in plots.items()).replace("geom_bar", layer)
        (self.recipes / "tiny.yaml").write_text(f"""id: tiny
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info: {{label: Tiny}}
data_schemas:
  T:
    label: T
    source: {{type: local_tsv, path: data/T.tsv}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}
      group: {{original_name: group, type: Categorical, label: Group}}
    wrangling: {{tier1: [], tier2: []}}
joins:
  C:
    label: C
    ingredients:
      - dataset_id: T
    steps: {{tier1: [], tier2: []}}
analysis_groups:
  g:
    label: G
    plots:
{body}""")

    def args(self, mode: str, folder: Path, *more) -> list:
        return [mode, str(folder), "--recipe-dir", str(self.recipes), "--data-root", str(self.root / "data"),
                "--palettes", str(self.root / "no_palettes.yaml"), *more]

    def write(self) -> int:
        return rp.main(self.args("--write", self.stored))

    def check(self) -> int:
        return rp.main(self.args("--check", self.stored, "--out", str(self.root / "check")))

    def manifest(self) -> dict:
        return json.loads((self.stored / "manifest.json").read_text())


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the data path of a recipe is relative to the project root
    return Project(tmp_path)


def test_an_unchanged_recipe_passes_and_is_recorded_by_recipe_group_plot(project, capsys):
    assert project.write() == 0
    plots = project.manifest()["plots"]
    assert [p["key"] for p in plots] == ["tiny::g::p"]
    assert plots[0]["status"] == "drawn" and plots[0]["width_px"] == 960 and plots[0]["height_px"] == 600
    assert project.check() == 0
    assert "PICTURES IDENTICAL" in capsys.readouterr().out


def test_a_changed_figure_title_is_detected(project, capsys):
    project.write()
    project.write_recipe({"p": ("Another title", "theme_gray")})
    assert project.check() == 1
    out = capsys.readouterr().out
    assert "different" in out and "tiny::g::p" in out and "pixels differ" in out
    assert list((project.root / "check" / "differences").glob("*_diff.png"))


def test_a_changed_theme_is_detected(project, capsys):
    project.write()
    project.write_recipe({"p": ("Hello", "theme_bw")})
    assert project.check() == 1
    assert "different" in capsys.readouterr().out


def test_a_plot_missing_from_the_new_run_is_reported(project, capsys):
    project.write_recipe({"p": ("Hello", "theme_gray"), "q": ("Second", "theme_gray")})
    project.write()
    assert {p["plot"] for p in project.manifest()["plots"]} == {"p", "q"}
    project.write_recipe({"p": ("Hello", "theme_gray")})
    assert project.check() == 1
    out = capsys.readouterr().out
    assert "missing" in out and "tiny::g::q" in out


def test_a_new_plot_is_reported(project, capsys):
    project.write()
    project.write_recipe({"p": ("Hello", "theme_gray"), "q": ("Second", "theme_gray")})
    assert project.check() == 1
    assert "new" in capsys.readouterr().out


def test_a_recipe_that_no_longer_loads_makes_the_check_fail(project, capsys):
    project.write()
    project.write_recipe({"p": ("Hello", "theme_gray")}, layer="geom_not_registered")
    assert project.check() == 1
    out = capsys.readouterr().out
    assert "error-changed" in out and "tiny::g::p" in out


def test_a_plot_that_cannot_be_drawn_is_recorded_with_its_error_and_fails_the_check(project, capsys, monkeypatch):
    project.write()
    from viz_factory.viz_factory import VizFactory
    real = VizFactory.render

    def broken(self, frame, raw, plot_id, *a, **k):
        raise RuntimeError("the draw broke")

    monkeypatch.setattr(VizFactory, "render", broken)
    assert project.check() == 1
    out = capsys.readouterr().out
    assert "error-changed" in out and "the draw broke" in out
    monkeypatch.setattr(VizFactory, "render", real)
    # written with the error: the record keeps the error text, and the same error again is "identical"
    monkeypatch.setattr(VizFactory, "render", broken)
    other = project.root / "stored_error"
    assert rp.main(project.args("--write", other)) == 0
    record = json.loads((other / "manifest.json").read_text())["plots"][0]
    assert record["status"] == "error" and "the draw broke" in record["error"]
    assert rp.main(project.args("--check", other, "--out", str(project.root / "check2"))) == 0


def test_a_plot_that_is_not_stable_is_named_in_the_manifest(project, monkeypatch):
    calls = {"n": 0}
    real_hash = rp.differing_pixels

    def always_differs(a, b):
        calls["n"] += 1
        return 7

    monkeypatch.setattr(rp, "differing_pixels", always_differs)
    project.write()
    monkeypatch.setattr(rp, "differing_pixels", real_hash)
    record = project.manifest()["plots"][0]
    assert record["status"] == "unstable" and "7 pixels" in record["error"]


def test_folders_that_are_not_recipes_are_listed_as_skipped(project):
    (project.recipes / "tiny").mkdir()
    (project.recipes / "notes.txt").write_text("x")
    project.write()
    reasons = {Path(s["path"]).name: s["reason"] for s in project.manifest()["skipped"]}
    assert "fragments" in reasons["tiny"] and reasons["notes.txt"] == "not a .yaml file"


def test_the_comparison_can_fail(tmp_path):
    """The pixel comparison itself: one changed pixel is a difference, equal pictures are not."""
    white = np.full((6, 8, 3), 255, dtype=np.uint8)
    dot = white.copy()
    dot[2, 3] = (0, 0, 0)
    Image.fromarray(white).save(tmp_path / "a.png")
    Image.fromarray(dot).save(tmp_path / "b.png")
    assert rp.differing_pixels(rp.pixels(tmp_path / "a.png"), rp.pixels(tmp_path / "a.png")) == 0
    assert rp.differing_pixels(rp.pixels(tmp_path / "a.png"), rp.pixels(tmp_path / "b.png")) == 1


# ---- which code draws (Part A of task ENGINE-KEYS): the check must use the libraries of THIS checkout, never another copy ----

def test_under_pytest_every_package_comes_from_this_checkout():
    origins = rp.library_origins()
    assert "app" in origins and "utils" in origins and "viz_gallery" in origins
    assert rp.outside_checkout(origins) == {}


def test_a_package_from_another_folder_is_named_with_its_folder_and_the_remedy():
    outside = rp.outside_checkout({"utils": "/elsewhere/libs/utils/src/utils", "app": str(ROOT / "app"), "gone": "not found"})
    assert set(outside) == {"utils", "gone"}
    message = rp.outside_message(outside)
    assert "utils: /elsewhere/libs/utils/src/utils" in message and "gone: not found" in message
    assert "libs/*/src" in message and "--allow-outside-checkout" in message


def test_the_manifest_records_where_each_library_was_imported_from(project):
    project.write()
    libraries = project.manifest()["libraries"]
    assert set(libraries) == set(rp.checkout_packages())
    assert all(Path(where).resolve().is_relative_to(ROOT) for where in libraries.values())


def test_the_tool_stops_before_drawing_when_a_package_comes_from_outside(project, capsys, monkeypatch):
    monkeypatch.setattr(rp, "library_origins", lambda *a, **k: {"utils": "/elsewhere/utils", "app": str(ROOT / "app")})
    monkeypatch.setattr(rp, "draw_all", lambda *a, **k: pytest.fail("drew with another copy of the code"))
    assert project.write() == 2
    assert not (project.stored / "manifest.json").exists()
    out = capsys.readouterr().out
    assert "STOPPED" in out and "utils: /elsewhere/utils" in out
    assert project.check() == 2


def test_the_flag_allows_it_and_says_so(project, capsys, monkeypatch):
    monkeypatch.setattr(rp, "library_origins", lambda *a, **k: {"utils": "/elsewhere/utils", "app": str(ROOT / "app")})
    assert rp.main(project.args("--write", project.stored, "--allow-outside-checkout")) == 0
    out = capsys.readouterr().out
    assert "WARNING" in out and "utils" in out
    assert project.manifest()["libraries"]["utils"] == "/elsewhere/utils"


def test_a_real_run_from_a_checkout_whose_libraries_are_elsewhere_stops(tmp_path):
    """End to end: a script copy in a folder that has no libraries of its own imports them from somewhere else, and stops."""
    import subprocess, sys
    fake = tmp_path / "checkout"
    (fake / "assets" / "scripts").mkdir(parents=True)
    (fake / "libs" / "utils" / "src" / "utils").mkdir(parents=True)  # a package this checkout claims; Python finds another copy first
    script = fake / "assets" / "scripts" / "recipe_pictures.py"
    script.write_text((ROOT / "assets" / "scripts" / "recipe_pictures.py").read_text())
    import os
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)}
    done = subprocess.run([sys.executable, str(script), "--write", str(tmp_path / "o"), "--recipe-dir", str(tmp_path / "none")],
                          cwd=fake, env=env, capture_output=True, text=True)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "STOPPED" in done.stdout and "utils" in done.stdout
    allowed = subprocess.run([sys.executable, str(script), "--write", str(tmp_path / "o2"), "--recipe-dir", str(tmp_path / "none"),
                              "--allow-outside-checkout"], cwd=fake, env=env, capture_output=True, text=True)
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr
    assert "libraries" in json.loads((tmp_path / "o2" / "manifest.json").read_text())


def test_help_gives_the_command_that_puts_the_checkout_first():
    text = (ROOT / "assets" / "scripts" / "recipe_pictures.py").read_text()
    assert 'PYTHONPATH=".:$(ls -d libs/*/src | paste -sd:)"' in text and "--allow-outside-checkout" in text


def test_the_manifest_records_the_hash_seed_and_a_check_names_a_different_one(project, capsys, monkeypatch):
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    assert project.write() == 0
    assert project.manifest()["python_hash_seed"] == "0"
    monkeypatch.setenv("PYTHONHASHSEED", "4")
    project.check()
    out = capsys.readouterr().out
    assert "the stored set was drawn with: 0" in out and "PYTHONHASHSEED=0" in out


def test_the_seed_note_covers_the_three_cases():
    assert "does not record" in rp.seed_note(None, "random")
    assert "same as the stored set" in rp.seed_note("0", "0")
    assert "PYTHONHASHSEED=0" in rp.seed_note("random", "3")  # a stored random seed: suggests 0 (rerun, not a proof)
