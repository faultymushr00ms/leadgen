"""
Daily aggregation monitor runner.
Run directly: python run_monitor.py
Cron (daily at 6am): 0 6 * * * cd /home/user/leadgen && python run_monitor.py >> logs/monitor.log 2>&1
"""

import os
import sys

# Ensure we run from project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")

from scraper.aggregation_monitor import run_monitor

if __name__ == "__main__":
    report = run_monitor()
    # Exit 1 if new communities found — useful for cron alert integration
    if report.get("new_communities_count", 0) > 0:
        print(f"\n⚠ ACTION NEEDED: {report['new_communities_count']} new aggregation communities found.")
        print("  Review output/agg_monitor_*.json and add missing zones to data/regions/")
        sys.exit(1)
    sys.exit(0)
