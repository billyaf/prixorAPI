# main.py (Versi Diperbaiki)

import os
import json
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

# --- Variabel Global untuk Database ---
# Kita siapkan variabel 'db' di sini, tapi kita isi nanti saat startup.
db = None

# --- Fungsi Startup Event ---
# Fungsi ini akan dijalankan oleh FastAPI HANYA SATU KALI saat aplikasi dimulai.
async def initialize_database():
    """Menginisialisasi koneksi ke Firebase Firestore saat startup."""
    global db
    try:
        # Ambil kredensial dari Environment Variable Vercel
        service_account_info_str = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        
        if not service_account_info_str:
            raise ValueError("Kredensial Firebase tidak ditemukan di environment variables.")
        
        service_account_info = json.loads(service_account_info_str)
        
        # Cek agar tidak menginisialisasi aplikasi yang sama berulang kali
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("--- KONEKSI DATABASE BERHASIL SAAT STARTUP ---")

    except Exception as e:
        # Jika koneksi gagal saat startup, catat error fatal
        print(f"--- KONEKSI DATABASE GAGAL SAAT STARTUP: {e} ---")
        db = None

# --- Inisialisasi Aplikasi FastAPI ---
# Kita daftarkan fungsi 'initialize_database' untuk dijalankan saat startup.
app = FastAPI(
    title="API Deteksi Harga Produk",
    on_startup=[initialize_database]
)

# --- Model Data Pydantic ---
class Product(BaseModel):
    name: str
    price: int
    description: str
    product_id: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Endpoint root untuk mengecek status server."""
    if db:
        return {"status": "OK", "message": "API server is running and connected to database."}
    else:
        return {"status": "ERROR", "message": "API server is running, but database connection FAILED."}

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    """Mengambil detail produk dari Firestore berdasarkan product_id."""
    if db is None:
        # Jika koneksi database gagal saat startup, kirim error ini.
        raise HTTPException(status_code=503, detail="Layanan database tidak tersedia.")

    try:
        product_ref = db.collection('products').document(product_id)
        doc = product_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail=f"Produk dengan ID '{product_id}' tidak ditemukan.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {e}")

