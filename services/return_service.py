from datetime import datetime
from database.db_manager import PengelolaDatabase

class LayananPengembalian:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def ambil_peminjaman_aktif(self):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("""
            SELECT l.id, l.loan_code, l.loan_date, l.status, u.name as nama_pj
            FROM loans l
            JOIN users u ON l.responsible_id = u.id
            WHERE l.status != 'Selesai'
            ORDER BY l.loan_date DESC
        """)
        daftar = kursor.fetchall()
        koneksi.close()
        return daftar

    def ambil_detail_sisa_barang(self, id_loan):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("""
            SELECT 
                ld.id as detail_id,
                ld.item_id,
                i.item_code,
                i.name as nama_barang,
                ld.quantity_borrowed,
                IFNULL(SUM(rd.quantity_returned), 0) as sudah_kembali
            FROM loan_details ld
            JOIN items i ON ld.item_id = i.id
            LEFT JOIN return_details rd ON ld.id = rd.loan_detail_id
            WHERE ld.loan_id = ?
            GROUP BY ld.id
        """, (id_loan,))

        hasil = []
        for baris in kursor.fetchall():
            sisa = baris["quantity_borrowed"] - baris["sudah_kembali"]
            hasil.append({
                "detail_id": baris["detail_id"],
                "item_id": baris["item_id"],
                "kode_barang": baris["item_code"],
                "nama_barang": baris["nama_barang"],
                "dipinjam": baris["quantity_borrowed"],
                "sudah_kembali": baris["sudah_kembali"],
                "sisa": sisa
            })

        koneksi.close()
        return hasil

    def proses_pengembalian(self, id_loan, id_pengembali, daftar_kembali, catatan=""):
        if not id_pengembali:
            raise ValueError("Pihak yang mengembalikan wajib dipilih!")
        if len(daftar_kembali) == 0:
            raise ValueError("Tidak ada barang yang dikembalikan!")

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        tanggal_kembali = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kursor.execute("""
            INSERT INTO returns (loan_id, returned_by_id, return_date, notes)
            VALUES (?, ?, ?, ?)
        """, (id_loan, id_pengembali, tanggal_kembali, catatan))

        id_return = kursor.lastrowid
        koneksi.commit()
        koneksi.close()
        return id_return