-- =====================================================================
-- Fake Medicine Detection System
-- Database Schema: SQLite3 Relational Database Definition
-- Academic Project: Second Year B.Tech Computer Science & Engineering
-- Institution: MIT-ADT University, Pune | Group ID: 1603
-- Mentor: Dr. Sachin More | Team: Yogesh Shinde, Pranav Jagtap, Rupesh Kawthekar, Kunal Kothari
-- =====================================================================

-- Table 1: Registered User Accounts & Roles
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT CHECK(role IN ('General User', 'Pharmacist')) NOT NULL DEFAULT 'General User',
    institution TEXT DEFAULT 'MIT-ADT University, Pune',
    department TEXT DEFAULT 'Computer Science & Engineering',
    phone TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- Table 2: Authorized Reference Medicines Registry
CREATE TABLE IF NOT EXISTS medicines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    generic_name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    license_no TEXT NOT NULL,
    batch_number TEXT NOT NULL UNIQUE,
    mfg_date TEXT NOT NULL,
    exp_date TEXT NOT NULL,
    mrp REAL NOT NULL,
    dosage_form TEXT DEFAULT 'Tablet',
    strength TEXT,
    packaging_type TEXT,
    schedule_class TEXT,
    verification_status TEXT CHECK(verification_status IN ('VERIFIED', 'SUSPICIOUS', 'UNABLE TO VERIFY')) NOT NULL DEFAULT 'VERIFIED',
    status_reason TEXT,
    safety_score INTEGER DEFAULT 100,
    is_recalled INTEGER DEFAULT 0,
    barcode TEXT,
    qr_code_data TEXT,
    therapeutic_category TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_medicines_batch ON medicines (batch_number);
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name);
CREATE INDEX IF NOT EXISTS idx_medicines_mfg ON medicines (manufacturer);

-- Table 3: User Verification Audit Trail / Scan Logs
CREATE TABLE IF NOT EXISTS verification_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    medicine_name TEXT,
    batch_number TEXT,
    manufacturer TEXT,
    user_price REAL,
    mrp REAL,
    status TEXT CHECK(status IN ('VERIFIED', 'SUSPICIOUS', 'UNABLE TO VERIFY')) NOT NULL,
    safety_score INTEGER NOT NULL,
    risk_level TEXT,
    anomalies_json TEXT,
    mfg_date TEXT,
    exp_date TEXT,
    check_type TEXT DEFAULT 'IMAGE_ANALYSIS',
    headline TEXT,
    summary TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_user_id ON verification_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON verification_logs (timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_status ON verification_logs (status);

-- Table 4: Incident Reports & Spurious Drug Vigilance Alerts
CREATE TABLE IF NOT EXISTS incident_reports (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    reporter_name TEXT,
    pharmacy_name TEXT,
    medicine_name TEXT NOT NULL,
    batch_number TEXT,
    city TEXT NOT NULL,
    description TEXT NOT NULL,
    investigation_status TEXT DEFAULT 'PENDING_INVESTIGATION',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_reports_city ON incident_reports (city);
CREATE INDEX IF NOT EXISTS idx_reports_user ON incident_reports (user_id);
