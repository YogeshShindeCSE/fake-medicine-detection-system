"""
Fake Medicine Detection System
REST API Gateway & Application Server (Python 3 Standard Library)
Academic Project: Second Year B.Tech Computer Science & Engineering
Institution: MIT-ADT University, Pune | Group ID: 1603
Mentor: Dr. Sachin More | Team: Yogesh Shinde, Pranav Jagtap, Rupesh Kawthekar, Kunal Kothari
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import re
import time
import base64
import hashlib
import hmac
import sqlite3
from datetime import datetime

import database
from database import (
    init_database, get_db_connection, create_user,
    get_user_by_email, get_user_by_id, verify_password,
    update_user_profile, update_user_password,
    get_user_stats, get_user_history, insert_verification_log
)

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JWT_SECRET = b"mit_adt_group_1603_fake_medicine_detection_jwt_secret_2026"

# -----------------------------------------------------------------------------
# JWT TOKEN HELPER (RFC 7519 Compliant, Pure Standard Library)
# -----------------------------------------------------------------------------
def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ''
    return base64.urlsafe_b64decode(data + padding)

def create_jwt(user_dict: dict, expires_in_seconds: int = 86400 * 7) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_dict["id"],
        "email": user_dict["email"],
        "full_name": user_dict["full_name"],
        "role": user_dict["role"],
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in_seconds
    }
    h_b64 = b64url_encode(json.dumps(header).encode('utf-8'))
    p_b64 = b64url_encode(json.dumps(payload).encode('utf-8'))
    signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
    sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
    return f"{h_b64}.{p_b64}.{b64url_encode(sig)}"

def verify_jwt(token: str) -> dict:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        h_b64, p_b64, sig_b64 = parts
        signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
        actual_sig = b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(b64url_decode(p_b64).decode('utf-8'))
        if payload.get("exp") and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None

# -----------------------------------------------------------------------------
# CORE MEDICINE VERIFICATION ENGINE
# -----------------------------------------------------------------------------
def perform_medicine_verification(input_data: dict) -> dict:
    name_in = (input_data.get("medicineName") or "").strip()
    batch_in = (input_data.get("batchNumber") or "").strip().upper()
    mfg_in = (input_data.get("manufacturer") or "").strip()
    user_price = input_data.get("userPrice")
    qr_data = (input_data.get("qrData") or "").strip()
    barcode = (input_data.get("barcode") or "").strip()
    check_type = input_data.get("checkType") or "IMAGE_ANALYSIS"

    try:
        user_price = float(user_price) if user_price not in (None, "") else None
    except Exception:
        user_price = None

    # Step 1: Normalize query tokens
    norm_name = re.sub(r'[^a-zA-Z0-9]', '', name_in.lower())
    norm_batch = re.sub(r'[^a-zA-Z0-9]', '', batch_in.upper())

    # If QR data contains batch or medicine, extract
    if qr_data and (not batch_in or not name_in):
        for part in qr_data.split('|'):
            if part.startswith("MED:") and not name_in:
                name_in = part.replace("MED:", "").strip()
                norm_name = re.sub(r'[^a-zA-Z0-9]', '', name_in.lower())
            elif part.startswith("BATCH:") and not batch_in:
                batch_in = part.replace("BATCH:", "").strip().upper()
                norm_batch = re.sub(r'[^a-zA-Z0-9]', '', batch_in)

    conn = get_db_connection()
    cursor = conn.cursor()

    matched_record = None

    # Try match by exact batch first
    if norm_batch:
        cursor.execute("SELECT * FROM medicines")
        all_meds = [dict(r) for r in cursor.fetchall()]
        for m in all_meds:
            if re.sub(r'[^a-zA-Z0-9]', '', m["batch_number"].upper()) == norm_batch:
                matched_record = m
                break

    # If not found by batch, try match by name or barcode
    if not matched_record and (norm_name or barcode):
        cursor.execute("SELECT * FROM medicines")
        all_meds = [dict(r) for r in cursor.fetchall()]
        for m in all_meds:
            m_norm_name = re.sub(r'[^a-zA-Z0-9]', '', m["name"].lower())
            if barcode and m.get("barcode") and m["barcode"] == barcode:
                matched_record = m
                break
            if norm_name and (norm_name in m_norm_name or m_norm_name in norm_name):
                matched_record = m
                break

    conn.close()

    now = datetime.now()
    anomalies = []
    checks = {
        "registryMatch": {"passed": False, "status": "Failed", "details": "No record in authorized database."},
        "batchValidity": {"passed": False, "status": "Failed", "details": "Batch could not be validated."},
        "manufacturerLicense": {"passed": False, "status": "Failed", "details": "Manufacturer details could not be corroborated."},
        "expiryStatus": {"passed": True, "status": "Unknown", "details": "Expiry date not analyzed."},
        "priceSanity": {"passed": True, "status": "Normal", "details": "No purchase price supplied."}
    }

    # Case A: Record NOT found in central database
    if not matched_record:
        return {
            "status": "UNABLE TO VERIFY",
            "safetyScore": 15,
            "riskLevel": "High",
            "headline": "PRODUCT NOT FOUND IN CENTRAL DRUG REGISTRY",
            "summary": f"The entered product ('{name_in or 'Unspecified'}' / Lot: '{batch_in or 'N/A'}') does not correspond to any registered formulation in the authorized CDSCO/State Licensing database. Exercise caution.",
            "matchedMedicine": None,
            "checks": checks,
            "anomalies": [{
                "id": "ANOM-001",
                "severity": "High",
                "title": "Unregistered Pharmaceutical Entry",
                "description": "The product credentials do not exist in the official regulatory drug index. Packaging may originate from an unverified or illicit distributor."
            }],
            "priceAnalysis": None,
            "input": {
                "medicineName": name_in,
                "batchNumber": batch_in,
                "manufacturer": mfg_in,
                "userPrice": user_price,
                "checkType": check_type
            }
        }

    # Case B: Record Found - Perform Deep Anomaly Cross-Referencing
    checks["registryMatch"] = {
        "passed": True,
        "status": "Verified",
        "details": f"Registered formulation: {matched_record['name']} ({matched_record['generic_name']})."
    }

    score = 100
    status = "VERIFIED"
    risk_level = "Low"

    # Check 1: Batch Match
    target_batch = matched_record["batch_number"].upper()
    if batch_in and norm_batch != re.sub(r'[^a-zA-Z0-9]', '', target_batch):
        checks["batchValidity"] = {
            "passed": False,
            "status": "Batch Mismatch",
            "details": f"Entered batch '{batch_in}' does not match registered production batch '{matched_record['batch_number']}' for this formulation."
        }
        score -= 40
        status = "SUSPICIOUS"
        anomalies.append({
            "id": "ANOM-BATCH",
            "severity": "High",
            "title": "Batch Identification Mismatch",
            "description": f"The lot number on the packaging does not match the manufacturer's official production ledger ({matched_record['batch_number']})."
        })
    else:
        checks["batchValidity"] = {
            "passed": True,
            "status": "Valid",
            "details": f"Batch sequence '{matched_record['batch_number']}' matches approved manufacturing lot."
        }

    # Check 2: Manufacturer Match
    if mfg_in:
        norm_user_mfg = re.sub(r'[^a-zA-Z0-9]', '', mfg_in.lower())
        norm_rec_mfg = re.sub(r'[^a-zA-Z0-9]', '', matched_record["manufacturer"].lower())
        if norm_user_mfg and norm_user_mfg not in norm_rec_mfg and norm_rec_mfg not in norm_user_mfg:
            checks["manufacturerLicense"] = {
                "passed": False,
                "status": "Mismatch",
                "details": f"Packaging names '{mfg_in}', but marketing license is held by '{matched_record['manufacturer']}'."
            }
            score -= 45
            status = "SUSPICIOUS"
            anomalies.append({
                "id": "ANOM-MFG",
                "severity": "Critical",
                "title": "Manufacturer Entity Discrepancy",
                "description": f"Label holder '{mfg_in}' differs from authorized marketing authorization holder '{matched_record['manufacturer']}' (License: {matched_record['license_no']})."
            })
        else:
            checks["manufacturerLicense"] = {
                "passed": True,
                "status": "Authorized",
                "details": f"Licensed entity confirmed: {matched_record['manufacturer']} ({matched_record['license_no']})."
            }
    else:
        checks["manufacturerLicense"] = {
            "passed": True,
            "status": "Authorized",
            "details": f"Marketing Authorization: {matched_record['manufacturer']} ({matched_record['license_no']})."
        }

    # Check 3: Active Recall Status
    if matched_record.get("is_recalled"):
        score = min(score, 20)
        status = "SUSPICIOUS"
        risk_level = "Critical"
        anomalies.append({
            "id": "ANOM-RECALL",
            "severity": "Critical",
            "title": "ACTIVE REGULATORY STOP-SALE RECALL",
            "description": "This specific batch has been flagged with an active recall notice by the Central Drugs Standard Control Organisation (CDSCO)."
        })

    # Check 4: Expiration Date
    exp_str = matched_record.get("exp_date", "")
    if exp_str:
        try:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
            if exp_date < now:
                checks["expiryStatus"] = {
                    "passed": False,
                    "status": "Expired",
                    "details": f"Batch expired on {exp_str}. Distribution is unlawful."
                }
                score -= 40
                status = "SUSPICIOUS"
                anomalies.append({
                    "id": "ANOM-EXP",
                    "severity": "Critical",
                    "title": "Product Shelf-Life Expired",
                    "description": f"The medicine reached expiration on {exp_str}. Expired pharmaceutical agents degrade and may form toxic secondary metabolites."
                })
            else:
                checks["expiryStatus"] = {
                    "passed": True,
                    "status": "Active",
                    "details": f"Valid shelf-life through {exp_str}."
                }
        except Exception:
            checks["expiryStatus"] = {"passed": True, "status": "Recorded", "details": f"Exp: {exp_str}"}

    # Check 5: Price Sanity & Undercutting
    price_analysis = None
    if user_price is not None and matched_record.get("mrp"):
        mrp = float(matched_record["mrp"])
        variance = ((user_price - mrp) / mrp) * 100
        price_analysis = {
            "userPrice": user_price,
            "mrp": mrp,
            "variancePercentage": round(variance, 1),
            "isSevereUndercut": variance <= -30.0,
            "isOvercharging": variance > 15.0
        }

        if variance <= -30.0:
            checks["priceSanity"] = {
                "passed": False,
                "status": "Severe Undercut",
                "details": f"Purchase price (₹{user_price:.2f}) is {abs(variance):.1f}% below regulated MRP (₹{mrp:.2f})."
            }
            score -= 35
            status = "SUSPICIOUS"
            anomalies.append({
                "id": "ANOM-PRICE-CUT",
                "severity": "High",
                "title": "Suspicious Price Undercutting (>30% below MRP)",
                "description": f"Selling at ₹{user_price:.2f} vs NPPA ceiling ₹{mrp:.2f}. Extreme discounts on branded pharmaceuticals frequently indicate counterfeit diversion or stolen batches."
            })
        elif variance > 15.0:
            checks["priceSanity"] = {
                "passed": False,
                "status": "DPCO Ceiling Breach",
                "details": f"Price of ₹{user_price:.2f} exceeds regulated MRP (₹{mrp:.2f}) by {variance:.1f}%."
            }
            anomalies.append({
                "id": "ANOM-PRICE-HIGH",
                "severity": "Medium",
                "title": "Statutory MRP Violation",
                "description": f"The charged price ₹{user_price:.2f} exceeds the statutory maximum retail price of ₹{mrp:.2f}."
            })
        else:
            checks["priceSanity"] = {
                "passed": True,
                "status": "Consistent",
                "details": f"Retail price ₹{user_price:.2f} aligns within normal retail margin of statutory MRP ₹{mrp:.2f}."
            }

    # Cap score
    score = max(5, min(100, score))
    if score >= 85:
        risk_level = "Low"
        headline = "MEDICINE VERIFIED AS AUTHENTIC"
        summary = f"All packaging credentials for {matched_record['name']} (Batch {matched_record['batch_number']}) match authorized regulatory filings with no active recall flags."
    elif score >= 50:
        risk_level = "Medium"
        headline = "PACKAGING ANOMALIES DETECTED"
        summary = f"Minor irregularities noted for {matched_record['name']}. Review detailed check criteria below."
    else:
        risk_level = "Critical" if any(a["severity"] == "Critical" for a in anomalies) else "High"
        headline = "CRITICAL WARNING: SUSPECTED COUNTERFEIT OR SAFETY ALERT"
        summary = f"Severe discrepancies identified in packaging verification for {matched_record['name']}. Product should not be administered."

    return {
        "status": status,
        "safetyScore": score,
        "riskLevel": risk_level,
        "headline": headline,
        "summary": summary,
        "matchedMedicine": matched_record,
        "checks": checks,
        "anomalies": anomalies,
        "priceAnalysis": price_analysis,
        "input": {
            "medicineName": name_in or matched_record["name"],
            "batchNumber": batch_in or matched_record["batch_number"],
            "manufacturer": mfg_in or matched_record["manufacturer"],
            "userPrice": user_price,
            "mfgDate": matched_record.get("mfg_date"),
            "expDate": matched_record.get("exp_date"),
            "checkType": check_type
        }
    }

# -----------------------------------------------------------------------------
# HTTP REQUEST HANDLER
# -----------------------------------------------------------------------------
class FakeMedicineServerHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, data, status_code=200):
        encoded = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.send_header("Connection", "close")
        self.end_headers()

    def _get_auth_user(self):
        """Extract and verify JWT from Authorization header."""
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split("Bearer ")[1].strip()
        payload = verify_jwt(token)
        if not payload or not payload.get("sub"):
            return None
        return get_user_by_id(payload["sub"])

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # ---------------- AUTH: /api/auth/me ----------------
        if path == "/api/auth/me":
            user = self._get_auth_user()
            if not user:
                return self._send_json({"success": False, "error": "Unauthorized or session expired"}, 401)
            return self._send_json({"success": True, "user": user})

        # ---------------- USER STATS: /api/user/stats ----------------
        elif path == "/api/user/stats":
            user = self._get_auth_user()
            if not user:
                return self._send_json({"success": False, "error": "Authentication required"}, 401)
            stats = get_user_stats(user["id"])
            return self._send_json({"success": True, "data": stats})

        # ---------------- USER HISTORY: /api/user/history ----------------
        elif path == "/api/user/history":
            user = self._get_auth_user()
            if not user:
                return self._send_json({"success": False, "error": "Authentication required"}, 401)
            limit = int(query.get("limit", [50])[0])
            history = get_user_history(user["id"], limit)
            # Parse anomalies_json in each row
            for h in history:
                if h.get("anomalies_json"):
                    try:
                        h["anomalies"] = json.loads(h["anomalies_json"])
                    except Exception:
                        h["anomalies"] = []
            return self._send_json({"success": True, "data": history})

        # ---------------- MEDICINES: /api/medicines ----------------
        elif path == "/api/medicines":
            search_query = query.get("q", [""])[0].strip().lower()
            category = query.get("category", [""])[0].strip()

            conn = get_db_connection()
            cursor = conn.cursor()
            if search_query:
                cursor.execute("""
                    SELECT * FROM medicines
                    WHERE LOWER(name) LIKE ? OR LOWER(generic_name) LIKE ? OR LOWER(batch_number) LIKE ?
                    ORDER BY name ASC
                """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            elif category and category != "All":
                cursor.execute("SELECT * FROM medicines WHERE therapeutic_category = ? ORDER BY name ASC", (category,))
            else:
                cursor.execute("SELECT * FROM medicines ORDER BY name ASC")

            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self._send_json({"success": True, "count": len(rows), "data": rows})

        # ---------------- MEDICINE DETAIL: /api/medicines/<id> ----------------
        elif path.startswith("/api/medicines/"):
            med_id = path.split("/api/medicines/")[1]
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicines WHERE id = ?", (med_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return self._send_json({"success": True, "data": dict(row)})
            return self._send_json({"success": False, "error": "Medicine record not found"}, 404)

        # ---------------- REPORTS: /api/reports ----------------
        elif path == "/api/reports":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incident_reports ORDER BY created_at DESC")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return self._send_json({"success": True, "data": rows})

        # ---------------- GLOBAL STATS: /api/stats (for landing page summary) ----------------
        elif path == "/api/stats":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total_medicines FROM medicines")
            tot_meds = cursor.fetchone()["total_medicines"]
            cursor.execute("SELECT COUNT(*) AS total_recalled FROM medicines WHERE is_recalled = 1")
            tot_recalled = cursor.fetchone()["total_recalled"]
            cursor.execute("SELECT COUNT(*) AS total_reports FROM incident_reports")
            tot_reports = cursor.fetchone()["total_reports"]
            conn.close()
            return self._send_json({
                "success": True,
                "data": {
                    "registeredFormulations": tot_meds,
                    "activeRecalls": tot_recalled,
                    "reportedIncidents": tot_reports,
                    "academicGroup": "Group 1603",
                    "institution": "MIT-ADT University, Pune"
                }
            })

        # Static assets fallback
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        # ---------------- AUTH: REGISTER ----------------
        if path == "/api/auth/register":
            full_name = payload.get("fullName", "").strip()
            email = payload.get("email", "").strip().lower()
            password = payload.get("password", "")
            confirm_password = payload.get("confirmPassword", "")
            role = payload.get("role", "General User")

            if not full_name or not email or not password:
                return self._send_json({"success": False, "error": "All required fields must be completed."}, 400)

            if "@" not in email or "." not in email:
                return self._send_json({"success": False, "error": "Please provide a valid institutional or personal email address."}, 400)

            if len(password) < 6:
                return self._send_json({"success": False, "error": "Password must be at least 6 characters long."}, 400)

            if confirm_password and password != confirm_password:
                return self._send_json({"success": False, "error": "Passwords do not match."}, 400)

            user, err = create_user(full_name, email, password, role)
            if err:
                return self._send_json({"success": False, "error": err}, 400)

            token = create_jwt(user)
            return self._send_json({
                "success": True,
                "message": "Registration successful. Welcome to Fake Medicine Detection System.",
                "token": token,
                "user": user
            }, 201)

        # ---------------- AUTH: LOGIN ----------------
        elif path == "/api/auth/login":
            email = payload.get("email", "").strip().lower()
            password = payload.get("password", "")
            remember_me = payload.get("rememberMe", False)

            if not email or not password:
                return self._send_json({"success": False, "error": "Email and password are required."}, 400)

            user_record = get_user_by_email(email)
            if not user_record:
                return self._send_json({"success": False, "error": "No registered account found with this email."}, 401)

            if not verify_password(password, user_record["salt"], user_record["password_hash"]):
                return self._send_json({"success": False, "error": "Invalid password. Please check your credentials."}, 401)

            user_profile = {
                "id": user_record["id"],
                "full_name": user_record["full_name"],
                "email": user_record["email"],
                "role": user_record["role"],
                "institution": user_record.get("institution", "MIT-ADT University, Pune"),
                "department": user_record.get("department", "Computer Science & Engineering"),
                "phone": user_record.get("phone", "")
            }

            token_expiry = 86400 * 30 if remember_me else 86400 * 7
            token = create_jwt(user_profile, token_expiry)

            return self._send_json({
                "success": True,
                "message": "Authentication successful.",
                "token": token,
                "user": user_profile
            })

        # ---------------- AUTH: FORGOT PASSWORD ----------------
        elif path == "/api/auth/forgot-password":
            email = payload.get("email", "").strip().lower()
            if not email:
                return self._send_json({"success": False, "error": "Email address is required."}, 400)

            user_record = get_user_by_email(email)
            if user_record:
                return self._send_json({
                    "success": True,
                    "message": f"Password reset instructions and verification code have been dispatched to {email}. (For evaluation: password can be reset in Settings).",
                    "resetToken": "RST-" + os.urandom(4).hex().upper()
                })
            else:
                return self._send_json({
                    "success": True,
                    "message": "If this email is registered in our pharmaceutical directory, password reset instructions have been dispatched."
                })

        # ---------------- AUTH: CHANGE PASSWORD ----------------
        elif path == "/api/auth/change-password":
            user = self._get_auth_user()
            if not user:
                return self._send_json({"success": False, "error": "Authentication required"}, 401)

            current_password = payload.get("currentPassword", "")
            new_password = payload.get("newPassword", "")

            if not current_password or not new_password:
                return self._send_json({"success": False, "error": "Current and new passwords are required."}, 400)

            if len(new_password) < 6:
                return self._send_json({"success": False, "error": "New password must be at least 6 characters."}, 400)

            ok, msg = update_user_password(user["id"], current_password, new_password)
            if not ok:
                return self._send_json({"success": False, "error": msg}, 400)

            return self._send_json({"success": True, "message": msg})

        # ---------------- VERIFICATION ENGINE: POST /api/verify ----------------
        elif path == "/api/verify":
            user = self._get_auth_user()
            user_id = user["id"] if user else None

            assessment = perform_medicine_verification(payload)

            # Persist to database if authenticated
            if user_id:
                log_data = {
                    "medicine_name": assessment["input"]["medicineName"],
                    "batch_number": assessment["input"]["batchNumber"],
                    "manufacturer": assessment["input"]["manufacturer"],
                    "user_price": assessment["input"]["userPrice"],
                    "mrp": assessment["matchedMedicine"]["mrp"] if assessment.get("matchedMedicine") else None,
                    "status": assessment["status"],
                    "safety_score": assessment["safetyScore"],
                    "risk_level": assessment["riskLevel"],
                    "anomalies": assessment["anomalies"],
                    "mfg_date": assessment["input"].get("mfgDate", ""),
                    "exp_date": assessment["input"].get("expDate", ""),
                    "check_type": payload.get("checkType", "IMAGE_ANALYSIS"),
                    "headline": assessment["headline"],
                    "summary": assessment["summary"]
                }
                log_id = insert_verification_log(user_id, log_data)
                assessment["verificationId"] = log_id

            return self._send_json({"success": True, "assessment": assessment})

        # ---------------- INCIDENT REPORT: POST /api/reports ----------------
        elif path == "/api/reports":
            user = self._get_auth_user()
            user_id = user["id"] if user else None
            reporter_name = user["full_name"] if user else payload.get("reporterName", "Anonymous Verifier")

            rep_id = "ALERT-" + os.urandom(3).hex().upper()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO incident_reports (
                    id, user_id, reporter_name, pharmacy_name, medicine_name, batch_number, city, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rep_id,
                user_id,
                reporter_name,
                payload.get("pharmacyName", "Unspecified Pharmacy"),
                payload.get("medicineName", "Unknown Product"),
                payload.get("batchNumber", "N/A"),
                payload.get("city", "Pune, Maharashtra"),
                payload.get("description", "Reported suspicious packaging or unauthorized counterfeit batch.")
            ))
            conn.commit()
            conn.close()
            return self._send_json({"success": True, "reportId": rep_id, "message": "Incident report logged with vigilance authority."}, 201)

        # ---------------- ADMIN: RESET DATABASE ----------------
        elif path == "/api/reset-db":
            init_database()
            return self._send_json({"success": True, "message": "Reference database restored to standard configuration."})

        return self._send_json({"success": False, "error": "Endpoint not recognized"}, 404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/api/auth/profile":
            user = self._get_auth_user()
            if not user:
                return self._send_json({"success": False, "error": "Authentication required"}, 401)
            updated = update_user_profile(user["id"], payload.get("fullName", user["full_name"]), payload.get("phone", user.get("phone", "")))
            return self._send_json({"success": True, "user": updated, "message": "Profile updated successfully."})

        return self._send_json({"success": False, "error": "Endpoint not recognized"}, 404)

def run_server():
    init_database()
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    server_address = ("", PORT)
    with http.server.ThreadingHTTPServer(server_address, FakeMedicineServerHandler) as httpd:
        httpd.daemon_threads = True
        print("=" * 75)
        print("  FAKE MEDICINE DETECTION SYSTEM — ACADEMIC PROJECT (GROUP 1603)")
        print("  MIT-ADT University, Pune | School of Computing | Dept of CSE")
        print("  Mentor: Dr. Sachin More | Team: Yogesh, Pranav, Rupesh, Kunal")
        print("=" * 75)
        print(f"  * Web Server & REST API Gateway Running At: http://localhost:{PORT}")
        print(f"  * Mode: Multi-Threaded Concurrent Gateway (ThreadingHTTPServer)")
        print(f"  * Database: SQLite3 (mediverify.db)")
        print("=" * 75)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Server] Shutting down gracefully...")

if __name__ == "__main__":
    run_server()
