import os
import sqlite3

class PengelolaDatabase:
    def __init__(self, lokasi_db="user_data/gearlog.db"):
        self.lokasi_db = lokasi_db
        folder = os.path.dirname(self.lokasi_db)
        if folder != "" and not os.path.exists(folder):
            os.makedirs(folder)

    def buat_koneksi(self):
        koneksi = sqlite3.connect(self.lokasi_db)
        koneksi.execute("PRAGMA foreign_keys = ON;")
        return koneksi

    def inisialisasi_db(self):
        folder_sekarang = os.path.dirname(__file__)
        lokasi_skema = os.path.join(folder_sekarang, "schema.sql")
        
        with open(lokasi_skema, "r", encoding="utf-8") as file:
            skrip_sql = file.read()
            
        koneksi = self.buat_koneksi()
        koneksi.executescript(skrip_sql)
        koneksi.commit()
        koneksi.close()