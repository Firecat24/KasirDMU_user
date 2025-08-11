import sqlite3, datetime

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
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                no_ref TEXT PRIMARY KEY,
                tanggal TEXT NOT NULL,
                id_pelanggan INTEGER,
                kredit INTEGER DEFAULT 0,
                tanggal_tempo TEXT,
                cara_bayar TEXT,
                jenis_pelanggan REAL,
                diskon_toko REAL,
                ongkir REAL,
                total_penjualan REAL,
                pembayaran REAL,
                nama_kasir TEXT,
                status TEXT DEFAULT 'normal',
                last_updated TEXT,
                poin_didapat INTEGER DEFAULT 0,
                FOREIGN KEY (id_pelanggan) REFERENCES data_pelanggan(id_pelanggan)
            )
        """)
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                no_ref TEXT NOT NULL,
                nama_obat TEXT NOT NULL,
                satuan TEXT NOT NULL,
                harga_satuan REAL NOT NULL,
                jumlah INTEGER NOT NULL,
                diskon REAL,
                total REAL NOT NULL,
                FOREIGN KEY (no_ref) REFERENCES transaksi(no_ref) ON DELETE CASCADE
            )
        """)
        self.kursor.execute("""
            CREATE TABLE IF NOT EXISTS data_pelanggan (
                id_pelanggan INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pelanggan TEXT NOT NULL,
                nomor_telfon TEXT NOT NULL,
                alamat TEXT NOT NULL,
                poin INTEGER DEFAULT 0
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
    
    def search_data_obat(self, keyword, jenis_pembeli):
        if jenis_pembeli == 'Umum':
            kolom_harga = 'harga_umum'
        elif jenis_pembeli == 'Karyawan':
            kolom_harga = 'harga_karyawan'
        elif jenis_pembeli == 'Resep':
            kolom_harga = 'harga_resep'
        elif jenis_pembeli == 'Halodoc':
            kolom_harga = 'harga_halodoc'
        elif jenis_pembeli == 'Cabang':
            kolom_harga = 'harga_cabang'
        elif jenis_pembeli == 'BPJS':
            kolom_harga = 'harga_bpjs'
        else:
            kolom_harga = 'harga_umum'

        query = f"SELECT nama_produk, satuan, {kolom_harga}, plu FROM data_obat WHERE nama_produk LIKE ?"
        self.kursor.execute(query, ('%' + keyword + '%',))
        return self.kursor.fetchall()
    
    def is_plu_exist(self, plu):
        result = self.kursor.execute("SELECT nama_produk, rak FROM data_obat WHERE plu = ?", (plu,)).fetchone()
        return result

    def stok_obat(self, plu):
        self.kursor.execute("SELECT stok_apotek FROM data_obat WHERE plu = ?", (plu,))
        row = self.kursor.fetchone()
        return int(row[0] or 0) if row else 0

    def stok_min_obat(self, plu):
        self.kursor.execute("SELECT stok_min FROM data_obat WHERE plu = ?", (plu,))
        row = self.kursor.fetchone()
        return int(row[0] or 0) if row else 0

    def stok_max_obat(self, plu):
        self.kursor.execute("SELECT stok_max FROM data_obat WHERE plu = ?", (plu,))
        row = self.kursor.fetchone()
        return int(row[0] or 0) if row else 0
    
    def pengurangan_stok_obat(self, plu, jumlah):
        self.kursor.execute("UPDATE data_obat SET stok_apotek = stok_apotek - ? WHERE plu = ?", (jumlah, plu))
        self.koneksi.commit()
        

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
        try:
            self.kursor.execute("DELETE FROM data_golongan_obat WHERE kode_golongan = ?", (kode_golongan,))
            self.koneksi.commit()

            if self.kursor.rowcount > 0:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting product with ID {kode_golongan}: {e}")
            return False

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

    def get_all_golongan(self):
        self.kursor.execute("SELECT * FROM data_golongan_obat")
        return self.kursor.fetchall()

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
        try:
            self.kursor.execute("DELETE FROM data_pajak WHERE jenis_pajak = ?", (jenis_pajak,))
            self.koneksi.commit()

            if self.kursor.rowcount > 0:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting product with ID {jenis_pajak}: {e}")
            return False

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


# ==================== TRANSAKSI ====================


    def new_transaksi(self, no_ref, tanggal, id_pelanggan, kredit, tanggal_tempo, cara_bayar, jenis_pelanggan, diskon_toko, ongkir, total_penjualan, pembayaran, nama_kasir, poin_didapat):
        status = "normal"
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.kursor.execute("""
            INSERT INTO transaksi (no_ref, tanggal, id_pelanggan, kredit, tanggal_tempo, cara_bayar, jenis_pelanggan, diskon_toko, ongkir, total_penjualan, pembayaran, nama_kasir, status, last_updated, poin_didapat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (no_ref, tanggal, id_pelanggan, kredit, tanggal_tempo, cara_bayar, jenis_pelanggan, diskon_toko, ongkir, total_penjualan, pembayaran, nama_kasir, status, last_updated, poin_didapat))
        self.koneksi.commit()

    def edit_transaksi(self, no_ref, tanggal=None, id_pelanggan=None, kredit=None, tanggal_tempo=None, cara_bayar=None, jenis_pelanggan=None, diskon_toko=None, ongkir=None, total_penjualan=None, pembayaran=None, nama_kasir=None, poin_didapat=None):
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "diedit"
        query = "UPDATE transaksi SET "
        params = []

        if tanggal is not None:
            query += "tanggal=?, "
            params.append(tanggal)
        if id_pelanggan is not None:
            query += "id_pelanggan=?, "
            params.append(id_pelanggan)
            #kenapa ini id pelanggan tapi yang masuk nama pelanggan?, karena id_pelanggan adalah foreign key yang mengacu pada data_pelanggan sedangkan nama pelanggan dibutuhkan untuk riwayat transaksi
        if kredit is not None:
            query += "kredit=?, "
            params.append(kredit)
        if tanggal_tempo is not None:
            query += "tanggal_tempo=?, "
            params.append(tanggal_tempo)
        if cara_bayar is not None:
            query += "cara_bayar=?, "
            params.append(cara_bayar)
        if jenis_pelanggan is not None:
            query += "jenis_pelanggan=?, "
            params.append(jenis_pelanggan)
        if diskon_toko is not None:
            query += "diskon_toko=?, "
            params.append(diskon_toko)
        if ongkir is not None:
            query += "ongkir=?, "
            params.append(ongkir)
        if total_penjualan is not None:
            query += "total_penjualan=?, "
            params.append(total_penjualan)
        if pembayaran is not None:
            query += "pembayaran=?, "
            params.append(pembayaran)
        if nama_kasir is not None:
            query += "nama_kasir=?, "
            params.append(nama_kasir)
        if poin_didapat is not None:
            query += "poin_didapat=?, "
            params.append(poin_didapat)

        query += "status=?, "
        params.append(status)
        query += "last_updated=? "
        params.append(last_updated)
        query = query.rstrip(", ") + " WHERE no_ref=?"
        params.append(no_ref)
        self.kursor.execute(query, tuple(params))
        self.koneksi.commit()

    def hapus_transaksi(self, no_ref):
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.kursor.execute(
            "UPDATE transaksi SET status = ?, last_updated = ? WHERE no_ref = ?",
            ('dihapus', last_updated , no_ref)
        )
        self.koneksi.commit()
        
    def get_all_transaksi(self):
        self.kursor.execute("SELECT * FROM transaksi")
        rows = self.kursor.fetchall()
        return rows
    
    def get_transaksi_by_no_ref(self, no_ref):
        self.kursor.execute("SELECT * FROM transaksi WHERE no_ref=?", (no_ref,))
        return self.kursor.fetchone()

    def pengurangan_poin_transaksi(self, no_ref):
        self.kursor.execute(
            "SELECT id_pelanggan, COALESCE(poin_didapat, 0) FROM transaksi WHERE no_ref = ?", 
            (no_ref,)
        )
        result = self.kursor.fetchone()
        if result:
            id_pelanggan, poin_dikurangi = result
            if not id_pelanggan or poin_dikurangi <= 0:
                return False
            
            self.kursor.execute(
                "UPDATE data_pelanggan SET poin = MAX(poin - ?, 0) WHERE id_pelanggan = ?", 
                (poin_dikurangi, id_pelanggan)
            )
            self.koneksi.commit()
            return True
        return False

# ==================== TRANSAKSI ITEM ====================


    def new_transaksi_item(self, no_ref, nama_obat, satuan, harga_satuan, jumlah, diskon, total):
        self.kursor.execute("""
            INSERT INTO transaksi_item (no_ref, nama_obat, satuan, harga_satuan, jumlah, diskon, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (no_ref, nama_obat, satuan, harga_satuan, jumlah, diskon, total))
        self.koneksi.commit()

    def edit_transaksi_item(self, id, no_ref=None, nama_obat=None, satuan=None, harga_satuan=None, jumlah=None, diskon=None, total=None):
        query = "UPDATE transaksi_item SET "
        params = []

        if no_ref is not None:
            query += "no_ref=?, "
            params.append(no_ref)
        if nama_obat is not None:
            query += "nama_obat=?, "
            params.append(nama_obat)
        if satuan is not None:
            query += "satuan=?, "
            params.append(satuan)
        if harga_satuan is not None:
            query += "harga_satuan=?, "
            params.append(harga_satuan)
        if jumlah is not None:
            query += "jumlah=?, "
            params.append(jumlah)
        if diskon is not None:
            query += "diskon=?, "
            params.append(diskon)
        if total is not None:
            query += "total=? "
            params.append(total)

        query = query.rstrip(", ") + " WHERE id=?"
        params.append(id)
        self.kursor.execute(query, tuple(params))
        self.koneksi.commit()

    def hapus_transaksi_item(self, id):
        try:
            self.kursor.execute("DELETE FROM transaksi_item WHERE id=?", (id,))
            self.koneksi.commit()

            if self.kursor.rowcount > 0:
                return True
            else:
                return False

        except Exception as e:
            print(f"Error deleting transaction item with ID {id}: {e}")
            return False

    def hapus_data_transaksi_item(self, no_ref):
        self.kursor.execute("DELETE FROM transaksi_item WHERE no_ref = ?", (no_ref,))
        self.koneksi.commit()
        
    def get_all_transaksi_item(self):
        self.kursor.execute("SELECT * FROM transaksi_item")
        rows = self.kursor.fetchall()
        return rows

    def get_transaksi_item_by_no_ref(self, no_ref):
        self.kursor.execute("SELECT * FROM transaksi_item WHERE no_ref=?", (no_ref,))
        return self.kursor.fetchall()


# ==================== DATA PELANGGAN ====================


    def tambah_pelanggan(self, nama_pelanggan, nomor_telfon, alamat):
        self.kursor.execute("""
            INSERT INTO data_pelanggan (nama_pelanggan, nomor_telfon, alamat) VALUES (?, ?, ?)
        """, (nama_pelanggan, nomor_telfon, alamat))
        self.koneksi.commit()

    def edit_pelanggan(self, id_pelanggan, nama_pelanggan=None, nomor_telfon=None, alamat=None, poin=None):
        query = "UPDATE data_pelanggan SET "
        params = []

        if nama_pelanggan is not None:
            query += "nama_pelanggan=?, "
            params.append(nama_pelanggan)
        if nomor_telfon is not None:
            query += "nomor_telfon=?, "
            params.append(nomor_telfon)
        if alamat is not None:
            query += "alamat=?, "
            params.append(alamat)
        if poin is not None:
            query += "poin=? "
            params.append(poin)

        query = query.rstrip(", ") + " WHERE id_pelanggan=?"
        params.append(id_pelanggan)
        self.kursor.execute(query, tuple(params))
        self.koneksi.commit()
    
    def hapus_pelanggan(self, id_pelanggan):
        try:
            self.kursor.execute("DELETE FROM data_pelanggan WHERE id_pelanggan=?", (id_pelanggan,))
            self.koneksi.commit()

            if self.kursor.rowcount > 0:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting patient with ID {id_pelanggan}: {e}")
            return False
    
    def get_all_pelanggan(self):
        self.kursor.execute("SELECT * FROM data_pelanggan")
        rows = self.kursor.fetchall()
        return rows
    
    def search_data_pelanggan(self, keyword):
        self.kursor.execute("SELECT * FROM data_pelanggan WHERE nama_pelanggan LIKE ?", ('%' + keyword + '%',))
        return self.kursor.fetchall()
    
    def get_poin_pelanggan(self, nama_pelanggan):
        self.kursor.execute("SELECT poin FROM data_pelanggan WHERE nama_pelanggan = ?", (nama_pelanggan,))
        result = self.kursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def tambah_poin_pelanggan(self, id_pelanggan, poin_tambahan):
        self.kursor.execute("UPDATE data_pelanggan SET poin = poin + ? WHERE id_pelanggan = ?", (poin_tambahan, id_pelanggan))
        self.koneksi.commit()

    def pengurangan_poin_pelanggan(self, id_pelanggan, poin_tambahan):
        self.kursor.execute("UPDATE data_pelanggan SET poin = poin - ? WHERE id_pelanggan = ?", (poin_tambahan, id_pelanggan))
        self.koneksi.commit()

    def get_id_pelanggan(self, nama_pelanggan):
        self.kursor.execute("SELECT id_pelanggan FROM data_pelanggan WHERE nama_pelanggan=?", (nama_pelanggan,))
        result = self.kursor.fetchone()
        return result[0] if result else None

    def get_nama_pelanggan_by_id(self, id_pelanggan):
        self.kursor.execute("SELECT nama_pelanggan FROM data_pelanggan WHERE id_pelanggan=?", (id_pelanggan,))
        result = self.kursor.fetchone()
        return result[0] if result else None

# ==================== TUTUP DATABASE ====================


    def close_connection(self):
        self.koneksi.close()


# ==================== OTHER ====================


    def automatis_no_ref(self):
        self.kursor.execute("SELECT no_ref FROM transaksi ORDER BY no_ref DESC LIMIT 1")
        last = self.kursor.fetchone()
        return last