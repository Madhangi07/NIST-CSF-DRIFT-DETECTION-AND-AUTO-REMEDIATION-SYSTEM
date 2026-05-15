def compare_services(current, expected):
    drift = {}

    for svc, exp in expected.items():
        cur = current.get(svc)
        if cur != exp:
            drift[svc] = {
                "expected": exp,
                "current": cur
            }

    return drift