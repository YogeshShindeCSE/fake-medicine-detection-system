# MediVerify – Installation & Execution Instructions

**Academic Level:** Second Year B.Tech Computer Science & Engineering  
**Operating Systems Supported:** Windows 10/11, macOS, Linux  
**Runtime Requirement:** Any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari) + Optional Python 3.8+ for full-stack backend.

---

## Method 1: Instant Launch (Zero Installation Required)

MediVerify is engineered with a **zero-friction client-side architecture**. You do **not** need Node.js, npm, or complex build steps to run and present this project.

1. Navigate to the project directory:
   ```
   mediverify-app/
   ```
2. Double-click the file:
   ```
   index.html
   ```
   *OR* right-click `index.html` -> **Open with** -> **Google Chrome** (or Microsoft Edge).
3. The application will launch instantly with the full React 18 UI, sample database, animated scanners, and LocalStorage persistence active.

---

## Method 2: Full-Stack Python REST Server Launch

If you wish to demonstrate backend API integration and persistent SQLite database queries during your project viva:

1. Ensure **Python 3.8+** is installed on your computer:
   ```bash
   python --version
   ```
2. Open PowerShell or Terminal in the project root directory:
   ```bash
   cd path/to/mediverify-app
   ```
3. Initialize the SQLite database and start the server:
   ```bash
   python server.py
   ```
4. You will see the server startup banner:
   ```
   ======================================================================
     MediVerify – Smart Fake Medicine Detection System
     College Engineering Project (Second Year B.Tech CSE)
   ======================================================================
     * Local Web App & REST API Server Running At: http://localhost:5000
     * Database: SQLite3 (mediverify.db)
     * Press Ctrl+C in terminal to stop server
   ======================================================================
   ```
5. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

---

## Method 3: Visual Studio Code Live Server

1. Open the `mediverify-app` folder in **Visual Studio Code**.
2. If you have the **Live Server** extension installed (`ritwickdey.LiveServer`):
   - Right-click `index.html` -> Click **"Open with Live Server"**.
3. The project runs seamlessly on `http://127.0.0.1:5500/index.html`.

---

## Project Viva / College Presentation Walkthrough

Use this recommended sequence when presenting to your project examiner or professor:

### Step 1: Introduction & Problem Context (Home Page)
- Show the **Hero Section** and explain the WHO counterfeit medicine statistics.
- Highlight the **4-Phase Inspection Pipeline** (Capture -> Lookup -> Anomaly Detection -> Verdict).

### Step 2: Test Case 1 – Genuine Medicine Verification (`Crocin 650`)
- Click **"Case 1: Authentic Medicine"** from the top Viva Demo bar (or in the QR scanner).
- Click **"Execute Verification Assessment"**.
- Point out the **Green VERIFIED** badge, 98% Safety Score, valid batch `GSK-CRC-8821`, and registered license.
- Click **"Print Certificate"** to showcase the laboratory-grade audit report.

### Step 3: Test Case 2 – Counterfeit Medicine Detection (`Augmentin 625 Duo`)
- Click **"Case 2: Counterfeit Alert"** from the Viva Demo bar.
- Note the inputs: Manufacturer is marked `"GSK Biotech India Pvt Ltd"` and price is `₹75.00` (normal is `₹204.50`).
- Click **"Execute Verification Assessment"**.
- Point out the **Red SUSPICIOUS** alert:
  - Manufacturer mismatch detected.
  - Price undercutting by 63.3% flagged.
  - Safety score drops to 18%.
- Click **"Report Spurious Batch"** to demonstrate the consumer complaint workflow.

### Step 4: Test Case 3 – Expired & Recalled Drug (`Azithral 500`)
- Click **"Case 3: Expired & Recalled Drug"**.
- Verify: The batch expired on `2024-06-30` and has an active DCGI recall order.
- Demonstrates automatic shelf-life and regulatory surveillance interception.

### Step 5: Test Case 4 – Unregistered Drug (`XyloCure Fast Relief`)
- Click **"Case 4: Unregistered Drug"**.
- Demonstrates the **UNABLE TO VERIFY** status when a drug is missing from official CDSCO registries.

### Step 6: Price Checker Tool
- Navigate to the **"Price Checker"** tab.
- Select a medicine, input a heavily discounted price, and show the anomaly graph and DPCO regulatory violation notice.

### Step 7: Admin Panel & Batch Recall Simulation
- Click **"Admin Panel"**.
- Enter examiner passcode: **`1234`**.
- Show the central sample database table.
- Click **"ACTIVE LOT (Click to recall)"** on any medicine.
- Return to scanner: that medicine now immediately triggers a **SUSPICIOUS** alert!

### Step 8: Dashboard & Audit Trail
- Click **"Dashboard"**.
- Show the total scans, safety distribution chart, and filterable history table.
- Click **"Export CSV"** to demonstrate downloadable audit logs.

---

## Admin Credentials
- **Admin Panel Access Passcode:** `1234` (or `admin`)
