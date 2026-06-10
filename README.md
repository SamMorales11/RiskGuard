# RiskGuard: End-to-End Credit Scoring & Risk Analytics Platform

RiskGuard is an enterprise-grade credit risk management and underwriting platform designed for automated credit assessment. The system covers the entire financial data lifecycle: from secure cloud ingestion and idempotent database orchestration to predictive machine learning, explainable AI diagnostics, risk-based credit pricing, and strategic vintage portfolio analytics.

---

## 🚀 Platform Architecture Overview

The system is engineered across 7 distinct milestone phases to replicate real-world fintech infrastructure:

### 1. Financial Data Governance & Security (Phase 1)
* **PII Anonymization**: Implements cryptographic SHA-256 salted hashing on sensitive customer identifiers (NIK) to prevent identity exposure.
* **Deterministic Masking**: Obfuscates names and email addresses directly within the pipeline, ensuring zero raw data leakage to downstream analytic tables while maintaining compliance with rigorous data privacy regulations (**UU PDP**).

### 2. Idempotent ETL & Cloud Ingestion (Phase 2 & 6)
* **Cloud Infrastructure**: Built upon a serverless PostgreSQL cloud instance (Neon.tech) utilizing an analytical Star Schema layout.
* **Resilient Batch Processing**: Implements multi-row bulk insert chunking strategies (500 rows per transaction) to respect connection pooler constraints and eliminate parameters limit overflow.
* **Truncate-and-Reload Idempotency**: Guarantees repeatable execution runs by maintaining historical records without foreign key or unique primary key conflicts.

### 3. Predictive Risk Modeling (Phase 3)
* **Class Imbalance Optimization**: Utilizes a Scikit-Learn Random Forest Classifier parameterized with balanced class weights to systematically offset highly skewed default-to-prime lending distributions.
* **Rigorous Metric Thresholds**: Achieved a highly robust model fit, eliminating typical blind predictor pitfalls:
  * **ROC-AUC Score**: `0.9245`
  * **Default Class Recall**: `89.00%` (Critical for limiting Non-Performing Loans)
  * **Default Class Precision**: `91.00%`

### 4. Explainable AI & Dynamic Pricing Engine (Phase 5)
* **Transparent Risk Diagnostics**: Computes mathematical feature contribution scores instantly based on mathematical input deviations against database population baselines, avoiding heavy third-party overhead.
* **Risk-Based Pricing (RBP)**: Calibrates and adjusts final credit exposure caps and nominal annual interest rates depending on the customer's calculated Probability of Default (PD) tier:
  * **Low-Risk Tier**: Maximum exposure up to Rp 80,000,000 at a premium interest rate of `10.5% p.a.`
  * **Medium-Risk Tier**: Restricted exposure up to Rp 35,000,000 at an interest rate of `18.5% p.a.`
  * **High-Risk Tier**: Automatic system rejection when calculated default probability exceeds `45.00%`.

### 5. Strategic Vintage Tracking (Phase 7)
* **Cohort Performance Tracking**: Implements complex historical time-series segmentation on transaction data to group loan originations based on month of application.
* **Months on Books (MOB)**: Monitors cumulative default performance progression from MOB 1 to MOB 4 to give risk managers a bird's-eye view of credit decay pattern variations.

---

## 🛠️ Tech Stack & Drivers

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Infrastruktur DB** | Cloud Serverless PostgreSQL (Neon.tech) | Production Star Schema Warehouse |
| **Pipa Data** | Python, Pandas, SQLAlchemy, Psycopg v3 | Multi-row batching ETL Engine |
| **Pemodelan AI** | Scikit-Learn (Random Forest Classifier) | Probability of Default prediction engine |
| **Interface** | Streamlit Architecture (v1.35.0+) | B2B Risk Assessment Dashboard & Simulator |

---

## 📊 Visualized Interface Dominance

### Executive KPI Monitoring Block
Provides immediate executive tracking metrics regarding overall portfolio exposure and macro default risk rates.

<img width="1817" height="397" alt="Screenshot 2026-06-09 092455" src="https://github.com/user-attachments/assets/38ff9267-e152-4bf4-bcca-2b436234d83f" />

### Risk Distributions & Descriptive Diagnostics
Tracks bureau credit score density variations along with multidimensional income-to-loan scattering characteristics.

<img width="920" height="765" alt="Screenshot 2026-06-09 092504" src="https://github.com/user-attachments/assets/597bdf3d-efc6-45fd-9bc8-656ae0f0db7d" />

### Real-Time Underwriting AI Simulator (Subprime Approval Condition)
Demonstrates the conditional approval engine optimizing maximum financing capacity caps and interest rates for mid-risk borrowers.

<img width="855" height="731" alt="Screenshot 2026-06-09 092525" src="https://github.com/user-attachments/assets/d9ad3a19-bb19-4486-9155-65bc1f2bc68a" />
<img width="885" height="592" alt="Screenshot 2026-06-09 092512" src="https://github.com/user-attachments/assets/53465f5b-234e-4d23-a992-478f24c2ef62" />


### Explainable AI System In Action (Automated Rejection Trigger)
Displays explicit feature risk factors (e.g., Past Due History) causing the default probability to break past threshold limits, prompting automatic credit rejection.

<img width="885" height="592" alt="Screenshot 2026-06-09 092512" src="https://github.com/user-attachments/assets/35c8a52b-31c9-46c3-aaf3-4d27d32bb2b1" />

## 📁 Repository Directory Tree

```text
RiskGuard/
├── app/
│   └── main.py              # Streamlit analytical dashboard & RBP interface
├── config/
│   └── database.py          # SQLAlchemy connection management via Psycopg v3
├── src/
│   ├── utils/
│   │   └── security.py      # Cryptographic hashing & PII data masking script
│   ├── modeling.py          # Machine learning model training & metrics evaluator
│   └── pipeline_etl.py      # Idempotent database setup and transaction generator
├── .env.example             # Template for required infrastructure environment keys
├── requirements.txt         # Production-ready package dependency lockfile
└── README.md                # Technical platform reference manual
```

### ⚙️ Quick Installation & Setup

1. Clone the Repository
```bash
git clone [https://github.com/SamMorales11/RiskGuard.git](https://github.com/SamMorales11/RiskGuard.git)
cd RiskGuard
```
2. Initialize and Activate Virtual Environment
```bash
python -m venv env
# For Windows
.\env\Scripts\activate
# For macOS/Linux
source env/bin/activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Configure Environment Keys
Create a .env file in the root directory:
```bash
DATABASE_URL=postgresql+psycopg://username:password@your-neon-host.tech/dbname?sslmode=require
APP_SALT=YourSuperSecretCustomSaltHereValue
```
5. Execute the Analytical Infrastructure Data Pipeline
```bash
python src/pipeline_etl.py
```
6. Boot up the Underwriting Interface Command Center
```bash
python -m streamlit run app/main.py
```



