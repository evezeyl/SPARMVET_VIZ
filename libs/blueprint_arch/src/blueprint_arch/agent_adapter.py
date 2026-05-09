"""libs/blueprint_arch/src/blueprint_arch/agent_adapter.py
AgentAdapter protocol + concrete adapters (ADR-076).

Three adapters share one protocol so the app stays backend-agnostic:
  ClaudeCliAdapter  — subprocess isolation per session dir (ADR-076 §11)
  DisabledAdapter   — sentinel returned when feature is off or init fails

Phase 2/3 (ClaudeApiAdapter, LocalModelAdapter) are not implemented here.

The bootloader instantiates the adapter via make_adapter() at startup and
falls back to DisabledAdapter on any init failure — startup is never blocked.

Constraints (Two-Category Law — ADR-045):
  Zero Shiny imports. Pure Python + subprocess. Importable headlessly.
"""

from __future__ import annotations

# @deps
# provides: class:AgentAdapter, class:ClaudeCliAdapter, class:DisabledAdapter, class:AgentResponse, class:Tool, function:make_adapter
# consumed_by: app/src/bootloader.py, app/handlers/blueprint_handlers.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-076
# @end_deps

import fcntl
import json
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class Tool:
    """Describes a callable tool (used by backends with native tool support)."""

    name: str
    description: str
    parameters: dict  # JSON Schema for the tool's arguments


@dataclass
class AgentResponse:
    """Unified response object returned by all adapter backends."""

    session_id: str
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    # Structured tool calls (claude_api native); for claude_cli these are
    # embedded as fenced blocks in `content` — use agent_tool_parser.py to extract.
    is_disabled: bool = False
    error: str | None = None


@runtime_checkable
class AgentAdapter(Protocol):
    """Protocol all agent backends implement.

    start_session: set up session state, return a session_id string.
    send_message:  deliver one user turn, return the assistant response.
    end_session:   release resources (lock file, etc.). Session dir is preserved.
    """

    def start_session(self, system_prompt: str, context: dict) -> str: ...
    def send_message(
        self,
        session_id: str,
        message: str,
        tools: list[Tool] | None = None,
    ) -> AgentResponse: ...
    def end_session(self, session_id: str) -> None: ...


# ── DisabledAdapter ──────────────────────────────────────────────────────────


class DisabledAdapter:
    """Graceful degradation — returned when blueprint_agent_enabled=False,
    when the configured backend fails to init, or the CLI binary is absent.

    All methods return sentinel values so callers need not special-case None.
    """

    is_disabled = True

    def __init__(self, reason: str = "Blueprint agent is not enabled."):
        self.reason = reason

    def start_session(self, system_prompt: str, context: dict) -> str:
        return "disabled"

    def send_message(
        self,
        session_id: str,
        message: str,
        tools: list[Tool] | None = None,
    ) -> AgentResponse:
        return AgentResponse(
            session_id=session_id,
            content="",
            is_disabled=True,
            error=self.reason,
        )

    def end_session(self, session_id: str) -> None:
        return


# ── ClaudeCliAdapter ─────────────────────────────────────────────────────────

_LOCK_FAIL_FAST = True  # fail-fast on lock contention; UI gate prevents duplication


class ClaudeCliAdapter:
    """Calls `claude -p` in an isolated working directory per session.

    Each session lives in `{project_root}/agent_sessions/{uuid}/`.
    Claude Code scopes conversation history per project directory, so running
    in a dedicated subdirectory keeps the agent's turns isolated from the
    user's main terminal session and from other agent sessions (ADR-076 §11).

    Single-flight discipline: an exclusive flock on `lock` prevents concurrent
    subprocess calls within the same session. The UI single-flight gate
    (handler disables input while in-flight) is the primary barrier; flock is
    the backend safety net.
    """

    BINARY = "claude"

    def __init__(self, project_root: Path, instructions_file: str | None = None):
        """Initialise and run the auth probe.

        Raises RuntimeError if the binary is not found or not logged in.
        The bootloader catches this and falls back to DisabledAdapter.
        """
        self.project_root = Path(project_root)
        self.sessions_root = self.project_root / "agent_sessions"
        self.sessions_root.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, dict] = {}
        self.is_disabled = False

        self._auth_probe()

    # -- Auth ----------------------------------------------------------------

    def _auth_probe(self) -> None:
        """Run `claude --version` then a trivial one-shot prompt in a temp dir.

        Raises RuntimeError on any failure so the bootloader falls back to
        DisabledAdapter with a meaningful banner reason.
        """
        try:
            ver = subprocess.run(
                [self.BINARY, "--version"],
                capture_output=True, text=True, timeout=10,
            )
            if ver.returncode != 0:
                raise RuntimeError(
                    f"'{self.BINARY} --version' exited {ver.returncode}. "
                    f"stderr: {ver.stderr.strip()}"
                )
        except FileNotFoundError:
            raise RuntimeError(
                f"Claude CLI binary '{self.BINARY}' not found on PATH. "
                "Install Claude Code (https://claude.ai/code) and verify 'claude' is on PATH."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"'{self.BINARY} --version' timed out — Claude CLI may be unresponsive."
            )

        with tempfile.TemporaryDirectory() as probe_dir:
            try:
                probe = subprocess.run(
                    [self.BINARY, "--output-format", "text", "-p", "ok"],
                    cwd=probe_dir,
                    capture_output=True, text=True, timeout=30,
                )
                if probe.returncode != 0:
                    raise RuntimeError(
                        f"Claude CLI auth probe failed (exit {probe.returncode}). "
                        "Run 'claude --status' to check authentication. "
                        f"stderr: {probe.stderr.strip()[:200]}"
                    )
            except subprocess.TimeoutExpired:
                raise RuntimeError(
                    "Claude CLI auth probe timed out (>30 s). "
                    "Check network connectivity and 'claude --status'."
                )

    # -- Session lifecycle ---------------------------------------------------

    def start_session(self, system_prompt: str, context: dict) -> str:
        """Create an isolated session directory and store session state.

        Returns a session_id (UUID string). No subprocess call yet —
        that happens on the first send_message().
        """
        session_id = str(uuid.uuid4())
        session_dir = self.sessions_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # .cwd-marker anchors a separate Claude Code project context (ADR-076 §11)
        (session_dir / ".cwd-marker").touch()

        meta = {
            "session_id": session_id,
            "system_prompt": system_prompt,
            "context": context,
        }
        (session_dir / "session_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2)
        )

        self._sessions[session_id] = {
            "dir": session_dir,
            "system_prompt": system_prompt,
            "context": context,
            "turn_count": 0,
        }
        return session_id

    def send_message(
        self,
        session_id: str,
        message: str,
        tools: list[Tool] | None = None,
    ) -> AgentResponse:
        """Deliver one user turn and return the assistant response.

        First turn: injects system prompt (via --system) and Layer 3 context
        JSON into the message body. Subsequent turns: uses --continue.

        `tools` is accepted for protocol compatibility but is not forwarded —
        tool descriptions live in the system prompt (fenced-block protocol,
        ADR-076 §10.1). The caller uses agent_tool_parser.py to extract tool
        calls from `AgentResponse.content`.
        """
        state = self._sessions.get(session_id)
        if state is None:
            return AgentResponse(
                session_id=session_id,
                content="",
                error="Session not found. Call start_session() first.",
            )

        session_dir = state["dir"]
        lock_path = session_dir / "lock"

        try:
            lock_fd = _acquire_lock(lock_path)
        except BlockingIOError:
            return AgentResponse(
                session_id=session_id,
                content="",
                error="Agent is busy — a turn is already in flight. Please wait.",
            )

        try:
            is_first = state["turn_count"] == 0

            if is_first:
                context_json = json.dumps(state["context"], indent=2)
                full_message = (
                    f"\n\n---\nSession context:\n{context_json}\n---\n\n{message}"
                )
                cmd = [
                    self.BINARY,
                    "--output-format", "text",
                    "--system", state["system_prompt"],
                    "-p", full_message,
                ]
            else:
                cmd = [
                    self.BINARY,
                    "--continue",
                    "--output-format", "text",
                    "-p", message,
                ]

            result = subprocess.run(
                cmd,
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=120,
            )

            state["turn_count"] += 1

            if result.returncode != 0:
                return AgentResponse(
                    session_id=session_id,
                    content="",
                    error=(
                        f"Claude CLI returned exit code {result.returncode}. "
                        f"stderr: {result.stderr.strip()[:300]}"
                    ),
                )

            content = result.stdout.strip()
            _append_conversation_log(session_dir, "user", message)
            _append_conversation_log(session_dir, "assistant", content)

            return AgentResponse(session_id=session_id, content=content)

        except subprocess.TimeoutExpired:
            return AgentResponse(
                session_id=session_id,
                content="",
                error="Claude CLI timed out after 120 s. Try a shorter or simpler message.",
            )
        except Exception as exc:
            return AgentResponse(
                session_id=session_id,
                content="",
                error=f"Unexpected error during agent turn: {exc}",
            )
        finally:
            _release_lock(lock_fd, lock_path)

    def end_session(self, session_id: str) -> None:
        """Release the lock file. Session dir + report bundle are preserved."""
        state = self._sessions.pop(session_id, None)
        if state is None:
            return
        lock_path = state["dir"] / "lock"
        if lock_path.exists():
            try:
                lock_path.unlink()
            except OSError:
                pass


# ── Helpers ──────────────────────────────────────────────────────────────────


def _acquire_lock(lock_path: Path) -> int:
    """Open and LOCK_EX flock on lock_path. Raises BlockingIOError if busy."""
    fd = os.open(str(lock_path), os.O_CREAT | os.O_WRONLY)
    flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if _LOCK_FAIL_FAST else 0)
    try:
        fcntl.flock(fd, flags)
    except BlockingIOError:
        os.close(fd)
        raise
    return fd


def _release_lock(fd: int, lock_path: Path) -> None:
    """Unlock and close the flock fd."""
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except OSError:
        pass


def _append_conversation_log(session_dir: Path, role: str, content: str) -> None:
    """Append one turn to conversation.jsonl for the session report bundle."""
    log_path = session_dir / "conversation.jsonl"
    entry = json.dumps({"role": role, "content": content}, ensure_ascii=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ── Factory ──────────────────────────────────────────────────────────────────


def make_adapter(
    backend: str,
    project_root: Path,
    instructions_file: str | None = None,
) -> "ClaudeCliAdapter | DisabledAdapter":
    """Instantiate the adapter for the given backend identifier.

    Falls back to DisabledAdapter on any init failure so app startup is
    never blocked by agent misconfiguration (ADR-076 §1 selection cascade).
    """
    if backend == "disabled":
        return DisabledAdapter("Blueprint agent backend is set to 'disabled'.")

    if backend == "claude_cli":
        try:
            return ClaudeCliAdapter(
                project_root=project_root,
                instructions_file=instructions_file,
            )
        except RuntimeError as exc:
            print(
                f"[AgentAdapter] WARNING: ClaudeCliAdapter init failed — "
                f"falling back to DisabledAdapter. Reason: {exc}"
            )
            return DisabledAdapter(str(exc))

    # claude_api and local are Phase 2/3 — degrade gracefully
    return DisabledAdapter(
        f"Backend '{backend}' is not implemented in Phase 1. "
        "Use 'claude_cli' or 'disabled'."
    )
