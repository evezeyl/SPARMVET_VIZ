#!/usr/bin/env bash
# Install SPARMVET audit systemd user timers.
# Run once. Re-run after editing any .service or .timer file to reload changes.
#
# What Persistent=true means:
#   If the scheduled time passed while your PC was off, systemd fires the timer
#   immediately on the next boot (or next login for user units). No missed audits.

set -euo pipefail

UNIT_DIR="${HOME}/.config/systemd/user"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing SPARMVET audit units to ${UNIT_DIR}..."
mkdir -p "${UNIT_DIR}"

cp "${SOURCE_DIR}/sparmvet-audit@.service" "${UNIT_DIR}/"
cp "${SOURCE_DIR}/sparmvet-audit-sunday.timer"    "${UNIT_DIR}/"
cp "${SOURCE_DIR}/sparmvet-audit-wednesday.timer" "${UNIT_DIR}/"
cp "${SOURCE_DIR}/sparmvet-audit-thursday.timer"  "${UNIT_DIR}/"
cp "${SOURCE_DIR}/sparmvet-audit-friday.timer"    "${UNIT_DIR}/"

systemctl --user daemon-reload

for timer in sunday wednesday thursday friday; do
  systemctl --user enable --now "sparmvet-audit-${timer}.timer"
  echo "  enabled: sparmvet-audit-${timer}.timer"
done

echo ""
echo "All timers active. Status:"
systemctl --user list-timers "sparmvet-audit-*" --no-pager
