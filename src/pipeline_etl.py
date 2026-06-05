import sys
import os
import pandas as pd
import numpy as np
import logging
from sqlalchemy import text

# Menambahkan root directory ke sys.path agar python bisa membaca folder 'config' dan 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db_engine
from src.utils.security import process_anonymization

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_tables_if_not_exists(engine):
    """
    Memastikan skema Star Schema (DDL) sudah terbuat di Cloud PostgreSQL sebelum data dimasukkan.
    """
    logging.info("Memeriksa dan menyiapkan skema database di Cloud...")
    
    ddl_query = """
    CREATE TABLE IF NOT EXISTS dim_customers (
        customer_id VARCHAR(64) PRIMARY KEY,
        age INT,
        income_annual NUMERIC(15, 2) NOT NULL,
        employment_type VARCHAR(50),
        housing_status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS dim_credit_history (
        credit_history_id SERIAL PRIMARY KEY,
        customer_id VARCHAR(64) REFERENCES dim_customers(customer_id),
        bureau_score INT,
        number_of_existing_loans INT DEFAULT 0,
        total_debt NUMERIC(15, 2) DEFAULT 0.00,
        past_due_days_max INT DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS fact_loan_applications (
        application_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(64) REFERENCES dim_customers(customer_id),
        credit_history_id INT REFERENCES dim_credit_history(credit_history_id),
        loan_amount NUMERIC(15, 2) NOT NULL,
        interest_rate NUMERIC(5, 2) NOT NULL,
        loan_term_months INT NOT NULL,
        loan_purpose VARCHAR(100),
        application_date DATE NOT NULL,
        loan_status VARCHAR(20) DEFAULT 'Pending',
        is_default INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_loan_applications(customer_id);
    CREATE INDEX IF NOT EXISTS idx_credit_history ON fact_loan_applications(credit_history_id);
    """
    
    try:
        with engine.begin() as connection:
            connection.execute(text(ddl_query))
        logging.info("✔ Skema database siap (Tabel Fakta & Dimensi terverifikasi).")
    except Exception as e:
        logging.error(f"❌ Gagal membuat skema database: {str(e)}")
        raise e

def extract_mock_data() -> pd.DataFrame:
    """
    [STAGE: EXTRACT]
    Mensimulasikan pengambilan data mentah (kotor) dari sistem registrasi Fintech.
    Menghasilkan 100 data pelamar pinjaman tiruan untuk pengujian.
    """
    logging.info("Sourcing data mentah dari aplikasi pendaftaran...")
    np.random.seed(42)
    n_samples = 100
    
    # Generate data kotor (mengandung missing values & PII)
    raw_df = pd.DataFrame({
        'nik': [f"647101{str(i).zfill(10)}" for i in range(1, n_samples + 1)],
        'name': np.random.choice(['Budi Santoso', 'Siti Aminah', 'Rian Hidayat', 'Dewi Lestari', 'Samuel Siregar'], n_samples),
        'email': np.random.choice(['user@gmail.com', 'kerja@itk.ac.id', None, 'nasabah@yahoo.com'], n_samples),
        'age': np.random.choice([20, 25, 30, 45, None, 60], n_samples), # Ada data bolong
        'income_annual': np.random.uniform(30000000, 250000000, n_samples),
        'employment_type': np.random.choice(['Full-time', 'Part-time', 'Self-employed', None], n_samples),
        'housing_status': np.random.choice(['Rent', 'Own', 'Mortgage'], n_samples),
        'bureau_score': np.random.choice([400, 580, 650, 720, 800], n_samples),
        'number_of_existing_loans': np.random.choice([0, 1, 2, 4], n_samples),
        'total_debt': np.random.uniform(0, 50000000, n_samples),
        'past_due_days_max': np.random.choice([0, 5, 15, 45, 95], n_samples),
        'loan_amount': np.random.uniform(5000000, 80000000, n_samples),
        'interest_rate': np.random.uniform(0.08, 0.24, n_samples),
        'loan_term_months': np.random.choice([6, 12, 24, 36], n_samples),
        'loan_purpose': np.random.choice(['Education', 'Business', 'Personal', 'Medical'], n_samples),
        'is_default': np.random.choice([0, 1], n_samples, p=[0.82, 0.18]) # 18% Rasio Gagal Bayar (Imbalanced)
    })
    
    # Buat ID Aplikasi unik
    raw_df['application_id'] = [f"APP-{2026}{str(i).zfill(4)}" for i in range(1, n_samples + 1)]
    raw_df['application_date'] = pd.Timestamp.now().date()
    
    return raw_df

def transform_data(raw_df: pd.DataFrame) -> tuple:
    """
    [STAGE: TRANSFORM]
    Membersihkan data kotor, menangani missing values, dan memecah data menjadi struktur Star Schema.
    """
    logging.info("Memulai transformasi data & penanganan data kosong...")
    df = raw_df.copy()
    
    # 1. Imputation (Mengisi data kosong dengan aturan bisnis yang aman)
    df['age'] = df['age'].fillna(df['age'].median())
    df['employment_type'] = df['employment_type'].fillna('Unknown')
    df['email'] = df['email'].fillna('hidden@riskguard.id')
    
    # 2. Panggil modul security untuk melakukan Hashing NIK & Masking Nama/Email
    df = process_anonymization(df)
    
    # 3. Pecah DataFrame menjadi 3 sesuai struktur tabel target di Cloud PostgreSQL
    
    # Tabel Dim_Customers
    dim_customers = df[['customer_id', 'age', 'income_annual', 'employment_type', 'housing_status']].drop_duplicates(subset=['customer_id'])
    
    # Tabel Dim_Credit_History
    dim_credit_history = df[['customer_id', 'bureau_score', 'number_of_existing_loans', 'total_debt', 'past_due_days_max']]
    
    # Tabel Fact_Loan_Applications
    fact_loan_applications = df[['application_id', 'customer_id', 'loan_amount', 'interest_rate', 'loan_term_months', 'loan_purpose', 'application_date', 'is_default']]
    fact_loan_applications = fact_loan_applications.copy()
    fact_loan_applications['loan_status'] = np.where(fact_loan_applications['is_default'] == 1, 'Default', 'Approved')

    return dim_customers, dim_credit_history, fact_loan_applications

def load_data_to_cloud(engine, df_cust, df_credit, df_fact):
    """
    [STAGE: LOAD]
    Memasukkan data yang telah bertransformasi ke Cloud PostgreSQL dengan mematuhi Foreign Key constraints.
    """
    logging.info("Memulai pengunggahan data ke Serverless PostgreSQL Cloud...")
    
    try:
        # 1. Load Dim_Customers terlebih dahulu (karena bertindak sebagai Parent Table)
        logging.info("Mengunggah data ke tabel 'dim_customers'...")
        df_cust.to_sql('dim_customers', con=engine, if_exists='append', index=False, method='multi')
        
        # 2. Load Dim_Credit_History
        logging.info("Mengunggah data ke tabel 'dim_credit_history'...")
        df_credit.to_sql('dim_credit_history', con=engine, if_exists='append', index=False, method='multi')
        
        # Ambil ID yang digenerate otomatis oleh Postgres untuk tabel Credit History agar bisa ditaruh di Tabel Fakta
        with engine.connect() as conn:
            credit_mapping = pd.read_sql("SELECT credit_history_id, customer_id FROM dim_credit_history", conn)
            
        # Petakan kembali credit_history_id ke tabel fakta berdasarkan customer_id
        df_fact = df_fact.merge(credit_mapping, on='customer_id', how='left')
        
        # 3. Load Fact_Loan_Applications (Tabel Fakta terakhir karena bergantung pada semua tabel Dimensi)
        logging.info("Mengunggah data ke tabel 'fact_loan_applications'...")
        df_fact.to_sql('fact_loan_applications', con=engine, if_exists='append', index=False, method='multi')
        
        logging.info("🎉 PIPELINE ETL BERJALAN SUKSES! Data berhasil di-ingest ke Cloud Database.")
        
    except Exception as e:
        logging.error(f"❌ Terjadi kegagalan saat loading data ke Cloud DB: {str(e)}")
        raise e

def run_pipeline():
    """
    Fungsi Orkestrator Utama ETL
    """
    try:
        engine = get_db_engine()
        create_tables_if_not_exists(engine)
        
        # Jalankan E-T-L
        raw_data = extract_mock_data()
        df_cust, df_credit, df_fact = transform_data(raw_data)
        load_data_to_cloud(engine, df_cust, df_credit, df_fact)
        
    except Exception as e:
        logging.critical(f"⚡ Pipeline Berhenti Total Akibat Critical Error: {str(e)}")

if __name__ == "__main__":
    run_pipeline()