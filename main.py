# main.py (Versi Debugging Hardcode - HANYA UNTUK TES)

import os
import json
import base64
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

# --- Variabel Global ---
db = None
DB_CONNECTION_ERROR = "Tidak ada error yang tercatat."

# ==============================================================================
# --- BAGIAN DEBUGGING ---
# Ganti teks di bawah ini dengan string Base64 Anda yang sangat panjang.
# Pastikan string berada di dalam tanda kutip ("").
# ==============================================================================
HARDCODED_BASE64_KEY = "PASTE_YOUR_VERY_LONG_BASE64_STRING_HERE"
# ==============================================================================


# --- Fungsi Startup Event ---
async def initialize_database():
    """Menginisialisasi koneksi ke Firebase menggunakan kunci yang di-hardcode."""
    global db, DB_CONNECTION_ERROR
    try:
        if not HARDCODED_BASE64_KEY or HARDCODED_BASE64_KEY == "PASTE_YOUR_VERY_LONG_BASE64_STRING_HERE":
            raise ValueError("Kunci Base64 yang di-hardcode belum diisi.")

        # Decode Base64 kembali menjadi string JSON
        decoded_key_str = base64.b64decode(HARDCODED_BASE64_KEY).decode('utf-8')
        service_account_info = json.loads(decoded_key_str)
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("--- KONEKSI DATABASE (HARDCODE) BERHASIL SAAT STARTUP ---")

    except Exception as e:
        DB_CONNECTION_ERROR = str(e)
        print(f"--- KONEKSI DATABASE (HARDCODE) GAGAL: {DB_CONNECTION_ERROR} ---")
        db = None

# --- Inisialisasi Aplikasi FastAPI ---
app = FastAPI(
    title="API Deteksi Harga Produk (Debug Mode)",
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
    if db:
        return {"status": "OK (DEBUG MODE)", "message": "API server is running and connected to database."}
    else:
        return {
            "status": "ERROR (DEBUG MODE)",
            "message": "Database connection FAILED.",
            "error_details": DB_CONNECTION_ERROR
        }

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    if db is None:
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

