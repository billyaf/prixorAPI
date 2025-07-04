# main.py (Versi Final dengan Base64)

import os
import json
import base64 # <-- Tambahkan import ini
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel

# Variabel Global untuk Database
db = None

# Fungsi Startup Event
async def initialize_database():
    """Menginisialisasi koneksi ke Firebase Firestore dari kunci Base64."""
    global db
    try:
        # Ambil kunci yang sudah di-encode Base64 dari Environment Variable
        base64_encoded_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64')
        
        if not base64_encoded_key:
            raise ValueError("Kunci Base64 Firebase tidak ditemukan di environment variables.")
        
        # Decode Base64 kembali menjadi string JSON
        decoded_key_str = base64.b64decode(base64_encoded_key).decode('utf-8')
        
        # Ubah string JSON menjadi dictionary Python
        service_account_info = json.loads(decoded_key_str)
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("--- KONEKSI DATABASE BASE64 BERHASIL SAAT STARTUP ---")

    except Exception as e:
        print(f"--- KONEKSI DATABASE BASE64 GAGAL SAAT STARTUP: {e} ---")
        db = None

# Inisialisasi Aplikasi FastAPI
app = FastAPI(
    title="API Deteksi Harga Produk",
    on_startup=[initialize_database]
)

# Model Data Pydantic
class Product(BaseModel):
    name: str
    price: int
    description: str
    product_id: str

# API Endpoints
@app.get("/")
def read_root():
    if db:
        return {"status": "OK", "message": "API server is running and connected to database."}
    else:
        return {"status": "ERROR", "message": "API server is running, but database connection FAILED."}

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
