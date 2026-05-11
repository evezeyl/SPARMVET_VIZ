#!/usr/bin/env bash
# assets/scripts/bundle_connect.sh
#
# Posit Connect bundle preparation (DEPLOY-CONNECT-1, ADR-048).
#
# Why this exists:
#   Posit Connect cannot install editable local packages (-e ./libs/...).
#   This script builds wheels for all local libs into pkgs/, which
#   requirements-connect.txt then references via --find-links pkgs/.
#
# Usage:
#   bash assets/scripts/bundle_connect.sh            # build + deploy dry-run
#   bash assets/scripts/bundle_connect.sh --deploy   # build + rsconnect deploy
#
# Requirements:
#   - ./.venv/bin/python (project venv)
#   - rsconnect-python installed: pip install rsconnect-python
#   - CONNECT_SERVER and CONNECT_API_KEY env vars set (for --deploy)
#
# The rsconnect deploy step bundles app/, config/, assets/, libs/, and pkgs/
# together and uploads them to the Connect server.

set -euo pipefail

PYTHON="./.venv/bin/python"
DEPLOY=0

for arg in "$@"; do
    case "$arg" in
        --deploy) DEPLOY=1 ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

echo "=== SPARMVET Connect Bundle Preparation ==="
echo ""

# ── Step 1: Build wheels for all local libs ───────────────────────────────────
echo "Step 1: Building wheels for local libraries..."
mkdir -p pkgs/

$PYTHON -m pip wheel \
    libs/utils \
    libs/ingestion \
    libs/transformer \
    libs/connector \
    libs/viz_factory \
    libs/viz_gallery \
    libs/blueprint_arch \
    libs/test_lab \
    app \
    --no-deps \
    --wheel-dir pkgs/ \
    --quiet

echo "  Wheels written to pkgs/:"
ls pkgs/*.whl | while read f; do echo "    $(basename $f)"; done
echo ""

# ── Step 2: Verify requirements-connect.txt references all libs ───────────────
echo "Step 2: Verifying requirements-connect.txt..."
MISSING=""
for lib in utils ingestion transformer connector viz_factory viz_gallery blueprint_arch app; do
    if ! grep -q "^$lib$" requirements-connect.txt; then
        MISSING="$MISSING $lib"
    fi
done
if [ -n "$MISSING" ]; then
    echo "  WARNING: These libs are not listed in requirements-connect.txt:$MISSING"
    echo "  Add them and re-run."
else
    echo "  All local libs present in requirements-connect.txt"
fi
echo ""

# ── Step 3: Sanity-check the app entry point ──────────────────────────────────
echo "Step 3: Checking app entry point (app/src/main.py)..."
if $PYTHON -c "from app.src.main import app; print('  Entry point OK')" 2>&1; then
    :
else
    echo "  FAIL: app/src/main import failed. Fix before deploying."
    exit 1
fi
echo ""

# ── Step 4 (optional): Deploy to Connect ─────────────────────────────────────
if [ "$DEPLOY" -eq 1 ]; then
    echo "Step 4: Deploying to Posit Connect..."

    if [ -z "${CONNECT_SERVER:-}" ] || [ -z "${CONNECT_API_KEY:-}" ]; then
        echo "  ERROR: CONNECT_SERVER and CONNECT_API_KEY must be set."
        echo "  export CONNECT_SERVER=https://your-connect-server.example.com"
        echo "  export CONNECT_API_KEY=<your-api-key>"
        exit 1
    fi

    # Set SPARMVET_PROFILE to the Connect profile path on the server.
    # Replace PLACEHOLDER_APP_GUID with the actual app GUID after first deploy.
    SPARMVET_PROFILE_PATH="${SPARMVET_PROFILE_PATH:-config/deployment/connect/connect_profile_template.yaml}"

    $PYTHON -m rsconnect deploy shiny . \
        --server "$CONNECT_SERVER" \
        --api-key "$CONNECT_API_KEY" \
        --entrypoint "app/src/main:app" \
        --requirements requirements-connect.txt \
        --environment "SPARMVET_PROFILE=$SPARMVET_PROFILE_PATH" \
        --environment "SPARMVET_PERSONA=pipeline-static" \
        --title "SPARMVET_VIZ"

    echo "  Deployment complete."
else
    echo "Step 4 (deploy) skipped — run with --deploy to upload to Connect."
fi

echo ""
echo "=== Done ==="
