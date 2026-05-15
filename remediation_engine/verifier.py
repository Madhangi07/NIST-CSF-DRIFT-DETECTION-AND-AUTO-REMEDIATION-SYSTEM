import json
from detection_engine.collectors.windows_collector import (
    get_password_policy,
    get_firewall_status,
    get_local_admin_users,
    get_service_status
)


def verify_fix(control):

    if control == "Password Policy":
        with open("baselines/windows/password_policy.json") as f:
            baseline = json.load(f)

        current = get_password_policy()

        return current.get("min_length", 0) >= baseline["min_length"]

    elif control == "Windows Firewall":
        with open("baselines/windows/firewall_policy.json") as f:
            baseline = json.load(f)

        current = get_firewall_status()

        return current == baseline["expected"]

    elif control == "Unauthorized Admin Users":
        with open("baselines/windows/user_accounts.json") as f:
            baseline = json.load(f)

        current = get_local_admin_users()

        return set(current) == set(baseline["expected"])

    elif control == "Services":
        with open("baselines/windows/services.json") as f:
            baseline = json.load(f)

        current = {
            svc: get_service_status(svc)
            for svc in baseline["expected"]
        }

        return current == baseline["expected"]

    return True