# Fake Medicine Detection System

[![Academic Evaluation](https://img.shields.io/badge/Project-MIT--ADT%20University-174EA6.svg)](https://mituniversity.ac.in/)
[![Department](https://img.shields.io/badge/Department-Computer%20Science%20%26%20Engineering-0D9488.svg)](#)
[![Academic Year](https://img.shields.io/badge/Year-Second%20Year%20B.Tech-blue.svg)](#)
[![Group ID](https://img.shields.io/badge/Group-1603-172B4D.svg)](#)
[![Python](https://img.shields.io/badge/Backend-Python%203.14%20Standard%20Library-yellow.svg)](#)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Tailwind%20CSS-10B981.svg)](#)

> An intelligent, full-stack pharmaceutical packaging examination and verification platform designed to detect suspicious, recalled, or counterfeit medicines by cross-referencing package details against authorized regulatory records.

---

## 🏛️ Academic Project Information

- **Institution:** MIT-ADT University, Pune
- **School:** School of Computing
- **Department:** Computer Science & Engineering
- **Academic Year:** Second Year B.Tech
- **Group ID:** 1603
- **Project Mentor:** Dr. Sachin More

### Project Team Members (Group 1603)
| Member Name | Role & Core Responsibilities |
| :--- | :--- |
| **Yogesh Shinde** | Team Lead, Architecture Design & System Integration |
| **Pranav Jagtap** | Backend API Gateway & Multi-Parameter Verification Engine |
| **Rupesh Kawthekar** | Frontend UI/UX, Optical Code Scanner & Image Filters |
| **Kunal Kothari** | Relational Database Schema, Security & Quality Testing |

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement & Objectives](#-problem-statement--objectives)
3. [Key Features & Modules](#-key-features--modules)
4. [Color System & Visual Design](#-color-system--visual-design)
5. [Technology Stack & Architecture](#-technology-stack--architecture)
6. [Security & Authentication](#-security--authentication)
7. [Installation & Execution Guide](#-installation--execution-guide)
8. [Demonstration Test Scenarios](#-demonstration-test-scenarios)
9. [Report Generation & Auditing](#-report-generation--auditing)
10. [Legal & Healthcare Disclaimer](#-legal--healthcare-disclaimer)

---

## 🏥 Project Overview

Counterfeit and substandard medicines represent a severe global health hazard. Falsified pharmaceuticals frequently contain sub-potent active ingredients, inert fillers such as chalk, or toxic chemical substitutes.

The **Fake Medicine Detection System** provides a multi-parameter digital screening platform that validates packaging data against registered CDSCO regulatory specifications, validates shelf-life validity, checks active stop-sale recall registers, and mathematically flags suspicious retail price undercutting.

---

## 🎯 Problem Statement & Objectives

- **Problem:** Consumers and local pharmacies lack accessible digital verification mechanisms to validate physical medicine packaging credentials prior to consumption.
- **Objectives:**
  1. Build an accessible, zero-install web application for medicine verification.
  2. Implement an optical camera viewfinder for decoding GS1 QR codes and 13-digit EAN barcodes.
  3. Provide image preprocessing filters (grayscale, contrast, edge detection) for package inspection.
  4. Cross-reference batch lots, licensed marketing authorization holders, and expiration dates.
  5. Detect price anomalies exceeding standard DPCO maximum retail price limits.
  6. Generate standardized, printable laboratory-style verification audit certificates.

---

## 🚀 Key Features & Modules

### 1. Landing Page & Visual Timeline
- **Hero Section:** Engaging headline *"Verify Medicines. Protect Lives."* with dual call-to-actions.
- **How It Works (6 Phases):** Visual step-by-step pipeline detailing image capture, code decoding, metadata extraction, preprocessing, regulatory comparison, and verdict output.
- **Key Features Grid:** 9 dedicated feature cards showcasing platform capabilities.
- **3-Tier Architecture Preview:** Visual depiction of client, API, and database layers.

### 2. User Authentication & Role Authorization
- **Registration:** Full Name, Email, Password confirmation, and Role assignment (`General User` or `Pharmacist`).
- **Login:** Password visibility toggle, *Remember Me* persistent sessions, and password recovery.
- **Security:** Salted `PBKDF2-HMAC-SHA256` hashing (100,000 rounds) and RFC 7519 HMAC-SHA256 JWT tokens.
- **Protected Routes:** Strict authentication gate on personal verifier dashboard pages.

### 3. User Dashboard
- **Telemetry Cards:** Total Scans, Verified Against Records, Information Mismatches, Unable to Verify.
- **Strict Genuine Counts:** For newly created user accounts, all metrics strictly start at **0**.
- **Recent Activity Table:** Filterable, user-scoped verification audit trail with one-click report inspection.

### 4. Verification Engine & Optical Code Scanner
- **Dual Verification Modes:** Packaging photo upload with OCR simulation OR live camera QR/barcode scanner.
- **Image Filters:** Real-time preview with Normal, Grayscale, High-Contrast, and Edge-Detection modes.
- **Optical Scanner:** Interactive camera viewfinder with animated teal laser line and 1-click test benchmarks.
- **Verification Classifications:**
  - `VERIFIED` (Green / Safety Score 85–100): Authentic batch match, licensed holder, active shelf-life.
  - `SUSPICIOUS` (Red / Safety Score 0–49): Counterfeit flags, recalled lot, manufacturer mismatch, or price undercutting > 30%.
  - `UNABLE TO VERIFY` (Amber / Safety Score 10–25): Product or lot missing from central regulatory database.

---

## 🎨 Color System & Visual Design

The platform adheres to an enterprise healthcare design palette:

| Element | Color | Hex Code |
| :--- | :--- | :--- |
| **Primary Brand** | Deep Medical Blue | `#174EA6` |
| **Secondary Accent** | Teal | `#0D9488` |
| **Canvas Background** | Soft Blue-White | `#F4F8FC` |
| **Container Cards** | Pure White | `#FFFFFF` |
| **Primary Typography** | Dark Navy | `#172B4D` |
| **Secondary Typography** | Slate Grey | `#64748B` |
| **Verified Status** | Green | `#16A34A` |
| **Warning Status** | Amber | `#D97706` |
| **Danger Status** | Red | `#DC2626` |
| **Clean Borders** | Light Blue Grey | `#DCE5EF` |

---

## 💻 Technology Stack & Architecture

- **Frontend:** React 18, Tailwind CSS, Google Fonts (*Plus Jakarta Sans* & *JetBrains Mono*), Responsive Grid.
- **Backend Server:** Python 3 Standard Library `http.server.ThreadingHTTPServer` (Multi-Threaded Concurrent Gateway, Port 5000). Zero external pip dependencies required.
- **Database:** SQLite3 relational engine (`mediverify.db`) with foreign-key constraints and B-tree indexes.
- **Security:** Salted PBKDF2-HMAC-SHA256, RFC 7519 JWT, Bearer token authorization headers.

```
mediverify-app/
├── assets/
│   ├── css/
│   │   └── style.css            # Custom animations, laser scanner, print styles
│   └── js/
│       ├── app.js               # React 18 frontend application
│       ├── data/
│       │   └── sampleMedicines.js # 16 CDSCO reference drug formulations
│       └── utils/
│           ├── storage.js       # JWT session & API synchronization layer
│           └── verificationEngine.js # Client-side assessment engine
├── database.py                  # SQLite3 database engine & PBKDF2 cryptography
├── index.html                   # HTML5 entry point & Tailwind configuration
├── schema.sql                   # Relational database table definitions
├── server.py                    # Multi-threaded REST API Gateway (Port 5000)
├── .env.example                 # Example configuration template
├── .gitignore                   # Comprehensive git exclusion rules
├── CONTRIBUTING.md              # Academic contribution workflow
├── LICENSE.md                   # Evaluation & educational license
└── README.md                    # Project documentation
```

---

## ⚡ Installation & Execution Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- *No Node.js, npm, or external pip package installations required.*

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/<your-username>/fake-medicine-detection-system.git
cd fake-medicine-detection-system

# 2. Start the Multi-Threaded Application Server
python server.py
```

Open your browser and navigate to:
```
http://localhost:5000/
```

---

## 🧪 Demonstration Test Scenarios

Use these pre-configured test cases during viva evaluation:

| Scenario | Sample Medicine | Batch Lot | Price Paid | Expected Verdict | Key Indicators |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Genuine Medicine** | Crocin 650 | `GSK-CRC-8821` | ₹ 32.50 | `VERIFIED` (Score: 100) | Authentic batch, valid license, shelf-life active. |
| **2. Counterfeit Alert** | Augmentin 625 Duo | `AUG-FAKE-990` | ₹ 75.00 | `SUSPICIOUS` (Score: 20) | Manufacturer entity discrepancy, 63% price undercutting. |
| **3. Recalled Batch** | Azithral 500 | `ALM-AZI-7712` | ₹ 119.00 | `SUSPICIOUS` (Score: 5) | Active CDSCO Stop-Sale Order, expired shelf-life. |
| **4. Unregistered Drug** | XyloCure Fast Relief | `XYLO-999-FAKE` | ₹ 499.00 | `UNABLE TO VERIFY` (Score: 15) | No regulatory filing in central drug registry. |

### Evaluation Quick Logins
- **Pharmacist (Yogesh):** `yogesh.shinde@mitadt.edu.in` / `Password@123`
- **General User (Pranav):** `pranav.jagtap@mitadt.edu.in` / `Password@123`
- **New Account:** Register any email to confirm that all metrics strictly initialize to 0.

---

## 📄 Professional Report Generation & Quality Auditing

The system offers complete pharmaceutical compliance reporting and regulatory export functionality:

1. **Certificate of Pharmaceutical Analysis (COA):** 
   - Interactive certificate generator under the *Reports* console.
   - Formal institutional header with MIT-ADT University branding, Group 1603 credentials, and Reference Tracking Number.
   - Comprehensive matrix covering Active Pharmaceutical Ingredients (API), manufacturing license number, registered batch, statutory DPCO price conformity, tamper-evident security packaging, and 2D GS1 DataMatrix cryptography.
   - Dual sign-off block with Project Mentor Dr. Sachin More and student analytical investigators.
   - One-click *Print Certificate / Save as PDF* (`window.print()`) formatted for standard A4 clinical paperwork.
   - One-click *Download JSON Dossier* for machine-readable storage.

2. **Pharmacovigilance Alert Network:** 
   - Report suspected spurious or counterfeit stock directly to the central vigilance registry.
   - Records dispensing pharmacy, suspect lot number, observed packaging defects, and geolocational coordinates.

3. **Multi-Format Compliance Exports:** 
   - **Verification Audit Log (CSV):** Tabular export of all personal scans, price paid vs. DPCO regulated MRP, integrity score, and verdict for spreadsheet analysis.
   - **Regulatory Audit Dossier (JSON):** Cryptographically formatted payload compliant with national pharmacovigilance sync specifications.

---

## 🌓 Clinical Light / Night Operations Dark Mode

- **Instant Theme Toggle:** Accessible via Sun/Moon icons in the top navigation bar and mobile menu.
- **Dedicated Theme Management:** Detailed visual cards in *Dashboard → Settings* to switch between **Clinical Light Mode** (optimized for daytime inspection and pharmacy counters) and **Night Operations Dark Mode** (engineered for low-light pharmaceutical laboratories).
- **Persistent Preferences:** The chosen appearance mode persists across sessions via `localStorage` (`fakemed_theme_mode`) and automatically synchronizes with operating system preferences.

---

## ⚖️ Legal & Healthcare Disclaimer

This software was engineered as an academic demonstration for the Department of Computer Science & Engineering, MIT-ADT University, Pune. Digital packaging verification inspects labeled packaging parameters and regulatory indices; it does not substitute for chemical spectrometry or professional medical advice. Always consult a certified healthcare professional for medical concerns.
