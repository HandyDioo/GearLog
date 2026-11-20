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

        detail_sekarang = self.ambil_detail_sisa_barang(id_loan)
        map_sisa = {}
        for d in detail_sekarang:
            map_sisa[d["detail_id"]] = d

        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        try:
            tanggal_kembali = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            kursor.execute("""
                INSERT INTO returns (loan_id, returned_by_id, return_date, notes)
                VALUES (?, ?, ?, ?)
            """, (id_loan, id_pengembali, tanggal_kembali, catatan))
            id_return = kursor.lastrowid

            for item in daftar_kembali:
                detail_id = item["detail_id"]
                jumlah = item["jumlah"]
                kondisi = item.get("kondisi", "Baik")

                if jumlah <= 0:
                    raise ValueError("Jumlah kembali harus lebih dari 0!")

                info = map_sisa.get(detail_id)
                if info is None:
                    raise ValueError("Detail barang tidak ditemukan!")

                if jumlah > info["sisa"]:
                    raise ValueError("Jumlah kembali " + info["nama_barang"] + " melebihi sisa pinjaman!")

                kursor.execute("""
                    INSERT INTO return_details (return_id, loan_detail_id, quantity_returned, condition_status)
                    VALUES (?, ?, ?, ?)
                """, (id_return, detail_id, jumlah, kondisi))

            #mengecek apakah semua barang dalam transaksi ini sdh kembali
            kursor.execute("""
                SELECT 
                    SUM(ld.quantity_borrowed) as total_pinjam,
                    IFNULL((
                        SELECT SUM(rd.quantity_returned)
                        FROM return_details rd
                        JOIN returns r ON rd.return_id = r.id
                        WHERE r.loan_id = ?
                    ), 0) as total_kembali
                FROM loan_details ld
                WHERE ld.loan_id = ?
            """, (id_loan, id_loan))
            rekap = kursor.fetchone()

            if rekap["total_kembali"] >= rekap["total_pinjam"]:
                status_baru = "Selesai"
            else:
                status_baru = "Sebagian Kembali"

            kursor.execute("UPDATE loans SET status = ? WHERE id = ?", (status_baru, id_loan))

            koneksi.commit()
            koneksi.close()
        except Exception as err:
            koneksi.rollback()
            koneksi.close()
            raise err