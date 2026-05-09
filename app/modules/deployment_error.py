# @deps
# provides: (re-exports from utils.deployment_error — see that file for the canonical source)
# consumes: utils.deployment_error
# consumed_by: app/modules/persona_validator.py, app/modules/sidebar_validator.py, app/src/bootloader.py, app/src/server.py, scripts/validate_persona_config.py
# doc: .claude/knowledge/architecture_decisions.md#adr-078
# @end_deps
"""
Backward-compat re-export shim (ADR-078 Phase C, DIAG-CONNECTOR-1).

Canonical source moved to libs/utils/src/utils/deployment_error.py (Tier 1 base lib)
so that connector and manifest-preflight libs can import it without violating ADR-011.

All existing callers that import from app.modules.deployment_error continue to work
unchanged — this module re-exports everything from the canonical location.
"""
from utils.deployment_error import (  # noqa: F401
    DeploymentError,
    DeploymentFailure,
    exit_if_errors,
    format_errors_block,
    raise_if_errors,
)
