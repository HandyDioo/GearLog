import tkinter as tk
from tkinter import ttk
from ui.inventory_page import HalamanBarang
from ui.users_page import HalamanPengguna
from ui.borrowing_page import HalamanPeminjaman
from ui.returns_page import HalamanPengembalian
from ui.history_page import HalamanRiwayat
from ui.dashboard_page import HalamanDashboard

class JendelaUtama:
    def __init__(self, root):
        self.root = root
        self.root.title("GearLog - Inventaris & Peminjaman Lab TKJ")
        self.root.geometry("950x600")
        self.root.minsize(850, 520)

        self.halaman_aktif = None
        self.daftar_halaman = {}

        self._bangun_kerangka()

    def _bangun_kerangka(self):
        sidebar = tk.Frame(self.root, bg="#1e293b", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        judul = tk.Label(
            sidebar, text="GearLog TKJ", bg="#1e293b", fg="white",
            font=("Segoe UI", 16, "bold"), pady=20
        )
        judul.pack(fill="x")

        self.area_konten = ttk.Frame(self.root, padding=15)
        self.area_konten.pack(side="right", fill="both", expand=True)

        menu_navigasi = [
            ("Dashboard", "dashboard"),
            ("Data Barang", "barang"),
            ("Data Pengguna", "pengguna"),
            ("Peminjaman", "peminjaman"),
            ("Pengembalian", "pengembalian"),
            ("Riwayat", "riwayat"),
        ]

        for teks, kunci in menu_navigasi:
            btn = tk.Button(
                sidebar, text=teks, bg="#1e293b", fg="white",
                activebackground="#334155", activeforeground="white",
                bd=0, anchor="w", padx=20, pady=12, font=("Segoe UI", 10),
                command=lambda k=kunci: self.tampilkan_halaman(k)
            )
            btn.pack(fill="x")

        for _, kunci in menu_navigasi:
            frame = ttk.Frame(self.area_konten)
            lbl = ttk.Label(frame, text=f"Halaman {kunci.capitalize()}", font=("Segoe UI", 14, "bold"))
            lbl.pack(pady=20)
            self.daftar_halaman[kunci] = frame

        self.daftarkan_halaman("barang", HalamanBarang(self.area_konten))
        self.daftarkan_halaman("pengguna", HalamanPengguna(self.area_konten))
        self.daftarkan_halaman("peminjaman", HalamanPeminjaman(self.area_konten))
        self.daftarkan_halaman("pengembalian", HalamanPengembalian(self.area_konten))
        self.daftarkan_halaman("riwayat", HalamanRiwayat(self.area_konten))
        self.daftarkan_halaman("dashboard", HalamanDashboard(self.area_konten))
        self.tampilkan_halaman("dashboard")

    def daftarkan_halaman(self, kunci, frame_halaman):
        self.daftar_halaman[kunci] = frame_halaman

    def tampilkan_halaman(self, kunci):
        if self.halaman_aktif:
            self.halaman_aktif.pack_forget()

        halaman = self.daftar_halaman.get(kunci)
        if halaman:
            if hasattr(halaman, "muat_data"):
                halaman.muat_data()
            if hasattr(halaman, "segarkan_pilihan"):
                halaman.segarkan_pilihan()
            halaman.pack(fill="both", expand=True)
            self.halaman_aktif = halaman