from database.db_manager import PengelolaDatabase
from utils.code_generator import buat_kode_pengguna

class LayananPengguna:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def tambah_pengguna(self, nama, jenis, nis=None, nip=None, kelas=None):
        if not nama or nama.strip() == "":
            raise ValueError("Nama pengguna wajib diisi!")

        if jenis not in ["Student", "Teacher"]:
            raise ValueError("Jenis pengguna harus Student atau Teacher!")

        if jenis == "Student":
            if not nis or str(nis).strip() == "":
                raise ValueError("NIS wajib diisi untuk siswa!")
            if not kelas or kelas.strip() == "":
                raise ValueError("Kelas wajib diisi untuk siswa!")

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        if jenis == "Student":
            kursor.execute("SELECT id FROM users WHERE student_id = ?", (str(nis).strip(),))
            if kursor.fetchone():
                koneksi.close()
                raise ValueError("NIS sudah terdaftar pada pengguna lain!")

        kursor.execute("SELECT COUNT(*) as total FROM users")
        total = kursor.fetchone()["total"]
        kode_baru = buat_kode_pengguna(total)

        kursor.execute("""
            INSERT INTO users (user_code, name, user_type, student_id, employee_id, class_name)
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

    def cari_pengguna(self, kata_kunci):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        pola = f"%{kata_kunci}%"
        kursor.execute("""
            SELECT * FROM users 
            WHERE is_active = 1 AND (name LIKE ? OR user_code LIKE ?)
        """, (pola, pola))
        data = kursor.fetchall()
        koneksi.close()
        return data

    def edit_pengguna(self, id_pengguna, nama, jenis, nis=None, nip=None, kelas=None):
        if not nama or nama.strip() == "":
            raise ValueError("Nama pengguna wajib diisi!")

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        kursor.execute("""
            UPDATE users 
            SET name = ?, user_type = ?, student_id = ?, employee_id = ?, class_name = ?
            WHERE id = ?
        """, (nama.strip(), jenis, nis, nip, kelas, id_pengguna))

        koneksi.commit()
        koneksi.close()

    def arsip_pengguna(self, id_pengguna):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        kursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (id_pengguna,))
        koneksi.commit()
        koneksi.close()