import subprocess
import json

def get_password_policy():
    
    result = subprocess.run(
        ["net", "accounts"],
        capture_output=True,
        text=True,
        shell=True
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to collect password policy")

    policy = {}

    for line in result.stdout.splitlines():
        if "Minimum password length" in line:
            policy["min_length"] = int(line.split(":")[-1].strip())
        elif "Maximum password age" in line:
            policy["max_age_days"] = int(line.split(":")[-1].strip().split()[0])

    return policy



def get_firewall_status():
    
    result = subprocess.run(
        ["powershell", "-Command", "Get-NetFirewallProfile | Select Name, Enabled"],
        capture_output=True,
        text=True,
        shell=True
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to collect firewall status")

    firewall = {}

    for line in result.stdout.splitlines():
        if "Domain" in line:
            firewall["Domain"] = "True" in line
        elif "Private" in line:
            firewall["Private"] = "True" in line
        elif "Public" in line:
            firewall["Public"] = "True" in line

    return firewall

def get_local_admin_users():
    
    result = subprocess.run(
        ["powershell", "-Command", "Get-LocalGroupMember Administrators | Select Name"],
        capture_output=True,
        text=True,
        shell=True
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to collect admin users")

    users = []

    for line in result.stdout.splitlines():
        if "\\" in line:
            users.append(line.strip())

    return users

def get_service_status(service_name):
    result = subprocess.run(
        ["powershell", "-Command", f"Get-Service {service_name} | Select -ExpandProperty Status"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error checking service {service_name}")
        return "UNKNOWN"

    status = result.stdout.strip()

    if status.lower() == "running":
        return "RUNNING"
    else:
        return "STOPPED"


if __name__ == "__main__":
    print("Password Policy:")
    print(json.dumps(get_password_policy(), indent=2))

    print("\nFirewall Status:")
    print(json.dumps(get_firewall_status(), indent=2))

    print("\nAdmin Users:")
    print(json.dumps(get_local_admin_users(), indent=2))

    print("\nServices:")
    print(json.dumps(get_service_status(), indent=2))

