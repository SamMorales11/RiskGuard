import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_engine() -> Engine:
    """
    Membuat dan mengembalikan database engine SQLAlchemy untuk Cloud PostgreSQL.
    Menggunakan kredensial aman dari environment variable.
    """
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logging.error("DATABASE_URL tidak ditemukan di file .env!")
        raise ValueError("Koneksi gagal: DATABASE_URL wajib dikonfigurasi.")
    
    # Penanganan isu internal SQLAlchemy untuk string 'postgres://' kuno
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    try:
        # Menambahkan parameter pool_pre_ping untuk mendeteksi koneksi drop secara otomatis (standar produksi)
        engine = create_engine(
            db_url, 
            pool_pre_ping=True,
            pool_recycle=3600
        )
        logging.info("✔ Database engine SQLAlchemy berhasil diinisialisasi.")
        return engine
    except Exception as e:
        logging.error(f"❌ Gagal membuat database engine: {str(e)}")
        raise e

if __name__ == "__main__":
    # Test koneksi langsung ke Cloud DB
    print("Mencoba melakukan test koneksi ke Cloud PostgreSQL...")
    try:
        engine = get_db_engine()
        with engine.connect() as connection:
            print("🎉 Koneksi BERHASIL! Aplikasi Anda terhubung ke Cloud PostgreSQL.")
    except Exception as e:
        print("⚡ Koneksi GAGAL. Periksa kembali isi file .env atau status database Cloud Anda.")