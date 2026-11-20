from database.db_manager import PengelolaDatabase
from services.inventory_service import LayananInventaris
from services.user_service import LayananPengguna

def isi_data_awal():
    db = PengelolaDatabase()
    db.inisialisasi_db()

    layanan_barang = LayananInventaris(db)
    layanan_user = LayananPengguna(db)

    # mengisi contoh barang jika tabel items masih kosong
    if len(layanan_barang.ambil_semua_barang()) == 0:
        daftar_alat = [
            ("NET-001", "Kabel LAN UTP Cat6", "Jaringan", 50, "Unit"),
            ("NET-002", "Router MikroTik hAP lite", "Jaringan", 10, "Unit"),
            ("NET-003", "Switch Hub 8 Port", "Jaringan", 8, "Unit"),
            ("TLS-001", "Tang Crimping RJ45", "Perkakas", 15, "Unit"),
            ("TLS-002", "LAN Cable Tester", "Perkakas", 12, "Unit"),
            ("HRD-001", "Obeng Set Teknisi", "Perkakas", 10, "Set"),
        ]
        for kode, nama, kategori, stok, satuan in daftar_alat:
            layanan_barang.tambah_barang(kode, nama, kategori, stok, satuan)
        print("Data contoh barang berhasil ditambahkan.")
    else:
        print("Data barang sudah ada, melewati proses isi barang.")

    # mengisi contoh pengguna jika tabel users masih kosong
    if len(layanan_user.ambil_semua_pengguna()) == 0:
        daftar_pengguna = [
            ("Pak Budi Santoso", "Teacher", None, "198504122010011005", None),
            ("Bu Siti Aminah", "Teacher", None, "198809202014022002", None),
            ("Ahmad Rizky", "Student", "24101", None, "XI TKJ 1"),
            ("Nadia Putri", "Student", "24102", None, "XI TKJ 1"),
            ("Dimas Pratama", "Student", "24103", None, "XI TKJ 2"),
        ]
        for nama, jenis, nis, nip, kelas in daftar_pengguna:
            layanan_user.tambah_pengguna(nama, jenis, nis, nip, kelas)
        print("Data contoh pengguna berhasil ditambahkan.")
    else:
        print("Data pengguna sudah ada, melewati proses isi pengguna.")

if __name__ == "__main__":
    isi_data_awal()