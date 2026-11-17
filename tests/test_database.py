import os
import sys
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import PengelolaDatabase

def cek_tabel_database():
    db_percobaan = "user_data/test_gearlog.db"
    db = PengelolaDatabase(lokasi_db=db_percobaan)
    
    koneksi = db.buat_koneksi()
    kursor = koneksi.cursor()
    kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    daftar_tabel = [baris["name"] for baris in kursor.fetchall()]
    
    tabel_wajib = ["users", "items", "loans", "loan_details", "returns", "return_details"]
    
    print("Mengecek tabel database...")
    for tabel in tabel_wajib:
        if tabel in daftar_tabel:
            print(f"[OK] Tabel '{tabel}' berhasil dibuat.")
        else:
            print(f"[GAGAL] Tabel '{tabel}' tidak ditemukan!")

    # Uji simpan dan baca data
    kursor.execute("""
        INSERT INTO items (item_code, name, category, total_stock, available_stock)
        VALUES ('NET-001', 'Kabel LAN', 'Jaringan', 50, 50)
    """)
    koneksi.commit()

    kursor.execute("SELECT * FROM items WHERE item_code = 'NET-001'")
    barang = kursor.fetchone()
    if barang:
        print(f"[OK] Simpan & baca data berhasil: {barang['name']} (Stok: {barang['total_stock']})")

    koneksi.close()
    if os.path.exists(db_percobaan):
        os.remove(db_percobaan)

if __name__ == "__main__":
    cek_tabel_database()