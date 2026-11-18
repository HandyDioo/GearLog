import tkinter as tk
from tkinter import ttk, messagebox
from services.user_service import LayananPengguna

class HalamanPengguna(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.layanan = LayananPengguna()
        self.buat_tampilan()
        self.muat_data()

    def buat_tampilan(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Manajemen Data Pengguna (Siswa & Guru)", font=("Segoe UI", 14, "bold")).pack(side="left")

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))

        ttk.Label(toolbar, text="Cari:").pack(side="left", padx=(0, 5))
        self.var_cari = tk.StringVar()
        ent_cari = ttk.Entry(toolbar, textvariable=self.var_cari, width=25)
        ent_cari.pack(side="left")
        ent_cari.bind("<KeyRelease>", lambda e: self.muat_data())

        ttk.Button(toolbar, text="Arsipkan", command=self.arsip_terpilih).pack(side="right", padx=2)
        ttk.Button(toolbar, text="+ Tambah Pengguna", command=self.buka_form_tambah).pack(side="right", padx=2)

        kolom = ("id", "kode", "nama", "jenis", "nis", "nip", "kelas")
        self.tabel = ttk.Treeview(self, columns=kolom, show="headings", height=15)

        self.tabel.heading("id", text="ID")
        self.tabel.heading("kode", text="Kode")
        self.tabel.heading("nama", text="Nama Lengkap")
        self.tabel.heading("jenis", text="Kategori")
        self.tabel.heading("nis", text="NIS")
        self.tabel.heading("nip", text="NIP")
        self.tabel.heading("kelas", text="Kelas")

        self.tabel.column("id", width=40, anchor="center")
        self.tabel.column("kode", width=90)
        self.tabel.column("nama", width=180)
        self.tabel.column("jenis", width=80, anchor="center")
        self.tabel.column("nis", width=90)
        self.tabel.column("nip", width=110)
        self.tabel.column("kelas", width=90)

        self.tabel.pack(fill="both", expand=True)

    def muat_data(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        kata = self.var_cari.get().strip()
        if kata != "":
            daftar = self.layanan.cari_pengguna(kata)
        else:
            daftar = self.layanan.ambil_semua_pengguna()

        for u in daftar:
            self.tabel.insert("", "end", values=(
                u["id"], u["user_code"], u["name"], u["user_type"],
                u["student_id"] or "-", u["employee_id"] or "-", u["class_name"] or "-"
            ))

    def buka_form_tambah(self):
        dialog = tk.Toplevel(self)
        dialog.title("Tambah Pengguna Baru")
        dialog.geometry("360x280")
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nama Lengkap:").grid(row=0, column=0, sticky="w", pady=5)
        ent_nama = ttk.Entry(frame, width=25)
        ent_nama.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Kategori:").grid(row=1, column=0, sticky="w", pady=5)
        cb_jenis = ttk.Combobox(frame, values=["Student", "Teacher"], state="readonly", width=22)
        cb_jenis.set("Student")
        cb_jenis.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="NIS (Siswa):").grid(row=2, column=0, sticky="w", pady=5)
        ent_nis = ttk.Entry(frame, width=25)
        ent_nis.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Kelas (Siswa):").grid(row=3, column=0, sticky="w", pady=5)
        ent_kelas = ttk.Entry(frame, width=25)
        ent_kelas.grid(row=3, column=1, pady=5)

        ttk.Label(frame, text="NIP (Guru):").grid(row=4, column=0, sticky="w", pady=5)
        ent_nip = ttk.Entry(frame, width=25)
        ent_nip.grid(row=4, column=1, pady=5)

        def simpan():
            try:
                kode = self.layanan.tambah_pengguna(
                    nama=ent_nama.get(),
                    jenis=cb_jenis.get(),
                    nis=ent_nis.get().strip() or None,
                    nip=ent_nip.get().strip() or None,
                    kelas=ent_kelas.get().strip() or None
                )
                messagebox.showinfo("Berhasil", "Pengguna berhasil disimpan dengan kode " + kode)
                self.muat_data()
                dialog.destroy()
            except ValueError as err:
                messagebox.showerror("Input Tidak Valid", str(err))

        ttk.Button(frame, text="Simpan", command=simpan).grid(row=5, column=0, columnspan=2, pady=15)

    def arsip_terpilih(self):
        terpilih = self.tabel.selection()
        if not terpilih:
            messagebox.showwarning("Peringatan", "Pilih pengguna terlebih dahulu!")
            return
        data = self.tabel.item(terpilih[0])["values"]
        if messagebox.askyesno("Konfirmasi", "Arsipkan pengguna " + str(data[2]) + "?"):
            self.layanan.arsip_pengguna(data[0])
            self.muat_data()