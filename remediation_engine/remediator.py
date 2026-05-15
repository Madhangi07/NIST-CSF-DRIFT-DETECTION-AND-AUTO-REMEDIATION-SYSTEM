from asyncio import subprocess
import json
from remediation_engine.snapshot_manager import take_snapshot
from remediation_engine.rollback_manager import rollback
from remediation_engine.verifier import verify_fix
from remediation_engine.executors.windows_executor import (
    fix_password_policy,
    fix_firewall,
    remove_unauthorized_users,
    fix_services
)
from evidence_vault.evidence_collector import collect_evidence
from approval_engine.email_notifier import send_notification

import subprocess, getpass

ALLOWED = {"Administrator"}  
CURRENT = getpass.getuser() 

def get_admin_users():
    result = subprocess.run(
        ["net", "localgroup", "administrators"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    users = []
    capture = False

    for line in lines:
        line = line.strip()

        if "Members" in line:
            capture = True
            continue

        if "command completed" in line.lower():
            break

        if capture:
            if not line or "----" in line:
                continue

            users.append(line)

    return users

def fix_admin_users():
    users = get_admin_users()
    print("Before fix:", users)
  

    allowed = {"Administrator", "madhangi"}

    for user in users:
        if user not in allowed:
            print(f"Removing unauthorized user: {user}")
            subprocess.run(
                ["net", "localgroup", "administrators", user, "/delete"],
                check=True
            )

    return True
    
def verify_admin_users():
    users = get_admin_users()
    print("After fix:", users)


    allowed = {"Administrator", "madhangi"}

    for user in users:
        if user not in allowed:
            return False

    return True

def handle_drift(drift_record):
    print("Remediation engine received drift")

    control = drift_record["control"]
    details = drift_record["details"]

    send_notification(
        "Drift Detected",
        f"{control} drift detected. Auto-remediation starting."
    )

    snapshot = take_snapshot()

    success = False

    try:
        if control == "Password Policy":
            print("Fixing password policy...")
            success = fix_password_policy()

        elif control == "Windows Firewall":
            print("Fixing firewall...")
            try:
                subprocess.run(
                    ["netsh", "advfirewall", "set", "allprofiles", "state", "on"],
                    check=True
                )
                print("Firewall enabled successfully")
            except Exception as e:
                print("Firewall fix failed:", e)
            success = fix_firewall()

        elif control == "Unauthorized Admin Users":
            print("Fixing admin users...")

            success = fix_admin_users()

            if not success:
                raise Exception("Fix failed")

            if not verify_admin_users():
                raise Exception("Verification failed")

            print("Admin users fixed and verified")
            return   

        elif control == "Critical Services":
            print("Fixing critical services...")

            try:
                for service in details:
                    print(f"Starting service: {service}")

                    subprocess.run(
                        ["net", "start", service],
                        check=True
                    )

                print("Services started successfully")
                success = True

            except Exception as e:
                print("Failed to fix services:", e)
                success = False

        verified = verify_fix(control)

        if not (success and verified):
            print("Fix failed or verification failed → Rolling back...")

            send_notification(
                "Remediation Failed",
                f"{control} failed. Rollback triggered."
            )
            
            rollback(snapshot)
            return

        print("Fix successful and verified")

        send_notification(
            "Remediation Success",
            f"{control} fixed successfully."
        )
        
        collect_evidence(snapshot, control, drift_record["severity"])

    except Exception as e:
        print(f"Error during remediation: {e}")
        rollback(snapshot)