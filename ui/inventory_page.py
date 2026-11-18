import tkinter as tk
from tkinter import ttk, messagebox
from services.inventory_service import LayananInventaris

class HalamanBarang(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan = LayananInventaris()
        self._bangun_ui()
        self.muat_data()

    def _bangun_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="Manajemen Inventaris Lab TKJ", font=("Segoe UI", 14, "bold")).pack(side="left")

        #pencarian dan tombol aksi
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Label(toolbar, text="Cari:").pack(side="left", padx=(0, 5))
        self.var_cari = tk.StringVar()
        entry_cari = ttk.Entry(toolbar, textvariable=self.var_cari, width=25)
        entry_cari.pack(side="left", padx=(0, 5))
        entry_cari.bind("<KeyRelease>", lambda e: self.muat_data())

        ttk.Button(toolbar, text="Arsipkan", command=self.arsip_terpilih).pack(side="right", padx=2)
        ttk.Button(toolbar, text="Ubah", command=self.buka_form_edit).pack(side="right", padx=2)
        ttk.Button(toolbar, text="+ Tambah Barang", command=self.buka_form_tambah).pack(side="right", padx=2)

        #tabel treeview
        kolom = ("id", "kode", "nama", "kategori", "total", "tersedia")
        self.tabel = ttk.Treeview(self, columns=kolom, show="headings", height=15)

        self.tabel.heading("id", text="ID")
        self.tabel.heading("kode", text="Kode Barang")
        self.tabel.heading("nama", text="Nama Barang")
        self.tabel.heading("kategori", text="Kategori")
        self.tabel.heading("total", text="Total Stok")
        self.tabel.heading("tersedia", text="Tersedia")

        self.tabel.column("id", width=40, anchor="center")
        self.tabel.column("kode", width=110)
        self.tabel.column("nama", width=220)
        self.tabel.column("kategori", width=130)
        self.tabel.column("total", width=90, anchor="center")
        self.tabel.column("tersedia", width=90, anchor="center")

        self.tabel.pack(fill="both", expand=True)

    def muat_data(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        kata_kunci = self.var_cari.get().strip()
        if kata_kunci:
            daftar = self.layanan.cari_barang(kata_kunci)
        else:
            daftar = self.layanan.ambil_semua_barang()

        for b in daftar:
            self.tabel.insert("", "end", values=(
                b["id"], b["item_code"], b["name"], b["category"],
                b["total_stock"], b["available_stock"]
            ))

    def buka_form_tambah(self):
        self._tampilkan_dialog("Tambah Barang Baru")

    def buka_form_edit(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih barang yang ingin diubah terlebih dahulu!")
            return
        data = self.tabel.item(terpilih[0])["values"]
        self._tampilkan_dialog("Ubah Data Barang", data)

    def _tampilkan_dialog(self, judul, data_lama=None):
        dialog = tk.Toplevel(self)
        dialog.title(judul)
        dialog.geometry("350x260")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Kode Barang:").grid(row=0, column=0, sticky="w", pady=5)
        ent_kode = ttk.Entry(frame, width=25)
        ent_kode.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Nama Barang:").grid(row=1, column=0, sticky="w", pady=5)
        ent_nama = ttk.Entry(frame, width=25)
        ent_nama.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Kategori:").grid(row=2, column=0, sticky="w", pady=5)
        ent_kategori = ttk.Entry(frame, width=25)
        ent_kategori.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Total Stok:").grid(row=3, column=0, sticky="w", pady=5)
        ent_stok = ttk.Entry(frame, width=25)
        ent_stok.grid(row=3, column=1, pady=5)

        if data_lama:
            ent_kode.insert(0, data_lama[1])
            ent_nama.insert(0, data_lama[2])
            ent_kategori.insert(0, data_lama[3])
            ent_stok.insert(0, str(data_lama[4]))

        def simpan():
            try:
                kode = ent_kode.get()
                nama = ent_nama.get()
                kategori = ent_kategori.get()
                stok = int(ent_stok.get())

                if data_lama:
                    selisih = stok - int(data_lama[4])
                    tersedia_baru = int(data_lama[5]) + selisih
                    self.layanan.edit_barang(data_lama[0], kode, nama, kategori, stok, tersedia_baru)
                else:
                    self.layanan.tambah_barang(kode, nama, kategori, stok)

                self.muat_data()
                dialog.destroy()
            except ValueError as err:
                messagebox.showerror("Input Tidak Valid", str(err))

        ttk.Button(frame, text="Simpan", command=simpan).grid(row=4, column=0, columnspan=2, pady=15)

    def arsip_terpilih(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih barang yang ingin diarsipkan!")
            return
        data = self.tabel.item(terpilih[0])["values"]
        if messagebox.askyesno("Konfirmasi", f"Arsipkan barang '{data[2]}'?"):
            try:
                self.layanan.arsip_barang(data[0])
                self.muat_data()
            except ValueError as err:
                messagebox.showerror("Gagal", str(err))