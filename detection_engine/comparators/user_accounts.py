def compare_admin_users(current, expected):
    drift = {}

    unauthorized = [u for u in current if u not in expected]

    if unauthorized:
        drift["unauthorized_users"] = {
            "expected": expected,
            "current": current
        }

    return drift
