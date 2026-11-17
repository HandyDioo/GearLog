from database.db_manager import PengelolaDatabase
from utils.code_generator import buat_kode_pengguna

class LayananPengguna:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def tambah_pengguna(self, nama, jenis, nis=None, nip=None, kelas=None):
        if not nama or nama.strip() == "":
            raise ValueError("Nama pengguna wajib diisi!")

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("SELECT COUNT(*) as total FROM users")
        total = kursor.fetchone()["total"]
        kode_baru = buat_kode_pengguna(total)

        kursor.execute("""
            INSERT INTO users (user_code, name, user_type, nis, employee_id, class_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (kode_baru, nama.strip(), jenis, nis, nip, kelas))

        koneksi.commit()
        koneksi.close()
        return kode_baru

    def ambil_semua_pengguna(self):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        kursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY name ASC")
        data = kursor.fetchall()
        koneksi.close()
        return data