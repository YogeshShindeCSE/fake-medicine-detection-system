# MediVerify – Database Schema & Data Dictionary

**System Name:** MediVerify – Smart Fake Medicine Detection System  
**Database Engine:** SQLite3 (Server Backend) + LocalStorage (Offline Client Cache)  
**Academic Level:** Second Year B.Tech Computer Science & Engineering  

---

## 1. Entity-Relationship (ER) Overview

```
+------------------------------------+
|             MEDICINES              |
+------------------------------------+
| PK  id: TEXT                       |
|     name: TEXT                     |
|     generic_name: TEXT             |
|     manufacturer: TEXT             |
|     license_no: TEXT               |
| UK  batch_number: TEXT             |
|     mfg_date: TEXT                 |
|     exp_date: TEXT                 |
|     mrp: REAL                      |
|     dosage_form: TEXT              |
|     strength: TEXT                 |
|     packaging_type: TEXT           |
|     schedule_class: TEXT           |
|     verification_status: TEXT      |
|     status_reason: TEXT            |
|     safety_score: INTEGER          |
|     is_recalled: INTEGER           |
|     barcode: TEXT                  |
|     qr_code_data: TEXT             |
|     therapeutic_category: TEXT     |
|     description: TEXT              |
|     created_at: TIMESTAMP          |
+------------------------------------+
                  |
                  | 1 : N (Audited via batch_number)
                  v
+------------------------------------+       +------------------------------------+
|         VERIFICATION_LOGS          |       |          INCIDENT_REPORTS          |
+------------------------------------+       +------------------------------------+
| PK  id: TEXT                       |       | PK  id: TEXT                       |
|     medicine_name: TEXT            |       |     pharmacy_name: TEXT            |
|     batch_number: TEXT             |       |     medicine_name: TEXT            |
|     manufacturer: TEXT             |       |     batch_number: TEXT             |
|     user_price: REAL               |       |     city: TEXT                     |
|     mrp: REAL                      |       |     description: TEXT              |
|     status: TEXT                   |       |     investigation_status: TEXT     |
|     safety_score: INTEGER          |       |     created_at: TIMESTAMP          |
|     risk_level: TEXT               |       +------------------------------------+
|     anomalies_json: TEXT           |
|     timestamp: TIMESTAMP           |
+------------------------------------+
```

---

## 2. Table Specifications

### Table 1: `medicines`
Main registry of approved pharmaceutical products, authorized batch codes, marketing authorization holders, and pricing limits.

| Field Name | Data Type | Nullable | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `TEXT` | No | None | `PRIMARY KEY` | Unique alphanumeric identifier (e.g., `MED-001`) |
| `name` | `TEXT` | No | None | None | Commercial brand name (e.g., `Crocin 650`) |
| `generic_name` | `TEXT` | No | None | None | Active Pharmaceutical Ingredient (API) & salt formulation |
| `manufacturer` | `TEXT` | No | None | None | Licensed pharmaceutical manufacturing company |
| `license_no` | `TEXT` | No | None | None | State Drug Controller marketing license number |
| `batch_number` | `TEXT` | No | None | `UNIQUE` | Production batch lot number printed on strip packaging |
| `mfg_date` | `TEXT` | No | None | ISO 8601 | Manufacturing date (`YYYY-MM-DD`) |
| `exp_date` | `TEXT` | No | None | ISO 8601 | Product expiration date (`YYYY-MM-DD`) |
| `mrp` | `REAL` | No | None | `CHECK(mrp > 0)` | Regulated Maximum Retail Price in Indian Rupees (₹) |
| `dosage_form` | `TEXT` | Yes | `'Tablet'` | None | Form of administration (Tablet, Capsule, Syrup, Injection) |
| `strength` | `TEXT` | Yes | None | None | Dosage potency per unit (e.g., `650 mg`, `625 mg`) |
| `packaging_type` | `TEXT` | Yes | None | None | Packaging material (Blister Pack, Alu-Alu Strip, Bottle) |
| `schedule_class` | `TEXT` | Yes | None | None | Drugs and Cosmetics Act Schedule (OTC, Schedule H, H1) |
| `verification_status`| `TEXT` | No | `'VERIFIED'`| `IN ('VERIFIED', 'SUSPICIOUS', 'UNABLE TO VERIFY')` | Baseline integrity classification |
| `status_reason` | `TEXT` | Yes | None | None | Regulatory audit commentary and notes |
| `safety_score` | `INTEGER` | Yes | `100` | `0 <= score <= 100` | Baseline computed safety score index |
| `is_recalled` | `INTEGER` | No | `0` | `IN (0, 1)` | Boolean flag indicating DCGI stop-sale/recall order |
| `barcode` | `TEXT` | Yes | None | None | GS1 13-digit EAN/UPC product code |
| `qr_code_data` | `TEXT` | Yes | None | None | Encoded 2D DataMatrix packaging string |
| `therapeutic_category`| `TEXT` | Yes | None | None | Medical treatment class (e.g. Analgesic, Antibiotic) |
| `description` | `TEXT` | Yes | None | None | Clinical usage indications and precautions |
| `created_at` | `TIMESTAMP` | No | `CURRENT_TIMESTAMP` | None | Timestamp of database registration |

---

### Table 2: `verification_logs`
Audit log recording every inspection attempt, input credentials, pricing analysis, and verdict.

| Field Name | Data Type | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `TEXT` | No | None | Primary key identifier (e.g., `VERIF-1718820000000`) |
| `medicine_name` | `TEXT` | Yes | None | Brand name entered by user or detected via OCR |
| `batch_number` | `TEXT` | Yes | None | Batch code inspected |
| `manufacturer` | `TEXT` | Yes | None | Manufacturer name entered or matched |
| `user_price` | `REAL` | Yes | `NULL` | Retail price paid by the user |
| `mrp` | `REAL` | Yes | `NULL` | Statutory MRP from central registry |
| `status` | `TEXT` | No | None | Final determination: `VERIFIED`, `SUSPICIOUS`, `UNABLE TO VERIFY` |
| `safety_score` | `INTEGER` | No | None | Computed safety integrity score (0–100%) |
| `risk_level` | `TEXT` | Yes | None | Risk tier (`Low`, `Medium`, `High`, `Critical`) |
| `anomalies_json` | `TEXT` | Yes | None | Serialized JSON array of flagged packaging defects |
| `timestamp` | `TIMESTAMP`| No | `CURRENT_TIMESTAMP` | Date and time of verification |

---

### Table 3: `incident_reports`
User-submitted counterfeit complaints tracking suspicious pharmacy retailers and fake batches.

| Field Name | Data Type | Nullable | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `TEXT` | No | None | Complaint reference code (e.g., `INC-ALERT-881920`) |
| `pharmacy_name` | `TEXT` | Yes | None | Retail medical store or vendor name |
| `medicine_name` | `TEXT` | No | None | Suspected drug product name |
| `batch_number` | `TEXT` | Yes | None | Packaging lot code under investigation |
| `city` | `TEXT` | No | None | City and state of purchase |
| `description` | `TEXT` | No | None | Detailed physical anomalies observed by consumer |
| `investigation_status`| `TEXT` | No | `'PENDING_INVESTIGATION'` | Case status (`PENDING_INVESTIGATION`, `ESCALATED`, `RESOLVED`) |
| `created_at` | `TIMESTAMP`| No | `CURRENT_TIMESTAMP` | Time of complaint submission |

---

## 3. Database Indexes for High-Speed Query Optimization

```sql
CREATE INDEX idx_medicines_batch ON medicines (batch_number);
CREATE INDEX idx_medicines_name ON medicines (name);
CREATE INDEX idx_medicines_mfg ON medicines (manufacturer);
CREATE INDEX idx_logs_timestamp ON verification_logs (timestamp);
CREATE INDEX idx_logs_status ON verification_logs (status);
CREATE INDEX idx_reports_city ON incident_reports (city);
```

---

## 4. Representative Sample Database Records

| ID | Brand Name | Batch Number | Manufacturer | Expiry Date | MRP (₹) | Status | Key Anomaly Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MED-001` | **Crocin 650** | `GSK-CRC-8821` | GlaxoSmithKline | `2026-06-30` | ₹32.50 | `VERIFIED` | 100% Genuine registered batch. |
| `MED-002` | **Augmentin 625 Duo** | `GSK-AUG-4491` | GlaxoSmithKline | `2025-09-30` | ₹204.50 | `VERIFIED` | Valid antibiotic batch registry. |
| `MED-003` | **Augmentin 625 Duo** | `AUG-FAKE-990` | GSK Biotech Fake Ltd | `2026-02-01` | ₹75.00 | `SUSPICIOUS` | 63% price discount & fake manufacturer. |
| `MED-004` | **Dolo 650** | `ML-DOLO-3120` | Micro Labs Limited | `2026-11-30` | ₹33.00 | `VERIFIED` | Micro-engraved seal valid. |
| `MED-005` | **Azithral 500** | `ALM-AZI-7712` | Alembic Pharma | `2024-06-30` | ₹119.00 | `SUSPICIOUS` | Expired date & active DCGI recall order. |
| `MED-016` | **XyloCure Relief** | `XYLO-999-FAKE` | Himalayan Naturals | `2027-01-01` | ₹499.00 | `UNABLE TO VERIFY` | Unregistered brand missing from CDSCO. |
