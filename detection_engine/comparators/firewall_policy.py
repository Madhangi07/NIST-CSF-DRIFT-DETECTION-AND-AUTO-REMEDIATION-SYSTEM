def compare_firewall_policy(current, expected):
    drift = {}
    for profile in expected:
        if current.get(profile) != expected[profile]:
            drift[profile] = {
                "expected": expected[profile],
                "current": current.get(profile)
            }
    return drift