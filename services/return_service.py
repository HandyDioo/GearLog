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
            SELECT ld.id, ld.item_id, i.item_code, i.name, ld.quantity_borrowed
            FROM loan_details ld
            JOIN items i ON ld.item_id = i.id
            WHERE ld.loan_id = ?
        """, (id_loan,))
        daftar_pinjam = kursor.fetchall()

        hasil = []
        for baris in daftar_pinjam:
            #menghitung barang yang sudah dikembalikan untuk detail ini
            kursor.execute("""
                SELECT quantity_returned FROM return_details WHERE loan_detail_id = ?
            """, (baris["id"],))
            
            sudah_kembali = 0
            for r in kursor.fetchall():
                sudah_kembali = sudah_kembali + r["quantity_returned"]

            sisa = baris["quantity_borrowed"] - sudah_kembali
            hasil.append({
                "detail_id": baris["id"],
                "item_id": baris["item_id"],
                "kode_barang": baris["item_code"],
                "nama_barang": baris["name"],
                "dipinjam": baris["quantity_borrowed"],
                "sudah_kembali": sudah_kembali,
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
                INSERT INTO returns (loan_id, returner_id, return_date, notes)
                VALUES (?, ?, ?, ?)
            """, (id_loan, id_pengembali, tanggal_kembali, catatan))
            id_return = kursor.lastrowid

            for item in daftar_kembali:
                detail_id = item["detail_id"]
                jumlah = item["jumlah"]
                kondisi = item["kondisi"]

                if kondisi not in ["Baik", "Rusak", "Hilang"]:
                    raise ValueError("Kondisi barang tidak valid!")
                if jumlah <= 0:
                    raise ValueError("Jumlah kembali harus lebih dari 0!")

                info = map_sisa.get(detail_id)
                if info is None:
                    raise ValueError("Detail barang tidak ditemukan!")

                if jumlah > info["sisa"]:
                    raise ValueError("Jumlah kembali " + info["nama_barang"] + " melebihi sisa pinjaman!")

                kursor.execute("""
                    INSERT INTO return_details (return_id, loan_detail_id, quantity_returned, condition)
                    VALUES (?, ?, ?, ?)
                """, (id_return, detail_id, jumlah, kondisi))

                # hanya barang dgn kondisi Baik yang menambah stok tersedia
                if kondisi == "Baik":
                    kursor.execute("""
                        UPDATE items SET available_stock = available_stock + ? WHERE id = ?
                    """, (jumlah, info["item_id"]))

            kursor.execute("SELECT id, quantity_borrowed FROM loan_details WHERE loan_id = ?", (id_loan,))
            semua_detail = kursor.fetchall()

            total_pinjam = 0
            total_kembali = 0
            ada_hilang = False

            for det in semua_detail:
                total_pinjam = total_pinjam + det["quantity_borrowed"]
                kursor.execute("""
                    SELECT quantity_returned, condition
                    FROM return_details WHERE loan_detail_id = ?
                """, (det["id"],))

                for ret in kursor.fetchall():
                    total_kembali = total_kembali + ret["quantity_returned"]
                    if ret["condition"] == "Hilang":
                        ada_hilang = True

            if ada_hilang:
                status_baru = "Bermasalah (Hilang)"
            elif total_kembali >= total_pinjam:
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