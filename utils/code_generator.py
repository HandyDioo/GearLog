from datetime import datetime

def buat_kode_pengguna(jumlah_sebelumnya):
    nomor_urut = jumlah_sebelumnya + 1
    return f"USR-{nomor_urut:04d}"

def buat_kode_peminjaman(nomor_terakhir):
    tahun = datetime.now().year
    nomor_urut = nomor_terakhir + 1
    return f"LN-{tahun}-{nomor_urut:04d}"