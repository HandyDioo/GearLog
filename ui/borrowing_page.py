import tkinter as tk
from tkinter import ttk, messagebox
from services.user_service import LayananPengguna
from services.inventory_service import LayananInventaris
from services.loan_service import LayananPeminjaman

class HalamanPeminjaman(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan_user = LayananPengguna()
        self.layanan_barang = LayananInventaris()
        self.layanan_pinjam = LayananPeminjaman()

        self.map_pengguna = {}
        self.map_barang = {}
        self.keranjang = []

        self.buat_tampilan()
        self.segarkan_pilihan()

    def buat_tampilan(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Transaksi Peminjaman Alat", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Segarkan Data", command=self.segarkan_pilihan).pack(side="right")

        form_user = ttk.LabelFrame(self, text="Identitas Peminjam", padding=10)
        form_user.pack(fill="x", pady=(0, 10))

        ttk.Label(form_user, text="Penanggung Jawab:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.cb_pj = ttk.Combobox(form_user, state="readonly", width=35)
        self.cb_pj.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form_user, text="Pengambil Barang:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.cb_pengambil = ttk.Combobox(form_user, state="readonly", width=35)
        self.cb_pengambil.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form_user, text="Catatan (Opsional):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.ent_catatan = ttk.Entry(form_user, width=38)
        self.ent_catatan.grid(row=2, column=1, padx=5, pady=4)

        form_barang = ttk.LabelFrame(self, text="Pilih Barang", padding=10)
        form_barang.pack(fill="x", pady=(0, 10))

        ttk.Label(form_barang, text="Alat / Barang:").pack(side="left", padx=5)
        self.cb_barang = ttk.Combobox(form_barang, state="readonly", width=35)
        self.cb_barang.pack(side="left", padx=5)

        ttk.Label(form_barang, text="Jumlah:").pack(side="left", padx=5)
        self.ent_jumlah = ttk.Entry(form_barang, width=8)
        self.ent_jumlah.insert(0, "1")
        self.ent_jumlah.pack(side="left", padx=5)

        ttk.Button(form_barang, text="+ Tambah ke Daftar", command=self.tambah_ke_keranjang).pack(side="left", padx=5)
        ttk.Button(form_barang, text="Hapus Baris", command=self.hapus_dari_keranjang).pack(side="left", padx=5)

        kolom = ("kode", "nama", "jumlah")
        self.tabel = ttk.Treeview(self, columns=kolom, show="headings", height=8)
        self.tabel.heading("kode", text="Kode Barang")
        self.tabel.heading("nama", text="Nama Barang")
        self.tabel.heading("jumlah", text="Jumlah Pinjam")

        self.tabel.column("kode", width=120)
        self.tabel.column("nama", width=300)
        self.tabel.column("jumlah", width=120, anchor="center")
        self.tabel.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Button(self, text="Simpan Transaksi Peminjaman", command=self.simpan_transaksi).pack(anchor="e")

    def segarkan_pilihan(self):
        self.map_pengguna.clear()
        daftar_user = self.layanan_user.ambil_semua_pengguna()
        opsi_user = []
        for u in daftar_user:
            label = u["user_code"] + " - " + u["name"] + " (" + u["user_type"] + ")"
            self.map_pengguna[label] = u["id"]
            opsi_user.append(label)

        self.cb_pj["values"] = opsi_user
        self.cb_pengambil["values"] = opsi_user

        self.map_barang.clear()
        daftar_barang = self.layanan_barang.ambil_semua_barang()
        opsi_barang = []
        for b in daftar_barang:
            label = b["item_code"] + " - " + b["name"] + " (Stok: " + str(b["available_stock"]) + ")"
            self.map_barang[label] = b
            opsi_barang.append(label)

        self.cb_barang["values"] = opsi_barang

    def tambah_ke_keranjang(self):
        label_barang = self.cb_barang.get()
        if label_barang == "":
            messagebox.showwarning("Peringatan", "Pilih barang terlebih dahulu!")
            return

        try:
            jumlah = int(self.ent_jumlah.get())
            if jumlah <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka lebih dari 0!")
            return

        barang = self.map_barang[label_barang]
        if jumlah > barang["available_stock"]:
            messagebox.showerror("Stok Kurang", "Stok tersedia hanya " + str(barang["available_stock"]) + "!")
            return

        for item in self.keranjang:
            if item["item_id"] == barang["id"]:
                if item["jumlah"] + jumlah > barang["available_stock"]:
                    messagebox.showerror("Stok Kurang", "Total melebihi stok tersedia!")
                    return
                item["jumlah"] = item["jumlah"] + jumlah
                self.update_tabel()
                return

        self.keranjang.append({
            "item_id": barang["id"],
            "kode": barang["item_code"],
            "nama": barang["name"],
            "jumlah": jumlah
        })
        self.update_tabel()

    def hapus_dari_keranjang(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            return
        index = self.tabel.index(terpilih[0])
        self.keranjang.pop(index)
        self.update_tabel()

    def update_tabel(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)
        for item in self.keranjang:
            self.tabel.insert("", "end", values=(item["kode"], item["nama"], item["jumlah"]))

    def simpan_transaksi(self):
        pj_label = self.cb_pj.get()
        pengambil_label = self.cb_pengambil.get()

        if pj_label == "" or pengambil_label == "":
            messagebox.showwarning("Peringatan", "Pilih penanggung jawab dan pengambil barang!")
            return

        if len(self.keranjang) == 0:
            messagebox.showwarning("Peringatan", "Tambahkan minimal 1 barang ke daftar!")
            return

        try:
            kode_transaksi = self.layanan_pinjam.buat_peminjaman(
                id_penanggung_jawab=self.map_pengguna[pj_label],
                id_pengambil=self.map_pengguna[pengambil_label],
                daftar_barang=self.keranjang,
                catatan=self.ent_catatan.get().strip()
            )
            messagebox.showinfo("Berhasil", "Peminjaman berhasil disimpan!\nKode Transaksi: " + kode_transaksi)
            self.keranjang.clear()
            self.update_tabel()
            self.ent_catatan.delete(0, "end")
            self.segarkan_pilihan()
        except Exception as err:
            messagebox.showerror("Transaksi Gagal", str(err))