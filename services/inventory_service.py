from database.db_manager import PengelolaDatabase

class LayananInventaris:
    def __init__(self, db=None):
        self.db = db if db else PengelolaDatabase()

    def tambah_barang(self, kode_barang, nama, kategori, total_stok):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("SELECT id FROM items WHERE item_code = ?", (kode_barang.strip(),))
        if kursor.fetchone():
            koneksi.close()
            raise ValueError("Kode barang sudah terdaftar!")

        kursor.execute("""
            INSERT INTO items (item_code, name, category, total_stock, available_stock)
            VALUES (?, ?, ?, ?, ?)
        """, (kode_barang.strip(), nama.strip(), kategori.strip(), total_stok, total_stok))

        koneksi.commit()
        koneksi.close()

    def ambil_semua_barang(self):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        kursor.execute("SELECT * FROM items WHERE is_archived = 0 ORDER BY name ASC")
        data = kursor.fetchall()
        koneksi.close()
        return data

    def cari_barang(self, kata_kunci):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        pola = f"%{kata_kunci}%"
        kursor.execute("""
            SELECT * FROM items 
            WHERE is_archived = 0 AND (name LIKE ? OR item_code LIKE ?)
            ORDER BY name ASC
        """, (pola, pola))
        data = kursor.fetchall()
        koneksi.close()
        return data

    def edit_barang(self, id_barang, kode_barang, nama, kategori, total_stok, stok_tersedia):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()
        kursor.execute("""
            UPDATE items 
            SET item_code = ?, name = ?, category = ?, total_stock = ?, available_stock = ?
            WHERE id = ?
        """, (kode_barang.strip(), nama.strip(), kategori.strip(), total_stok, stok_tersedia, id_barang))
        koneksi.commit()
        koneksi.close()

    def arsip_barang(self, id_barang):
        koneksi = self.db.buat_koneksi()
        kursor = koneksi.cursor()

        kursor.execute("SELECT total_stock, available_stock FROM items WHERE id = ?", (id_barang,))
        barang = kursor.fetchone()
        if barang and barang["available_stock"] < barang["total_stock"]:
            koneksi.close()
            raise ValueError("Barang sedang dipinjam, tidak bisa diarsipkan!")

        kursor.execute("UPDATE items SET is_archived = 1 WHERE id = ?", (id_barang,))
        koneksi.commit()
        koneksi.close()