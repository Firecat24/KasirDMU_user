import re

from datetime import datetime
from database.db import DatabaseObat

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty


#----------------------------------------------------------------------------------------------------------#

class SessionCache:
    _data_obat = []
    _data_golongan = []
    _data_pajak = []

    @classmethod
    def get_data_obat(cls):
        return cls._data_obat
    
    @classmethod
    def set_data_obat(cls, data):
        cls._data_obat = data

    @classmethod
    def clear_data_obat(cls):
        cls._data_obat = []

    @classmethod
    def get_data_golongan(cls):
        return cls._data_golongan
    
    @classmethod
    def set_data_golongan(cls, data):
        cls._data_golongan = data

    @classmethod
    def clear_data_golongan(cls):
        cls._data_golongan = []

    @classmethod
    def get_data_pajak(cls):    
        return cls._data_pajak

    @classmethod
    def set_data_pajak(cls, data):
        cls._data_pajak = data

    @classmethod
    def clear_data_pajak(cls):
        cls._data_pajak = []

#----------------------------------------------------------------------------------------------------------#

class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        current_time = datetime.now().strftime('%H:%M:%S')
        time_label = self.ids.get('time_label')
        if time_label:
            time_label.text = f'{current_time}'

#----------------------------------------------------------------------------------------------------------#

class DataObat(Screen):
    def on_enter(self):
        if hasattr(self, 'data_table') and self.data_table:
            self.ids.table_container.remove_widget(self.data_table)
        rows = SessionCache.get_data_obat()
        self.create_table(rows)

    def create_table(self, rows):
        if not rows:
            print("Data obat kosong!")
            return

        column_data = [
            ("[font=Roboto][size=10sp]Jenis[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]PLU[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Nama[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Satuan[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Beli[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Umum[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Resep[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Cabang[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Halodoc[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga Karyawan[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Harga BPJS[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Kode Golongan[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Nama Golongan[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Rak[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Supplier[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Fast_Moving[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Kemasan Beli[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Isi[/size][/font]", dp(10)),
            ("[font=Roboto][size=10sp]Tgl Kadaluarsa[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Stok Apotek[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Stok Minimal[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]Stok Maksimal[/size][/font]", dp(20)),
            ("[font=Roboto][size=10sp]PPN[/size][/font]", dp(10)),
        ]

        row_data = []
        for row in rows:
            row_data.append(tuple(f"[font=Roboto][size=10sp]{str(item)}[/size][/font]" for item in row))

        self.data_table = MDDataTable(
            size_hint=(1, 1),
            column_data=column_data,
            row_data=row_data,
            use_pagination=True,
            pagination_menu_height="140dp",
            check=True,
        )
        self.ids.table_container.add_widget(self.data_table)
        
    def tampilkan_dialog(self, pesan, setelah_dialog=None, on_yes=None, on_no=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                setelah_dialog()

        def yes_pressed(instance):
            if on_yes:
                on_yes()
            tutup_dialog(instance)

        def no_pressed(instance):
            if on_no:
                on_no()
            tutup_dialog(instance)

        dialog = MDDialog(
            text=pesan,
            buttons=[
                MDFlatButton(text="No", on_release=no_pressed),
                MDFlatButton(text="Yes", on_release=yes_pressed),
            ],
        )
        dialog.open()

    def hapus_terpilih(self):
        checked_rows = self.data_table.get_row_checks()
        if not checked_rows:
            toast("Belum ada yang dipilih")
            return

        plu_ids = []
        for row in checked_rows:
            if len(row) > 1:
                cleaned = re.sub(r'\[.*?\]', '', row[1])
                plu_ids.append(cleaned)

        if not plu_ids:
            toast("Tidak menemukan PLU untuk dihapus")
            return

        pesan_konfirmasi = "Apakah Anda yakin ingin menghapus data berikut?\n\n" + "\n".join(plu_ids)

        def confirm_hapus():
            db = MDApp.get_running_app().db
            deleted = 0

            for plu in plu_ids:
                try:
                    plu_int = int(plu)
                    success = db.delete_product(plu_int)
                    if success:
                        deleted += 1
                    else:
                        toast(f"Gagal hapus ID {plu_int}")
                except Exception as e:
                    toast(f"Error: {str(e)}")

            if deleted > 0:
                toast(f"{deleted} data berhasil dihapus")
                rows = db.get_all_obat()
                SessionCache.set_data_obat(rows)
                self.manager.current = 'data_obat'
                data_obat_screen = self.manager.get_screen('data_obat')
                data_obat_screen.on_enter()

        self.tampilkan_dialog(
            pesan_konfirmasi,
            on_yes=confirm_hapus,
            on_no=None
        )

    def bersihkan_field(self, text):
        if not text:
            return ""
        return re.sub(r'\[.*?\]', '', str(text)).strip()

    def edit_data_obat(self,):
        selected_rows = self.data_table.get_row_checks()
        if len(selected_rows) == 1:
            data_row = selected_rows[0]

            data = {
                "jenis": self.bersihkan_field(data_row[0]),
                "plu": self.bersihkan_field(data_row[1]),
                "nama_produk": self.bersihkan_field(data_row[2]),
                "satuan": self.bersihkan_field(data_row[3]),
                "harga_beli": self.bersihkan_field(data_row[4]),
                "golongan": self.bersihkan_field(data_row[11]),
                "rak": self.bersihkan_field(data_row[13]),
                "supplier": self.bersihkan_field(data_row[14]),
                "fast_moving": self.bersihkan_field(data_row[15]),
                "kemasan_beli": self.bersihkan_field(data_row[16]),
                "isi": self.bersihkan_field(data_row[17]),
                "tanggal_kadaluarsa": self.bersihkan_field(data_row[18]),
                "stok_apotek": self.bersihkan_field(data_row[19]),
                "stok_min": self.bersihkan_field(data_row[20]),
                "stok_max": self.bersihkan_field(data_row[21]),
                "pajak": self.bersihkan_field(data_row[22]),
            }

            screen_edit = self.manager.get_screen('edit_obat')
            screen_edit.isi_data_edit(data)
            self.manager.current = 'edit_obat'
        else:
            dialog = MDDialog(
                text="Pilih satu data saja untuk diedit!",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())
                ],
            )
            dialog.open()


class InsertObat(Screen):
    kode_golongan_aktif = StringProperty("")
    golongan_nama_list = ListProperty([])
    kode_pajak_aktif = StringProperty("")
    pajak_nama_list = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_golongan = MDApp.get_running_app().db.get_nama_kode_golongan()
        self.golongan_nama_list = [nama for _ ,nama in self.data_golongan]

        self.data_pajak = MDApp.get_running_app().db.get_all_pajak()
        self.pajak_nama_list = [jenis for jenis, _ in self.data_pajak]

    def on_kv_post(self, base_widget):
        menu_items_golongan = [
            {
                "text": nama,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_golongan(x),
            }
            for nama in self.golongan_nama_list
        ]
        
        self.menu_golongan = MDDropdownMenu(
            caller=self.ids.dropdown_golongan,
            items=menu_items_golongan,
            width_mult=4,
        )

        menu_items_pajak = [
            {
                "text": str(nama),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_pajak(x),
            }
            for nama in self.pajak_nama_list
        ]

        self.menu_pajak = MDDropdownMenu(
            caller=self.ids.dropdown_pajak,
            items=menu_items_pajak,
            width_mult=4,
        )

    def set_selected_golongan(self, selected_nama):
        self.ids.dropdown_golongan.text = selected_nama
        self.menu_golongan.dismiss()
        self.update_kode_golongan(selected_nama)

    def set_selected_pajak(self, selected_nama):
        self.ids.dropdown_pajak.text = str(selected_nama)
        self.menu_pajak.dismiss()
        self.update_kode_pajak(selected_nama)

    def update_kode_golongan(self, selected_nama):
        for kode, nama in self.data_golongan:
            if nama == selected_nama:
                self.kode_golongan_aktif = str(kode)
                break

    def update_kode_pajak(self, selected_nama):
        for kode, nama in self.data_pajak:
            if kode == selected_nama:
                self.kode_pajak_aktif = str(kode)
                break

    def bersihkan_field_add_obat(self):
        fields = [
            'jenis', 'plu', 'nama_produk', 'satuan', 'harga_beli',
            'rak', 'supplier', 'fast_moving', 'kemasan_beli',
            'isi', 'tanggal_kadaluarsa', 'stok_apotek',
            'stok_min', 'stok_max'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

        self.ids.dropdown_golongan.text = "Pilih Golongan"
        self.ids.dropdown_pajak.text = "Pilih Pajak"
        self.kode_golongan_aktif = ""
        self.kode_pajak_aktif = ""

    def get_form_values(self):
        fields = [
            'jenis', 'plu', 'nama_produk', 'satuan', 'harga_beli',
            'rak', 'supplier', 'fast_moving', 'kemasan_beli',
            'isi', 'tanggal_kadaluarsa', 'stok_apotek',
            'stok_min', 'stok_max'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values

    def simpan_data_obat(self):
        data = self.get_form_values()

        kode_golongan = self.kode_golongan_aktif
        nama_golongan = self.ids.dropdown_golongan.text

        kode_ppn = self.kode_pajak_aktif

        margin_data = MDApp.get_running_app().db.get_margin_golongan(kode_golongan)

        harga_beli = float(data['harga_beli'])

        harga_resep = round(harga_beli * (1 + margin_data['margin_resep'] / 100))
        harga_umum = round(harga_beli * (1 + margin_data['margin_umum'] / 100))
        harga_cabang = round(harga_beli * (1 + margin_data['margin_cabang'] / 100))
        harga_halodoc = round(harga_beli * (1 + margin_data['margin_halodoc'] / 100))
        harga_karyawan = round(harga_beli * (1 + margin_data['margin_karyawan'] / 100))
        harga_bpjs = round(harga_beli * (1 + margin_data['margin_bpjs'] / 100))

        if not data['plu'] or not data['nama_produk']:
            self.tampilkan_dialog("PLU dan Nama Produk wajib diisi!")
            return

        try:
            MDApp.get_running_app().db.new_produk( 
                data['jenis'], 
                data['plu'], 
                data['nama_produk'], 
                data['satuan'], 
                data['harga_beli'], 
                harga_umum, 
                harga_resep, 
                harga_cabang, 
                harga_halodoc, 
                harga_karyawan, 
                harga_bpjs, 
                kode_golongan, 
                nama_golongan, 
                data['rak'], 
                data['supplier'], 
                data['fast_moving'], 
                data['kemasan_beli'], 
                data['isi'], 
                data['tanggal_kadaluarsa'], 
                data['stok_apotek'], 
                data['stok_min'], 
                data['stok_max'], 
                kode_ppn)

            rows = MDApp.get_running_app().db.get_all_obat()
            SessionCache.set_data_obat(rows)
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_obat', 'left'))

        except Exception as e:
            print("Error saat menyimpan data:", str(e))
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                self.bersihkan_field(), 
                setelah_dialog()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )
        dialog.open()


class EditObat(Screen):
    kode_golongan_aktif = StringProperty("")
    golongan_nama_list = ListProperty([])
    kode_pajak_aktif = StringProperty("")
    pajak_nama_list = ListProperty([])
    editing_plu = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_golongan = MDApp.get_running_app().db.get_nama_kode_golongan()
        self.golongan_nama_list = [nama for _, nama in self.data_golongan]

        self.data_pajak = MDApp.get_running_app().db.get_all_pajak()
        self.pajak_nama_list = [jenis for jenis, _ in self.data_pajak]


    def on_pre_enter(self, *args):
        Clock.schedule_once(self.reset_scroll, 0.1)

    def reset_scroll(self, dt):
        self.ids.scroll_edit.scroll_y = 1

    def on_kv_post(self, base_widget):
        menu_items_golongan = [
            {
                "text": nama,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_golongan(x),
            }
            for nama in self.golongan_nama_list
        ]
        
        self.menu_golongan = MDDropdownMenu(
            caller=self.ids.dropdown_golongan_edit,
            items=menu_items_golongan,
            width_mult=4,
        )

        menu_items_pajak = [
            {
                "text": str(nama),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_pajak(x),
            }
            for nama in self.pajak_nama_list
        ]

        self.menu_pajak = MDDropdownMenu(
            caller=self.ids.dropdown_pajak_edit,
            items=menu_items_pajak,
            width_mult=4,
        )

    def bersihkan_field_insert_obat(self):
        fields = [
            'jenis', 'plu', 'nama_produk', 'satuan', 'harga_beli',
            'rak', 'supplier', 'fast_moving', 'kemasan_beli',
            'isi', 'tanggal_kadaluarsa', 'stok_apotek',
            'stok_min', 'stok_max'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

        self.ids.dropdown_golongan_edit.text = "Pilih Golongan"
        self.ids.dropdown_pajak_edit.text = "Pilih Pajak"
        self.kode_golongan_aktif = ""
        self.kode_pajak_aktif = ""

    def isi_data_edit(self, data):
        self.bersihkan_field_insert_obat()
        self.editing_plu = self._safe_get(data, 'plu')
        
        # Isi field teks
        self._set_text_field('jenis', data, 'jenis')
        self._set_text_field('plu', data, 'plu')
        self._set_text_field('nama_produk', data, 'nama_produk')
        self._set_text_field('satuan', data, 'satuan')
        self._set_numeric_field('harga_beli', data, 'harga_beli')
        self._set_text_field('rak', data, 'rak')
        self._set_text_field('supplier', data, 'supplier')
        self._set_text_field('fast_moving', data, 'fast_moving')
        self._set_text_field('kemasan_beli', data, 'kemasan_beli')
        self._set_numeric_field('isi', data, 'isi')
        self._set_text_field('tanggal_kadaluarsa', data, 'tanggal_kadaluarsa')
        self._set_numeric_field('stok_apotek', data, 'stok_apotek')
        self._set_numeric_field('stok_min', data, 'stok_min')
        self._set_numeric_field('stok_max', data, 'stok_max')

        # Handle dropdown golongan
        self.kode_golongan_aktif = self._safe_get(data, 'kode_golongan')
        nama_golongan = self.get_nama_golongan(self.kode_golongan_aktif)
        if hasattr(self.ids, 'dropdown_golongan'):
            self.ids.dropdown_golongan_edit.text = nama_golongan if nama_golongan else "Pilih Golongan"
        
        # Handle dropdown pajak
        self.kode_pajak_aktif = self._safe_get(data, 'kode_pajak')
        nama_pajak = self.get_nama_pajak(self.kode_pajak_aktif)
        if hasattr(self.ids, 'dropdown_pajak'):
            self.ids.dropdown_pajak_edit.text = str(nama_pajak) if nama_pajak else "Pilih Pajak"

    # Helper methods
    def _safe_get(self, data, key, default=''):
        """Safe get from dictionary with default empty string"""
        return str(data.get(key, default)) if data.get(key, default) is not None else default

    def _set_text_field(self, field_id, data, data_key):
        """Set text field safely"""
        if hasattr(self.ids, field_id):
            self.ids[field_id].text = self._safe_get(data, data_key)

    def _set_numeric_field(self, field_id, data, data_key):
        """Set numeric field with validation"""
        if hasattr(self.ids, field_id):
            value = data.get(data_key)
            self.ids[field_id].text = str(value) if value is not None else ""

    def get_nama_golongan(self, kode):
        for k, nama in self.data_golongan:
            if str(k) == str(kode):
                return nama
        return None

    def get_nama_pajak(self, kode):
        for jenis, k in self.data_pajak:
            if str(k) == str(kode):
                return jenis
        return None

    def set_selected_golongan(self, selected_nama):
        self.ids.dropdown_golongan_edit.text = selected_nama
        self.menu_golongan.dismiss()
        self.update_kode_golongan(selected_nama)

    def set_selected_pajak(self, selected_nama):
        self.ids.dropdown_pajak_edit.text = str(selected_nama)
        self.menu_pajak.dismiss()
        self.update_kode_pajak(selected_nama)

    def update_kode_golongan(self, selected_nama):
        for kode, nama in self.data_golongan:
            if nama == selected_nama:
                self.kode_golongan_aktif = str(kode)
                break

    def update_kode_pajak(self, selected_nama):
        for nama, kode in self.data_pajak:
            if nama == selected_nama:
                self.kode_pajak_aktif = str(nama)
                break

    def get_form_values(self):
        fields = [
            'jenis', 'plu', 'nama_produk', 'satuan', 'harga_beli',
            'rak', 'supplier', 'fast_moving', 'kemasan_beli',
            'isi', 'tanggal_kadaluarsa', 'stok_apotek',
            'stok_min', 'stok_max'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values
    
    def simpan_edit(self):
        data = self.get_form_values()

        # Validasi wajib isi
        if not data['plu'] or not data['nama_produk']:
            self.tampilkan_dialog("PLU dan Nama Produk wajib diisi!")
            return

        try:
            db = MDApp.get_running_app().db

            kode_golongan = self.kode_golongan_aktif
            nama_golongan = self.ids.dropdown_golongan_edit.text
            kode_ppn = self.kode_pajak_aktif
            margin_data = db.get_margin_golongan(kode_golongan)
            harga_beli = float(data['harga_beli'])

            harga_resep = round(harga_beli * (1 + margin_data['margin_resep'] / 100))
            harga_umum = round(harga_beli * (1 + margin_data['margin_umum'] / 100))
            harga_cabang = round(harga_beli * (1 + margin_data['margin_cabang'] / 100))
            harga_halodoc = round(harga_beli * (1 + margin_data['margin_halodoc'] / 100))
            harga_karyawan = round(harga_beli * (1 + margin_data['margin_karyawan'] / 100))
            harga_bpjs = round(harga_beli * (1 + margin_data['margin_bpjs'] / 100))

            # Simpan ke DB
            db.edit_produk(
                data['jenis'], data['plu'], data['nama_produk'], data['satuan'], data['harga_beli'],
                harga_umum, harga_resep, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs,
                kode_golongan, nama_golongan, data['rak'], data['supplier'], data['fast_moving'],
                data['kemasan_beli'], data['isi'], data['tanggal_kadaluarsa'], data['stok_apotek'],
                data['stok_min'], data['stok_max'], kode_ppn
            )

            rows = MDApp.get_running_app().db.get_all_obat()
            SessionCache.set_data_obat(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_obat', 'left')
                print("telah berhasil update data")

            self.bersihkan_field_insert_obat()
            self.tampilkan_dialog("Data berhasil diperbarui!", setelah_dialog=setelah_ditutup)

        except Exception as e:
            self.tampilkan_dialog(f"Error saat update: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                setelah_dialog()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )
        dialog.open()

#----------------------------------------------------------------------------------------------------------#

class DataGolonganObat(Screen):
    pass

class InsertGolonganObat(Screen):
    pass

class EditGolonganObat(Screen):
    pass

#----------------------------------------------------------------------------------------------------------#

class DataPajak(Screen):
    pass

class InsertPajak(Screen):
    pass

class EditPajak(Screen):
    pass

#----------------------------------------------------------------------------------------------------------#

class Kasir(Screen):
    pass

#----------------------------------------------------------------------------------------------------------#

class WindowsManager(ScreenManager):
    pass

#----------------------------------------------------------------------------------------------------------#

class KasirApp(MDApp):
    def build(self):
        self.db = DatabaseObat("database/kasir_dmu_user.db")

        if not SessionCache.get_data_obat():
            SessionCache.set_data_obat(self.db.get_all_obat())

        return Builder.load_file('user_interface/gui.kv')
    
    def change_screen(self, screen_name, direction='left'):
        self.root.transition.direction = direction
        self.root.current = screen_name

    def simpan_data_obat(self):
        screen = self.root.get_screen('insert_obat')
        screen.simpan_data_obat()