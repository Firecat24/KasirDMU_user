import sqlite3

class DatabaseObat:
    def __init__(self, nama_database):
        self.koneksi = sqlite3.connect(nama_database)
        self.kursor = self.koneksi.cursor()
        self.kursor.execute("PRAGMA foreign_keys = ON")
        self.koneksi.commit()
        self.buat_tabel()

    def buat_tabel(self):
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS data_obat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jenis TEXT NOT NULL,
                plu TEXT UNIQUE NOT NULL,
                nama_produk TEXT NOT NULL,
                satuan TEXT NOT NULL,
                harga_beli REAL NOT NULL,
                harga_umum REAL,
                harga_resep REAL,
                harga_cabang REAL,
                harga_halodoc REAL,
                harga_karyawan REAL,
                harga_bpjs REAL,
                kode_golongan INTEGER,
                nama_golongan TEXT,
                rak TEXT,
                supplier TEXT,
                fast_moving TEXT,
                kemasan_beli TEXT,
                isi INTEGER,
                tanggal_kadaluarsa TEXT,
                stok_apotek INTEGER DEFAULT 0,
                stok_min INTEGER DEFAULT 0,
                stok_max INTEGER DEFAULT 0,
                ppn TEXT DEFAULT 11.0,
                FOREIGN KEY (kode_golongan) REFERENCES data_golongan_obat(kode_golongan)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL,
                FOREIGN KEY (ppn) REFERENCES data_pajak(jenis_pajak)
                    ON UPDATE CASCADE
                    ON DELETE SET NULL
            )
        """)
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS data_pajak (
                jenis_pajak TEXT PRIMARY KEY,
                persen_pajak REAL NOT NULL
            )
        """)
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS data_golongan_obat (
                kode_golongan INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_golongan TEXT NOT NULL,
                margin_umum REAL DEFAULT 0,
                margin_resep REAL DEFAULT 0,
                margin_cabang REAL DEFAULT 0,
                margin_halodoc REAL DEFAULT 0,
                margin_karyawan REAL DEFAULT 0,
                margin_bpjs REAL DEFAULT 0
            )
        """)
        self.koneksi.commit()


 # ==================== DATA OBAT ====================


    def new_produk(self, jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_resep, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn):
        self.kursor.execute("""
            INSERT INTO data_obat (jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_resep, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_resep, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn))
        self.koneksi.commit()

    def edit_produk(self, jenis=None, plu=None, nama_produk=None, satuan=None, harga_beli=None, harga_umum=None, harga_resep=None, harga_cabang=None, harga_halodoc=None, harga_karyawan=None, harga_bpjs=None, kode_golongan=None, nama_golongan=None, rak=None, supplier=None, fast_moving=None, kemasan_beli=None, isi=None, tanggal_kadaluarsa=None, stok_apotek=None, stok_min=None, stok_max=None, ppn=None):
        query = "UPDATE data_obat SET "
        params = []

        if jenis is not None:
            query += "jenis=?, "
            params.append(jenis)
        if plu is not None:
            query += "plu=?, "
            params.append(plu)
        if nama_produk is not None:
            query += "nama_produk=?, "
            params.append(nama_produk)
        if satuan is not None:
            query += "satuan=?, "
            params.append(satuan)
        if harga_beli is not None:
            query += "harga_beli=?, "
            params.append(harga_beli)
        if harga_umum is not None:
            query += "harga_umum=?, "
            params.append(harga_umum)
        if harga_resep is not None:
            query += "harga_resep=?, "
            params.append(harga_resep)
        if harga_cabang is not None:
            query += "harga_cabang=?, "
            params.append(harga_cabang)
        if harga_halodoc is not None:
            query += "harga_halodoc=?, "
            params.append(harga_halodoc)
        if harga_karyawan is not None:
            query += "harga_karyawan=?, "
            params.append(harga_karyawan)
        if harga_bpjs is not None:
            query += "harga_bpjs=?, "
            params.append(harga_bpjs)
        if kode_golongan is not None:
            query += "kode_golongan=?, "
            params.append(kode_golongan)
        if nama_golongan is not None:
            query += "nama_golongan=?, "
            params.append(nama_golongan)
        if rak is not None:
            query += "rak=?, "
            params.append(rak)
        if supplier is not None:
            query += "supplier=?, "
            params.append(supplier)
        if fast_moving is not None:
            query += "fast_moving=?, "
            params.append(fast_moving)
        if kemasan_beli is not None:
            query += "kemasan_beli=?, "
            params.append(kemasan_beli) 
        if isi is not None:
            query += "isi=?, "
            params.append(isi)
        if tanggal_kadaluarsa is not None:
            query += "tanggal_kadaluarsa=?, "
            params.append(tanggal_kadaluarsa)
        if stok_apotek is not None:
            query += "stok_apotek=?, "
            params.append(stok_apotek)
        if stok_min is not None:
            query += "stok_min=?, "
            params.append(stok_min)
        if stok_max is not None:
            query += "stok_max=?, "
            params.append(stok_max)
        if ppn is not None:
            query += "ppn=?, "
            params.append(ppn)

        query = query.rstrip(", ") + " WHERE plu=?"
        params.append(plu)
        self.kursor.execute(query, tuple(params))
        self.koneksi.commit()

    def delete_product(self, plu):
        try:
            self.kursor.execute("DELETE FROM data_obat WHERE plu=?", (plu,))
            self.koneksi.commit()

            if self.kursor.rowcount > 0:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting product with ID {plu}: {e}")
            return False
    
    def get_all_obat(self):
        self.kursor.execute("SELECT * FROM data_obat")
        rows = self.kursor.fetchall()
        return [row[1:] for row in rows]
    
    def jumlah_obat(self):
        self.kursor.execute("SELECT COUNT(*) FROM data_obat")
        return self.kursor.fetchone()[0]
    

# ==================== GOLONGAN ====================


    def tambah_golongan(self, nama_golongan, margin_umum=0, margin_resep=0, margin_halodoc=0, margin_cabang=0, margin_karyawan=0, margin_bpjs=0):
        self.kursor.execute("""
            INSERT INTO data_golongan_obat (nama_golongan, margin_umum, margin_resep, margin_halodoc, margin_cabang, margin_karyawan, margin_bpjs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nama_golongan, margin_umum, margin_resep, margin_halodoc, margin_cabang, margin_karyawan, margin_bpjs))
        self.koneksi.commit()

    def edit_golongan(self, kode_golongan, nama_golongan=None, margin_umum=None, margin_resep=None, margin_halodoc=None, margin_cabang=None, margin_karyawan=None, margin_bpjs=None):
        query = "UPDATE data_golongan_obat SET "
        params = []
        if nama_golongan is not None:
            query += "nama_golongan=?, "
            params.append(nama_golongan)
        if margin_umum is not None:
            query += "margin_umum=?, "
            params.append(margin_umum)
        if margin_resep is not None:
            query += "margin_resep=?, "
            params.append(margin_resep)
        if margin_halodoc is not None:
            query += "margin_halodoc=?, "
            params.append(margin_halodoc)
        if margin_cabang is not None:
            query += "margin_cabang=?, "
            params.append(margin_cabang)
        if margin_karyawan is not None:
            query += "margin_karyawan=?, "
            params.append(margin_karyawan)
        if margin_bpjs is not None:
            query += "margin_bpjs=?, "
            params.append(margin_bpjs)

        query = query.rstrip(", ") + " WHERE kode_golongan=?"
        params.append(kode_golongan)
        self.kursor.execute(query, params)
        self.koneksi.commit()

    def hapus_golongan(self, kode_golongan):
        self.kursor.execute("DELETE FROM data_golongan_obat WHERE kode_golongan = ?", (kode_golongan,))
        self.koneksi.commit()

    def get_nama_kode_golongan(self):
        self.kursor.execute("SELECT kode_golongan, nama_golongan FROM data_golongan_obat")
        return self.kursor.fetchall()
    
    def get_margin_golongan(self, kode_golongan):
        self.kursor.execute("""
            SELECT margin_umum, margin_resep, margin_halodoc, margin_cabang, margin_karyawan, margin_bpjs 
            FROM data_golongan_obat 
            WHERE kode_golongan = ?
        """, (kode_golongan,))
        result = self.kursor.fetchone()
        if result:
            return {
                "margin_umum": result[0],
                "margin_resep": result[1],
                "margin_halodoc": result[2],
                "margin_cabang": result[3],
                "margin_karyawan": result[4],
                "margin_bpjs": result[5]
            }
        else:
            return None


# ==================== PAJAK ====================


    def tambah_pajak(self, jenis_pajak, persen_pajak):
        self.kursor.execute("""
            INSERT INTO data_pajak (jenis_pajak, persen_pajak) VALUES (?, ?)
        """, (jenis_pajak, persen_pajak))
        self.koneksi.commit()

    def edit_pajak(self, jenis_pajak, persen_pajak):
        self.kursor.execute("""
            UPDATE data_pajak SET persen_pajak = ? WHERE jenis_pajak = ?
        """, (persen_pajak, jenis_pajak))
        self.koneksi.commit()

    def hapus_pajak(self, jenis_pajak):
        self.kursor.execute("DELETE FROM data_pajak WHERE jenis_pajak = ?", (jenis_pajak,))
        self.koneksi.commit()

    def get_all_pajak(self):
        self.kursor.execute("SELECT * FROM data_pajak")
        return self.kursor.fetchall()

    def get_pajak_by_jenis(self, jenis_pajak):
        self.kursor.execute("SELECT persen_pajak FROM data_pajak WHERE jenis_pajak = ?", (jenis_pajak,))
        result = self.kursor.fetchone()
        if result:
            return result[0]
        else:
            return None 


# ==================== TUTUP DATABASE ====================


    def close_connection(self):
        self.koneksi.close()