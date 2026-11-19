/**
 * Fake Medicine Detection System
 * Persistent Data Storage & API Sync Layer
 * Academic Project: MIT-ADT University, Pune | School of Computing | Group 1603
 */

const STORAGE_KEYS = {
  TOKEN: "fakemed_auth_token_v1",
  USER: "fakemed_auth_user_v1",
  SETTINGS: "fakemed_settings_v1",
  CACHED_MEDS: "fakemed_cached_medicines_v1"
};

class StorageManager {
  constructor() {
    this.apiBaseUrl = "/api";
    this.token = this.loadToken();
    this.user = this.loadUser();
  }

  // --------------------------------------------------------------------------
  // NETWORK UTILITY WITH TIMEOUT
  // --------------------------------------------------------------------------
  async fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error("Server response timed out. Please check your connection.");
      }
      throw err;
    }
  }

  // --------------------------------------------------------------------------
  // AUTH TOKEN & SESSION MANAGEMENT
  // --------------------------------------------------------------------------
  loadToken() {
    return localStorage.getItem(STORAGE_KEYS.TOKEN) || sessionStorage.getItem(STORAGE_KEYS.TOKEN) || null;
  }

  loadUser() {
    const raw = localStorage.getItem(STORAGE_KEYS.USER) || sessionStorage.getItem(STORAGE_KEYS.USER);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  setSession(token, user, rememberMe = true) {
    this.token = token;
    this.user = user;
    const store = rememberMe ? localStorage : sessionStorage;
    const otherStore = rememberMe ? sessionStorage : localStorage;

    store.setItem(STORAGE_KEYS.TOKEN, token);
    store.setItem(STORAGE_KEYS.USER, JSON.stringify(user));

    otherStore.removeItem(STORAGE_KEYS.TOKEN);
    otherStore.removeItem(STORAGE_KEYS.USER);
  }

  clearSession() {
    this.token = null;
    this.user = null;
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    sessionStorage.removeItem(STORAGE_KEYS.TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER);
  }

  isAuthenticated() {
    return !!(this.token && this.user);
  }

  getAuthHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  // --------------------------------------------------------------------------
  // AUTHENTICATION API CALLS
  // --------------------------------------------------------------------------
  async login(email, password, rememberMe = true) {
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, rememberMe })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Login failed. Check your email and password.");
      }
      this.setSession(data.token, data.user, rememberMe);
      return data.user;
    } catch (err) {
      console.error("Login Error:", err);
      throw err;
    }
  }

  async register(fullName, email, password, confirmPassword, role = "General User") {
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fullName, email, password, confirmPassword, role })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Registration failed.");
      }
      this.setSession(data.token, data.user, true);
      return data.user;
    } catch (err) {
      console.error("Registration Error:", err);
      throw err;
    }
  }

  async checkCurrentSession() {
    if (!this.token) return null;
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/me`, {
        headers: this.getAuthHeaders()
      }, 4000);
      const data = await res.json();
      if (res.ok && data.success && data.user) {
        this.user = data.user;
        return data.user;
      } else {
        this.clearSession();
        return null;
      }
    } catch {
      // Offline fallback: keep cached session if available
      return this.user;
    }
  }

  async updateProfile(fullName, phone) {
    const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/profile`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ fullName, phone })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Failed to update profile.");
    }
    this.user = data.user;
    if (localStorage.getItem(STORAGE_KEYS.USER)) {
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(data.user));
    } else {
      sessionStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(data.user));
    }
    return data.user;
  }

  async changePassword(currentPassword, newPassword) {
    const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/change-password`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ currentPassword, newPassword })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Password change failed.");
    }
    return data;
  }

  async forgotPassword(email) {
    const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    return await res.json();
  }

  // --------------------------------------------------------------------------
  // USER METRICS & VERIFICATION AUDIT TRAIL
  // --------------------------------------------------------------------------
  async getUserStats() {
    if (!this.token) {
      return { totalAttempts: 0, verifiedAgainstRecords: 0, informationMismatches: 0, unableToVerify: 0 };
    }
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/user/stats`, {
        headers: this.getAuthHeaders()
      }, 4000);
      const data = await res.json();
      if (res.ok && data.success) {
        return data.data;
      }
      return { totalAttempts: 0, verifiedAgainstRecords: 0, informationMismatches: 0, unableToVerify: 0 };
    } catch {
      return { totalAttempts: 0, verifiedAgainstRecords: 0, informationMismatches: 0, unableToVerify: 0 };
    }
  }

  async getUserHistory(limit = 50) {
    if (!this.token) return [];
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/user/history?limit=${limit}`, {
        headers: this.getAuthHeaders()
      }, 4000);
      const data = await res.json();
      if (res.ok && data.success) {
        return data.data || [];
      }
      return [];
    } catch {
      return [];
    }
  }

  async verifyMedicine(payload) {
    const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/verify`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Verification engine failed.");
    }
    return data.assessment;
  }

  // --------------------------------------------------------------------------
  // REFERENCE MEDICINES REPOSITORY
  // --------------------------------------------------------------------------
  async getMedicines(query = "", category = "") {
    try {
      let url = `${this.apiBaseUrl}/medicines`;
      const params = new URLSearchParams();
      if (query) params.append("q", query);
      if (category && category !== "All") params.append("category", category);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await this.fetchWithTimeout(url, {}, 5000);
      const data = await res.json();
      if (res.ok && data.success) {
        return data.data;
      }
    } catch (e) {
      console.warn("Falling back to local reference medicines:", e);
    }
    // Fallback to window.SAMPLE_MEDICINES if server is unreachable
    let meds = (typeof window !== "undefined" && window.SAMPLE_MEDICINES) ? window.SAMPLE_MEDICINES : [];
    if (query) {
      const q = query.toLowerCase();
      meds = meds.filter(m => (m.name && m.name.toLowerCase().includes(q)) || (m.batchNumber && m.batchNumber.toLowerCase().includes(q)));
    }
    if (category && category !== "All") {
      meds = meds.filter(m => m.therapeuticCategory === category);
    }
    return meds;
  }

  // --------------------------------------------------------------------------
  // INCIDENT REPORTS
  // --------------------------------------------------------------------------
  async getReports() {
    try {
      const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/reports`, {
        headers: this.getAuthHeaders()
      }, 5000);
      const data = await res.json();
      if (res.ok && data.success) return data.data;
    } catch (err) {
      console.warn("Failed fetching reports from server:", err);
    }
    return [];
  }

  async submitReport(reportData) {
    const res = await this.fetchWithTimeout(`${this.apiBaseUrl}/reports`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(reportData)
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || "Failed to submit incident report.");
    }
    return data;
  }

  // --------------------------------------------------------------------------
  // EXPORT CSV UTILITY
  // --------------------------------------------------------------------------
  exportHistoryCSV(history) {
    if (!history || history.length === 0) {
      alert("No verification logs available to export.");
      return;
    }
    const headers = ["Scan ID", "Timestamp", "Medicine Name", "Batch Number", "Manufacturer", "User Price (INR)", "Regulated MRP (INR)", "Verdict", "Safety Score", "Risk Level", "Summary"];
    const rows = history.map(h => [
      `"${h.id || ''}"`,
      `"${h.timestamp || ''}"`,
      `"${(h.medicine_name || '').replace(/"/g, '""')}"`,
      `"${(h.batch_number || '').replace(/"/g, '""')}"`,
      `"${(h.manufacturer || '').replace(/"/g, '""')}"`,
      h.user_price !== null && h.user_price !== undefined ? h.user_price : '',
      h.mrp !== null && h.mrp !== undefined ? h.mrp : '',
      `"${h.status || ''}"`,
      h.safety_score || 0,
      `"${h.risk_level || ''}"`,
      `"${(h.summary || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `mediverify_audit_log_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // --------------------------------------------------------------------------
  // EXPORT JSON AUDIT DOSSIER
  // --------------------------------------------------------------------------
  exportHistoryJSON(history) {
    if (!history || history.length === 0) {
      alert("No verification logs available to export.");
      return;
    }
    const exportPayload = {
      institution: "MIT-ADT University, Pune",
      department: "School of Computing, Department of Computer Science & Engineering",
      academic_project: "Fake Medicine Detection System (Group ID 1603)",
      mentor: "Dr. Sachin More",
      exported_at: new Date().toISOString(),
      total_records: history.length,
      records: history
    };
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `mediverify_audit_dossier_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// Global instance for use in React components
window.storageManager = new StorageManager();
