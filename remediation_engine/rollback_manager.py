import subprocess

def rollback(snapshot):
    print("Starting rollback...")

    try:
        pw = snapshot["password_policy"]

        print("Restoring password policy...")
        subprocess.run(
            [
                "net",
                "accounts",
                f"/minpwlen:{pw.get('min_length', 12)}",
                f"/maxpwage:{pw.get('max_age_days', 90)}"
            ],
            check=True
        )

        fw = snapshot["firewall"]

        print("Restoring firewall...")
        for profile, state in fw.items():
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Set-NetFirewallProfile -Profile {profile} -Enabled {'True' if state else 'False'}"
                ],
                check=True
            )

        users = snapshot["users"]

        print("Restoring admin users...")
        for user in users:
            result = subprocess.run(
                ["net", "localgroup", "Administrators", user, "/add"],
                capture_output=True,
                text=True
            )

            output = (result.stdout + result.stderr).lower()

            if "already a member" in output:
                print(f"{user} already in group (skipping)")
            elif result.returncode != 0:
                raise Exception(result.stderr)

        services = snapshot["services"]

        print("Restoring services...")
        for svc, state in services.items():
            if state == "Running":
                subprocess.run(["sc", "start", svc], check=True)
            else:
                subprocess.run(["sc", "stop", svc], check=True)

        print("Rollback completed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Rollback failed at step: {e}")
        print("System may be in partial state. Manual intervention required.")
        raise