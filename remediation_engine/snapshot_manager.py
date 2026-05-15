import json
import os
from datetime import datetime

from detection_engine.collectors.windows_collector import (
    get_password_policy,
    get_firewall_status,
    get_local_admin_users,
    get_service_status
)

SNAPSHOT_DIR = "evidence_vault/snapshots"

def take_snapshot(services_list=None):
    

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    password_policy = get_password_policy()
    firewall = get_firewall_status()
    users = get_local_admin_users()

    services = {}
    if services_list:
        for svc in services_list:
            services[svc] = get_service_status(svc)

    snapshot = {
        "timestamp": timestamp,
        "password_policy": password_policy,
        "firewall": firewall,
        "users": users,
        "services": services
    }

    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    filename = f"{SNAPSHOT_DIR}/{timestamp}_snapshot.json"

    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=4)

    print(f"Snapshot saved: {filename}")

    return snapshot