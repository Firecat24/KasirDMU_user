# Built-in modules
import re
from datetime import datetime
from utils.formatting import FormatHelper, get_digits_only

# Local modules
from database.db import DatabaseObat

# KivyMD modules
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

# Kivy modules
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty

#---------------------------------------------------------------------------------------------#

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

#---------------------------------------------------------------------------------------------#

class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        current_time = datetime.now().strftime('%H:%M:%S')
        time_label = self.ids.get('time_label')
        if time_label:
            time_label.text = f'{current_time}'

#---------------------------------------------------------------------------------------------#

class DataObat(Screen):
    def on_enter(self):
        self.checkbox_refs = {}
        self.selected_rows = set()
        self.load_data_table()
        self.prepare_table(self.loaded_rows)

    def load_data_table(self):
        self.loaded_rows = SessionCache.get_data_obat()

    def prepare_table(self, rows):
        self.create_table(rows)

    def create_table(self, rows):
        grid = self.ids.grid_obat
        grid.clear_widgets()
        self.rows_data_asli = rows
        self.checkbox_refs = {}

        header = [
            "Jenis", "PLU", "Nama", "Satuan", "Harga Beli", "Harga Umum",
            "Harga Resep", "Harga Cabang", "Harga Halodoc", "Harga Karyawan",
            "Harga BPJS", "Kode Gol", "Nama Gol", "Rak", "Supplier",
            "Fast_Moving", "Kemasan", "Isi", "Tgl Kadaluarsa", "Stok Apotek",
            "Stok Min", "Stok Max", "PPN", "Pilih"
        ]
        grid.cols = len(header)

        # Header
        for judul in header:
            label = Factory.TabelLabel(text=judul, bold=True)
            grid.add_widget(label)

        # Data + Checkbox
        for row in rows:
            for item in row:
                grid.add_widget(Factory.TabelLabel(text=str(item)))
            cb_box = Factory.TabelCheckBox()
            cb = cb_box.ids.checkbox
            plu_value = str(row[1])
            self.checkbox_refs[plu_value] = cb
            cb.bind(active=lambda checkbox, value, plu=plu_value: self.on_checkbox_toggle(plu, value))
            grid.add_widget(cb_box)

    def on_checkbox_toggle(self, plu, value):
        if value:
            self.selected_rows.add(plu)
        else:
            self.selected_rows.discard(plu)

    def hapus_terpilih(self):
        if not self.selected_rows:
            toast("Belum ada yang dipilih")
            return

        plu_ids = list(self.selected_rows)

        pesan_konfirmasi = "Apakah Anda yakin ingin menghapus data berikut?\n\n" + "\n".join(plu_ids)

        def confirm_hapus():
            db = MDApp.get_running_app().db
            deleted = 0

            for plu in plu_ids:
                try:
                    success = db.delete_product(plu)
                    if success:
                        deleted += 1
                    else:
                        toast(f"Gagal hapus ID {plu}")
                except Exception as e:
                    toast(f"Error: {str(e)}")

            if deleted > 0:
                toast(f"{deleted} data berhasil dihapus")
                rows = db.get_all_obat()
                SessionCache.set_data_obat(rows)
                self.reload_table(rows)
                self.reset_centang()

        def batal_hapus():
            self.reset_centang()

        self.tampilkan_dialog(pesan_konfirmasi, on_yes=confirm_hapus, on_no=batal_hapus)

    def edit_data_obat(self):
        if len(self.selected_rows) == 1:
            selected_plu = list(self.selected_rows)[0]
            for row in self.rows_data_asli:
                if str(row[1]) == selected_plu:
                    data_row = row
                    break
            else:
                toast("Data tidak ditemukan.")
                return

            data = {
                "jenis": str(data_row[0]),
                "plu": str(data_row[1]),
                "nama_produk": str(data_row[2]),
                "satuan": str(data_row[3]),
                "harga_beli": str(data_row[4]),
                "golongan": str(data_row[11]),
                "rak": str(data_row[13]),
                "supplier": str(data_row[14]),
                "fast_moving": str(data_row[15]),
                "kemasan_beli": str(data_row[16]),
                "isi": str(data_row[17]),
                "tanggal_kadaluarsa": str(data_row[18]),
                "stok_apotek": str(data_row[19]),
                "stok_min": str(data_row[20]),
                "stok_max": str(data_row[21]),
                "pajak": str(data_row[22]),
            }

            screen_edit = self.manager.get_screen('edit_obat')
            screen_edit.isi_data_edit(data)
            self.manager.current = 'edit_obat'
            self.reset_centang()
        else:
            self.reset_centang()
            dialog = MDDialog(
                text="Pilih satu data saja untuk diedit!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()

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

    def reload_table(self, rows):
        self.clear_table()
        self.create_table(rows)

    def reset_centang(self):
        for plu in list(self.selected_rows):
            if plu in self.checkbox_refs:
                self.checkbox_refs[plu].active = False
        self.selected_rows.clear()

    def clear_table(self):
        self.ids.grid_obat.clear_widgets()

    def on_leave(self):
        self.clear_table()

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
        Clock.schedule_once(self.build_dropdowns, 0.1)
        
    def build_dropdowns(self, dt):
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
            max_height=dp(200),
            width=dp(200),
        )

        menu_items_pajak = [
            {
                "text": nama,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_pajak(x),
            }
            for nama in self.pajak_nama_list
        ]

        self.menu_pajak = MDDropdownMenu(
            caller=self.ids.dropdown_pajak,
            items=menu_items_pajak,
            max_height=dp(200),
            width=dp(200),
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

        harga_beli = int(get_digits_only(data['harga_beli']))

        harga_resep = round(harga_beli * (1 + margin_data['margin_resep'] / 100))
        harga_umum = round(harga_beli * (1 + margin_data['margin_umum'] / 100))
        harga_cabang = round(harga_beli * (1 + margin_data['margin_cabang'] / 100))
        harga_halodoc = round(harga_beli * (1 + margin_data['margin_halodoc'] / 100))
        harga_karyawan = round(harga_beli * (1 + margin_data['margin_karyawan'] / 100))
        harga_bpjs = round(harga_beli * (1 + margin_data['margin_bpjs'] / 100))

        # HANDLING ERRORS
        if not data['plu'] or not data['nama_produk']:
            self.tampilkan_dialog("PLU dan Nama Produk wajib diisi!")
            return
        if MDApp.get_running_app().db.is_plu_exist(data['plu']):
            self.tampilkan_dialog(f"PLU '{data['plu']}' sudah terdaftar. Gunakan PLU lain.")
            return
        #_____________________________________________________________________________________#
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
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_obat', 'right'))

        except Exception as e:
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                self.bersihkan_field_add_obat(), 
                setelah_dialog()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )
        dialog.open()

class EditObat(Screen):
    kode_golongan_nama = StringProperty("Pilih Golongan")
    kode_pajak_nama = StringProperty("Pilih Pajak")
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
        Clock.schedule_once(self.build_dropdowns, 0.1)

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.reset_scroll, 0.1)

    def reset_scroll(self, dt):
        self.ids.scroll_edit.scroll_y = 1

    def build_dropdowns(self, dt):
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
            max_height=dp(200),
            width=dp(200),
        )

        menu_items_pajak = [
            {
                "text": nama,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=nama: self.set_selected_pajak(x),
            }
            for nama in self.pajak_nama_list
        ]

        self.menu_pajak = MDDropdownMenu(
            caller=self.ids.dropdown_pajak_edit,
            items=menu_items_pajak,
            max_height=dp(200),
            width=dp(200),
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

        self.kode_golongan_aktif = ""
        self.kode_golongan_nama = "Pilih Golongan"
        self.kode_pajak_aktif = ""
        self.kode_pajak_nama = "Pilih Pajak"

    def isi_data_edit(self, data):
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

        self.kode_golongan_aktif = self._safe_get(data, 'kode_golongan') or self._safe_get(data, 'golongan')
        nama_golongan = self.get_nama_golongan(self.kode_golongan_aktif)
        self.kode_golongan_nama = nama_golongan or "Pilih Golongan"

        self.kode_pajak_aktif = self._safe_get(data, 'kode_pajak')
        if not self.kode_pajak_aktif:
            for nama, kode in self.data_pajak:
                if nama == data.get("pajak"):
                    self.kode_pajak_aktif = str(kode)
                    break

        nama_pajak = self.get_nama_pajak(self.kode_pajak_aktif)
        self.kode_pajak_nama = nama_pajak or "Pilih Pajak"

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
        kode = str(kode).strip()
        for k, nama in self.data_golongan:
            if str(k).strip() == kode:
                return nama
        return None

    def get_nama_pajak(self, kode):
        kode = str(kode).strip()
        for nama, k in self.data_pajak:
            if str(k).strip() == kode:
                return nama
        return None

    def set_selected_golongan(self, selected_nama):
        self.kode_golongan_nama = selected_nama
        self.menu_golongan.dismiss()
        self.update_kode_golongan(selected_nama)

    def set_selected_pajak(self, selected_nama):
        self.kode_pajak_nama = selected_nama
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

        # HANDLING ERRORS
        if not data['plu'] or not data['nama_produk']:
            self.tampilkan_dialog("PLU dan Nama Produk wajib diisi!")
            return
        #_____________________________________________________________________________________#

        try:
            db = MDApp.get_running_app().db

            kode_golongan = self.kode_golongan_aktif
            nama_golongan = self.kode_golongan_nama
            kode_ppn = self.kode_pajak_nama
            margin_data = db.get_margin_golongan(kode_golongan)
            harga_beli = int(get_digits_only(data['harga_beli']))

            harga_resep = round(harga_beli * (1 + margin_data['margin_resep'] / 100))
            harga_umum = round(harga_beli * (1 + margin_data['margin_umum'] / 100))
            harga_cabang = round(harga_beli * (1 + margin_data['margin_cabang'] / 100))
            harga_halodoc = round(harga_beli * (1 + margin_data['margin_halodoc'] / 100))
            harga_karyawan = round(harga_beli * (1 + margin_data['margin_karyawan'] / 100))
            harga_bpjs = round(harga_beli * (1 + margin_data['margin_bpjs'] / 100))

            # Simpan ke DB
            db.edit_produk(
                data['jenis'], data['plu'], data['nama_produk'], data['satuan'], harga_beli,
                harga_umum, harga_resep, harga_cabang, harga_halodoc, harga_karyawan, harga_bpjs,
                kode_golongan, nama_golongan, data['rak'], data['supplier'], data['fast_moving'],
                data['kemasan_beli'], data['isi'], data['tanggal_kadaluarsa'], data['stok_apotek'],
                data['stok_min'], data['stok_max'], kode_ppn
            )

            rows = MDApp.get_running_app().db.get_all_obat()
            SessionCache.set_data_obat(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_obat', 'right')

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

#---------------------------------------------------------------------------------------------#

class DataGolonganObat(Screen):
    def on_enter(self):
        self.selected_rows = set()
        self.load_table_data()
        self.checkbox_refs = {}
        self.show_table(self._rows)

    def load_table_data(self):
        self._rows = SessionCache.get_data_golongan()

    def check_thread_done(self, dt):
        self.show_table(self._rows)

    def show_table(self, rows):
        grid = self.ids.grid_golongan
        grid.clear_widgets()
        grid.cols = 9  # 8 kolom data + 1 kolom checkbox

        self._rows = rows
        self.selected_rows = set()
        self.checkbox_refs = {}
        self.kode_to_nama = {}

        headers = [
            "Kode", "Nama Golongan", "Margin Umum", "Margin Resep",
            "Margin Cabang", "Margin Halodoc", "Margin Karyawan", "Margin BPJS", "Pilih"
        ]

        for header in headers:
            grid.add_widget(Factory.TabelLabel(text=header, bold=True))

        for row in rows:
            kode = int(row[0])
            nama = row[1]
            self.kode_to_nama[kode] = nama
            for value in row:
                grid.add_widget(Factory.TabelLabel(text=str(value)))
            cb_box = Factory.TabelCheckBox()
            cb = cb_box.ids.checkbox
            kode_value = int(row[0])
            self.checkbox_refs[kode] = cb
            cb.bind(active=lambda checkbox, value, kode=kode_value: self.toggle_checkbox(kode, value))
            grid.add_widget(cb_box)

    def toggle_checkbox(self, kode, value):
        if value:
            self.selected_rows.add(kode)
        else:
            self.selected_rows.discard(kode)

    def hapus_terpilih(self):
        if not self.selected_rows:
            toast("Belum ada yang dipilih")
            return
        kode_ids = list(self.selected_rows)
        pesan_konfirmasi = "Yakin ingin menghapus golongan:\n\n" + "\n".join( f"{kode} - {self.kode_to_nama.get(kode, 'Nama tidak ditemukan')}" for kode in kode_ids)

        def confirm_hapus():
            db = MDApp.get_running_app().db
            deleted = 0

            for kode in kode_ids:
                try:
                    success = db.hapus_golongan(kode)
                    if success:
                        deleted += 1
                    else:
                        toast(f"Gagal hapus ID {kode}")
                except Exception as e:
                    toast(f"Error: {str(e)}")

            if deleted > 0:
                toast(f"{deleted} data berhasil dihapus")
                rows = db.get_all_golongan()
                SessionCache.set_data_golongan(rows)
                data_golongan_screen = self.manager.get_screen('data_golongan_obat')
                data_golongan_screen.reload_table(rows)
                self.manager.current = 'data_golongan_obat'
                self.reset_centang()

        def batal_hapus():
            self.reset_centang()

        self.tampilkan_dialog(
            pesan_konfirmasi,
            on_yes=confirm_hapus,
            on_no=batal_hapus
        )

    def edit_data_golongan_obat(self):
        if len(self.selected_rows) == 1:
            selected_kode = list(self.selected_rows)[0]
            for row in self._rows:
                if int(row[0]) == selected_kode:
                    data_row = row
                    break
            else:
                toast("Data tidak ditemukan.")
                return
            data = {
                "kode_golongan": str(data_row[0]),
                "nama_golongan": str(data_row[1]),
                "margin_umum": str(data_row[2]),
                "margin_resep": str(data_row[3]),
                "margin_cabang": str(data_row[4]),
                "margin_halodoc": str(data_row[5]),
                "margin_karyawan": str(data_row[6]),
                "margin_bpjs": str(data_row[7]),
            }
            screen_edit = self.manager.get_screen('edit_golongan_obat')
            screen_edit.isi_data_edit_golongan(data)
            self.manager.current = 'edit_golongan_obat'
            self.reset_centang()
        else:
            dialog = MDDialog(
                text="Pilih satu data saja untuk diedit!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
            self.reset_centang()

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

    def bersihkan_field(self, text):
        if not text:
            return ""
        return re.sub(r'\[.*?\]', '', str(text)).strip()

    def reload_table(self, rows):
        self.clear_table()
        self.show_table(rows)

    def reset_centang(self):
        for plu in list(self.selected_rows):
            if plu in self.checkbox_refs:
                self.checkbox_refs[plu].active = False
        self.selected_rows.clear()

    def clear_table(self):
        self.ids.grid_golongan.clear_widgets()

    def on_leave(self):
        self.clear_table()

class InsertGolonganObat(Screen):
    def bersihkan_field_add_golongan(self):
        fields = [
            'nama_golongan', 'margin_umum', 'margin_resep',
            'margin_cabang', 'margin_halodoc', 'margin_karyawan', 'margin_bpjs'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def get_form_values(self):
        fields = [
            'nama_golongan', 'margin_umum', 'margin_resep',
            'margin_cabang', 'margin_halodoc', 'margin_karyawan', 'margin_bpjs'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values

    def simpan_data_golongan_obat(self):
        data = self.get_form_values()

        if not data['nama_golongan']:
            self.tampilkan_dialog("Nama Golongan wajib diisi!")
            return

        try:
            MDApp.get_running_app().db.tambah_golongan( 
                data['nama_golongan'], 
                data['margin_umum'],
                data['margin_resep'],
                data['margin_halodoc'],
                data['margin_cabang'],
                data['margin_karyawan'],
                data['margin_bpjs']
                )

            rows = MDApp.get_running_app().db.get_all_golongan()
            SessionCache.set_data_golongan(rows)
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_golongan_obat', 'right'))

        except Exception as e:
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                self.bersihkan_field_add_golongan(), 
                setelah_dialog()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )
        dialog.open()

class EditGolonganObat(Screen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(self.reset_scroll, 0.1)

    def reset_scroll(self, dt):
        self.ids.scroll_edit_golongan.scroll_y = 1

    def bersihkan_field_insert_golongan(self):
        fields = [
            'kode_golongan','nama_golongan', 'margin_umum', 'margin_resep',
            'margin_cabang', 'margin_halodoc', 'margin_karyawan', 'margin_bpjs'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def isi_data_edit_golongan(self, data):
        self.bersihkan_field_insert_golongan()
        self._set_numeric_field('kode_golongan', data, 'kode_golongan')
        self._set_text_field('nama_golongan', data, 'nama_golongan')
        self._set_numeric_field('margin_umum', data, 'margin_umum')
        self._set_numeric_field('margin_resep', data, 'margin_resep')
        self._set_numeric_field('margin_cabang', data, 'margin_cabang')
        self._set_numeric_field('margin_halodoc', data, 'margin_halodoc')
        self._set_numeric_field('margin_karyawan', data, 'margin_karyawan')
        self._set_numeric_field('margin_bpjs', data, 'margin_bpjs')

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

    def get_form_values(self):
        fields = [
            'kode_golongan','nama_golongan', 'margin_umum', 'margin_resep',
            'margin_cabang', 'margin_halodoc', 'margin_karyawan', 'margin_bpjs'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""
        return values
    
    def simpan_edit_golongan(self):
        data = self.get_form_values()
        if not data['nama_golongan']:
            self.tampilkan_dialog("Nama Golongan wajib diisi!")
            return

        try:
            MDApp.get_running_app().db.edit_golongan( 
                data['kode_golongan'],
                data['nama_golongan'],
                data['margin_umum'],
                data['margin_resep'],
                data['margin_halodoc'],
                data['margin_cabang'],
                data['margin_karyawan'],
                data['margin_bpjs']
                )

            rows = MDApp.get_running_app().db.get_all_golongan()
            SessionCache.set_data_golongan(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_golongan_obat', 'right')

            self.bersihkan_field_insert_golongan()
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

#---------------------------------------------------------------------------------------------#

class DataPajak(Screen):
    def on_enter(self):
        self.selected_rows = set()
        self.checkbox_refs = {}
        self.load_table_data()
        self.show_table(self._rows)

    def load_table_data(self):
        self._rows = SessionCache.get_data_pajak()

    def show_table(self, rows):
        grid = self.ids.grid_pajak
        grid.clear_widgets()
        grid.cols = 3

        self.selected_rows.clear()
        self.checkbox_refs.clear()

        headers = ["Jenis Pajak", "Persen Pajak", "Pilih"]
        for header in headers:
            grid.add_widget(Factory.TabelLabel(text=header, bold=True))

        for row in rows:
            kode = str(row[0])
            for value in row:
                grid.add_widget(Factory.TabelLabel(text=str(value)))

            cb_box = Factory.TabelCheckBox()
            cb = cb_box.ids.checkbox
            self.checkbox_refs[kode] = cb
            cb.bind(active=lambda cb_obj, value, kode=kode: self.on_checkbox_toggle(kode, value))
            grid.add_widget(cb_box)

    def on_checkbox_toggle(self, kode, value):
        if value:
            self.selected_rows.add(kode)
        else:
            self.selected_rows.discard(kode)

    def hapus_terpilih(self):
        if not self.selected_rows:
            toast("Belum ada yang dipilih")
            return

        ids = list(self.selected_rows)
        pesan_konfirmasi = "Yakin ingin menghapus data berikut?\n\n" + "\n".join(ids)

        def confirm_hapus():
            db = MDApp.get_running_app().db
            deleted = 0
            for kode in ids:
                kode_bersih = self.bersihkan_field(kode)
                try:
                    if db.hapus_pajak(kode_bersih):
                        deleted += 1
                    else:
                        toast(f"Gagal hapus {kode_bersih}")
                except Exception as e:
                    toast(f"Error: {str(e)}")

            if deleted > 0:
                toast(f"{deleted} data berhasil dihapus")
                rows = db.get_all_pajak()
                SessionCache.set_data_pajak(rows)
                self.reload_table(rows)
                self.reset_centang()

        def batal_hapus():
            self.reset_centang()

        self.tampilkan_dialog(pesan_konfirmasi, on_yes=confirm_hapus, on_no=batal_hapus)

    def edit_data_pajak(self):
        if len(self.selected_rows) == 1:
            selected_kode = list(self.selected_rows)[0]
            selected_kode = self.bersihkan_field(selected_kode)
            for row in self._rows:
                if self.bersihkan_field(row[0]) == selected_kode:
                    data_row = row
                    break
            else:
                toast("Data tidak ditemukan.")
                return
            data = {
                "jenis_pajak": self.bersihkan_field(data_row[0]),
                "persen_pajak": self.bersihkan_field(data_row[1]),
            }
            screen_edit = self.manager.get_screen('edit_pajak')
            screen_edit.isi_data_edit_pajak(data)
            self.manager.current = 'edit_pajak'
            self.reset_centang()
        else:
            dialog = MDDialog(
                text="Pilih satu data saja untuk diedit!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
            self.reset_centang()

    def tampilkan_dialog(self, pesan, on_yes=None, on_no=None):
        dialog = MDDialog(
            text=pesan,
            buttons=[
                MDFlatButton(text="No", on_release=lambda x: (on_no() if on_no else None, dialog.dismiss())),
                MDFlatButton(text="Yes", on_release=lambda x: (on_yes() if on_yes else None, dialog.dismiss())),
            ],
        )
        dialog.open()

    def bersihkan_field(self, text):
        return re.sub(r'\[.*?\]', '', str(text)).strip() if text else ""

    def reload_table(self, rows):
        self.clear_table()
        self.show_table(rows)

    def reset_centang(self):
        for plu in list(self.selected_rows):
            if plu in self.checkbox_refs:
                self.checkbox_refs[plu].active = False
        self.selected_rows.clear()

    def clear_table(self):
        self.ids.grid_pajak.clear_widgets()

    def on_leave(self):
        self.clear_table()

class InsertPajak(Screen):
    def bersihkan_field_add_pajak(self):
        fields = [
            'jenis_pajak', 'persen_pajak'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def get_form_values(self):
        fields = [
            'jenis_pajak', 'persen_pajak'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values

    def simpan_data_pajak(self):
        data = self.get_form_values()

        if not data['jenis_pajak']:
            self.tampilkan_dialog("Jenis Pajak wajib diisi!")
            return

        try:
            MDApp.get_running_app().db.tambah_pajak( 
                data['jenis_pajak'], 
                data['persen_pajak']
                )

            rows = MDApp.get_running_app().db.get_all_pajak()
            SessionCache.set_data_pajak(rows)
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_pajak', 'right'))

        except Exception as e:
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()
            if setelah_dialog:
                self.bersihkan_field_add_pajak(), 
                setelah_dialog()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )
        dialog.open()

class EditPajak(Screen):
    def bersihkan_field_insert_pajak(self):
        fields = [
            'jenis_pajak', 'persen_pajak'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def isi_data_edit_pajak(self, data):
        self.bersihkan_field_insert_pajak()
        self._set_text_field('jenis_pajak', data, 'jenis_pajak')
        self._set_numeric_field('persen_pajak', data, 'persen_pajak')

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

    def get_form_values(self):
        fields = [
            'jenis_pajak', 'persen_pajak'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values
    
    def simpan_edit_pajak(self):
        data = self.get_form_values()
        if not data['jenis_pajak']:
            self.tampilkan_dialog("Jenis Pajak wajib diisi!")
            return

        try:
            MDApp.get_running_app().db.edit_pajak( 
                data['jenis_pajak'],
                data['persen_pajak']
                )

            rows = MDApp.get_running_app().db.get_all_pajak()
            SessionCache.set_data_pajak(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_pajak', 'right')

            self.bersihkan_field_insert_pajak()
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

#---------------------------------------------------------------------------------------------#

class Kasir(Screen):
    hasil_pencarian = ListProperty()
    daftar_belanja = ListProperty()
    total_akhir = NumericProperty(0)
    kembalian = NumericProperty(0)
    poin_pelanggan = NumericProperty(0)
    is_kredit = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)
        self.no_ref_sedang_diedit = None
        self.mode_edit = False

    def on_pre_enter(self):
        if not getattr(self, 'mode_edit', False):
            self.ids.diskon_rp.text = ''
            self.ids.diskon_persen.text = ''
            self.ids.ongkir_input.text = ''
            self.ids.uang_pelanggan_input.text = ''
            self.reset_form_kasir()
            self.update_totals()

    def update_totals(self):
        total_belanja = sum(item['total'] for item in self.daftar_belanja)
        diskon_id = get_digits_only(self.ids.diskon_rp.text)
        ongkir_id = get_digits_only(self.ids.ongkir_input.text)
        uang_pelanggan_id = get_digits_only(self.ids.uang_pelanggan_input.text)
        total_setelah_diskon = total_belanja

        if diskon_id:
            try:
                total_setelah_diskon = total_belanja - int(diskon_id)
            except ValueError:
                total_setelah_diskon = 0

        elif self.ids.diskon_persen.text:
            try:
                persen = int(self.ids.diskon_persen.text)
                if persen > 100:
                    persen = 100
                    self.ids.diskon_persen.text = '100'
                total_setelah_diskon = total_belanja * (1 - (persen / 100.0))
            except ValueError:
                total_setelah_diskon = 0

        try:
            ongkir = int(ongkir_id) if ongkir_id else 0
        except ValueError:
            ongkir = 0
            
        total_setelah_ongkir = total_setelah_diskon + ongkir

        self.total_akhir = total_setelah_ongkir
        self.ids.total_setelah_diskon.text = "Total Setelah Diskon = Rp{:,.0f}".format(total_setelah_diskon).replace(',', '.')
        self.ids.total_setelah_ongkir.text = "Total Setelah Ongkir = Rp{:,.0f}".format(total_setelah_ongkir).replace(',', '.')

        try:
            uang_pelanggan = int(uang_pelanggan_id) if uang_pelanggan_id else 0
            kembalian = uang_pelanggan - total_setelah_ongkir
            self.kembalian = max(0, kembalian)
            self.ids.kembalian_label.text = "Kembalian     : Rp{:,.0f}".format(self.kembalian).replace(',', '.')
        except (ValueError, AttributeError):
            self.kembalian = 0
            self.ids.kembalian_label.text = "Kembalian     : Rp.0"

    def update_time(self, dt):
        current_time = datetime.now().strftime('%Y-%m-%d || %H:%M:%S')
        time_label = self.ids.get('time_label')
        if time_label:
            time_label.text = f'{current_time}'

    def tampilkan_popup_obat(self, hasil_pencarian):
        layout = Factory.PopupLayout()
        tombol_layout = layout.ids.tombol_layout

        for obat in hasil_pencarian:
            nama, satuan, harga = obat
            btn = Button(
                text=f"{nama} ({satuan}) - Rp{harga}",
                size_hint_y=None,
                height=40
            )

            btn.bind(on_release=lambda btn, data=obat: (self.tambah_ke_keranjang(data[0], data[1], data[2]), popup.dismiss()))
            tombol_layout.add_widget(btn)

        popup = Popup(
            title="Pilih Obat",
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        popup.open()

    def tambah_ke_keranjang(self, nama, satuan, harga):
        harga_int = int(harga)
        self.daftar_belanja.append({
            'nama': nama,
            'satuan': satuan,
            'harga': int(round(harga_int / 500.0) * 500),
            'qty': 1,
            'diskon': 0,
            'total': int(round(harga_int / 500.0) * 500),
        })
        self.update_totals()
        self.refresh_keranjang()

    def update_item(self, index, qty_str, diskon_str):
        try:
            item = self.daftar_belanja[index]
            harga = int(round(item['harga'] / 500.0) * 500)
            qty = int(qty_str.strip()) if qty_str.strip().isdigit() else 1
            diskon = int(diskon_str.strip()) if diskon_str.strip().isdigit() else 0
            qty = max(min(qty, 999), 1)
            diskon = max(min(diskon, 100), 0)
            total = round((harga * qty) * (1 - (diskon / 100)) / 500.0) * 500
            self.daftar_belanja[index]['qty'] = qty
            self.daftar_belanja[index]['diskon'] = diskon
            self.daftar_belanja[index]['total'] = int(total)
            self.update_totals()
            self.refresh_keranjang()
        except Exception as e:
            self.tampilkan_popup("Error saat memperbarui item. Pastikan input valid. PESAN ERROR: " + str(e))

    def hapus_item(self, index):
        if 0 <= index < len(self.daftar_belanja):
            del self.daftar_belanja[index]
            self.update_totals()
            self.refresh_keranjang()

    def refresh_keranjang(self):
        self.ids.keranjang_view.data = [
            {
                'index': i,
                'nama': item['nama'],
                'satuan': item['satuan'],
                'harga': item['harga'],
                'qty': item['qty'],
                'diskon': item['diskon'],
                'total': item['total'],
            }
            for i, item in enumerate(self.daftar_belanja)
        ]

    def cari_obat(self, keyword):
        jenis = self.ids.jenis_pelanggan_spinner.text
        hasil = MDApp.get_running_app().db.search_data_obat(keyword, jenis)
        if hasil:
            self.tampilkan_popup_obat(hasil)
        else:
            self.tampilkan_popup("Obat tidak ditemukan")

    def open_cara_bayar_popup(self):
        popup = Popup(
            title='Informasi',
            content=Label(text='Menu Cara Bayar'),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True
        )
        popup.open()

    def toggle_kredit(self, value):
        self.is_kredit = value
        if not value:
            self.ids.input_tanggal_tempo.text = ''

    def generate_no_ref(self):
        last = MDApp.get_running_app().db.automatis_no_ref()
        if last and last[0].isdigit():
            last_number = int(last[0])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{new_number:07d}"
    
    def periksa_pelanggan_kosong(self, input_widget):
        if not input_widget.focus and input_widget.text.strip() == "":
            self.ids.label_nama_pelanggan.text = "Umum"

    def cari_pelanggan(self, keyword):
        hasil = MDApp.get_running_app().db.search_data_pelanggan(keyword)
        if hasil:
            self.tampilkan_popup_pelanggan(hasil)
        else:
            self.tampilkan_popup("pelanggan tidak ditemukan")

    def tampilkan_popup_pelanggan(self, daftar_pelanggan):
        layout = Factory.PopupLayoutPelanggan()
        tombol_layout = layout.ids.tombol_layout

        popup = Popup(
            title="Pilih PELANGGAN",
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        for pelanggan in daftar_pelanggan:
            _, nama, no_telp, alamat, poin = pelanggan
            self.poin_pelanggan = poin
            btn = Button(
                text=f"{nama} ({no_telp}) - {alamat} - Poin: {poin}",
                size_hint_y=None,
                height=40
            )

            btn.bind(on_release=lambda btn, data=pelanggan: (
                setattr(self.ids.label_nama_pelanggan, 'text', data[1]),
                setattr(self.ids.input_nama_pelanggan, 'text', ''),
                setattr(self.ids.label_poin_pelanggan, 'text', f"Poin: {self.poin_pelanggan}"),
                popup.dismiss()
            ))
            tombol_layout.add_widget(btn)
        popup.open()

    def simpan_transaksi(self):
        db = MDApp.get_running_app().db
        now = datetime.now()
        if not self.mode_edit:
            no_ref = self.generate_no_ref()
        else:
            no_ref = self.no_ref_sedang_diedit
        nama_pelanggan = self.ids.label_nama_pelanggan.text.strip()
        pelanggan = db.get_id_pelanggan(nama_pelanggan) if nama_pelanggan != "Umum" else None
        kredit = 1 if self.is_kredit else 0
        tanggal_tempo = self.ids.input_tanggal_tempo.text if kredit else None
        cara_bayar = self.ids.cara_bayar.text
        jenis_pelanggan = self.ids.jenis_pelanggan_spinner.text
        nama_kasir = "User_percobaan"
        tanggal = now.strftime("%Y-%m-%d")

        try:
            diskon = int(self.ids.diskon_rp.text)
        except ValueError:
            diskon = 0
        try:
            ongkir = int(self.ids.ongkir_input.text)
        except ValueError:
            ongkir = 0
        try:
            pembayaran = int(get_digits_only(self.ids.uang_pelanggan_input.text))
        except ValueError:
            pembayaran = 0
        total = self.total_akhir
        if self.mode_edit:
            db.edit_transaksi(no_ref, tanggal=tanggal, id_pelanggan=pelanggan, kredit=kredit, tanggal_tempo=tanggal_tempo, cara_bayar=cara_bayar, jenis_pelanggan=jenis_pelanggan, diskon_toko=diskon, ongkir=ongkir, total_penjualan=total, pembayaran=pembayaran, nama_kasir=nama_kasir)
            db.hapus_data_transaksi_item(no_ref)
        else:
            db.new_transaksi(no_ref, tanggal, pelanggan, kredit, tanggal_tempo, cara_bayar,
                            jenis_pelanggan, diskon, ongkir, total, pembayaran, nama_kasir)

        for item in self.daftar_belanja:
            db.new_transaksi_item(no_ref, item['nama'], item['satuan'], item['harga'],
                                item['qty'], item['diskon'], item['total'])
            
        self.daftar_belanja.clear()
        self.refresh_keranjang()
        self.update_totals()
        self.mode_edit = False
        self.no_ref_sedang_diedit = None
        self.reset_form_kasir()

        self.tampilkan_popup("Transaksi berhasil disimpan!")
        
    def tampilkan_popup(self, pesan):
        popup = Popup(
            title="Info",
            content=Label(text=pesan),
            size_hint=(None, None),
            size=(300, 150)
        )
        popup.open()

    def load_transaksi(self, no_ref):
        self.no_ref_sedang_diedit = no_ref
        self.mode_edit = True
        db = MDApp.get_running_app().db
        transaksi = db.get_transaksi_by_no_ref(no_ref)
        if not transaksi:
            self.tampilkan_popup("Transaksi tidak ditemukan")
            return

        nama_pelanggan = db.get_nama_pelanggan_by_id(transaksi[2]) if transaksi[2] else "Umum"
        self.ids.label_nama_pelanggan.text = nama_pelanggan
        if nama_pelanggan != "Umum":
            self.ids.label_poin_pelanggan.text = f"Poin: {db.get_poin_pelanggan(nama_pelanggan)}"
        else:
            self.ids.label_poin_pelanggan.text = "Poin: 0"

        self.ids.jenis_pelanggan_spinner.text = str(transaksi[6])
        self.is_kredit = transaksi[3] == 1
        self.ids.toggle_kredit.state = 'down' if self.is_kredit else 'normal'
        self.ids.input_tanggal_tempo.text = transaksi[4] or ''
        self.ids.cara_bayar.text = transaksi[5]
        self.ids.diskon_rp.text = str(int(transaksi[7]))
        self.ids.diskon_persen.text = ''
        self.ids.ongkir_input.text = str(int(transaksi[8]))
        self.ids.uang_pelanggan_input.text = str(int(transaksi[10]))
        item_list = db.get_transaksi_item_by_no_ref(no_ref)
        self.daftar_belanja.clear()
        for item in item_list:
            self.daftar_belanja.append({
                'nama': item[2],
                'satuan': item[3],
                'harga': int(item[4]),
                'qty': int(item[5]),
                'diskon': int(item[6]),
                'total': int(item[7]),
            })

        self.refresh_keranjang()
        self.update_totals()

    def reset_form_kasir(self):
        if not self.mode_edit:
            self.no_ref_sedang_diedit = None

        self.ids.label_nama_pelanggan.text = "Umum"
        self.ids.label_poin_pelanggan.text = "Poin: 0"
        self.ids.input_tanggal_tempo.text = ''
        self.ids.jenis_pelanggan_spinner.text = 'Umum'
        self.ids.diskon_rp.text = ''
        self.ids.diskon_persen.text = ''
        self.ids.ongkir_input.text = ''
        self.ids.uang_pelanggan_input.text = ''
        self.ids.kembalian_label.text = "Kembalian     : Rp.0"
        self.ids.total_setelah_diskon.text = "Total Setelah Diskon = Rp.0"
        self.ids.total_setelah_ongkir.text = "Total Setelah Ongkir = Rp.0"
        self.ids.cara_bayar.text = "Tunai"
        self.is_kredit = False
        self.ids.input_tanggal_tempo.disabled = True
        self.daftar_belanja.clear()
        self.refresh_keranjang()
        self.total_akhir = 0
        self.kembalian = 0
        self.mode_edit = False
        self.update_totals()

    def hapus_transaksi(self, no_ref):
        db = MDApp.get_running_app().db
        db.hapus_transaksi(no_ref)
        toast(f"Transaksi {no_ref} telah dihapus.")
        Clock.schedule_once(lambda dt: self.manager.get_screen('riwayat_transaksi').muat_riwayat_transaksi(), 0.2)
        self.manager.current = 'riwayat_transaksi'

    def konfirmasi_hapus_transaksi(self, no_ref):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Label(text=f"Yakin ingin menghapus transaksi {no_ref}?", halign='center'))

        tombol = BoxLayout(spacing=10, size_hint_y=None, height=40)
        btn_ya = Button(text="Ya")
        btn_tidak = Button(text="Tidak")
        tombol.add_widget(btn_ya)
        tombol.add_widget(btn_tidak)
        layout.add_widget(tombol)

        popup = Popup(title='Konfirmasi Hapus', content=layout, size_hint=(None, None), size=(400, 200), auto_dismiss=False)

        btn_ya.bind(on_release=lambda *args: (self.hapus_transaksi(no_ref), popup.dismiss()))
        btn_tidak.bind(on_release=popup.dismiss)

        popup.open()
        
class KeranjangItem(BoxLayout):
    index = NumericProperty()
    nama = StringProperty()
    satuan = StringProperty()
    harga = NumericProperty()
    qty = NumericProperty()
    diskon = NumericProperty()
    total = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_scheduled = False

    def _do_update(self, *args):
        app = MDApp.get_running_app()
        kasir_screen = app.root.get_screen('Kasir')
        kasir_screen.update_item(self.index, str(self.qty), str(self.diskon))
        self._update_scheduled = False

    def on_qty_changed(self, qty_text):
        qty_text = qty_text.strip()
        self.qty = int(qty_text) if qty_text.isdigit() else 1
        if not self._update_scheduled:
            Clock.schedule_once(self._do_update, 0)
            self._update_scheduled = True

    def on_diskon_changed(self, diskon_text):
        diskon_text = diskon_text.strip()
        self.diskon = int(diskon_text) if diskon_text.isdigit() else 0
        if not self._update_scheduled:
            Clock.schedule_once(self._do_update, 0)
            self._update_scheduled = True

class RowRiwayat(GridLayout):
    tanggal = StringProperty()
    no_ref = StringProperty()
    pelanggan = StringProperty()
    kredit = StringProperty()
    tempo = StringProperty()
    cara_bayar = StringProperty()
    harga = StringProperty()
    total = StringProperty()
    kasir = StringProperty()
    status = StringProperty()

class RiwayatTransaksi(Screen):
    def muat_riwayat_transaksi(self):
        db = MDApp.get_running_app().db
        semua = db.get_all_transaksi()
        rv_data = []

        for tr in semua:
            tanggal = tr[1]
            no_ref = tr[0]
            pelanggan = db.get_nama_pelanggan_by_id(tr[2]) or "Umum"
            kredit = str(tr[3])
            tempo = tr[4] or '-'
            cara_bayar = tr[5]
            harga = f"Rp{int(tr[9]):,}".replace(",", ".")
            total = f"Rp{int(tr[10]):,}".replace(",", ".")
            kasir = tr[11]
            status = tr[12] if len(tr) > 12 else 'normal'

            rv_data.append({
                'tanggal': tanggal,
                'no_ref': no_ref,
                'pelanggan': pelanggan,
                'kredit': kredit,
                'tempo': tempo,
                'cara_bayar': cara_bayar,
                'harga': harga,
                'total': total,
                'kasir': kasir,
                'status': status
            })

        self.ids.rv_riwayat.data = rv_data

#---------------------------------------------------------------------------------------------#

class WindowsManager(ScreenManager):
    pass

#---------------------------------------------------------------------------------------------#

class DookaApp(MDApp):
    def build(self):
        Window.size = (1200, 800)
        Window.set_icon("assets\image\DOOKA_Logo_besar.png")
        self.db = DatabaseObat("database/dooka_user.db")
        self.formatter = FormatHelper()

        if not SessionCache.get_data_obat():
            SessionCache.set_data_obat(self.db.get_all_obat())

        if not SessionCache.get_data_golongan():
            SessionCache.set_data_golongan(self.db.get_all_golongan())

        if not SessionCache.get_data_pajak():
            SessionCache.set_data_pajak(self.db.get_all_pajak())

        return Builder.load_file('user_interface/gui.kv')
    
    def on_stop(self):
        if hasattr(self, "db"):
            self.db.close_connection()
    
    def change_screen(self, screen_name, direction):
        self.root.transition.direction = direction
        self.root.current = screen_name