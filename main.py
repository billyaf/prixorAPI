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
        if not HARDCODED_BASE64_KEY or HARDCODED_BASE64_KEY == "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicHJpeG9yYXBwIiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiZTczMTVjNGM2MzQ5MzQxMzczOWU1YmMyZDJjZTI3NGJhMjcyZGY4NyIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZBSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS1l3Z2dTaUFnRUFBb0lCQVFEVVl4MEZxeThHSDNrYVxuakJoVmxOcFQ5bllGVElTU3hYUXl3eW9UTVFXdyswRkY2NW4zejIyRmowVnhYY0RnNTliWnJTYXBOYlptR1Z5Y1xuWUhvTTF5L1Q5UDVsV2NmdjM1djdnTTUrRm9FMHlkTlV0WmJvcnI0VCtKdUx0SHJjaC9pb1EvSk42OWNUb1hUaFxuU2hMamw3QlVkMjJUSnQ5TWdrdFlsUnJjMjZVcFpFWnY1MW1GV1Y4a2tlQlh1cjRKMUMyK3B5WmVaRExQWW1JZlxuQnJFSDBrME93RGxUQXVLanhFV0kwMjZtN1ZvcWFaNERpTThrc3NQblpGRS9rQ05VNHNoU2FYdHNWV1VkRDk0VlxuZjFvd2c0SnI0T1VpQXgzb2tDekdvREZIbDlrZEJtUnZHUFlHZU9OSmUyeFQ2MVJZWE94bDlIQzZ5ZzhSY2dma1xuZExMaUtiU3ZBZ01CQUFFQ2dnRUFXR1dzTmFqTEdLUk8xbUxLMmd2clZ4ajBoRDRWeTdUTktUZWJzb01yMkQ2clxuS3p2bFNJUVlGSWZPSW1JZ0hqdkFhN2NxcVRERzZ2WFJXdkM0dTlGd2dhcXRtMmRqMVEzZnNTMHFSTVovSG9hR1xuSS9LMGpjSDFNUUMvVk1WWWdhTkNObDZaWWg4djFHYlY2OUxWeTg1ZHdMbzRiQSs0enZKSUErV0RXYnM5b2R6c1xudW9jd3c0Wi9uQkJRZUVhYUVQbTFUeVJkdWdmU0hhZ2lBd2k3M0tDYUdXN0UwSnZJT0FyM0o3N1V0ek5IblRyV1xuQkp5aHRkQTBqM3VKTGhnWGhSaXVmRG9OZ2FQTEE0OGNONWdjMTMzcjMvVU1zV1BkY3dJL3ZGT3o3ekpiWFlkZ1xubWpwL3JoS2RtWDlucFdSbTU2WG8yWEMxUWY5Vyt4OU5FVzlUeTlVR3dRS0JnUUQ5MnNwK05wUUFGanFuZlZ2c1xuK21ENS9GY21aQkl2WmZHZk5JWDVORHhxL3FjN2J1WVUyWlRRenVXTFIrM1Jzc3crMWJUM0pkRUFMZjN3S0FXd1xuZ1ZpSllTVXNRSURSWjhsbFJBcGhZVTVBQVl2VC8zN2p1R3FBUlRnZEUwNFBUSlhvUys5T21JVzZ6akpseFdLUFxuMDhQTmMvWWF3aEJhb0RaQyt1blRDdmcrendLQmdRRFdMcHU5NWF4UHd5Tko3YlFGaVhXdFhVc1ZVMDQvblFtM1xuRFRQSGVrV0hrZ3ZacEZNNjhQYVpQTWNkRkpMWVNKYzJlS0Y5TjhRd000VHBsLzVTWVVPVVN0TWdWU1FsM3E1OVxuZkVPdnA4K3Jya3p6dDYzNVltMHVtMmlvaWNqZU5aWUlxbVNmUCtjOTlDOXdzaVFuMG44N1dkcXZMajVhL05oU1xuWlliTzlJT2tJUUtCZ0ZBV2FyUU8rL3BiQ1A0MmFuNEZML3N1UlVCemFkbFNURHh5RWFKaGZINDFBUVdiSXpPSVxud1k1dTk3Uk5hUll6Vm9Tc1gzOXBpdHFIcUFuUVZwc3M4NFhFQkRwRnoxNUJaQ1J5cHVPNkV6bldRd3NMSERrelxud1VYZWtLbDdvYkRwOUpGcEE0TEVVOHh2cVM2NmF6SDlHVlVFTkt5VWRSeGlWendpZFFxRDkzVzVBb0dBWkQxTVxuQm9RSE1RMVM1cmFwR2k1TE5PZ0V5K1pCS09TR04zV21WaVdUaE8rRlBFYjc3UW41WDU1aVVlbmZEL3BwU3NVS1xuVDJCYUlYVDdMNWhESHFzR3hkQi9IeEs1NkQ5ZnlycnRzcmdIS1lKWjRYYUZwY0c2OTZVa1JqeTJGY2xlZm8vQVxucUFkd1lqNTJOWGdxRTdrZ2N0YUswcElCL1BONUNwY1prS0kvT2dFQ2dZQXdHV2lkQXBwY1JkME1BQUY4Skt1MFxucGZwczBhRTVvZDh5WnlkVXZ2SmdET2lEUXNET2ZBMEM5RFRPeFpTM092Tmd6ZDgya0VZQW41RUU1UVpSWEFuZFxuREJ4ZkpINDFSQ1RJMXR6ZjVQVUk1Q0RqZWtneG9MSTB5K3poS1czTnNYekdRN1UzbEFZWnZ0a1J1V2V5MS8vclxuT0djU20zSlJIT2VweTBSWDgxRzRlUT09XG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAiZmlyZWJhc2UtYWRtaW5zZGstZmJzdmNAcHJpeG9yYXBwLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjExMzQ0NTg5MjYzNzU4NTgxMDk2MCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvZmlyZWJhc2UtYWRtaW5zZGstZmJzdmMlNDBwcml4b3JhcHAuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K":
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

