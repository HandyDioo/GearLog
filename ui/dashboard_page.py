import tkinter as tk
from tkinter import ttk
from services.history_service import LayananRiwayat

class HalamanDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan = LayananRiwayat()
        self.label_angka = {}
        self.buat_tampilan()
        self.muat_data()

    def buat_tampilan(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))
        ttk.Label(header, text="Dashboard Ringkasan Lab TKJ", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Refresh", command=self.muat_data).pack(side="right")

        wadah_kartu = ttk.Frame(self)
        wadah_kartu.pack(fill="x", pady=(0, 15))

        daftar_kartu = [
            ("jenis_barang", "Jenis Alat Aktif", "#2563eb"),
            ("stok_tersedia", "Total Unit Tersedia", "#16a34a"),
            ("sedang_dipinjam", "Transaksi Sedang Dipinjam", "#d97706"),
            ("bermasalah", "Transaksi Bermasalah", "#dc2626"),
        ]

        for idx, (kunci, judul, warna) in enumerate(daftar_kartu):
            kartu = tk.Frame(wadah_kartu, bg=warna, padx=15, pady=15)
            kartu.grid(row=0, column=idx, padx=6, sticky="nsew")
            wadah_kartu.columnconfigure(idx, weight=1)

            lbl_judul = tk.Label(kartu, text=judul, bg=warna, fg="white", font=("Segoe UI", 9))
            lbl_judul.pack(anchor="w")

            lbl_nilai = tk.Label(kartu, text="0", bg=warna, fg="white", font=("Segoe UI", 20, "bold"))
            lbl_nilai.pack(anchor="w", pady=(5, 0))
            self.label_angka[kunci] = lbl_nilai

        info_lab = ttk.Label(
            self,
            text="Catatan Lab: Alat yang dikembalikan dalam kondisi Rusak atau Hilang tidak otomatis menambah stok tersedia.",
            foreground="#475569"
        )
        info_lab.pack(anchor="w", pady=(0, 10))

        # Daftar transaksi yang masih dipinjam saat ini
        kotak_aktif = ttk.LabelFrame(self, text="Transaksi Peminjaman Terbaru", padding=10)
        kotak_aktif.pack(fill="both", expand=True)

        kolom = ("kode", "tanggal", "pj", "status")
        self.tabel = ttk.Treeview(kotak_aktif, columns=kolom, show="headings", height=10)
        self.tabel.heading("kode", text="Kode Transaksi")
        self.tabel.heading("tanggal", text="Tanggal Pinjam")
        self.tabel.heading("pj", text="Penanggung Jawab")
        self.tabel.heading("status", text="Status")

        self.tabel.column("kode", width=130)
        self.tabel.column("tanggal", width=150)
        self.tabel.column("pj", width=200)
        self.tabel.column("status", width=140, anchor="center")
        self.tabel.pack(fill="both", expand=True)

    def muat_data(self):
        ringkasan = self.layanan.ambil_ringkasan_dashboard()
        for kunci, lbl in self.label_angka.items():
            lbl.config(text=str(ringkasan[kunci]))

        for item in self.tabel.get_children():
            self.tabel.delete(item)

        daftar = self.layanan.ambil_semua_riwayat()
        for r in daftar[:10]:
            self.tabel.insert("", "end", values=(
                r["loan_code"], r["loan_date"], r["nama_pj"], r["status"]
            ))