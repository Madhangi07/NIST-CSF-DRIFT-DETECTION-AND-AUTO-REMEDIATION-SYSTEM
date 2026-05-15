import json
import subprocess
from messaging.producer import send_to_queue
from detection_engine.comparators.password_policy import compare_password_policy
from detection_engine.comparators.firewall_policy import compare_firewall_policy
from detection_engine.collectors.windows_collector import get_firewall_status
from detection_engine.collectors.windows_collector import get_local_admin_users
from detection_engine.comparators.user_accounts import compare_admin_users
from detection_engine.collectors.windows_collector import get_service_status
from detection_engine.comparators.services import compare_services
from detection_engine.severity_calculator import calculate_severity
from approval_engine.email_notifier import send_notification

DETECTED_CONTROLS = []

def run_detection():
    
    with open("baselines/windows/password_policy.json", "r") as f:
        baseline = json.load(f)

    with open("baselines/windows/firewall_policy.json", "r") as f:
        firewall_baseline = json.load(f)

    with open("baselines/windows/user_accounts.json") as f:
        user_baseline = json.load(f)

    with open("baselines/windows/services.json") as f:
        svc_baseline = json.load(f)

    
    current_config = {
        "min_length": 6,          
        "complexity": True,
        "max_age_days": 90
    }

    current_firewall = get_firewall_status()
    current_users = get_local_admin_users()

    current_services = {
        svc: get_service_status(svc)
        for svc in svc_baseline["expected"]
    }

    print("Detection engine running...")

    any_drift = False

    drift_details = compare_password_policy(current_config, baseline)

    if drift_details:
        control = baseline["control"]
        severity = calculate_severity(control, drift_details)

        print("PASSWORD DRIFT DETECTED")
        print("Drift details:", drift_details)
        print("Severity level:", severity)

        any_drift = True

        drift_record = {
            "control": control,
            "severity": severity,
            "details": drift_details,
            "status": "PENDING"
        }
        DETECTED_CONTROLS.append(control)
        print("Drift record created:", drift_record)
        send_to_queue(drift_record)

    firewall_drift = compare_firewall_policy(current_firewall, firewall_baseline["expected"])

    if firewall_drift:
        control = firewall_baseline["control"]
        severity = calculate_severity(control, firewall_drift)

        print("FIREWALL DRIFT DETECTED")
        print("Drift details:", firewall_drift)

        any_drift = True

        drift_record = {
            "control": control,
            "severity": severity,
            "details": firewall_drift,
            "status": "PENDING"
        }
        DETECTED_CONTROLS.append(control)
        print("Firewall drift record created:", drift_record)
        send_to_queue(drift_record)

    user_drift = compare_admin_users(current_users, user_baseline["expected"])

    if user_drift:
        control = user_baseline["control"]
        severity = calculate_severity(control, user_drift)

        print("USER DRIFT DETECTED")
        print("Drift details:", user_drift)

        any_drift = True

        drift_record = {
            "control": control,
            "severity": severity,
            "details": user_drift,
            "status": "PENDING"
        }
        DETECTED_CONTROLS.append(control)
        print("User drift record created:", drift_record)
        send_to_queue(drift_record)

    service_drift = compare_services(current_services, svc_baseline["expected"])

    if service_drift:
        control = svc_baseline["control"]
        severity = calculate_severity(control, service_drift)

        print("SERVICE DRIFT DETECTED")
        print("Drift details:", service_drift)

        any_drift = True

        drift_record = {
            "control": control,
            "severity": severity,
            "details": service_drift,
            "status": "PENDING"
        }
        DETECTED_CONTROLS.append(control)
        print("Service drift record created:", drift_record)
        send_to_queue(drift_record)

    if not any_drift:
        print("No drift detected")

    if DETECTED_CONTROLS:
        message = "Detected Drifts:\n\n"

        for ctrl in DETECTED_CONTROLS:
            message += f"- {ctrl}\n"

        send_notification("Drift Alert", message)