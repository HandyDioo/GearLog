import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import PengelolaDatabase
from services.user_service import LayananPengguna

def uji_layanan_pengguna():
    db_tes = "user_data/test_users.db"
    db = PengelolaDatabase(lokasi_db=db_tes)
    layanan = LayananPengguna(db)

    #add siswa dan guru
    kode1 = layanan.tambah_pengguna("Andi Saputra", "Student", nis="12345", kelas="XI TKJ 1")
    kode2 = layanan.tambah_pengguna("Pak Ahmad", "Teacher", nip="19800101")
    print("Berhasil tambah:", kode1, "dan", kode2)

    #test validasi nis kembar
    try:
        layanan.tambah_pengguna("Budi", "Student", nis="12345", kelas="XI TKJ 2")
    except ValueError as e:
        print("[OK] Validasi NIS kembar berjalan:", e)

    #test edit pengguna
    semua = layanan.ambil_semua_pengguna()
    id_andi = semua[0]["id"]
    layanan.edit_pengguna(id_andi, "Andi Saputra Pratama", "Student", nis="12345", kelas="XI TKJ 2")
    print("[OK] Berhasil edit data pengguna.")

    #test arsip pengguna
    layanan.arsip_pengguna(id_andi)
    sisa = layanan.ambil_semua_pengguna()
    print("[OK] Sisa pengguna aktif setelah diarsip:", len(sisa))

    if os.path.exists(db_tes):
        os.remove(db_tes)

if __name__ == "__main__":
    uji_layanan_pengguna()