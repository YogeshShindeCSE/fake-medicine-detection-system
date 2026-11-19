"""
Fake Medicine Detection System
Database Engine & Persistence Layer (SQLite3)
Academic Project: Second Year B.Tech Computer Science & Engineering
Institution: MIT-ADT University, Pune | Group ID: 1603
Mentor: Dr. Sachin More | Team: Yogesh Shinde, Pranav Jagtap, Rupesh Kawthekar, Kunal Kothari
"""

import sqlite3
import json
import os
import hashlib
import hmac
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mediverify.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------------------------------------------------------
# PASSWORD SECURITY & HASHING (PBKDF2-HMAC-SHA256)
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: str = None) -> tuple:
    """Derive salted PBKDF2 hash using SHA-256 with 100,000 iterations."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return hashed, salt

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Constant-time verification of supplied password against stored hash."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, expected_hash)

# -----------------------------------------------------------------------------
# DATABASE INITIALIZATION & MIGRATIONS
# -----------------------------------------------------------------------------
def init_database():
    """Initializes tables from schema and performs seamless column migrations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Execute Base Schema
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    conn.commit()

    # 2. Check and migrate verification_logs columns if already existed
    cursor.execute("PRAGMA table_info(verification_logs)")
    columns = [col["name"] for col in cursor.fetchall()]
    migration_cols = [
        ("user_id", "TEXT"),
        ("mfg_date", "TEXT"),
        ("exp_date", "TEXT"),
        ("check_type", "TEXT DEFAULT 'IMAGE_ANALYSIS'"),
        ("headline", "TEXT"),
        ("summary", "TEXT")
    ]
    for col_name, col_type in migration_cols:
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE verification_logs ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Migration Note] verification_logs.{col_name}: {e}")

    # 3. Check and migrate incident_reports columns
    cursor.execute("PRAGMA table_info(incident_reports)")
    rep_columns = [col["name"] for col in cursor.fetchall()]
    rep_migrations = [
        ("user_id", "TEXT"),
        ("reporter_name", "TEXT")
    ]
    for col_name, col_type in rep_migrations:
        if col_name not in rep_columns:
            try:
                cursor.execute(f"ALTER TABLE incident_reports ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"[Migration Note] incident_reports.{col_name}: {e}")

    conn.commit()

    # 4. Seed Reference Medicines if empty
    cursor.execute("SELECT COUNT(*) AS count FROM medicines")
    if cursor.fetchone()["count"] == 0:
        seed_sample_medicines(cursor)
        conn.commit()
        print("[Database] Seeded 16 standard Indian Pharmacopoeia reference medicines.")

    # 5. Seed Demo Project Accounts if users table empty
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    if cursor.fetchone()["count"] == 0:
        seed_default_users(cursor)
        conn.commit()
        print("[Database] Seeded academic demo user accounts.")

    conn.close()

# -----------------------------------------------------------------------------
# SEED DATA
# -----------------------------------------------------------------------------
def seed_default_users(cursor):
    """Seed project team and demo evaluation accounts."""
    p_hash_1, salt_1 = hash_password("Password@123")
    p_hash_2, salt_2 = hash_password("Password@123")

    users = [
        (
            "USR-MIT-1601",
            "Yogesh Shinde",
            "yogesh.shinde@mitadt.edu.in",
            p_hash_1,
            salt_1,
            "Pharmacist",
            "MIT-ADT University, Pune",
            "Computer Science & Engineering",
            "+91 98765 43210"
        ),
        (
            "USR-MIT-1602",
            "Pranav Jagtap",
            "pranav.jagtap@mitadt.edu.in",
            p_hash_2,
            salt_2,
            "General User",
            "MIT-ADT University, Pune",
            "Computer Science & Engineering",
            "+91 98765 12345"
        )
    ]
    cursor.executemany("""
        INSERT INTO users (
            id, full_name, email, password_hash, salt, role, institution, department, phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

def seed_sample_medicines(cursor):
    """Inserts realistic reference dataset of verified, recalled, and suspicious drugs."""
    seeds = [
        ("MED-001", "Crocin 650", "Paracetamol (Acetaminophen) 650mg", "GlaxoSmithKline Pharmaceuticals Ltd", "MH/DRUG/28-B/1042", "GSK-CRC-8821", "2024-01-15", "2027-12-31", 32.50, "Tablet", "650 mg", "Blister Pack (15 Tablets)", "OTC", "VERIFIED", "Valid manufacturer license, authentic packaging security hash, registered batch in CDSCO central database.", 98, 0, "8901030882105", "MED:Crocin 650|BATCH:GSK-CRC-8821|MRP:32.50", "Analgesic & Antipyretic", "Indicated for mild to moderate fever and headache."),
        ("MED-002", "Augmentin 625 Duo", "Amoxicillin (500mg) + Clavulanic Acid (125mg)", "GlaxoSmithKline Pharmaceuticals Ltd", "MH/DRUG/28-B/1042", "GSK-AUG-4491", "2024-03-10", "2027-10-31", 204.50, "Tablet", "625 mg", "Alu-Alu Strip (10 Tablets)", "Schedule H1", "VERIFIED", "Authentic batch registered with national antibiotic surveillance portal.", 96, 0, "8901030449102", "MED:Augmentin 625 Duo|BATCH:GSK-AUG-4491|MRP:204.50", "Broad-spectrum Antibiotic", "Bacterial respiratory and urinary infections."),
        ("MED-003", "Augmentin 625 Duo", "Amoxicillin (500mg) + Clavulanic Acid (125mg)", "GSK Biotech India Pvt Ltd", "FAKE/LIC/9981-INVALID", "AUG-FAKE-990", "2024-02-01", "2027-02-01", 75.00, "Tablet", "625 mg", "Counterfeit Strip (10 Tablets)", "Schedule H1", "SUSPICIOUS", "Critical warning: Manufacturer entity does not match marketing authorization holder. Price 63% below NPPA ceiling.", 18, 1, "8909999000111", "MED:Augmentin 625 Duo|BATCH:AUG-FAKE-990|MRP:75.00", "Broad-spectrum Antibiotic (SUSPECTED COUNTERFEIT)", "CONFIRMED COUNTERFEIT ALERT. Contains inert chalk. DO NOT CONSUME."),
        ("MED-004", "Dolo 650", "Paracetamol 650mg", "Micro Labs Limited", "KT/DRUG/25/4412", "ML-DOLO-3120", "2024-05-12", "2028-04-30", 33.00, "Tablet", "650 mg", "Blister Pack (15 Tablets)", "OTC", "VERIFIED", "Micro Labs registered serial batch. Micro-engraved seal and batch registration fully validated.", 99, 0, "8901148312015", "MED:Dolo 650|BATCH:ML-DOLO-3120|MRP:33.00", "Analgesic & Antipyretic", "Widely prescribed antipyretic for reducing fever."),
        ("MED-005", "Azithral 500", "Azithromycin 500mg", "Alembic Pharmaceuticals Ltd", "GJ/DRUG/28/7710", "ALM-AZI-7712", "2023-01-10", "2024-06-30", 119.00, "Tablet", "500 mg", "Strip (5 Tablets)", "Schedule H1", "SUSPICIOUS", "EXPIRED & RECALLED BATCH. The batch expired on 2024-06-30 and was issued a formal recall notice.", 25, 1, "8901043771212", "MED:Azithral 500|BATCH:ALM-AZI-7712|MRP:119.00", "Macrolide Antibiotic (RECALLED)", "WARNING: This specific batch is recalled and expired."),
        ("MED-006", "Pan-D", "Pantoprazole (40mg) + Domperidone (30mg SR)", "Alkem Laboratories Ltd", "HP/DRUG/25/8891", "ALK-PND-5541", "2024-02-01", "2027-08-31", 198.00, "Capsule", "40mg + 30mg", "Alu-Alu Strip (15 Capsules)", "Schedule H", "VERIFIED", "Valid manufacturer batch credentials, hologram security verified.", 97, 0, "8901235554118", "MED:Pan-D|BATCH:ALK-PND-5541|MRP:198.00", "Proton Pump Inhibitor", "Prescribed for gastroesophageal reflux disease (GERD)."),
        ("MED-007", "Lipitor 20mg", "Atorvastatin Calcium 20mg", "Pfizer India Ltd", "MH/DRUG/28-B/3301", "PFZ-LIP-9011", "2024-04-18", "2028-02-28", 315.00, "Tablet", "20 mg", "Blister Pack (10 Tablets)", "Schedule H", "VERIFIED", "Authentic Pfizer global batch code, CDSCO clearance code active.", 99, 0, "8901009901123", "MED:Lipitor 20mg|BATCH:PFZ-LIP-9011|MRP:315.00", "Cardiovascular / Statin", "Lowers LDL cholesterol and prevents cardiovascular disease."),
        ("MED-008", "Glycomet-GP 2", "Metformin (500mg SR) + Glimepiride (2mg)", "USV Private Limited", "MH/DRUG/28/1109", "USV-GLY-2190", "2024-06-01", "2027-11-30", 142.00, "Tablet", "500mg + 2mg", "Strip (15 Tablets)", "Schedule H", "VERIFIED", "Valid manufacturing batch, verified USV hologram authenticity.", 96, 0, "8901238219010", "MED:Glycomet-GP 2|BATCH:USV-GLY-2190|MRP:142.00", "Oral Anti-diabetic", "Glycemic control in adult patients with Type 2 Diabetes."),
        ("MED-009", "Telma 40", "Telmisartan 40mg", "Glenmark Pharmaceuticals Ltd", "GA/DRUG/25/6602", "GLN-TEL-6602", "2024-02-20", "2028-01-31", 110.00, "Tablet", "40 mg", "Alu-Alu Strip (15 Tablets)", "Schedule H", "VERIFIED", "Authentic Glenmark batch. Tamper-proof packaging verified.", 98, 0, "8901117660214", "MED:Telma 40|BATCH:GLN-TEL-6602|MRP:110.00", "Antihypertensive (ARB)", "Management of essential hypertension."),
        ("MED-010", "Montair-LC", "Montelukast (10mg) + Levocetirizine (5mg)", "Cipla Limited", "MH/DRUG/28/9912", "CIP-MLC-8840", "2024-03-05", "2027-09-30", 215.00, "Tablet", "10mg + 5mg", "Strip (10 Tablets)", "Schedule H", "VERIFIED", "Valid Cipla registered batch, certified active anti-counterfeit QR code.", 99, 0, "8901115884019", "MED:Montair-LC|BATCH:CIP-MLC-8840|MRP:215.00", "Antiallergic & Bronchodilator", "Treatment of allergic rhinitis and chronic asthma symptoms."),
        ("MED-011", "Allegra 120mg", "Fexofenadine Hydrochloride 120mg", "Sanofi India Limited", "GA/DRUG/28/1022", "SNF-ALL-1022", "2024-01-25", "2027-07-31", 185.00, "Tablet", "120 mg", "Blister Pack (10 Tablets)", "Schedule H", "VERIFIED", "Valid Sanofi registered batch. Hologram matches official records.", 95, 0, "8901004102217", "MED:Allegra 120mg|BATCH:SNF-ALL-1022|MRP:185.00", "Second-generation Antihistamine", "Non-drowsy relief from allergic rhinitis and urticaria."),
        ("MED-012", "Taxim-O 200", "Cefixime 200mg", "Alkem Laboratories Ltd", "HP/DRUG/25/8891", "ALK-TXM-3304", "2024-05-15", "2028-03-31", 108.00, "Tablet", "200 mg", "Strip (10 Tablets)", "Schedule H1", "VERIFIED", "Valid Alkem licensed batch. Cross-checked with state drug testing portal.", 97, 0, "8901235330415", "MED:Taxim-O 200|BATCH:ALK-TXM-3304|MRP:108.00", "Cephalosporin Antibiotic", "Third-generation cephalosporin for bacterial infections."),
        ("MED-013", "Zifi 200", "Cefixime Trihydrate 200mg", "FDC Limited", "MH/DRUG/28/9912", "FDC-ZIF-9912", "2024-04-01", "2027-12-31", 115.00, "Tablet", "200 mg", "Strip (10 Tablets)", "Schedule H1", "VERIFIED", "FDC authorized batch. Secure printing typography matches registered die-line.", 96, 0, "8901211991218", "MED:Zifi 200|BATCH:FDC-ZIF-9912|MRP:115.00", "Cephalosporin Antibiotic", "Broad spectrum antibiotic for respiratory tract infections."),
        ("MED-014", "Shelcal 500", "Calcium (500mg) + Vitamin D3 (250 IU)", "Torrent Pharmaceuticals Ltd", "GJ/DRUG/25/4411", "TOR-SHL-4411", "2024-03-12", "2028-05-31", 131.00, "Tablet", "500mg + 250 IU", "Bottle (15 Tablets)", "Nutraceutical / OTC", "VERIFIED", "Authentic Torrent batch. Cap seal and serialization code valid.", 98, 0, "8901088441113", "MED:Shelcal 500|BATCH:TOR-SHL-4411|MRP:131.00", "Mineral & Vitamin Supplement", "Bone density and calcium absorption in osteoporosis."),
        ("MED-015", "Supradyn Daily", "Multivitamin with Minerals and Trace Elements", "Bayer Pharmaceuticals Pvt Ltd", "MH/DRUG/28/7721", "BYR-SUP-7721", "2024-05-20", "2028-06-30", 54.00, "Tablet", "Multi-complex", "Strip (15 Tablets)", "OTC Supplement", "VERIFIED", "Bayer genuine packaging verified. Unique cross-hatch micro-print seal valid.", 99, 0, "8901009772114", "MED:Supradyn Daily|BATCH:BYR-SUP-7721|MRP:54.00", "Multivitamin", "Daily immunity booster and essential micronutrient supplement."),
        ("MED-016", "XyloCure Fast Relief", "Unregistered Herbal Mixture / Unknown Active", "Himalayan Naturals Bio Labs", "UNREGISTERED/NONE", "XYLO-999-FAKE", "2024-01-01", "2027-01-01", 499.00, "Capsule", "Unknown", "Plastic Bottle (60 Capsules)", "Unregistered Proprietary", "UNABLE TO VERIFY", "No regulatory record found in CDSCO or State Licensing Authorities.", 10, 0, "0000000000000", "MED:XyloCure|BATCH:XYLO-999|PRICE:499", "Unclassified Proprietary (UNVERIFIED)", "Unverified product circulating through unauthorized online channels.")
    ]
    cursor.executemany("""
        INSERT INTO medicines (
            id, name, generic_name, manufacturer, license_no, batch_number,
            mfg_date, exp_date, mrp, dosage_form, strength, packaging_type,
            schedule_class, verification_status, status_reason, safety_score,
            is_recalled, barcode, qr_code_data, therapeutic_category, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seeds)

# -----------------------------------------------------------------------------
# USER REPOSITORY
# -----------------------------------------------------------------------------
def create_user(full_name: str, email: str, password: str, role: str = "General User", institution: str = "MIT-ADT University, Pune"):
    """Register a new user with hashed password."""
    email_clean = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check email duplicate
    cursor.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
    if cursor.fetchone():
        conn.close()
        return None, "An account with this email address already exists."

    user_id = "USR-" + uuid.uuid4().hex[:8].upper()
    p_hash, salt = hash_password(password)

    valid_role = "Pharmacist" if role == "Pharmacist" else "General User"

    cursor.execute("""
        INSERT INTO users (id, full_name, email, password_hash, salt, role, institution, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name.strip(), email_clean, p_hash, salt, valid_role, institution, "Computer Science & Engineering"))

    conn.commit()
    cursor.execute("SELECT id, full_name, email, role, institution, department, phone, created_at FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    conn.close()
    return user, None

def get_user_by_email(email: str):
    """Retrieve full user record by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: str):
    """Retrieve user profile by ID (excluding password credentials)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, role, institution, department, phone, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_profile(user_id: str, full_name: str, phone: str = ""):
    """Update profile fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET full_name = ?, phone = ? WHERE id = ?", (full_name.strip(), phone.strip(), user_id))
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def update_user_password(user_id: str, old_password: str, new_password: str):
    """Update password after confirming previous password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "User not found."

    if not verify_password(old_password, row["salt"], row["password_hash"]):
        conn.close()
        return False, "Current password does not match."

    new_hash, new_salt = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?", (new_hash, new_salt, user_id))
    conn.commit()
    conn.close()
    return True, "Password successfully updated."

# -----------------------------------------------------------------------------
# USER-SCOPED METRICS & VERIFICATION LOGS
# -----------------------------------------------------------------------------
def get_user_stats(user_id: str) -> dict:
    """
    Returns strictly genuine database verification statistics for the specified user.
    For a new user account with no scans, all values return exactly 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM verification_logs WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS verified FROM verification_logs WHERE user_id = ? AND status = 'VERIFIED'", (user_id,))
    verified = cursor.fetchone()["verified"]

    cursor.execute("SELECT COUNT(*) AS mismatches FROM verification_logs WHERE user_id = ? AND status = 'SUSPICIOUS'", (user_id,))
    mismatches = cursor.fetchone()["mismatches"]

    cursor.execute("SELECT COUNT(*) AS unable FROM verification_logs WHERE user_id = ? AND status = 'UNABLE TO VERIFY'", (user_id,))
    unable = cursor.fetchone()["unable"]

    conn.close()
    return {
        "totalAttempts": total,
        "verifiedAgainstRecords": verified,
        "informationMismatches": mismatches,
        "unableToVerify": unable
    }

def get_user_history(user_id: str, limit: int = 50) -> list:
    """Retrieve personal verification history for user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM verification_logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def insert_verification_log(user_id: str, data: dict) -> str:
    """Records a single verification attempt bound to the active user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    log_id = "SCAN-" + uuid.uuid4().hex[:8].upper()

    anomalies_json = json.dumps(data.get("anomalies", []))

    cursor.execute("""
        INSERT INTO verification_logs (
            id, user_id, medicine_name, batch_number, manufacturer,
            user_price, mrp, status, safety_score, risk_level,
            anomalies_json, mfg_date, exp_date, check_type, headline, summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_id,
        user_id,
        data.get("medicine_name", "Unknown"),
        data.get("batch_number", "UNKNOWN"),
        data.get("manufacturer", "Unknown"),
        data.get("user_price"),
        data.get("mrp"),
        data.get("status", "UNABLE TO VERIFY"),
        int(data.get("safety_score", 0)),
        data.get("risk_level", "Medium"),
        anomalies_json,
        data.get("mfg_date", ""),
        data.get("exp_date", ""),
        data.get("check_type", "IMAGE_ANALYSIS"),
        data.get("headline", ""),
        data.get("summary", "")
    ))
    conn.commit()
    conn.close()
    return log_id

if __name__ == "__main__":
    init_database()
    print("[Database] Schema verified and initialized successfully.")
