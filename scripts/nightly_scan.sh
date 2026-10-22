#!/usr/bin/env bash
# FORGE Nightly Scan — NE Ohio zones
# Runs run_monitor.py and run_refresh.py --fetch --region ne_ohio
# Logs to logs/scan_YYYY-MM-DD.log
# Non-zero exits are logged as ACTION NEEDED, not crashes.
# Schedule: launchd at 6:30 AM daily (see ~/Library/LaunchAgents/com.forge.nightlyscan.plist)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

DATE="$(date +%F)"
LOG_DIR="$PROJECT_DIR/logs"
REPORT_DIR="$PROJECT_DIR/data/reports"
LOG_FILE="$LOG_DIR/scan_${DATE}.log"

mkdir -p "$LOG_DIR" "$REPORT_DIR"

exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "FORGE Nightly Scan — $DATE $(date +%T)"
echo "========================================"

# Activate virtualenv
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "[setup] venv activated: $VIRTUAL_ENV"
else
    echo "[setup] WARNING: .venv not found, using system Python"
fi

PYTHON="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"
PYTHON="${PYTHON:-python3}"
echo "[setup] Python: $($PYTHON --version 2>&1)"

REPORT_FILE="$REPORT_DIR/scan_${DATE}.md"
ACTION_NEEDED=0

# ── Step 1: Aggregation monitor ───────────────────────────────────────────────
echo ""
echo "[monitor] Running aggregation monitor..."
if "$PYTHON" "$PROJECT_DIR/run_monitor.py" ; then
    echo "[monitor] OK — no new communities found"
else
    EXIT_CODE=$?
    echo "[monitor] ACTION NEEDED (exit $EXIT_CODE) — new aggregation communities detected"
    echo "[monitor] Review output/agg_monitor_*.json and add missing zones to data/regions/"
    ACTION_NEEDED=1
fi

# ── Step 2: Rate refresh — NE Ohio only ───────────────────────────────────────
echo ""
echo "[refresh] Running rate refresh (NE Ohio)..."
if "$PYTHON" "$PROJECT_DIR/run_refresh.py" --fetch --region ne_ohio \
    --report "$PROJECT_DIR/output/refresh_report_${DATE}.json" ; then
    echo "[refresh] OK"
else
    EXIT_CODE=$?
    echo "[refresh] ACTION NEEDED (exit $EXIT_CODE)"
    ACTION_NEEDED=1
fi

# ── Step 3: Write markdown report ─────────────────────────────────────────────
echo ""
echo "[report] Writing $REPORT_FILE..."
"$PYTHON" - <<PYEOF
import json, os, glob
from datetime import date

today = "$DATE"
report_file = "$REPORT_FILE"
output_dir = os.path.join("$PROJECT_DIR", "output")

lines = [f"# FORGE Scan Report — {today}", ""]

# Pull latest refresh report
pattern = os.path.join(output_dir, f"refresh_report_{today}.json")
matches = sorted(glob.glob(pattern))
if matches:
    with open(matches[-1]) as f:
        data = json.load(f)
    added = data.get("added", [])
    if added:
        lines.append("## Changes Detected")
        lines.append("")
        for item in added:
            zone = item.get("zone", "?")
            field = item.get("field", "?")
            old = item.get("stored_value", "?")
            new = item.get("observed_value", "?")
            url = item.get("source_url", "")
            lines.append(f"- **{zone}** — {field}: {old!r} → {new!r}")
            if url:
                lines.append(f"  Source: {url}")
        lines.append("")
    else:
        lines.append("## No changes detected")
        lines.append("")
    lines.append(f"Zones scanned: {data.get('zones_loaded', '?')} | "
                 f"Observations: {data.get('observations', '?')} | "
                 f"Diffs: {data.get('diffs_found', '?')}")
else:
    lines.append("## No refresh report found for today")

lines.append("")
lines.append(f"Log: logs/scan_{today}.log")

with open(report_file, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"[report] Written: {report_file}")
PYEOF

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [ "$ACTION_NEEDED" -eq 1 ]; then
    echo "SCAN COMPLETE — ACTION NEEDED. Review log: $LOG_FILE"
    echo "Report: $REPORT_FILE"
else
    echo "SCAN COMPLETE — no action needed."
    echo "Report: $REPORT_FILE"
fi

# Always exit 0 so launchd doesn't treat this as a crash
exit 0
