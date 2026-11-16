from database.db_manager import PengelolaDatabase

def utama():
    print("Menjalankan aplikasi GearLog...")
    db = PengelolaDatabase()
    print("Database berhasil dimuat di:", db.lokasi_db)

if __name__ == "__main__":
    utama()