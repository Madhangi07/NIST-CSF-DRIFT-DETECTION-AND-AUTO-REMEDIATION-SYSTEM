CREATE TABLE systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT,
    ip_address TEXT,
    os_type TEXT,
    created_at TEXT
);

CREATE TABLE baselines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    os_type TEXT,
    control_name TEXT,
    expected_value TEXT,
    nist_control TEXT
);

CREATE TABLE drift_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER,
    control_name TEXT,
    current_value TEXT,
    expected_value TEXT,
    severity TEXT,
    status TEXT,
    detected_at TEXT
);

CREATE TABLE remediation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drift_id INTEGER,
    action_taken TEXT,
    status TEXT,
    executed_at TEXT
);

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drift_id INTEGER,
    before_state TEXT,
    after_state TEXT,
    collected_at TEXT
);