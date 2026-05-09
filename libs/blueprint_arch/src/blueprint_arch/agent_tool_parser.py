"""libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py
Parse fenced-block tool calls from agent response text (ADR-076 §10.1).

Protocol expected in AgentResponse.content:
    <!-- AGENT_TOOL_CALL -->
    ```json
    {"tool": "tool_name", "args": {...}}
    ```
    <!-- /AGENT_TOOL_CALL -->

Multiple blocks may appear in a single response. Partial success is supported:
valid blocks yield ParsedToolCall objects; invalid blocks yield error strings.
`format_error_turn()` packages errors into a message the caller can feed back
to the agent for a self-correction retry.

Constraints (Two-Category Law — ADR-045):
    Zero Shiny imports. Pure Python stdlib. Importable headlessly.
"""

from __future__ import annotations

# @deps
# provides: function:extract_tool_calls, function:register_tool_schema, class:ParseResult, class:ParsedToolCall
# consumed_by: app/handlers/blueprint_handlers.py, libs/blueprint_arch/src/blueprint_arch/agent_tools.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-076
# @end_deps

import json
import re
from dataclasses import dataclass, field
from typing import Any

# ── Marker constants ──────────────────────────────────────────────────────────

_OPEN = "<!-- AGENT_TOOL_CALL -->"
_CLOSE = "<!-- /AGENT_TOOL_CALL -->"

# Matches the full fenced block between the HTML comment markers.
# re.DOTALL so the JSON content may span multiple lines.
_BLOCK_RE = re.compile(
    re.escape(_OPEN) + r"(.*?)" + re.escape(_CLOSE),
    re.DOTALL,
)

# Matches ```json ... ``` (optional language tag; also accepts raw ```)
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class ParsedToolCall:
    """One successfully parsed and validated tool call."""

    tool_name: str
    args: dict[str, Any]
    raw_block: str  # original text between the markers, useful for debugging


@dataclass
class ParseResult:
    """Result of extracting tool calls from one response string.

    Both `tool_calls` and `errors` may be non-empty (partial success).
    """

    tool_calls: list[ParsedToolCall] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def format_error_turn(self) -> str:
        """Return a retry message suitable for sending back to the agent.

        The agent receives this as the next user turn so it can correct
        its tool-call syntax before the next application cycle.
        """
        lines = [
            "Your previous response contained tool-call block(s) with errors.",
            "Please re-emit ONLY the corrected block(s) and nothing else.",
            "",
        ]
        for i, err in enumerate(self.errors, 1):
            lines.append(f"Error {i}: {err}")

        lines += [
            "",
            "Correct format:",
            "<!-- AGENT_TOOL_CALL -->",
            "```json",
            '{"tool": "<tool_name>", "args": {<key>: <value>, ...}}',
            "```",
            "<!-- /AGENT_TOOL_CALL -->",
        ]
        return "\n".join(lines)


# ── Tool schema registry ──────────────────────────────────────────────────────
# Populated by agent_tools.py via register_tool_schema().
# Maps tool_name -> {"required": [...], "properties": {...}}.
# If a tool is not registered, only the base structure (tool + args keys) is
# validated — unknown tools are accepted with a warning in the error list only
# if strict_unknown is True (default False for forward-compatibility).

_TOOL_SCHEMAS: dict[str, dict] = {}


def register_tool_schema(
    tool_name: str,
    *,
    required: list[str] | None = None,
    properties: dict[str, dict] | None = None,
) -> None:
    """Register a tool's expected argument schema.

    required:   list of arg names that must be present in `args`.
    properties: dict mapping arg name -> {"type": <python type name>} for
                lightweight type coercion checks. Example:
                  {"manifest_path": {"type": "str"}, "schema_id": {"type": "str"}}
    """
    _TOOL_SCHEMAS[tool_name] = {
        "required": required or [],
        "properties": properties or {},
    }


def get_registered_tools() -> list[str]:
    """Return names of all registered tools."""
    return list(_TOOL_SCHEMAS.keys())


# ── Core extraction ───────────────────────────────────────────────────────────


def extract_tool_calls(
    text: str,
    *,
    strict_unknown: bool = False,
) -> ParseResult:
    """Extract and validate all AGENT_TOOL_CALL blocks from agent response text.

    Args:
        text:           The full content string from AgentResponse.content.
        strict_unknown: When True, tool names not in the schema registry are
                        treated as errors. Default False — accepts new tools
                        that haven't been registered yet (forward compat).

    Returns a ParseResult with zero or more ParsedToolCall objects and zero or
    more structured error strings. The caller decides how to handle partial
    success (e.g. execute valid calls, send format_error_turn() for failures).
    """
    result = ParseResult()

    raw_blocks = _BLOCK_RE.findall(text)

    if not raw_blocks and _OPEN in text:
        # Marker found but regex didn't match — likely unclosed marker
        result.errors.append(
            f"Found '{_OPEN}' but no matching '{_CLOSE}'. "
            "Ensure every opening marker has a closing marker on its own line."
        )
        return result

    for block_idx, raw in enumerate(raw_blocks, 1):
        _parse_one_block(raw, block_idx, result, strict_unknown=strict_unknown)

    return result


# ── Internal helpers ──────────────────────────────────────────────────────────


def _parse_one_block(
    raw: str,
    block_idx: int,
    result: ParseResult,
    *,
    strict_unknown: bool,
) -> None:
    """Parse one raw block string (text between markers) into result in-place."""
    label = f"Block {block_idx}"

    # 1. Extract JSON string — prefer content inside ```json ... ``` fence;
    #    fall back to the raw block content if no fence is present.
    json_str = _extract_json_string(raw)
    if json_str is None:
        result.errors.append(
            f"{label}: No JSON content found. "
            "Wrap your JSON in a ```json ... ``` fence inside the markers."
        )
        return

    # 2. Parse JSON
    try:
        payload = json.loads(json_str)
    except json.JSONDecodeError as exc:
        snippet = json_str[:120].replace("\n", " ")
        result.errors.append(
            f"{label}: Invalid JSON — {exc.msg} at line {exc.lineno} col {exc.colno}. "
            f"Content: {snippet!r}"
        )
        return

    # 3. Validate base structure
    if not isinstance(payload, dict):
        result.errors.append(
            f"{label}: JSON must be an object (dict), got {type(payload).__name__}."
        )
        return

    tool_name = payload.get("tool")
    args = payload.get("args")

    if not tool_name:
        result.errors.append(
            f'{label}: Missing required key "tool". '
            'Expected: {"tool": "<name>", "args": {...}}.'
        )
        return

    if not isinstance(tool_name, str):
        result.errors.append(
            f'{label}: "tool" must be a string, got {type(tool_name).__name__}.'
        )
        return

    if args is None:
        result.errors.append(
            f'{label} (tool={tool_name!r}): Missing required key "args". '
            "Provide an empty object {{}} if no arguments are needed."
        )
        return

    if not isinstance(args, dict):
        result.errors.append(
            f'{label} (tool={tool_name!r}): "args" must be an object (dict), '
            f"got {type(args).__name__}."
        )
        return

    # 4. Unknown tool check
    if strict_unknown and tool_name not in _TOOL_SCHEMAS:
        known = ", ".join(sorted(_TOOL_SCHEMAS)) or "(none registered)"
        result.errors.append(
            f"{label}: Unknown tool {tool_name!r}. Known tools: {known}."
        )
        return

    # 5. Per-tool schema validation (if schema registered)
    if tool_name in _TOOL_SCHEMAS:
        schema_error = _validate_args(tool_name, args, label)
        if schema_error:
            result.errors.append(schema_error)
            return

    result.tool_calls.append(ParsedToolCall(tool_name=tool_name, args=args, raw_block=raw))


def _extract_json_string(block: str) -> str | None:
    """Return the JSON string from inside a fenced block, or None if absent."""
    fence_match = _FENCE_RE.search(block)
    if fence_match:
        return fence_match.group(1).strip()
    # No fence — try the block text directly after stripping whitespace
    stripped = block.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return stripped
    return None


def _validate_args(tool_name: str, args: dict, label: str) -> str | None:
    """Validate args against the registered schema. Returns an error string or None."""
    schema = _TOOL_SCHEMAS[tool_name]

    # Required fields
    missing = [k for k in schema["required"] if k not in args]
    if missing:
        return (
            f"{label} (tool={tool_name!r}): Missing required arg(s): "
            f"{', '.join(missing)}."
        )

    # Lightweight type checks (str / int / float / bool / list / dict)
    _PY_TYPES: dict[str, type] = {
        "str": str, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict,
    }
    for arg_name, prop in schema["properties"].items():
        if arg_name not in args:
            continue
        expected_type_name = prop.get("type")
        if not expected_type_name:
            continue
        expected_type = _PY_TYPES.get(expected_type_name)
        if expected_type is None:
            continue
        actual = args[arg_name]
        if not isinstance(actual, expected_type):
            return (
                f"{label} (tool={tool_name!r}): Arg {arg_name!r} must be "
                f"{expected_type_name}, got {type(actual).__name__}."
            )

    return None
