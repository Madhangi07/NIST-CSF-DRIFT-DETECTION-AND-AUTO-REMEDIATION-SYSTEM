import subprocess


def fix_password_policy():
    print("Running password fix NOW...")

    result = subprocess.run(
        ["net", "accounts", "/minpwlen:12", "/maxpwage:90"],
        capture_output=True,
        text=True
    )

    print("RETURN CODE:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return result.returncode == 0

def fix_firewall():
    try:
        subprocess.run(
            [
                "powershell",
                "-Command",
                "Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True"
            ],
            check=True
        )
        return True
    except:
        return False


def remove_unauthorized_users(details):
    try:
        for user in details:
            subprocess.run(
                ["net", "localgroup", "Administrators", user, "/delete"],
                check=True
            )
        return True
    except:
        return False


def fix_services(details):
    try:
        for svc, state in details.items():
            if state == "Running":
                subprocess.run(["sc", "start", svc], check=True)
            else:
                subprocess.run(["sc", "stop", svc], check=True)
        return True
    except:
        return False