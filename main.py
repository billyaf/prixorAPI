# main.py (Versi Final dengan Debugging Error Eksplisit)

import os
import json
import base64
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

# --- Variabel Global ---
db = None
# Variabel ini akan menyimpan pesan error spesifik jika koneksi gagal.
DB_CONNECTION_ERROR = "Tidak ada error yang tercatat. Koneksi seharusnya berhasil."

# --- Fungsi Startup Event ---
async def initialize_database():
    """Menginisialisasi koneksi ke Firebase saat startup dan mencatat error jika ada."""
    global db, DB_CONNECTION_ERROR
    try:
        # Ambil kunci Base64 dari Environment Variable Vercel
        base64_encoded_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64')
        
        if not base64_encoded_key:
            raise ValueError("Environment variable 'FIREBASE_SERVICE_ACCOUNT_BASE64' tidak ditemukan.")
        
        # Decode Base64 kembali menjadi string JSON
        decoded_key_str = base64.b64decode(base64_encoded_key).decode('utf-8')
        service_account_info = json.loads(decoded_key_str)
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("--- KONEKSI DATABASE BERHASIL SAAT STARTUP ---")

    except Exception as e:
        # INI BAGIAN PENTING: Simpan pesan error ke variabel global
        DB_CONNECTION_ERROR = str(e)
        print(f"--- KONEKSI DATABASE GAGAL: {DB_CONNECTION_ERROR} ---")
        db = None

# --- Inisialisasi Aplikasi FastAPI ---
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
    """Endpoint root untuk mengecek status server dan detail error koneksi."""
    if db:
        return {"status": "OK", "message": "API server is running and connected to database."}
    else:
        # Tampilkan pesan error spesifik yang telah kita simpan
        return {
            "status": "ERROR",
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
