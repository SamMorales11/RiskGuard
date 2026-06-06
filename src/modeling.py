import sys
import os
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# Menghubungkan root directory agar bisa membaca folder 'config'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import get_db_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data_from_cloud():
    """
    [STAGE: EXTRACT FOR ML]
    Menarik data dari Star Schema di Cloud PostgreSQL menggunakan query JOIN
    untuk disatukan menjadi flat-table yang siap dibaca oleh Machine Learning.
    """
    logging.info("Menarik data analitik dari Cloud PostgreSQL...")
    engine = get_db_engine()
    
    query = """
        SELECT 
            f.loan_amount, f.interest_rate, f.loan_term_months, f.loan_purpose, f.is_default,
            c.age, c.income_annual, c.employment_type, c.housing_status,
            h.bureau_score, h.number_of_existing_loans, h.total_debt, h.past_due_days_max
        FROM fact_loan_applications f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        JOIN dim_credit_history h ON f.credit_history_id = h.credit_history_id;
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        logging.info(f"✔ Berhasil menarik {len(df)} baris data untuk training.")
        return df
    except Exception as e:
        logging.error(f"❌ Gagal menarik data dari DB: {str(e)}")
        raise e

def preprocess_features(df: pd.DataFrame):
    """
    [STAGE: FEATURE ENGINEERING]
    Mengubah variabel kategorikal (teks) menjadi bentuk numerik biner (One-Hot Encoding)
    agar dapat diproses secara matematis oleh algoritma Random Forest.
    """
    logging.info("Memulai rekayasa fitur (Feature Engineering)...")
    
    X = df.drop(columns=['is_default'])
    y = df['is_default']
    
    # Mengubah data teks menjadi kolom biner 0 dan 1
    categorical_cols = ['loan_purpose', 'employment_type', 'housing_status']
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Konversi tipe data ke float untuk kompatibilitas penuh Python 3.13
    X = X.astype(float)
    
    return X, y

def train_and_evaluate():
    """
    [STAGE: MODEL TRAINING & EVALUATION]
    Melatih algoritma Random Forest dengan penanganan ketidakseimbangan kelas (class_weight)
    dan menguji performa model menggunakan metrik industri.
    """
    try:
        raw_df = fetch_data_from_cloud()
        X, y = preprocess_features(raw_df)
        
        # Split data: 80% untuk latihan, 20% untuk ujian harian (Test Set)
        # Stratify=y memastikan rasio kelas gagal bayar tetap sama di kedua set data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logging.info(f"Komposisi Data Uji: Lancar={list(y_test).count(0)}, Gagal Bayar={list(y_test).count(1)}")
        
        # Inisialisasi Model Random Forest Classifier
        logging.info("Melatih model Random Forest Classifier dengan penalti bobot seimbang...")
        model = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced', # Solusi Industri: memberi penalti berat jika salah tebak gagal bayar
            random_state=42,
            max_depth=8
        )
        model.fit(X_train, y_train)
        
        # Prediksi hasil
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Cetak Laporan Analisis ke Terminal
        print("\n" + "="*20 + " EVALUASI MODEL RISKGUARD " + "="*20)
        print(classification_report(y_test, y_pred, target_names=['Lancar (0)', 'Gagal Bayar (1)']))
        
        auc_score = roc_auc_score(y_test, y_proba)
        print(f"ROC-AUC Score: {auc_score:.4f}")
        
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:\n{cm}")
        print("="*66)
        
        logging.info("✔ Evaluasi Fase 3 selesai sukses.")
        
    except Exception as e:
        logging.error(f"⚠️ Proses modeling gagal: {str(e)}")

if __name__ == "__main__":
    train_and_evaluate()