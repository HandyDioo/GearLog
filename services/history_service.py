from database.db_manager import PengelolaDatabase

class LayananRiwayat:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def ambil_semua_riwayat(self, kata_kunci="", filter_status="Semua"):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        query = """
            SELECT 
                l.id, l.loan_code, l.loan_date, l.status, l.notes,
                u_pj.name as nama_pj,
                u_ambil.name as nama_pengambil
            FROM loans l
            JOIN users u_pj ON l.responsible_id = u_pj.id
            JOIN users u_ambil ON l.collected_by_id = u_ambil.id
            WHERE 1=1
        """
        parameter = []

        if kata_kunci != "":
            query += " AND (l.loan_code LIKE ? OR u_pj.name LIKE ? OR u_ambil.name LIKE ?)"
            pola = "%" + kata_kunci + "%"
            parameter.extend([pola, pola, pola])

        if filter_status != "Semua":
            query += " AND l.status = ?"
            parameter.append(filter_status)

        query += " ORDER BY l.loan_date DESC"

        kursor.execute(query, parameter)
        daftar = kursor.fetchall()
        koneksi.close()
        return daftar

    def ambil_rincian_transaksi(self, id_loan):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        #mengambil daftar barang yang dipinjam
        kursor.execute("""
            SELECT i.item_code, i.name, ld.quantity_borrowed
            FROM loan_details ld
            JOIN items i ON ld.item_id = i.id
            WHERE ld.loan_id = ?
        """, (id_loan,))
        daftar_barang = kursor.fetchall()

        #mengambil catatan waktu & kondisi pengembalian
        kursor.execute("""
            SELECT r.return_date, u.name as nama_pengembali, i.name as nama_barang, rd.quantity_returned, rd.condition
            FROM returns r
            JOIN users u ON r.returner_id = u.id
            JOIN return_details rd ON r.id = rd.return_id
            JOIN loan_details ld ON rd.loan_detail_id = ld.id
            JOIN items i ON ld.item_id = i.id
            WHERE r.loan_id = ?
            ORDER BY r.return_date ASC
        """, (id_loan,))
        daftar_kembali = kursor.fetchall()

        koneksi.close()
        return daftar_barang, daftar_kembali

    def ambil_ringkasan_dashboard(self):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("SELECT COUNT(*) as total, IFNULL(SUM(available_stock), 0) as stok FROM items WHERE is_archived = 0")
        data_barang = kursor.fetchone()

        kursor.execute("SELECT COUNT(*) as total FROM loans WHERE status IN ('Dipinjam', 'Sebagian Kembali')")
        sedang_dipinjam = kursor.fetchone()["total"]

        kursor.execute("SELECT COUNT(*) as total FROM loans WHERE status = 'Bermasalah (Hilang)'")
        bermasalah = kursor.fetchone()["total"]

        kursor.execute("SELECT COUNT(*) as total FROM users")
        total_pengguna = kursor.fetchone()["total"]

        koneksi.close()
        return {
            "jenis_barang": data_barang["total"],
            "stok_tersedia": data_barang["stok"],
            "sedang_dipinjam": sedang_dipinjam,
            "bermasalah": bermasalah,
            "total_pengguna": total_pengguna
        }