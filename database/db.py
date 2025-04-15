import sqlite3

class Database_obat:
    def __init__(self, nama_database):
        self.koneksi = sqlite3.connect(nama_database)
        self.kursor = self.koneksi.cursor()
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
                harga_cabang REAL,
                harga_halodoc REAL,
                harga_karyawan REAL,
                harga_bpjs REAL,
                kode_golongan TEXT,
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
                ppn REAL DEFAULT 11.0
            )
        """)
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS data_pajak (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jenis_pajak TEXT NOT NULL,
                persen_pajak REAL NOT NULL
            )
        """)
        self.koneksi.commit()

    def new_produk(self, jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn):
        self.kursor.execute("""
            INSERT INTO data_obat (jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (jenis, plu, nama_produk, satuan, harga_beli, harga_umum, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs, kode_golongan, nama_golongan, rak, supplier, fast_moving, kemasan_beli, isi, tanggal_kadaluarsa, stok_apotek, stok_min, stok_max, ppn))
        self.koneksi.commit()

    def edit_produk(self, id, jenis=None, plu=None, nama_produk=None, satuan=None, harga_beli=None, harga_umum=None, harga_cabang=None, harga_halodoc=None, harga_karyawan=None, harga_bpjs=None, kode_golongan=None, nama_golongan=None, rak=None, supplier=None, fast_moving=None, kemasan_beli=None, isi=None, tanggal_kadaluarsa=None, stok_apotek=None, stok_min=None, stok_max=None, ppn=None):
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

        query = query.rstrip(", ") +  f" WHERE id={id}"
        self.kursor.execute(query,*params)  
        self.koneksi.commit()

    def delete_product(self,id):
      self.kursor.execute("DELETE FROM data_obat WHERE id=?", (id,))
      self.koneksi.commit()

    def close_connection(self):
        self.koneksi.close()