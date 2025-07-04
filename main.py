# main.py
from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from pydantic import BaseModel

# ...
try:
    # Ambil konten JSON dari environment variable Vercel
    service_account_info_str = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
    
    if service_account_info_str:
        # Ubah string JSON menjadi dictionary Python
        service_account_info = json.loads(service_account_info_str)
        
        # Inisialisasi Firebase menggunakan dictionary tersebut
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Koneksi ke Firebase Firestore berhasil dari Environment Variable.")
    else:
        # Fallback untuk development lokal (jika file ada)
        print("Mencoba koneksi lokal menggunakan serviceAccountKey.json...")
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Koneksi ke Firebase Firestore berhasil dari file lokal.")

except Exception as e:
    print(f"Gagal terhubung ke Firebase: {e}")
    db = None

# --- Model Data (Pydantic) ---
# Ini mendefinisikan struktur data yang akan dikembalikan oleh API.
# FastAPI akan menggunakannya untuk validasi dan dokumentasi otomatis.
class Product(BaseModel):
    name: str
    price: int
    description: str
    product_id: str

# --- Endpoint Utama API ---
# Ini adalah "jantung" dari API Anda.
@app.get("/api/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    """
    Mengambil detail produk dari Firestore berdasarkan product_id.
    Contoh ID: MIE_INDOMIE_GORENG
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Layanan database tidak tersedia.")

    try:
        # Mengambil dokumen dari koleksi 'products'
        product_ref = db.collection('products').document(product_id)
        doc = product_ref.get()

        if doc.exists:
            # Jika dokumen ditemukan, kembalikan datanya.
            # FastAPI akan otomatis mengubahnya menjadi JSON.
            return doc.to_dict()
        else:
            # Jika tidak ditemukan, kirim error 404 Not Found.
            raise HTTPException(status_code=404, detail=f"Produk dengan ID '{product_id}' tidak ditemukan.")
    except Exception as e:
        # Menangani error tak terduga lainnya
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {e}")

# Endpoint root sederhana untuk memastikan server berjalan
@app.get("/")
def read_root():
    return {"status": "API server is running!"}
