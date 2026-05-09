#!/usr/bin/env bash
# Local audit runner for SPARMVET_VIZ.
# Invoked by cron for scheduled audits, or manually for on-demand runs.
#
# Usage:
#   ./scripts/run_audits.sh sunday       # @deps + cross-lib (23:00 Sun)
#   ./scripts/run_audits.sh wednesday    # manifest integrity + coherence (22:00 Wed)
#   ./scripts/run_audits.sh thursday     # phase order + changelog + template flags (21:00 Thu)
#   ./scripts/run_audits.sh friday       # task drift (20:00 Fri)
#   ./scripts/run_audits.sh all          # run every scheduled audit now
#   ./scripts/run_audits.sh ondemand     # run slower on-demand audits (deps health, tests, parity)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PROJECT_ROOT}/.venv/bin/python"
LOGS="${PROJECT_ROOT}/.claude/logs/audits"
DATE="$(date +%Y-%m-%d)"
AUDIT_BRANCH="dev"

cd "${PROJECT_ROOT}"

if [[ ! -x "${PYTHON}" ]]; then
  echo "ERROR: .venv/bin/python not found at ${PYTHON}" >&2
  exit 2
fi

# Ensure we are on the correct branch before scanning.
# Audits must reflect active development state, not an older or unrelated branch.
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
if [[ "${CURRENT_BRANCH}" != "${AUDIT_BRANCH}" ]]; then
  echo "INFO: switching from '${CURRENT_BRANCH}' to '${AUDIT_BRANCH}' for audit run"
  git checkout "${AUDIT_BRANCH}"
fi

DAY="${1:-}"
if [[ -z "${DAY}" ]]; then
  echo "Usage: $0 <sunday|wednesday|thursday|friday|all|ondemand>"
  exit 1
fi

run_audit() {
  local script="$1"
  local out="$2"
  echo "--- $(date '+%H:%M:%S') Running ${script} ---"
  "${PYTHON}" "scripts/${script}" --output "${LOGS}/${out}_${DATE}.md" || true
  echo "    -> ${LOGS}/${out}_${DATE}.md"
}

if [[ "${DAY}" == "sunday" || "${DAY}" == "all" ]]; then
  run_audit audit_deps_verify.py     audit_deps
  run_audit audit_cross_lib.py       audit_cross_lib
fi

if [[ "${DAY}" == "wednesday" || "${DAY}" == "all" ]]; then
  run_audit audit_manifest_integrity.py  audit_manifest
  run_audit audit_manifest_coherence.py  audit_manifest_coherence
fi

if [[ "${DAY}" == "thursday" || "${DAY}" == "all" ]]; then
  run_audit audit_phase_order.py     audit_phase_order
  run_audit audit_changelog_sync.py  audit_changelog
  run_audit audit_template_flags.py  audit_templates_weekly
  run_audit audit_css_style.py        audit_css_style
  run_audit audit_hardcoded_config.py audit_hardcoded_config
  run_audit audit_palette_registry.py audit_palette
fi

if [[ "${DAY}" == "friday" || "${DAY}" == "all" ]]; then
  run_audit audit_task_drift.py      audit_task_drift
fi

if [[ "${DAY}" == "ondemand" ]]; then
  run_audit audit_package_deps.py    audit_package_deps
  run_audit audit_parity_coverage.py audit_parity_coverage
  run_audit audit_docs_sync.py       audit_docs_sync
  run_audit audit_library_tests.py   audit_library_tests
fi

echo "=== Audit run complete. Unprocessed reports ==="
grep -rL "^Status: PROCESSED" "${LOGS}"/*.md 2>/dev/null | xargs -I{} basename {} || echo "(none)"
