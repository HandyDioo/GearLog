import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import PengelolaDatabase
from services.user_service import LayananPengguna

def uji_layanan_pengguna():
    db_tes = "user_data/test_users.db"
    db = PengelolaDatabase(lokasi_db=db_tes)
    layanan = LayananPengguna(db)

    kode1 = layanan.tambah_pengguna("Andi Saputra", "Student", nis="12345", kelas="XI TKJ 1")
    kode2 = layanan.tambah_pengguna("Pak Ahmad", "Teacher", nip="19800101")

    print("Kode siswa:", kode1)
    print("Kode guru:", kode2)

    hasil_cari = layanan.cari_pengguna("Andi")
    print("Hasil pencarian 'Andi':", len(hasil_cari), "data ditemukan.")

    if os.path.exists(db_tes):
        os.remove(db_tes)

if __name__ == "__main__":
    uji_layanan_pengguna()