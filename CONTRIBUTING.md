# Contribution Guidelines — Fake Medicine Detection System

**Institution:** MIT-ADT University, Pune  
**Department:** Computer Science & Engineering (School of Computing)  
**Academic Group:** 1603 | Second Year B.Tech  
**Project Mentor:** Dr. Sachin More  

Thank you for contributing to the **Fake Medicine Detection System** academic project.

---

## 1. Team Code of Conduct
- Maintain high academic and professional coding standards.
- Ensure all sample medicine data complies with educational and mock verification guidelines.
- Never hardcode API keys, JWT secrets, or production passwords into git commits.

---

## 2. Development Workflow

### Step 1: Clone Repository
```bash
git clone https://github.com/<your-username>/fake-medicine-detection-system.git
cd fake-medicine-detection-system
```

### Step 2: Environment Configuration
Copy `.env.example` to `.env` and configure local development variables:
```bash
cp .env.example .env
```

### Step 3: Run the Local Gateway & Web App
```bash
python server.py
```
Access the application at `http://localhost:5000/`.

---

## 3. Branching Strategy
- `main`: Production-ready, verified academic evaluation branch.
- `feature/<feature-name>`: New feature modules (e.g., `feature/ocr-enhancement`, `feature/pdf-export`).
- `fix/<bug-description>`: Bug fixes and security patches.

---

## 4. Coding Standards
- **Python Backend:** Standard library PEP 8 guidelines. Zero unnecessary third-party package dependencies for maximum portability.
- **Frontend Components:** Clean React 18 modular structure with Tailwind CSS styling and accessible semantic markup.
- **Database Migrations:** All schema changes must be updated in `schema.sql` and backwards-compatible in `database.py`.

---

## 5. Contact & Support
For academic inquiries or viva review queries:
- **Project Lead:** Yogesh Shinde (`yogesh.shinde@mitadt.edu.in`)
- **Project Mentor:** Dr. Sachin More (`sachin.more@mitadt.edu.in`)
