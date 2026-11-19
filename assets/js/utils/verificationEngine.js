/**
 * MediVerify – Smart Fake Medicine Detection System
 * Core Verification Engine
 * Analyzes medicine credentials, batch registries, manufacturer licenses,
 * expiry dates, and pricing deviations to detect counterfeit indicators.
 */

class MedicineVerificationEngine {
  constructor(database) {
    this.database = database || (typeof window !== "undefined" && window.SAMPLE_MEDICINES) || [];
  }

  /**
   * Set or update active database reference
   */
  setDatabase(database) {
    this.database = database;
  }

  /**
   * Normalize text for fuzzy matching
   */
  normalize(str) {
    if (!str) return "";
    return str.toLowerCase().replace(/[^a-z0-9]/g, "");
  }

  /**
   * Verify medicine data provided by user
   * @param {Object} input - { medicineName, batchNumber, manufacturer, userPrice, qrData, imageUploaded }
   * @returns {Object} Comprehensive verification assessment
   */
  verify(input) {
    const {
      medicineName = "",
      batchNumber = "",
      manufacturer = "",
      userPrice = null,
      qrData = "",
      imageUploaded = false
    } = input;

    const trimmedName = medicineName.trim();
    const trimmedBatch = batchNumber.trim().toUpperCase();
    const trimmedMfg = manufacturer.trim();
    const parsedPrice = userPrice !== null && userPrice !== "" ? parseFloat(userPrice) : null;

    // Default assessment template
    const result = {
      timestamp: new Date().toISOString(),
      input: {
        medicineName: trimmedName,
        batchNumber: trimmedBatch,
        manufacturer: trimmedMfg,
        userPrice: parsedPrice,
        imageUploaded: !!imageUploaded,
        qrData: qrData || null
      },
      status: "UNABLE TO VERIFY", // "VERIFIED" | "SUSPICIOUS" | "UNABLE TO VERIFY"
      safetyScore: 0,
      riskLevel: "High", // "Low" | "Medium" | "High" | "Critical"
      headline: "",
      summary: "",
      matchedMedicine: null,
      checks: {
        registryMatch: { passed: false, status: "Failed", details: "" },
        batchValidity: { passed: false, status: "Failed", details: "" },
        manufacturerLicense: { passed: false, status: "Failed", details: "" },
        expiryStatus: { passed: false, status: "Unknown", details: "" },
        priceSanity: { passed: true, status: "Normal", details: "No price specified for comparison." }
      },
      anomalies: [],
      priceAnalysis: null,
      disclaimer: "LEGAL & HEALTHCARE ADVISORY: Digital verification compares entered packaging parameters against official regulatory registries. It CANNOT analyze active chemical composition or bio-equivalence. In case of adverse reactions or doubtful medicines, immediately discontinue use and consult a physician or government drug testing laboratory."
    };

    // Edge check: Empty input validation
    if (!trimmedName && !trimmedBatch && !trimmedMfg && !qrData) {
      result.status = "UNABLE TO VERIFY";
      result.safetyScore = 0;
      result.riskLevel = "High";
      result.headline = "No Input Data Provided";
      result.summary = "Please provide medicine name, batch number, or scan a valid packaging QR code to initiate verification.";
      return result;
    }

    const normName = this.normalize(trimmedName);
    const normBatch = this.normalize(trimmedBatch);
    const normMfg = this.normalize(trimmedMfg);

    // Step 1: Find match in database
    // Strategy: First match by exact batch number if provided; else match by name
    let matched = null;

    if (trimmedBatch) {
      matched = this.database.find(m => this.normalize(m.batchNumber) === normBatch);
    }

    if (!matched && trimmedName) {
      // Find by exact or contained name
      matched = this.database.find(m => {
        const mNorm = this.normalize(m.name);
        return mNorm === normName || mNorm.includes(normName) || normName.includes(mNorm);
      });
    }

    // If still not matched, check if QR data reveals any record
    if (!matched && qrData) {
      matched = this.database.find(m => qrData.includes(m.batchNumber) || qrData.includes(m.name));
    }

    // -------------------------------------------------------------
    // SCENARIO 1: RECORD FOUND IN SAMPLE REGULATORY DATABASE
    // -------------------------------------------------------------
    if (matched) {
      result.matchedMedicine = { ...matched };
      let score = 100;
      const anomalies = [];

      // Check 1: Registry Match
      result.checks.registryMatch = {
        passed: true,
        status: "Verified Genuine Brand",
        details: `Registered brand "${matched.name}" (${matched.genericName}) recognized in Central Drug Registry.`
      };

      // Check 2: Batch Number Verification
      if (!trimmedBatch) {
        result.checks.batchValidity = {
          passed: false,
          status: "Batch Not Provided",
          details: `Batch number was not specified. Official registered batch for this drug is "${matched.batchNumber}".`
        };
        score -= 20;
        anomalies.push("Missing Batch Number: Authentication requires verified packaging lot identifier.");
      } else if (this.normalize(matched.batchNumber) === normBatch) {
        if (matched.verificationStatus === "SUSPICIOUS" || matched.isRecalled) {
          result.checks.batchValidity = {
            passed: false,
            status: "Suspicious / Recalled Batch",
            details: `Batch ${matched.batchNumber} has been officially flagged or recalled.`
          };
          score -= 50;
          anomalies.push(`Alert on Batch ${matched.batchNumber}: ${matched.statusReason}`);
        } else {
          result.checks.batchValidity = {
            passed: true,
            status: "Valid Batch Identifier",
            details: `Batch code ${matched.batchNumber} matches active licensed manufacturing lot.`
          };
        }
      } else {
        // Name matches but user entered a different batch
        result.checks.batchValidity = {
          passed: false,
          status: "Unrecognized Batch Lot",
          details: `Entered batch "${trimmedBatch}" does not match registered batch "${matched.batchNumber}" for this authorization.`
        };
        score -= 35;
        anomalies.push(`Unregistered Batch Number: "${trimmedBatch}" not found in manufacturer's release records.`);
      }

      // Check 3: Manufacturer License Verification
      if (trimmedMfg) {
        const mfgNormDB = this.normalize(matched.manufacturer);
        const isExactMatch = mfgNormDB === normMfg || mfgNormDB.includes(normMfg) || normMfg.includes(mfgNormDB);
        
        if (isExactMatch) {
          result.checks.manufacturerLicense = {
            passed: true,
            status: "Licensed Manufacturer Verified",
            details: `${matched.manufacturer} (License: ${matched.licenseNo}) is an authorized pharmaceutical holder.`
          };
        } else {
          result.checks.manufacturerLicense = {
            passed: false,
            status: "Manufacturer Discrepancy",
            details: `Entered manufacturer "${trimmedMfg}" differs from marketing authorization holder "${matched.manufacturer}".`
          };
          score -= 40;
          anomalies.push(`Manufacturer Mismatch: Entered "${trimmedMfg}", but authorized holder is "${matched.manufacturer}".`);
        }
      } else {
        result.checks.manufacturerLicense = {
          passed: true,
          status: "Authorized Holder on File",
          details: `Authorized by ${matched.manufacturer} (${matched.licenseNo}).`
        };
      }

      // Check 4: Expiry Date Status
      if (matched.expDate) {
        const exp = new Date(matched.expDate);
        const now = new Date();
        const diffDays = Math.ceil((exp - now) / (1000 * 60 * 60 * 24));

        if (diffDays < 0) {
          result.checks.expiryStatus = {
            passed: false,
            status: "Expired Medication",
            details: `Lapsed on ${matched.expDate} (${Math.abs(diffDays)} days ago). Consuming expired medicine can be toxic.`
          };
          score -= 45;
          anomalies.push(`Expired Product: Expired on ${matched.expDate}. Discontinue use immediately.`);
        } else if (diffDays <= 60) {
          result.checks.expiryStatus = {
            passed: true,
            status: "Expiring Soon",
            details: `Valid until ${matched.expDate} (Expires in ${diffDays} days).`
          };
          score -= 5;
        } else {
          result.checks.expiryStatus = {
            passed: true,
            status: "Active & Valid Expiry",
            details: `Expiry date is ${matched.expDate}. Safe shelf life active.`
          };
        }
      }

      // Check 5: Price Analysis / Anomaly Detection
      if (parsedPrice !== null && !isNaN(parsedPrice) && matched.mrp) {
        const mrp = matched.mrp;
        const diff = parsedPrice - mrp;
        const pctDiff = ((diff / mrp) * 100);

        const priceAnalysis = {
          enteredPrice: parsedPrice,
          registeredMrp: mrp,
          difference: diff,
          percentageDiff: parseFloat(pctDiff.toFixed(1)),
          isAbnormalDiscount: pctDiff < -30,
          isOverpriced: pctDiff > 5,
          advice: ""
        };

        if (priceAnalysis.isAbnormalDiscount) {
          priceAnalysis.advice = `Abnormal discount of ${Math.abs(pctDiff).toFixed(1)}% below MRP detected! Genuine pharmaceuticals have low retail margins (10-20%). Undercutting by over 30% is a primary signature of counterfeit manufacturing, diluted salts, or stolen lots.`;
          result.checks.priceSanity = {
            passed: false,
            status: "Severe Price Anomaly",
            details: `Entered price ₹${parsedPrice.toFixed(2)} is ${Math.abs(pctDiff).toFixed(1)}% below registered MRP ₹${mrp.toFixed(2)}.`
          };
          score -= 30;
          anomalies.push(`Price Red Flag: ₹${parsedPrice.toFixed(2)} vs MRP ₹${mrp.toFixed(2)} (${Math.abs(pctDiff).toFixed(1)}% undercutting). Counterfeit risk high.`);
        } else if (priceAnalysis.isOverpriced) {
          priceAnalysis.advice = `Price ₹${parsedPrice.toFixed(2)} exceeds maximum retail price ₹${mrp.toFixed(2)}. Overcharging breaches consumer drug price protection.`;
          result.checks.priceSanity = {
            passed: false,
            status: "Overpriced / DPCO Violation",
            details: `Price exceeds statutory MRP by ₹${diff.toFixed(2)}.`
          };
          score -= 10;
          anomalies.push(`Overpricing Alert: Sold above registered ceiling price.`);
        } else {
          priceAnalysis.advice = `Price ₹${parsedPrice.toFixed(2)} is within customary pharmacy retail discount threshold (0% to 25% discount).`;
          result.checks.priceSanity = {
            passed: true,
            status: "Normal Retail Price",
            details: `Entered price conforms to standard Indian pharma retail pricing structure.`
          };
        }

        result.priceAnalysis = priceAnalysis;
      }

      // Inherit database anomalies if marked suspicious
      if (Array.isArray(matched.counterfeitRiskFactors)) {
        matched.counterfeitRiskFactors.forEach(factor => {
          if (!anomalies.includes(factor)) {
            anomalies.push(factor);
          }
        });
      }

      // Final score clamping
      result.safetyScore = Math.max(0, Math.min(100, score));
      result.anomalies = anomalies;

      // Determine final status
      if (matched.verificationStatus === "SUSPICIOUS" || matched.isRecalled || score < 60 || anomalies.length >= 2) {
        result.status = "SUSPICIOUS";
        result.riskLevel = score < 30 ? "Critical" : "High";
        result.headline = "POTENTIAL COUNTERFEIT OR SAFETY RISK DETECTED";
        result.summary = `MediVerify flagged ${anomalies.length} anomaly/anomalies in this batch. Do not consume this medication until confirmed by a licensed pharmacist.`;
      } else if (score >= 80 && anomalies.length === 0) {
        result.status = "VERIFIED";
        result.riskLevel = "Low";
        result.headline = "MEDICINE VERIFIED AS AUTHENTIC";
        result.summary = "All batch parameters, manufacturer credentials, shelf life, and packaging registers match CDSCO and manufacturer standards.";
      } else {
        result.status = "SUSPICIOUS";
        result.riskLevel = "Medium";
        result.headline = "SUSPICIOUS CREDENTIALS DETECTED";
        result.summary = "Certain credentials do not align with standard distribution records. Review highlighted anomalies carefully.";
      }

      return result;
    }

    // -------------------------------------------------------------
    // SCENARIO 2: RECORD NOT FOUND IN SAMPLE REGULATORY DATABASE
    // -------------------------------------------------------------
    result.status = "UNABLE TO VERIFY";
    result.safetyScore = 20;
    result.riskLevel = "High";
    result.headline = "MEDICINE RECORD NOT FOUND IN REGISTRY";
    result.summary = `Neither the medicine name "${trimmedName}" nor the batch code "${trimmedBatch}" was found in the MediVerify regulatory drug sample repository.`;

    result.checks.registryMatch = {
      passed: false,
      status: "Unregistered Drug / Not Found",
      details: `No approved drug under name "${trimmedName}" is indexed in this database.`
    };

    result.checks.batchValidity = {
      passed: false,
      status: "Batch Unverified",
      details: `Batch "${trimmedBatch || 'N/A'}" could not be cross-referenced against any authorized production lot.`
    };

    // Check if manufacturer is at least known
    const knownMfg = (typeof window !== "undefined" && window.LICENSED_MANUFACTURERS) || [];
    const isKnownMfg = knownMfg.some(m => this.normalize(m).includes(normMfg) || normMfg.includes(this.normalize(m)));

    if (isKnownMfg && trimmedMfg) {
      result.checks.manufacturerLicense = {
        passed: true,
        status: "Known Manufacturer (Unmatched Batch)",
        details: `"${trimmedMfg}" is an authorized company, but this specific product/batch is not on file.`
      };
      result.safetyScore = 40;
    } else {
      result.checks.manufacturerLicense = {
        passed: false,
        status: "Unregistered Entity",
        details: `Manufacturer "${trimmedMfg || 'Unknown'}" is not listed among licensed pharmaceutical holders.`
      };
    }

    result.anomalies.push("Unlisted Medicine: Product is missing from the authorized pharmaceutical registry.");
    result.anomalies.push("Unverified Supply Chain: Sourcing cannot be validated digitally.");

    if (parsedPrice) {
      result.priceAnalysis = {
        enteredPrice: parsedPrice,
        registeredMrp: null,
        difference: null,
        percentageDiff: null,
        isAbnormalDiscount: false,
        isOverpriced: false,
        advice: "Unable to compare pricing because official registered MRP is unavailable for this unlisted drug."
      };
    }

    return result;
  }
}

// Attach to window object for browser access
if (typeof window !== "undefined") {
  window.MedicineVerificationEngine = MedicineVerificationEngine;
}
