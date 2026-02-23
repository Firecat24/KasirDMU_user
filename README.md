# DOOKA - Kasir DMU (User Module) 🛒💻

> 🚧 **Status Proyek: Aktif Dikembangkan (On Progress)** 🚧

**DOOKA (User Module)** adalah subsistem aplikasi berbasis *desktop* yang merupakan bagian dari ekosistem **Kasir DMU**. Repositori ini secara spesifik memuat modul klien (kasir/pengguna) yang dirancang untuk mempercepat operasional kasir harian, manajemen basis data lokal, dan pelaporan transaksi.

Sistem ini didesain berdampingan dengan **DOOKA Admin** (sedang dikembangkan) untuk membentuk arsitektur *client-server* yang efisien.

## 📸 Tangkapan Layar (Screenshots)
* [Tampilan Menu Utama / Kasir]
<img width="1919" height="1048" alt="image" src="https://github.com/user-attachments/assets/f560d0d3-83cd-4709-9866-44853aee7b23" />
* [Tampilan Lainnya]
<img width="1917" height="1030" alt="image" src="https://github.com/user-attachments/assets/f0969e9a-eeed-49bd-bd9f-f49b7764a0b8" />
<img width="1920" height="1040" alt="image" src="https://github.com/user-attachments/assets/672d91c7-7f8e-4f5f-8723-381671a42ae3" />
<img width="1920" height="940" alt="image" src="https://github.com/user-attachments/assets/1d7fbe29-a635-42d4-ae4a-c7bdf901129e" />
<img width="1920" height="938" alt="image" src="https://github.com/user-attachments/assets/5a9f1be1-f954-4754-b57b-65bcf4bf6a30" />
<img width="1920" height="1037" alt="image" src="https://github.com/user-attachments/assets/fed6a3aa-8c67-4e7e-b1ec-cbba56ac1279" />
<img width="1920" height="1029" alt="image" src="https://github.com/user-attachments/assets/da374871-6778-491a-811c-690d6994df3c" />
<img width="1920" height="993" alt="image" src="https://github.com/user-attachments/assets/2de846c9-4463-4d9f-b51b-da8ce7efe832" />



## ✨ Fitur Utama & Fungsionalitas
* **Arsitektur Database Hybrid (SQLite & MySQL):** * Menggunakan **SQLite** sebagai basis data lokal agar aplikasi *user* tetap berjalan sangat cepat, ringan, dan mandiri saat memproses transaksi harian.
  * Disiapkan untuk terintegrasi dengan **MySQL** guna sinkronisasi data terpusat (seperti data master obat, pajak, dan rekap transaksi) dengan sistem **DOOKA Admin**.
* **Manajemen Data Spesifik:** Modul manajemen basis data relasional yang difokuskan pada pengolahan **data obat** dan kalkulasi **data pajak**.
* **Integrasi Laporan Excel:** Memiliki modul khusus untuk mengolah, mengimpor, atau mengekspor data laporan operasional ke dalam format spreadsheet (Excel).
* **Pemrosesan Dokumen Lanjutan:** Menggunakan teknologi *markup* HTML dan **TeX** untuk kebutuhan format cetak dokumen, *invoice*, atau *reporting* dengan presisi tinggi.
* **Standalone Executable (.exe):** Aplikasi telah dikonfigurasi (`DOOKA.spec`) untuk di-*build* menjadi *file executable* mandiri Windows menggunakan PyInstaller.

## 🛠️ Teknologi & Stack
* **Bahasa Pemrograman Inti:** Python
* **GUI Framework:** Kivy & Kvlang
* **Database Management:** SQLite (Lokal) & MySQL (Server/Sinkronisasi)
* **Document Formatting:** HTML & TeX
* **Packaging:** PyInstaller

## 📂 Struktur Direktori Utama
* `user_interface/` : Berisi komponen-komponen visual dan tata letak antarmuka aplikasi (`.kv` files).
* `database/` : Menyimpan skema, koneksi (SQLite/MySQL), dan manipulasi basis data aplikasi.
* `excel/` : Modul untuk pemrosesan dan manajemen *file* spreadsheet.
* `utils/` : Kumpulan fungsi utilitas dan pembantu untuk logika *backend*.
* `dist/DOOKA/` & `build/DOOKA/` : Direktori *output* tempat *file* hasil kompilasi aplikasi (`.exe`) disimpan.

---
*Repositori ini memuat source code utama beserta log pekerjaan (`last_pekerjaan.txt`). Pembaruan dan perombakan arsitektur klien-server masih terus dilakukan untuk mencapai versi rilis final.*
