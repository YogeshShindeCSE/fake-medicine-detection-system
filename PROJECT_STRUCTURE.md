# MediVerify – Project Folder Structure & Architecture

**Project Name:** MediVerify – Smart Fake Medicine Detection System  
**Academic Level:** Second Year B.Tech Computer Science & Engineering  
**Technology Stack:** React.js 18, Tailwind CSS, JavaScript ES6+, Python 3, SQLite3, HTML5, CSS3  

---

## 1. Directory Tree Overview

```
mediverify-app/
│
├── index.html                  # Main SPA entry point (React mount, Tailwind CDN, Fonts)
├── server.py                   # Python standard library HTTP/REST server (Port 5000)
├── database.py                 # SQLite database initializer & query helper
├── schema.sql                  # Relational database DDL definitions & table constraints
│
├── README.md                   # Comprehensive project documentation & viva presentation guide
├── PROJECT_STRUCTURE.md        # Detailed directory & module architectural specifications
├── DATABASE_SCHEMA.md          # ER diagram, table dictionaries, data types & indexes
├── INSTALLATION.md             # One-click execution & full-stack server setup guide
├── FUTURE_SCOPE.md             # Research roadmap (Blockchain, AI OCR, Raman IoT)
│
├── assets/
│   ├── css/
│   │   └── style.css           # Custom styles, scanner laser animation, print certificate stylesheet
│   │
│   └── js/
│       ├── data/
│       │   └── sampleMedicines.js   # 16 realistic pharmaceutical datasets & viva demo presets
│       │
│       ├── utils/
│       │   ├── verificationEngine.js # Core verification algorithm, price anomaly formulas & risk scoring
│       │   └── storage.js            # LocalStorage & SQLite REST API synchronization layer
│       │
│       └── app.js              # Complete React application & all user interface views
│
└── mediverify.db               # SQLite database file (automatically created on initialization)
```

---

## 2. Architectural Data Flow Diagram

```
+-----------------------------------------------------------------------------------+
|                                 USER INTERFACE                                    |
|   (React 18 SPA + Tailwind CSS + Lucide Icons + White, Navy & Light Green Theme)  |
+-----------------------------------------------------------------------------------+
         |                                                 |
         | [1] Upload Image / Enter Batch / Scan QR        | [5] View History / Dashboard
         v                                                 v
+----------------------------------+             +----------------------------------+
|      MEDICINE SCANNER MODULE     |             |       ANALYTICS & DASHBOARD      |
|   - Image Preview & Drag-Drop    |             |   - Scans & Safety Distribution  |
|   - OCR Optical Text Simulation  |             |   - Filterable Audit History     |
|   - QR Viewfinder Laser Cam      |             |   - CSV Audit Log Export         |
+----------------------------------+             +----------------------------------+
         |
         | [2] Raw Form Parameters
         v
+-----------------------------------------------------------------------------------+
|                        CORE VERIFICATION ENGINE (Client & API)                    |
|   - Batch Registry Exact Match: (Matched / Unrecognized / Recalled)              |
|   - Manufacturer License Authorization Check                                      |
|   - Shelf Life & Expiration Analysis (Lapsed Date vs Today)                       |
|   - Price Sanity Engine: ((Price - MRP) / MRP) * 100                             |
|       * Undercutting > 30% -> Suspicious Counterfeit Flag                         |
|       * Price > MRP -> DPCO Statutory Violation Flag                              |
|   - Safety Score Metric Calculation (0 - 100%)                                    |
+-----------------------------------------------------------------------------------+
         |                                                 |
         | [3] Lookup / Sync                               | [4] Verdict Output
         v                                                 v
+----------------------------------+             +----------------------------------+
|       PERSISTENCE LAYER          |             |       VERIFICATION RESULT        |
|   - LocalStorage (Offline Cache) |             |   - VERIFIED (Green)             |
|   - SQLite3 Database (REST API)  |             |   - SUSPICIOUS (Red/Amber)       |
|   - 16 Indexed Sample Medicines  |             |   - UNABLE TO VERIFY (Gray)      |
|   - Admin CRUD & Recall Toggles  |             |   - Printable Audit Certificate  |
+----------------------------------+             +----------------------------------+
```

---

## 3. Detailed Module Breakdown

### Module 1: Home Page (`HomeView`)
* **Hero Section:** High-impact healthcare presentation featuring dynamic badge ticker, animated ping badges, and immediate CTA buttons.
* **Public Health Context:** WHO statistics detailing the global counterfeit drug crisis, highlighting inactive chalk fillers and toxic substitutes.
* **How It Works (4-Phase Pipeline):** Interactive step cards illustrating Data Capture -> Registry Lookup -> Anomaly Detection -> Safety Verdict.
* **Core Capabilities Grid:** 6 high-level feature cards demonstrating batch tracking, price sanity, and printable certificates.

### Module 2: Medicine Scanner (`ScannerView`)
* **Dual Operation Modes:** Switch between manual/image upload and camera QR/barcode viewfinder.
* **Image Upload Zone:** Drag-and-drop container with mock OCR text extraction progress bar and auto-populating detected tags.
* **Smart Input Fields:** Form validation, medicine name autocomplete suggestions, and quick chips.
* **QR Viewfinder:** Laser scanning animation with 4 built-in rapid test presets for live viva demonstrations.

### Module 3 & 4: Medicine Verification & Certificate (`VerificationResultModal`)
* **3-Tier Verdict Output:** `VERIFIED`, `SUSPICIOUS`, or `UNABLE TO VERIFY`.
* **Safety Gauge:** Visual 0–100% integrity score bar.
* **Anomaly Checklist:** Pass/Fail badges on batch number, license match, expiration date, and price variance.
* **Printable Certificate:** Formats into an official laboratory-style audit report on browser print.
* **Prominent Disclaimer:** Clearly states that digital/optical validation does not substitute chemical laboratory assays.

### Module 5: Price Checker (`PriceCheckerView`)
* **Price Anomaly Detection:** Compares purchased price with Government NPPA Maximum Retail Price (MRP).
* **Undercutting Detection:** Flags discounts > 30% as high-risk counterfeit or adulterated stock.
* **DPCO Enforcement:** Flags illegal overcharging when price exceeds statutory MRP.

### Module 6: User Dashboard (`DashboardView`)
* **Metrics Cards:** Total scanned, verified genuine, suspicious alerts, unable to verify.
* **History Table:** Filterable by status (`ALL`, `VERIFIED`, `SUSPICIOUS`, `UNABLE TO VERIFY`), search bar, and CSV export.

### Module 7: Admin Panel (`AdminView`)
* **Passcode Gate:** Protected by examiner PIN (`1234`).
* **CRUD Operations:** Create new medicines, edit formulations, delete records.
* **Instant Batch Recall Simulation:** One-click toggle that marks a batch recalled, instantly converting scan results into `SUSPICIOUS`.
* **Seed Data Reset:** One-click restoration of default 16 medications.

### Module 8: Public Health Awareness & Incident Reporting
* **Counterfeit Guide (`CounterfeitGuideView`):** Educational visual guide on holograms, typography errors, and packaging symmetry.
* **Incident Report Portal (`ContactView`):** Citizen reporting form that logs suspicious pharmacies and generates unique incident tracking IDs.
