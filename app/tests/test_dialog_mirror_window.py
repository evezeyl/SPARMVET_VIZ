"""The filter dialog never meets one plot's audit steps with another plot's table (PLOT-TABLE-ORDER-1, review round 3, point 4).

The dialog (`filter_and_audit_handlers._active_frame`) needs two things in one step: the table of the open plot and the audit
steps of the open plot. A first version mirrored the steps in a Value written by an Effect. An output that is created before
that Effect runs first on a plot switch, with the NEW plot's table and the OLD plot's steps; the Effect then corrects the
Value and the output runs again. This file shows the window on the first pattern (it is real) and that the pattern in use
(the Value only signals a change; the steps are read fresh for the open plot in the same step) never has it. The handler itself is
a closure and cannot be imported, so the two patterns are replicated here with the real `reactive` objects of Shiny; the browser
test `test_shiny_step_order.py::test_the_dialog_of_another_plot_is_not_emptied_by_a_drop_on_this_one` checks the real handler.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_dialog_mirror_window.py -q
"""
import asyncio

from shiny import reactive


def _run(pattern: str) -> list:
    async def main():
        seen = []
        subtab = reactive.Value("A")
        state = reactive.Value({"A": ["drop A"], "B": []})
        signal = reactive.Value(["drop A"])

        def nodes_now(plot):
            with reactive.isolate():
                return list(state.get().get(plot, []))

        @reactive.Effect
        def output_like():          # created BEFORE the effect below, like filter_form_ui
            plot = subtab.get()
            if pattern == "mirror holds the steps":
                seen.append((plot, tuple(signal.get())))
            else:
                signal.get()
                seen.append((plot, tuple(nodes_now(plot))))

        @reactive.Effect
        def signal_effect():
            plot = subtab.get()
            nodes = list(state.get().get(plot, []))
            with reactive.isolate():
                if signal.get() != nodes:
                    signal.set(nodes)

        await reactive.flush()
        seen.clear()
        subtab.set("B")
        await reactive.flush()
        return seen
    return asyncio.run(main())


def test_a_mirror_that_holds_the_steps_is_one_flush_late_on_a_plot_switch():
    seen = _run("mirror holds the steps")
    assert ("B", ("drop A",)) in seen, f"the window was not reproduced: {seen}"


def test_a_signal_with_a_fresh_read_never_pairs_a_plot_with_the_steps_of_another():
    seen = _run("signal and fresh read")
    assert seen and all(not (plot == "B" and steps == ("drop A",)) for plot, steps in seen), seen
    assert seen[-1] == ("B", ())


def test_a_change_of_the_steps_of_the_open_plot_still_builds_the_dialog_again():
    async def main():
        runs = []
        subtab = reactive.Value("A")
        state = reactive.Value({"A": []})
        signal = reactive.Value([])

        @reactive.Effect
        def output_like():
            signal.get()
            runs.append(1)

        @reactive.Effect
        def signal_effect():
            nodes = list(state.get().get(subtab.get(), []))
            with reactive.isolate():
                if signal.get() != nodes:
                    signal.set(nodes)

        await reactive.flush()
        runs.clear()
        state.set({"A": ["a new step"]})
        await reactive.flush()
        changed = len(runs)
        runs.clear()
        state.set({"A": ["a new step"], "other": ["x"]})     # another plot's steps change: the dialog is not built again
        await reactive.flush()
        return changed, len(runs)
    changed, unrelated = asyncio.run(main())
    assert changed >= 1 and unrelated == 0, (changed, unrelated)
