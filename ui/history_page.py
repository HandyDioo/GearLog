import tkinter as tk
from tkinter import ttk, messagebox
from services.history_service import LayananRiwayat

class HalamanRiwayat(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan = LayananRiwayat()
        self.buat_tampilan()
        self.muat_data()

    def buat_tampilan(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Riwayat Peminjaman & Pengembalian", font=("Segoe UI", 14, "bold")).pack(side="left")

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Label(toolbar, text="Cari Kode / Nama:").pack(side="left", padx=(0, 5))
        self.var_cari = tk.StringVar()
        ent_cari = ttk.Entry(toolbar, textvariable=self.var_cari, width=25)
        ent_cari.pack(side="left", padx=(0, 10))
        ent_cari.bind("<KeyRelease>", lambda e: self.muat_data())

        ttk.Label(toolbar, text="Status:").pack(side="left", padx=(0, 5))
        self.cb_status = ttk.Combobox(
            toolbar,
            values=["Semua", "Dipinjam", "Sebagian Kembali", "Selesai", "Bermasalah (Hilang)"],
            state="readonly",
            width=20
        )
        self.cb_status.set("Semua")
        self.cb_status.pack(side="left")
        self.cb_status.bind("<<ComboboxSelected>>", lambda e: self.muat_data())

        ttk.Button(toolbar, text="Lihat Detail Transaksi", command=self.buka_detail).pack(side="right")

        kolom = ("id", "kode", "tanggal", "pj", "pengambil", "status", "catatan")
        self.tabel = ttk.Treeview(self, columns=kolom, show="headings", height=15)

        self.tabel.heading("id", text="ID")
        self.tabel.heading("kode", text="Kode Transaksi")
        self.tabel.heading("tanggal", text="Tanggal Pinjam")
        self.tabel.heading("pj", text="Penanggung Jawab")
        self.tabel.heading("pengambil", text="Pengambil")
        self.tabel.heading("status", text="Status")
        self.tabel.heading("catatan", text="Catatan")

        self.tabel.column("id", width=40, anchor="center")
        self.tabel.column("kode", width=120)
        self.tabel.column("tanggal", width=135)
        self.tabel.column("pj", width=140)
        self.tabel.column("pengambil", width=140)
        self.tabel.column("status", width=130, anchor="center")
        self.tabel.column("catatan", width=150)

        #warna baris berdasarkan status transaksi
        self.tabel.tag_configure("Selesai", background="#dcfce7")
        self.tabel.tag_configure("Bermasalah (Hilang)", background="#fee2e2")
        self.tabel.tag_configure("Sebagian Kembali", background="#fef9c3")

        self.tabel.pack(fill="both", expand=True)
        self.tabel.bind("<Double-1>", lambda e: self.buka_detail())

    def muat_data(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        kata = self.var_cari.get().strip()
        status = self.cb_status.get()
        daftar = self.layanan.ambil_semua_riwayat(kata, status)

        for r in daftar:
            self.tabel.insert("", "end", values=(
                r["id"], r["loan_code"], r["loan_date"],
                r["nama_pj"], r["nama_pengambil"],
                r["status"], r["notes"] or "-"
            ), tags=(r["status"],))

    def buka_detail(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih salah satu transaksi pada tabel!")
            return

        data = self.tabel.item(terpilih[0])["values"]
        id_loan = data[0]
        kode_trx = data[1]

        daftar_barang, daftar_kembali = self.layanan.ambil_rincian_transaksi(id_loan)

        dialog = tk.Toplevel(self)
        dialog.title("Detail Transaksi " + str(kode_trx))
        dialog.geometry("560x420")
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Kode Transaksi: " + str(kode_trx) + " (" + str(data[5]) + ")", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Daftar Barang Dipinjam:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tbl_pinjam = ttk.Treeview(frame, columns=("kode", "nama", "jumlah"), show="headings", height=5)
        tbl_pinjam.heading("kode", text="Kode")
        tbl_pinjam.heading("nama", text="Nama Barang")
        tbl_pinjam.heading("jumlah", text="Jumlah")
        tbl_pinjam.column("kode", width=100)
        tbl_pinjam.column("nama", width=280)
        tbl_pinjam.column("jumlah", width=80, anchor="center")
        tbl_pinjam.pack(fill="x", pady=(3, 12))

        for b in daftar_barang:
            tbl_pinjam.insert("", "end", values=(b["item_code"], b["name"], b["quantity_borrowed"]))

        ttk.Label(frame, text="Riwayat Pengembalian:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tbl_kembali = ttk.Treeview(frame, columns=("tgl", "oleh", "barang", "jml", "kondisi"), show="headings", height=5)
        tbl_kembali.heading("tgl", text="Waktu Kembali")
        tbl_kembali.heading("oleh", text="Dikembalikan Oleh")
        tbl_kembali.heading("barang", text="Barang")
        tbl_kembali.heading("jml", text="Jml")
        tbl_kembali.heading("kondisi", text="Kondisi")
        tbl_kembali.column("tgl", width=130)
        tbl_kembali.column("oleh", width=120)
        tbl_kembali.column("barang", width=140)
        tbl_kembali.column("jml", width=50, anchor="center")
        tbl_kembali.column("kondisi", width=70, anchor="center")
        tbl_kembali.pack(fill="x", pady=(3, 10))

        for k in daftar_kembali:
            tbl_kembali.insert("", "end", values=(
                k["return_date"], k["nama_pengembali"], k["nama_barang"],
                k["quantity_returned"], k["condition"]
            ))