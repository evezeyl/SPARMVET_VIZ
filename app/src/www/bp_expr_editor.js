// bp_expr_editor.js — BLUEPRINT expression widget column autocomplete (BP-EXPR-EDITOR-1)
//
// Vanilla JS, no external dependencies. ADR-071 compliant (no CDN).
// Activates on any .bp-expr-container element — the wrapper div rendered by
// wrangle_studio._render_action_form for the "expression" widget type.
// Column names are read from the container's data-columns attribute (JSON array).
//
// Trigger: typing pl.col(' or pl.col(" shows a dropdown of matching upstream columns.
// Selection inserts the column name and closing bracket, then fires a change event
// so Shiny updates input.bp_form_expression.

(function () {
    'use strict';

    var TRIGGERS = ["pl.col('", 'pl.col("'];

    function getColumns(container) {
        try {
            return JSON.parse(container.dataset.columns || '[]');
        } catch (e) {
            return [];
        }
    }

    function findActiveTrigger(text, cursorPos) {
        for (var i = 0; i < TRIGGERS.length; i++) {
            var trigger = TRIGGERS[i];
            var last = text.lastIndexOf(trigger, cursorPos - 1);
            if (last === -1) continue;
            var after = text.slice(last + trigger.length, cursorPos);
            // Only show if no closing quote between trigger and cursor
            if (after.indexOf("'") === -1 && after.indexOf('"') === -1) {
                return { prefix: after, triggerStart: last, trigger: trigger };
            }
        }
        return null;
    }

    function removeDropdown() {
        var el = document.getElementById('bp-expr-autocomplete');
        if (el) el.parentNode.removeChild(el);
    }

    function showDropdown(textarea, columns, match) {
        removeDropdown();
        var prefix = match.prefix;
        var matches = columns.filter(function (c) {
            return c.toLowerCase().indexOf(prefix.toLowerCase()) === 0;
        });
        if (matches.length === 0) return;

        var dropdown = document.createElement('div');
        dropdown.id = 'bp-expr-autocomplete';
        dropdown.className = 'bp-expr-autocomplete-dropdown';

        var rect = textarea.getBoundingClientRect();
        dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
        dropdown.style.left = rect.left + 'px';
        dropdown.style.minWidth = Math.min(240, rect.width) + 'px';

        var closing = match.trigger.indexOf("'") !== -1 ? "')" : '")';

        matches.slice(0, 8).forEach(function (col) {
            var item = document.createElement('div');
            item.className = 'bp-expr-autocomplete-item';
            item.textContent = col;
            item.addEventListener('mousedown', function (e) {
                e.preventDefault();
                var before = textarea.value.slice(0, match.triggerStart + match.trigger.length);
                var after = textarea.value.slice(match.triggerStart + match.trigger.length + prefix.length);
                textarea.value = before + col + closing + after;
                textarea.dispatchEvent(new Event('input', { bubbles: true }));
                textarea.dispatchEvent(new Event('change', { bubbles: true }));
                removeDropdown();
                textarea.focus();
            });
            dropdown.appendChild(item);
        });

        document.body.appendChild(dropdown);
    }

    function hookTextarea(textarea, container) {
        if (textarea.dataset.bpExprHooked) return;
        textarea.dataset.bpExprHooked = '1';

        textarea.addEventListener('input', function () {
            var pos = textarea.selectionEnd;
            var match = findActiveTrigger(textarea.value, pos);
            if (match) {
                showDropdown(textarea, getColumns(container), match);
            } else {
                removeDropdown();
            }
        });

        textarea.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                removeDropdown();
            }
        });

        textarea.addEventListener('blur', function () {
            setTimeout(removeDropdown, 200);
        });
    }

    function hookContainer(container) {
        var ta = container.querySelector('textarea');
        if (ta) hookTextarea(ta, container);
    }

    function hookAll() {
        document.querySelectorAll('.bp-expr-container').forEach(hookContainer);
    }

    // Initial hook after DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hookAll);
    } else {
        hookAll();
    }

    // Watch for Shiny-rendered containers
    var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (m) {
            m.addedNodes.forEach(function (node) {
                if (node.nodeType !== 1) return;
                if (node.classList && node.classList.contains('bp-expr-container')) {
                    hookContainer(node);
                }
                if (node.querySelectorAll) {
                    node.querySelectorAll('.bp-expr-container').forEach(hookContainer);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
}());
