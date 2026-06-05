import hashlib
import os
import re
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_salt() -> str:
    return os.getenv("APP_SALT", "RiskGuardSuperSecretSalt123!")

def hash_identifier(identifier: str) -> str:
    if pd.isna(identifier) or not str(identifier).strip():
        return None
    salt = generate_salt()
    salted_data = str(identifier).strip() + salt
    return hashlib.sha256(salted_data.encode('utf-8')).hexdigest()

def mask_name(name: str) -> str:
    if pd.isna(name) or not str(name).strip():
        return "Unknown"
    words = str(name).strip().split()
    masked_words = []
    for word in words:
        if len(word) <= 2:
            masked_words.append(word[0] + "*")
        else:
            masked_words.append(word[0] + "*" * (len(word) - 2) + word[-1])
    return " ".join(masked_words)

def mask_email(email: str) -> str:
    if pd.isna(email) or not str(email).strip():
        return "hidden@riskguard.id"
    email = str(email).strip()
    match = re.match(r"([^@]+)(@.+)", email)
    if not match:
        return "invalid_email@mask.id"
    local_part, domain = match.groups()
    if len(local_part) <= 2:
        masked_local = local_part[0] + "*"
    else:
        masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]
    return f"{masked_local}{domain}"

# FUNGSI UTAMA YANG DICARI OLEH PIPELINE_ETL.PY
def process_anonymization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menerima DataFrame mentah dan mengembalikan DataFrame yang aman (NIK di-hash, Nama & Email dimask)
    """
    anonymized_df = df.copy()
    try:
        if 'nik' in anonymized_df.columns:
            anonymized_df['customer_id'] = anonymized_df['nik'].astype(str).apply(hash_identifier)
            anonymized_df.drop(columns=['nik'], inplace=True)
        
        if 'name' in anonymized_df.columns:
            anonymized_df['name'] = anonymized_df['name'].apply(mask_name)
            
        if 'email' in anonymized_df.columns:
            anonymized_df['email'] = anonymized_df['email'].apply(mask_email)
            
        return anonymized_df
    except Exception as e:
        logging.error(f"Gagal melakukan masking data: {str(e)}")
        raise RuntimeError(e)