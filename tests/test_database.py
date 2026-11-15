import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import PengelolaDatabase

def cek_tabel_database():
    db_percobaan = "user_data/test_gearlog.db"
    db = PengelolaDatabase(lokasi_db=db_percobaan)
    
    koneksi = db.buat_koneksi()
    kursor = koneksi.cursor()
    kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    daftar_tabel = [baris["name"] for baris in kursor.fetchall()]
    koneksi.close()
    
    tabel_wajib = ["users", "items", "loans", "loan_details", "returns", "return_details"]
    
    print("Mengecek tabel database...")
    for tabel in tabel_wajib:
        if tabel in daftar_tabel:
            print(f"[OK] Tabel '{tabel}' berhasil dibuat.")
        else:
            print(f"[GAGAL] Tabel '{tabel}' tidak ditemukan!")
            
    if os.path.exists(db_percobaan):
        os.remove(db_percobaan)

if __name__ == "__main__":
    cek_tabel_database()