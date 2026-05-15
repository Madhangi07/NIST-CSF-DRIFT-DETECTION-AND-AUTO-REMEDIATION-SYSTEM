import json
import os
from datetime import datetime
from database.db_connection import get_connection
from datetime import datetime

from detection_engine.collectors.windows_collector import (
    get_password_policy,
    get_firewall_status,
    get_local_admin_users,
    get_service_status
)

BASE_PATH = "evidence_vault"


def _ensure_dirs():
    os.makedirs(f"{BASE_PATH}/snapshots/before", exist_ok=True)
    os.makedirs(f"{BASE_PATH}/snapshots/after", exist_ok=True)
    os.makedirs(f"{BASE_PATH}/diffs", exist_ok=True)


def _collect_after_state(services_list=None):
    after = {
        "password_policy": get_password_policy(),
        "firewall": get_firewall_status(),
        "users": get_local_admin_users(),
        "services": {}
    }

    if services_list:
        for svc in services_list:
            after["services"][svc] = get_service_status(svc)

    return after


def _generate_diff(before, after):
    diff = {}

    for key in before:
        if before[key] != after.get(key):
            diff[key] = {
                "before": before[key],
                "after": after.get(key)
            }

    return diff


def collect_evidence(before_snapshot, control, severity):
    """
    Save before/after/diff evidence + store in DB
    """

    _ensure_dirs()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    before_file = f"{BASE_PATH}/snapshots/before/{timestamp}_before_{control}.json"
    with open(before_file, "w") as f:
        json.dump(before_snapshot, f, indent=4)

    after_snapshot = _collect_after_state()
    after_file = f"{BASE_PATH}/snapshots/after/{timestamp}_after_{control}.json"
    with open(after_file, "w") as f:
        json.dump(after_snapshot, f, indent=4)

    diff = _generate_diff(before_snapshot, after_snapshot)
    diff_file = f"{BASE_PATH}/diffs/{timestamp}_diff_{control}.json"
    with open(diff_file, "w") as f:
        json.dump(diff, f, indent=4)

    print("Evidence collected:")
    print(f"   BEFORE → {before_file}")
    print(f"   AFTER  → {after_file}")
    print(f"   DIFF   → {diff_file}")

    conn = get_connection()
    cur = conn.cursor()

    db_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
    INSERT INTO evidence (control, severity, before_state, after_state, collected_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        control,
        severity,
        json.dumps(before_snapshot),
        json.dumps(after_snapshot),
        db_timestamp
    ))

    conn.commit()
    conn.close()