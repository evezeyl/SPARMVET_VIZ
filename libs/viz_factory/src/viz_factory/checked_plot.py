"""A plot that explains its own failure: the plot the factory builds, and the one checked call that draws it (VIZ-STANDARD-1, V7).

# @deps
# provides: class:CheckedPlot, class:PlotContext, class:Step, function:draw_checked, function:show_draw_errors, function:explain_build_failure
# consumes: libs/viz_factory/src/viz_factory/errors.py, libs/viz_factory/src/viz_factory/arguments.py, libs/viz_factory/src/viz_factory/registry.py, plotnine, matplotlib
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py, app/handlers/home_theater.py, app/modules/wrangle_studio.py, app/modules/gallery_examples.py
# doc: .claude/design/decisions_2026-11-14/viz_plan_for_eve.md (V7), .claude/rules/rules_viz_factory.md
# @end_deps

plotnine builds a plot lazily: a wrong value in a layer (`size: big`) is found when the plot is drawn, after the factory
returned it, and arrives as a bare `TypeError` that names no plot and no layer. `VizFactory.render` therefore returns a
`CheckedPlot`: a `ggplot` that knows the layers it was built from. When drawing fails, it finds the layer (and the
parameter) by drawing the plot again layer by layer, and raises the one error form of `errors.plot_failure`. That
extra work happens only when drawing has already failed; a plot that draws is drawn once.

Drawing goes through `ggplot.draw`, which `save`, `save_helper` (Shiny) and `draw_checked` all call, so every way of
drawing a factory plot is checked. Nothing about the picture of a good plot changes.

`show_draw_errors` is for a screen: the failing plot draws the message in the place of the plot instead of raising, and
reports the error to a callback (the alerts panel). A file that is exported never uses it.
"""
from __future__ import annotations

import copy
import difflib
import re
import textwrap
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from plotnine import aes, ggplot
from utils.errors import VisualizationError

from viz_factory.errors import CannotAct, layer_label, plot_failure


@dataclass
class Step:
    """One thing done to the plot, in order: a layer the author wrote, a default, or a block (labels, guides, palette)."""
    name: str
    params: dict
    func: Callable[[Any, dict], Any]
    tier: Optional[str] = None
    layer_no: Optional[int] = None
    label: Optional[str] = None

    @property
    def where(self) -> str:
        return self.label or layer_label(self.tier, self.layer_no, self.name)


def _short(exc: BaseException, limit: int = 160) -> str:
    text = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _number(text) -> bool:
    try:
        float(text)
        return True
    except (TypeError, ValueError):
        return False


def _default_of(name: str, key: str):
    """The value plotnine uses for `key` of component `name` when the author gives none, or None when it cannot be told."""
    from plotnine.geoms.geom import geom as _Geom
    from plotnine.stats.stat import stat as _Stat
    import inspect

    from viz_factory.arguments import _wrapped_object
    try:
        wrapped = _wrapped_object(name)
    except (KeyError, AttributeError, ImportError):
        return None
    if wrapped is None:
        return None
    try:
        if inspect.isclass(wrapped) and issubclass(wrapped, (_Geom, _Stat)):
            layer = wrapped().to_layer()
            for owner in (layer.geom, layer.stat):
                if key in owner.DEFAULT_AES:
                    return owner.DEFAULT_AES[key]
                if key in owner.DEFAULT_PARAMS:
                    return owner.DEFAULT_PARAMS[key]
            return None
        parameter = inspect.signature(wrapped).parameters.get(key)
        return None if parameter is None or parameter.default is inspect.Parameter.empty else parameter.default
    except Exception:
        return None


def describe_failure(exc: BaseException, name: str, culprit: Optional[tuple]) -> tuple:
    """(what, fix) for an exception of plotnine in layer `name`; `culprit` is (parameter, value) when one was found."""
    text = str(exc)
    unknown = re.search(r"Parameters \{(.*?)\},? are not understood", text)
    keyword = re.search(r"got an unexpected keyword argument '([^']+)'", text)
    if unknown or keyword:
        names = ((re.findall(r"'([^']+)'", unknown.group(1)) or [unknown.group(1)]) if unknown else [keyword.group(1)])
        from viz_factory.arguments import allowed_arguments
        try:
            allowed = allowed_arguments(name)
        except KeyError:
            allowed = None
        pairs = []
        for bad in names:
            close = difflib.get_close_matches(bad, sorted(allowed), n=1, cutoff=0.6) if allowed else []
            pairs.append((bad, close[0] if close else None))
        what = ", ".join(repr(bad) for bad, _ in pairs) + (" is" if len(pairs) == 1 else " are") + f" not an argument of {name}"
        fix = "; ".join(f"write {good}" if good else f"remove {bad!r}, or see the arguments of {name} in the plotnine documentation"
                        for bad, good in pairs)
        return what, fix
    missing = re.search(r"requires the following missing aesthetics: ([\w, ]+)", text)
    if missing:
        wanted = [a.strip() for a in missing.group(1).split(",") if a.strip()]
        what = (f"{name} needs the aesthetic{'s' if len(wanted) > 1 else ''} "
                + ", ".join(repr(a) for a in wanted) + " and the mapping does not give it" + ("" if len(wanted) == 1 else " to it"))
        return what, f"add {wanted[0]} under mapping, for example {wanted[0]}: <a column of the data>"
    if culprit is not None:
        key, value = culprit
        default = _default_of(name, key)
        if isinstance(value, str) and isinstance(default, (int, float)) and not isinstance(default, bool) and not _number(value):
            example = 3 if default > 1 else 0.5
            return f"the value {value!r} for '{key}' is not a number", f"write a number, for example {key}: {example}"
        return (f"the value {value!r} for '{key}' is refused by plotnine ({type(exc).__name__}: {_short(exc)})",
                f"check the allowed values of '{key}' for {name} in the plotnine documentation, or remove '{key}' to use its default")
    return (f"plotnine refused it ({type(exc).__name__}: {_short(exc)})",
            f"check the parameters of this layer against the plotnine documentation of {name}")


def _find_culprit(try_without: Callable[[dict], bool], params: dict) -> Optional[tuple]:
    """The one parameter whose removal makes `try_without(params_without_it)` succeed, or None."""
    for key in list(params):
        trial = {k: v for k, v in params.items() if k != key}
        try:
            if try_without(trial):
                return key, params[key]
        except Exception:
            continue
    return None


def explain_build_failure(plot_id: str, p_before, step: Step, exc: BaseException) -> VisualizationError:
    """The one error form for a component that raised while the plot was built."""
    where = step.where
    evidence = {"layer": step.name, "params": str(step.params)[:200], "error_type": type(exc).__name__}
    if isinstance(exc, CannotAct):
        return plot_failure(plot_id, exc.what, exc.fix, layer=where, evidence=evidence)
    if isinstance(exc, VisualizationError):
        return plot_failure(plot_id, exc.message, exc.tip, layer=where, evidence=evidence)

    def builds(params: dict) -> bool:
        step.func(p_before, dict(params))
        return True

    culprit = _find_culprit(builds, step.params)
    what, fix = describe_failure(exc, step.name, culprit)
    evidence["error_detail"] = str(exc)[:200]
    return plot_failure(plot_id, what, fix, layer=where, evidence=evidence)


def _drawable(p) -> Optional[bool]:
    """True or False when drawing `p` works or fails; None when a plot with no geom cannot be judged."""
    if not len(p.layers):
        return None
    from matplotlib import pyplot as plt
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            figure = p.draw(show=False)
    except Exception:
        return False
    plt.close(figure)
    return True


class PlotContext:
    """What a factory plot was built from, kept so that a failure to draw can be traced to a layer and a parameter."""

    def __init__(self, plot_id: str, df, mapping: dict):
        self.plot_id = plot_id
        self.df = df
        self.mapping = dict(mapping)
        self.steps: list[Step] = []
        self.in_place = False
        self.on_error: Optional[Callable[[VisualizationError], None]] = None

    def __deepcopy__(self, memo):
        return self   # the data and the steps are shared by every copy of the plot; only `with_in_place` makes another

    def with_in_place(self, on_error) -> "PlotContext":
        other = copy.copy(self)
        other.in_place = True
        other.on_error = on_error
        return other

    def build(self, count: int, skip: Optional[tuple] = None):
        """The plot with the first `count` steps, as a plain ggplot; `skip` = (step index, parameter) leaves one parameter out."""
        p = ggplot(self.df, aes(**self.mapping))
        for index, step in enumerate(self.steps[:count]):
            params = dict(step.params)
            if skip and skip[0] == index:
                params.pop(skip[1], None)
            p = step.func(p, params)
        return p

    def locate(self) -> Optional[tuple]:
        """(step index, (parameter, value) or None) of the step whose layer first makes drawing fail, or None."""
        failing = None
        for count in range(1, len(self.steps) + 1):
            try:
                ok = _drawable(self.build(count))
            except Exception:
                continue
            if ok is False:
                failing = count
                break
        if failing is None:
            return None
        for index in range(failing - 1, -1, -1):
            for key in self.steps[index].params:
                try:
                    if _drawable(self.build(failing, skip=(index, key))) is True:
                        return index, (key, self.steps[index].params[key])
                except Exception:
                    continue
        return failing - 1, None

    def explain_draw(self, exc: BaseException) -> VisualizationError:
        if isinstance(exc, VisualizationError):
            return exc
        found = self.locate()
        if found is None:
            return plot_failure(self.plot_id, f"plotnine could not draw it ({type(exc).__name__}: {_short(exc)})",
                                "check the mapping and the layers of this plot against the plotnine documentation",
                                evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]})
        index, culprit = found
        step = self.steps[index]
        what, fix = describe_failure(exc, step.name, culprit)
        return plot_failure(self.plot_id, what, fix, layer=step.where,
                            evidence={"layer": step.name, "params": str(step.params)[:200],
                                      "error_type": type(exc).__name__, "error_detail": str(exc)[:200]})


def error_figure(error: VisualizationError, size=(6.4, 4.8)):
    """A figure that shows the error in the place of the plot."""
    from matplotlib.figure import Figure
    figure = Figure(figsize=size)
    body = "\n".join(textwrap.fill(line, 72) for line in str(error).splitlines())
    figure.text(0.5, 0.5, "The plot could not be drawn\n\n" + body, ha="center", va="center", color="#d62828", fontsize=9)
    return figure


class CheckedPlot(ggplot):
    """A `ggplot` that names the layer and the fix when drawing fails. The factory returns this; it draws like any ggplot."""

    def draw(self, *, show: bool = False):
        try:
            return super().draw(show=show)
        except Exception as exc:
            context = getattr(self, "_sparmvet", None)
            error = context.explain_draw(exc) if context is not None else _plain_failure(exc, "plot")
            if context is not None and context.in_place:
                if context.on_error is not None:
                    context.on_error(error)
                try:
                    size = tuple(self.theme.getp("figure_size"))
                except Exception:
                    size = (6.4, 4.8)
                return error_figure(error, size)
            raise error from exc


def _plain_failure(exc: BaseException, plot_id: str) -> VisualizationError:
    if isinstance(exc, VisualizationError):
        return exc
    return plot_failure(plot_id, f"plotnine could not draw it ({type(exc).__name__}: {_short(exc)})",
                        "check the layers and the mapping of this plot against the plotnine documentation",
                        evidence={"error_type": type(exc).__name__, "error_detail": str(exc)[:200]})


def draw_checked(plot, plot_id: str = "plot"):
    """Draw a plot once and return its matplotlib figure; every failure is the one error form.

    A plot from `VizFactory.render` names its layer and parameter. A plain `ggplot` (not built by the factory) gets the
    plot-level form, with `plot_id` as its name. Callers that need the figure (an export, a gallery picture) use the
    returned figure instead of drawing the plot a second time.
    """
    if isinstance(plot, CheckedPlot):
        return plot.draw(show=False)
    try:
        return plot.draw(show=False)
    except Exception as exc:
        raise _plain_failure(exc, plot_id) from exc


def show_draw_errors(plot: CheckedPlot, on_error: Optional[Callable[[VisualizationError], None]] = None) -> CheckedPlot:
    """A copy of the plot that, when drawing fails, draws the error message in its place and calls `on_error(error)`.

    For a screen (HOME, the Blueprint preview): the user reads what is wrong, where the plot would be, and the alerts
    panel gets the same record. The copy draws exactly like the plot when drawing works.
    """
    context = getattr(plot, "_sparmvet", None)
    if context is None:
        raise TypeError("show_draw_errors needs a plot built by VizFactory.render")
    other = copy.deepcopy(plot)
    other._sparmvet = context.with_in_place(on_error)
    return other
