def calculate_severity(control, drift_details):
    if control == "Password Policy":
        current = drift_details["min_length"]["current"]

        if current < 8:
            return "CRITICAL"
        return "HIGH"

    if control == "Unauthorized Admin Users":
        return "CRITICAL"

    if control == "Windows Firewall":
        return "HIGH"

    if control == "Services":
        return "MEDIUM"

    return "LOW"