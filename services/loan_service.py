from datetime import datetime
from database.db_manager import PengelolaDatabase
from utils.code_generator import buat_kode_peminjaman

class LayananPeminjaman:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def _buat_kode_unik(self, kursor):
        tahun = datetime.now().year
        pola = f"LN-{tahun}-%"
        kursor.execute("SELECT COUNT(*) as total FROM loans WHERE loan_code LIKE ?", (pola,))
        total = kursor.fetchone()["total"]

        kode = buat_kode_peminjaman(total)
        while True:
            kursor.execute("SELECT id FROM loans WHERE loan_code = ?", (kode,))
            if not kursor.fetchone():
                return kode
            total += 1
            kode = buat_kode_peminjaman(total)

    def buat_peminjaman(self, id_penanggung_jawab, id_pengambil, daftar_barang, id_peminta=None, catatan=""):
        if not daftar_barang:
            raise ValueError("Daftar barang yang dipinjam tidak boleh kosong!")

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kode_transaksi = self._buat_kode_unik(kursor)
        tanggal_pinjam = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        kursor.execute("""
            INSERT INTO loans (loan_code, responsible_id, requested_by_id, collected_by_id, loan_date, status, notes)
            VALUES (?, ?, ?, ?, ?, 'Dipinjam', ?)
        """, (kode_transaksi, id_penanggung_jawab, id_peminta, id_pengambil, tanggal_pinjam, catatan))
        id_loan = kursor.lastrowid

        for item in daftar_barang:
            id_barang = item["item_id"]
            jumlah = item["jumlah"]

            if jumlah <= 0:
                koneksi.close()
                raise ValueError("Jumlah barang yang dipinjam harus lebih dari 0!")

            kursor.execute("SELECT name, is_archived FROM items WHERE id = ?", (id_barang,))
            barang = kursor.fetchone()
            if not barang or barang["is_archived"] == 1:
                koneksi.close()
                raise ValueError("Barang tidak ditemukan atau sudah diarsipkan!")

            kursor.execute("""
                INSERT INTO loan_details (loan_id, item_id, quantity_borrowed)
                VALUES (?, ?, ?)
            """, (id_loan, id_barang, jumlah))

        koneksi.commit()
        koneksi.close()
        return kode_transaksi