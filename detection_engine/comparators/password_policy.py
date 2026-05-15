def compare_password_policy(current, baseline):
    drift = {}
    if current["min_length"] < baseline["min_length"]:
        drift["min_length"] = {
            "expected": baseline["min_length"],
            "current": current["min_length"]
        }
    return drift