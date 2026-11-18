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

    def simpan_header_peminjaman(self, id_penanggung_jawab, id_pengambil, id_peminta=None, catatan=""):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kode_transaksi = self._buat_kode_unik(kursor)
        tanggal_pinjam = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        kursor.execute("""
            INSERT INTO loans (loan_code, responsible_id, requested_by_id, collected_by_id, loan_date, status, notes)
            VALUES (?, ?, ?, ?, ?, 'Dipinjam', ?)
        """, (kode_transaksi, id_penanggung_jawab, id_peminta, id_pengambil, tanggal_pinjam, catatan))

        id_loan = kursor.lastrowid
        koneksi.commit()
        koneksi.close()
        return id_loan, kode_transaksi