import tkinter as tk
from tkinter import ttk, messagebox
from services.return_service import LayananPengembalian
from services.user_service import LayananPengguna

class HalamanPengembalian(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan_kembali = LayananPengembalian()
        self.layanan_user = LayananPengguna()

        self.map_transaksi = {}
        self.map_pengguna = {}
        self.detail_aktif = []

        self.buat_tampilan()
        self.segarkan_pilihan()

    def buat_tampilan(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Pengembalian Peralatan Lab", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Segarkan Data", command=self.segarkan_pilihan).pack(side="right")

        # memilih transaksi dan orang yg mengembalikan
        form_atas = ttk.LabelFrame(self, text="Data Pengembalian", padding=10)
        form_atas.pack(fill="x", pady=(0, 10))

        ttk.Label(form_atas, text="Transaksi Aktif:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.cb_transaksi = ttk.Combobox(form_atas, state="readonly", width=45)
        self.cb_transaksi.grid(row=0, column=1, padx=5, pady=4)
        self.cb_transaksi.bind("<<ComboboxSelected>>", lambda e: self.muat_detail_transaksi())

        ttk.Label(form_atas, text="Dikembalikan Oleh:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.cb_pengembali = ttk.Combobox(form_atas, state="readonly", width=45)
        self.cb_pengembali.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form_atas, text="Catatan (Opsional):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.ent_catatan = ttk.Entry(form_atas, width=48)
        self.ent_catatan.grid(row=2, column=1, padx=5, pady=4)

        #tabel rincian barang yang dipinjam
        kolom = ("detail_id", "kode", "nama", "dipinjam", "kembali", "sisa")
        self.tabel = ttk.Treeview(self, columns=kolom, show="headings", height=7)
        self.tabel.heading("detail_id", text="ID")
        self.tabel.heading("kode", text="Kode")
        self.tabel.heading("nama", text="Nama Barang")
        self.tabel.heading("dipinjam", text="Dipinjam")
        self.tabel.heading("kembali", text="Sudah Kembali")
        self.tabel.heading("sisa", text="Sisa Pinjam")

        self.tabel.column("detail_id", width=40, anchor="center")
        self.tabel.column("kode", width=100)
        self.tabel.column("nama", width=220)
        self.tabel.column("dipinjam", width=80, anchor="center")
        self.tabel.column("kembali", width=100, anchor="center")
        self.tabel.column("sisa", width=90, anchor="center")
        self.tabel.pack(fill="both", expand=True, pady=(0, 10))

        #area input jumlah & kondisi brg terpilih
        form_bawah = ttk.LabelFrame(self, text="Proses Barang Terpilih di Tabel", padding=10)
        form_bawah.pack(fill="x")

        ttk.Label(form_bawah, text="Jumlah Kembali:").pack(side="left", padx=5)
        self.ent_jumlah = ttk.Entry(form_bawah, width=8)
        self.ent_jumlah.insert(0, "1")
        self.ent_jumlah.pack(side="left", padx=5)

        ttk.Label(form_bawah, text="Kondisi:").pack(side="left", padx=5)
        self.cb_kondisi = ttk.Combobox(form_bawah, values=["Baik", "Rusak", "Hilang"], state="readonly", width=12)
        self.cb_kondisi.set("Baik")
        self.cb_kondisi.pack(side="left", padx=5)

        ttk.Button(form_bawah, text="Simpan Pengembalian Barang Ini", command=self.simpan_pengembalian).pack(side="right", padx=5)

    def segarkan_pilihan(self):
        self.map_transaksi.clear()
        daftar_pinjam = self.layanan_kembali.ambil_peminjaman_aktif()
        opsi_pinjam = []
        for p in daftar_pinjam:
            label = p["loan_code"] + " - PJ: " + p["nama_pj"] + " (" + p["status"] + ")"
            self.map_transaksi[label] = p["id"]
            opsi_pinjam.append(label)

        self.cb_transaksi["values"] = opsi_pinjam
        if opsi_pinjam:
            self.cb_transaksi.set(opsi_pinjam[0])
            self.muat_detail_transaksi()
        else:
            self.cb_transaksi.set("")
            for item in self.tabel.get_children():
                self.tabel.delete(item)

        self.map_pengguna.clear()
        daftar_user = self.layanan_user.ambil_semua_pengguna()
        opsi_user = []
        for u in daftar_user:
            label = u["user_code"] + " - " + u["name"]
            self.map_pengguna[label] = u["id"]
            opsi_user.append(label)
        self.cb_pengembali["values"] = opsi_user

    def muat_detail_transaksi(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        label = self.cb_transaksi.get()
        if label == "" or label not in self.map_transaksi:
            return

        id_loan = self.map_transaksi[label]
        self.detail_aktif = self.layanan_kembali.ambil_detail_sisa_barang(id_loan)

        for d in self.detail_aktif:
            self.tabel.insert("", "end", values=(
                d["detail_id"], d["kode_barang"], d["nama_barang"],
                d["dipinjam"], d["sudah_kembali"], d["sisa"]
            ))

    def simpan_pengembalian(self):
        label_trx = self.cb_transaksi.get()
        label_user = self.cb_pengembali.get()
        terpilih = self.tabel.selection()

        if label_trx == "" or label_user == "":
            messagebox.showwarning("Peringatan", "Pilih transaksi dan pihak yang mengembalikan!")
            return

        if not terpilih:
            messagebox.showwarning("Peringatan", "Klik salah satu baris barang pada tabel di atas!")
            return

        data_baris = self.tabel.item(terpilih[0])["values"]
        detail_id = data_baris[0]
        sisa_pinjam = int(data_baris[5])

        if sisa_pinjam <= 0:
            messagebox.showinfo("Info", "Barang ini sudah dikembalikan seluruhnya.")
            return

        try:
            jumlah = int(self.ent_jumlah.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return

        daftar_kembali = [{
            "detail_id": detail_id,
            "jumlah": jumlah,
            "kondisi": self.cb_kondisi.get()
        }]

        try:
            self.layanan_kembali.proses_pengembalian(
                id_loan=self.map_transaksi[label_trx],
                id_pengembali=self.map_pengguna[label_user],
                daftar_kembali=daftar_kembali,
                catatan=self.ent_catatan.get().strip()
            )
            messagebox.showinfo("Berhasil", "Pengembalian berhasil dicatat!")
            self.ent_catatan.delete(0, "end")
            self.segarkan_pilihan()
        except ValueError as err:
            messagebox.showerror("Gagal", str(err))