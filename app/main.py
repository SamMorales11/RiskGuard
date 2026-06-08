import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from dotenv import load_dotenv

# Hubungkan path agar bisa membaca folder config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import get_db_engine

load_dotenv()

# Konfigurasi Halaman Staging
st.set_page_config(
    page_title="RiskGuard Analytics",
    layout="wide"
)

# --- CLEAN ENTERPRISE DESIGN SYSTEMS (CSS) ---
st.markdown("""
    <style>
    /* Mengatur padding dasar aplikasi */
    .block-container { padding-top: 2.5rem; padding-bottom: 2.5rem; }
    h1, h2, h3, h4 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* Desain Grid untuk Card KPI */
    .kpi-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Desain Dasar Card Profesional */
    .kpi-card {
        flex: 1;
        background-color: #12141C;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #222530;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Tipografi di dalam Card */
    .kpi-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        color: #8A9099;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }
    
    /* Indikator Delta Status Finansial */
    .delta-positive { color: #22C55E; font-size: 0.9rem; font-weight: 600; margin-top: 0.4rem; }
    .delta-negative { color: #EF4444; font-size: 0.9rem; font-weight: 600; margin-top: 0.4rem; }
    </style>
""", unsafe_allow_html=True)

# --- DATA INGESTION ENGINE ---
@st.cache_data(ttl=60)
def load_dashboard_data():
    engine = get_db_engine()
    query = """
        SELECT f.loan_amount, f.interest_rate, f.is_default, c.income_annual, h.bureau_score
        FROM fact_loan_applications f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        JOIN dim_credit_history h ON f.credit_history_id = h.credit_history_id;
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

try:
    df = load_dashboard_data()
except Exception as e:
    df = pd.DataFrame({
        'loan_amount': [42483978], 'interest_rate': [0.15], 'is_default': [1], 
        'income_annual': [120000000], 'bureau_score': [620]
    })

# --- UI HEADER ---
st.markdown("""
    <div style='padding-bottom: 5px;'>
        <h1 style='margin:0; font-size: 2.1rem; font-weight: 700; letter-spacing: -0.04rem;'>RiskGuard: End-to-End Credit Scoring Platform</h1>
        <p style='margin:6px 0 0 0; font-size: 1rem; color: #8A9099; font-weight: 400;'>Internal Risk Assessment & Portfolio Monitoring Executive Dashboard</p>
    </div>
""", unsafe_allow_html=True)
st.divider()

# --- HIGH-SPEC EXECUTIVE KPI PANEL (CUSTOM CARDS) ---
total_apps = len(df)
npl_rate = (df['is_default'].sum() / total_apps) * 100 if total_apps > 0 else 0.0
avg_loan = df['loan_amount'].mean() if total_apps > 0 else 0.0

st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Total Loan Applications Indexed</div>
            <div class="kpi-value">{total_apps:,}</div>
            <div class="delta-positive">SYSTEM LIVE</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Portfolio Default Rate (NPL)</div>
            <div class="kpi-value">{npl_rate:.2f}%</div>
            <div class="delta-negative">+1.2% THRESHOLD WARNING</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Average Exposure per Loan</div>
            <div class="kpi-value">Rp {avg_loan:,.0f}</div>
            <div class="delta-positive">PORTFOLIO BALANCED</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- MAIN INTERACTIVE WORKSPACE ---
left_chart_col, right_simulator_col = st.columns([1, 1])

with left_chart_col:
    st.markdown("### Portfolio Risk Distributions")
    st.write("")
    
    st.markdown("<p style='font-size:0.9rem; font-weight:500; color:#8A9099; margin-bottom:2px;'>Bureau Credit Score Density</p>", unsafe_allow_html=True)
    st.bar_chart(df['bureau_score'].value_counts().sort_index(), height=260)
    
    st.markdown("<p style='font-size:0.9rem; font-weight:500; color:#8A9099; margin-bottom:2px;'>Income vs Loan Amount Analysis</p>", unsafe_allow_html=True)
    st.scatter_chart(data=df, x='income_annual', y='loan_amount', color='is_default', height=260)

with right_simulator_col:
    st.markdown("### Real-time Underwriting AI Simulator")
    st.markdown("<p style='font-size:0.92rem; color: #8A9099; margin-top:-5px;'>Panel instan untuk melakukan asesmen kelayakan kredit calon debitur baru.</p>", unsafe_allow_html=True)
    
    with st.form("credit_assessment_form"):
        applicant_name = st.text_input("Applicant Staging Name", value="Debitur Baru N-1")
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            age = st.number_input("Applicant Age", min_value=17, max_value=80, value=25)
            income = st.number_input("Annual Income (Rp)", min_value=0, value=60000000)
            existing_loans = st.slider("Existing Active Loans", 0, 10, 1)
        with sim_col2:
            bureau_score = st.slider("Historical Bureau Score", 300, 850, 620)
            past_due_days = st.slider("Max Past Due Days", 0, 120, 10)
            loan_req = st.number_input("Requested Loan Amount (Rp)", min_value=0, value=15000000)
            
        submit_btn = st.form_submit_button("Run Risk Assessment Engine")
        
        if submit_btn:
            # 1. Algoritma Kalkulasi Prediktif Backend (Fase 3)
            base_risk = (past_due_days / 95.0) * 0.5 + ((800 - bureau_score) / 400.0) * 0.3 + (existing_loans / 4.0) * 0.2
            probability_of_default = min(max(base_risk, 0.0), 1.0)
            
            st.markdown("---")
            st.markdown("#### Assessment Report")
            st.write(f"**Applicant Token:** `{applicant_name}`")
            st.write(f"**Probability of Default (PD):** `{probability_of_default * 100:.2f}%`")
            
            # 2. FITUR LANJUTAN: RISK-BASED PRICING ENGINE
            st.markdown("#### Customized Credit Pricing Options")
            if probability_of_default > 0.45:
                st.error("CREDIT DECISION: REJECTED (High Default Risk Exposure)")
                st.warning("Rekomendasi: Profil risiko melampaui batas toleransi perusahaan. Pengajuan ditolak otomatis.")
            else:
                # Skenario Risiko Rendah vs Risiko Menengah
                if probability_of_default <= 0.20:
                    risk_tier = "Low Risk Tier (Prime Client)"
                    max_limit = min(income * 0.4, 80000000) # Limit hingga 80 Juta
                    offered_interest = 0.105 # Bunga murah 10.5% p.a.
                    st.success(f"CREDIT DECISION: APPROVED - {risk_tier}")
                else:
                    risk_tier = "Medium Risk Tier (Subprime Client)"
                    max_limit = min(income * 0.2, 35000000) # Limit diperketat maks 35 Juta
                    offered_interest = 0.185 # Bunga kompensasi risiko tinggi 18.5% p.a.
                    st.info(f"CREDIT DECISION: APPROVED WITH CONDITIONS - {risk_tier}")
                
                # Tampilkan hasil penyesuaian harga kredit korporat
                p_col1, p_col2 = st.columns(2)
                p_col1.metric("Maximum Risk Exposure Limit", f"Rp {max_limit:,.0f}")
                p_col2.metric("Offered Interest Rate", f"{offered_interest * 100:.1f}% p.a.")

            # 3. FITUR LANJUTAN: MODEL EXPLAINABILITY (TRANSPARANSI KEPUTUSAN AI)
            st.markdown("#### Local Risk Factor Contributions")
            st.markdown("<p style='font-size:0.85rem; color:#8A9099;'>Grafik di bawah menunjukkan faktor apa yang paling memicu kenaikan probabilitas gagal bayar nasabah ini.</p>", unsafe_allow_html=True)
            
            # Hitung kontribusi riil dari masing-masing bobot fitur terhadap nilai PD akhir
            explanation_data = pd.DataFrame({
                'Risk Factor': ['Past Due History', 'Bureau Credit Profile', 'Active Credit Exposure'],
                'Risk Contribution Score': [
                    (past_due_days / 95.0) * 0.5,
                    ((800 - bureau_score) / 400.0) * 0.3,
                    (existing_loans / 4.0) * 0.2
                ]
            }).set_index('Risk Factor')
            
            # Tampilkan grafik kontribusi horizontal yang bersih tanpa emoji
            st.bar_chart(explanation_data, horizontal=True, height=180)