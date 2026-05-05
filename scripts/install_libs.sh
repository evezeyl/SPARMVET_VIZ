#!/usr/bin/env bash
# Install all SPARMVET_VIZ local libraries into the active venv as editable installs.
# Run once after cloning or after adding a new lib.
#
# Usage:
#   ./scripts/install_libs.sh              # uses .venv/bin/pip
#   VENV=.my_venv ./scripts/install_libs.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-${REPO_ROOT}/.venv}"
PIP="${VENV}/bin/pip"

if [[ ! -x "${PIP}" ]]; then
    echo "ERROR: pip not found at ${PIP}"
    echo "Create the venv first: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "Installing SPARMVET_VIZ libs into ${VENV}"
echo

LIBS=(
    utils
    connector
    ingestion
    transformer
    viz_factory
    viz_gallery
    blueprint_arch
    test_lab
)

for lib in "${LIBS[@]}"; do
    lib_path="${REPO_ROOT}/libs/${lib}"
    if [[ ! -f "${lib_path}/pyproject.toml" ]]; then
        echo "  SKIP  ${lib}  (no pyproject.toml)"
        continue
    fi
    echo "  INSTALL  ${lib}"
    "${PIP}" install -e "${lib_path}" --quiet
done

echo
echo "All libs installed. Verify with:"
echo "  ${VENV}/bin/pip list | grep -E 'utils|connector|ingestion|transformer|viz|blueprint|test_lab'"
