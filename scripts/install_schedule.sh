#!/usr/bin/env bash
# Install the FORGE nightly scan as a user LaunchAgent.
#
# The repo root on this Mac is /Users/sky/leadgen/leadgen (the directory that
# contains app.py and scripts/, not the parent folder). Override with
# FORGE_ROOT if the checkout lives somewhere else.
#
# If the Mac is asleep at 6:30 AM, launchd runs the missed StartCalendarInterval
# job once on wake. It does not replay a separate run for every missed day.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/com.forge.nightlyscan.plist"
DEFAULT_ROOT="/Users/sky/leadgen/leadgen"
ROOT="${FORGE_ROOT:-$DEFAULT_ROOT}"
LABEL="com.forge.nightlyscan"
DOMAIN="gui/$(id -u)"
DEST="${HOME}/Library/LaunchAgents/${LABEL}.plist"

if [[ ! -f "$TEMPLATE" ]]; then
    echo "missing plist template: $TEMPLATE" >&2
    exit 1
fi

mkdir -p "${HOME}/Library/LaunchAgents" "${ROOT}/logs"
sed "s#${DEFAULT_ROOT}#${ROOT}#g" "$TEMPLATE" > "$DEST"

# Replace a previously loaded job so the new plist is the one launchd runs.
launchctl bootout "${DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
launchctl unload "$DEST" >/dev/null 2>&1 || true

if launchctl bootstrap "$DOMAIN" "$DEST"; then
    echo "bootstrapped ${LABEL}"
elif launchctl load "$DEST"; then
    echo "loaded ${LABEL}"
else
    echo "failed to bootstrap or load ${DEST}" >&2
    exit 1
fi

if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
    echo "verified: launchctl print ${DOMAIN}/${LABEL}"
elif launchctl list | grep -q "${LABEL}"; then
    echo "verified: launchctl list contains ${LABEL}"
else
    echo "verification failed: ${LABEL} is not loaded" >&2
    exit 1
fi

cat <<EOF
Installed ${DEST}
Project: ${ROOT}
Schedule: every day at 6:30 AM local time.
If the Mac is asleep at 6:30, launchd runs the job once on wake (StartCalendarInterval). A long sleep does not replay one run per missed day.
EOF
