# Built-in modules
import re, json, os
from datetime import datetime

# Local modules
from database.db import DatabaseObat
from utils.formatting import FormatHelper, get_digits_only, date_only
from utils.settings_manager import SettingsManager

# KivyMD modules
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
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
    _data_pelanggan = []

    @classmethod
    def get_data_obat(cls):
        return cls._data_obat
    
    @classmethod
    def set_data_obat(cls, data):
        cls._data_obat = data

    @classmethod
    def clear_data_obat(cls):
        cls._data_obat = []

    #---------------------------------------------------------------------------------------------#
    @classmethod
    def get_data_golongan(cls):
        return cls._data_golongan
    
    @classmethod
    def set_data_golongan(cls, data):
        cls._data_golongan = data

    @classmethod
    def clear_data_golongan(cls):
        cls._data_golongan = []

    #---------------------------------------------------------------------------------------------#

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

    @classmethod
    def get_data_pelanggan(cls):    
        return cls._data_pelanggan

    @classmethod
    def set_data_pelanggan(cls, data):
        cls._data_pelanggan = data

    @classmethod
    def clear_data_pelanggan(cls):
        cls._data_pelanggan = []

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
            MDApp.get_running_app().change_screen('edit_obat', 'left')
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
        data['plu'] = str(data['plu']).zfill(6)
        # HANDLING ERRORS
        if not data['jenis']:
            self.tampilkan_dialog("Jenis Produk wajib diisi!")
            return
        if not data['plu'] or not data['plu'].isdigit():
            self.tampilkan_dialog("PLU wajib diisi dan harus angka!")
            return
        duplicate = MDApp.get_running_app().db.is_plu_exist(data['plu'])
        if duplicate:
            self.tampilkan_dialog(f"PLU '{data['plu']}' sudah terdaftar untuk produk '{duplicate[0]}' pada rak '{duplicate[1]}'. Gunakan PLU lain.")
            return
        if not data['nama_produk']:
            self.tampilkan_dialog("Nama Produk wajib diisi!")
            return
        if not data['satuan']:
            self.tampilkan_dialog("Satuan wajib diisi!")
            return
        if not kode_golongan:
            self.tampilkan_dialog("Golongan wajib dipilih!")
            return
        if not data['rak']:
            self.tampilkan_dialog("Rak wajib diisi!")
            return
        if not re.fullmatch(r'[A-Za-z0-9]+', data['rak']):
            self.tampilkan_dialog("Rak hanya boleh berisi huruf dan angka, contoh: A1, B2, C10.")
            return
        if not data['supplier']:
            self.tampilkan_dialog("Supplier wajib diisi!")
            return
        if not data['fast_moving']or not "ya" in data['fast_moving'].lower() and not "tidak" in data['fast_moving'].lower():
            self.tampilkan_dialog("Fast Moving wajib diisi! (wajib Ya atau Tidak)")
            return
        if not data['kemasan_beli']:
            self.tampilkan_dialog("Kemasan Beli wajib diisi!")
            return
        if not data['isi'] or not data['isi'].isdigit():
            self.tampilkan_dialog("Isi harus diisi dan harus berupa angka!")
            return
        if not data['tanggal_kadaluarsa'] or not date_only(data['tanggal_kadaluarsa']):
            self.tampilkan_dialog("tanggal harus diisi atau Format tanggal salah! Gunakan format YYYY-MM-DD")
            return
        if not data['stok_apotek'] or not data['stok_apotek'].isdigit():
            self.tampilkan_dialog("Stok Apotek harus diisi dan harus berupa angka!")
            return
        stok_apotek = int(data['stok_apotek'])
        if stok_apotek < 1 or stok_apotek > 1000:
            self.tampilkan_dialog("Stok Apotek harus antara 1 dan 1000!")
            return
        if not data['stok_min'] or not data['stok_min'].isdigit():
            self.tampilkan_dialog("Stok Min harus diisi dan harus berupa angka!")
            return
        stok_min = int(data['stok_min'])
        max_stok_min = stok_apotek // 2
        if stok_min < 1 or stok_min > max_stok_min:
            self.tampilkan_dialog(f"Stok Min harus antara 1 dan {max_stok_min} (tidak lebih dari 50% stok)!")
            return
        if not data['stok_max'] or not data['stok_max'].isdigit():
            self.tampilkan_dialog("Stok Max harus diisi dan harus berupa angka!")
            return
        stok_max = int(data['stok_max'])
        min_stok_max = stok_apotek // 2
        if stok_max < min_stok_max or stok_max > 1000:
            self.tampilkan_dialog(f"Stok Max harus antara {min_stok_max} dan 1000 (tidak boleh kurang dari 50% stok)!")
            return
        if not kode_ppn:
            self.tampilkan_dialog("Pajak wajib dipilih!")
            return
        #_____________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
        margin_data = MDApp.get_running_app().db.get_margin_golongan(kode_golongan)
        harga_beli = int(get_digits_only(data['harga_beli']))
        harga_resep = round(harga_beli * (1 + margin_data['margin_resep'] / 100))
        harga_umum = round(harga_beli * (1 + margin_data['margin_umum'] / 100))
        harga_cabang = round(harga_beli * (1 + margin_data['margin_cabang'] / 100))
        harga_halodoc = round(harga_beli * (1 + margin_data['margin_halodoc'] / 100))
        harga_karyawan = round(harga_beli * (1 + margin_data['margin_karyawan'] / 100))
        harga_bpjs = round(harga_beli * (1 + margin_data['margin_bpjs'] / 100))
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
                stok_apotek, 
                stok_min, 
                stok_max, 
                kode_ppn)

            rows = MDApp.get_running_app().db.get_all_obat()
            SessionCache.set_data_obat(rows)
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_obat', 'right'))

        except Exception as e:
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        dialog = None

        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            def on_tutup(*args):
                self.bersihkan_field_add_obat()
                setelah_dialog()
            dialog.bind(on_dismiss=on_tutup)

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

    def bersihkan_field_edit_obat(self):
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
        kode_golongan = self.kode_golongan_aktif
        nama_golongan = self.kode_golongan_nama
        kode_ppn = self.kode_pajak_nama
        # HANDLING ERRORS
        if not data['jenis']:
            self.tampilkan_dialog("Jenis Produk wajib diisi!")
            return
        if not data['nama_produk']:
            self.tampilkan_dialog("Nama Produk wajib diisi!")
            return
        if not data['satuan']:
            self.tampilkan_dialog("Satuan wajib diisi!")
            return
        if not kode_golongan:
            self.tampilkan_dialog("Golongan wajib dipilih!")
            return
        if not data['rak']:
            self.tampilkan_dialog("Rak wajib diisi!")
            return
        if not re.fullmatch(r'[A-Za-z0-9]+', data['rak']):
            self.tampilkan_dialog("Rak hanya boleh berisi huruf dan angka, contoh: AA, 01, A1, B2.")
            return
        if not data['supplier']:
            self.tampilkan_dialog("Supplier wajib diisi!")
            return
        if not data['fast_moving']or not "ya" in data['fast_moving'].lower() and not "tidak" in data['fast_moving'].lower():
            self.tampilkan_dialog("Fast Moving wajib diisi! (wajib Ya atau Tidak)")
            return
        if not data['kemasan_beli']:
            self.tampilkan_dialog("Kemasan Beli wajib diisi!")
            return
        if not data['isi'] or not data['isi'].isdigit():
            self.tampilkan_dialog("Isi harus diisi dan harus berupa angka!")
            return
        if not data['tanggal_kadaluarsa'] or not date_only(data['tanggal_kadaluarsa']):
            self.tampilkan_dialog("tanggal harus diisi atau Format tanggal salah! Gunakan format YYYY-MM-DD")
            return
        stok_apotek = int(data['stok_apotek'])
        if stok_apotek < 1 or stok_apotek > 1000:
            self.tampilkan_dialog("Stok Apotek harus antara 1 dan 1000!")
            return
        if not data['stok_min'] or not data['stok_min'].isdigit():
            self.tampilkan_dialog("Stok Min harus diisi dan harus berupa angka!")
            return
        stok_min = int(data['stok_min'])
        max_stok_min = stok_apotek // 2
        if stok_min < 1 or stok_min > max_stok_min:
            self.tampilkan_dialog(f"Stok Min harus antara 1 dan {max_stok_min} (tidak lebih dari 50% stok)!")
            return
        if not data['stok_max'] or not data['stok_max'].isdigit():
            self.tampilkan_dialog("Stok Max harus diisi dan harus berupa angka!")
            return
        stok_max = int(data['stok_max'])
        min_stok_max = stok_apotek // 2
        if stok_max < min_stok_max or stok_max > 1000:
            self.tampilkan_dialog(f"Stok Max harus antara {min_stok_max} dan 1000 (tidak boleh kurang dari 50% stok)!")
            return
        if not kode_ppn:
            self.tampilkan_dialog("Pajak wajib dipilih!")
            return
        #_____________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
        try:
            db = MDApp.get_running_app().db
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
                data['kemasan_beli'], data['isi'], data['tanggal_kadaluarsa'], stok_apotek,
                stok_min, stok_max, kode_ppn
            )

            rows = MDApp.get_running_app().db.get_all_obat()
            SessionCache.set_data_obat(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_obat', 'right')

            self.bersihkan_field_edit_obat()
            self.tampilkan_dialog("Data berhasil diperbarui!", setelah_dialog=setelah_ditutup)

        except Exception as e:
            self.tampilkan_dialog(f"Error saat update: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            dialog.bind(on_dismiss=lambda *args: setelah_dialog())

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
        grid.cols = 9

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
            MDApp.get_running_app().change_screen('edit_golongan_obat', 'left')
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
        # HANDLING ERRORS
        if not data['nama_golongan']:
            self.tampilkan_dialog("Nama Golongan wajib diisi!")
            return
        #______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
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
        dialog = None

        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            def on_tutup(*args):
                self.bersihkan_field_add_golongan()
                setelah_dialog()
            dialog.bind(on_dismiss=on_tutup)

        dialog.open()

class EditGolonganObat(Screen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(self.reset_scroll, 0.1)

    def reset_scroll(self, dt):
        self.ids.scroll_edit_golongan.scroll_y = 1

    def bersihkan_field_edit_golongan(self):
        fields = [
            'kode_golongan','nama_golongan', 'margin_umum', 'margin_resep',
            'margin_cabang', 'margin_halodoc', 'margin_karyawan', 'margin_bpjs'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def isi_data_edit_golongan(self, data):
        self.bersihkan_field_edit_golongan()
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
        # HANDLING ERRORS
        if not data['nama_golongan']:
            self.tampilkan_dialog("Nama Golongan wajib diisi!")
            return
        #______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
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

            self.bersihkan_field_edit_golongan()
            self.tampilkan_dialog("Data berhasil diperbarui!", setelah_dialog=setelah_ditutup)

        except Exception as e:
            self.tampilkan_dialog(f"Error saat update: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            dialog.bind(on_dismiss=lambda *args: setelah_dialog())

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
            MDApp.get_running_app().change_screen('edit_pajak', 'left')
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
        # HANDLING ERRORS
        if not data['jenis_pajak']:
            self.tampilkan_dialog("Jenis Pajak wajib diisi!")
            return
        if not data['persen_pajak'] or not data['persen_pajak'].isdigit() or not (0 <= int(data['persen_pajak']) <= 30):
            self.tampilkan_dialog("Persen Pajak harus diisi dan harus berupa angka!(0-30%)")
            return
        #______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
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
        dialog = None

        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            def on_tutup(*args):
                self.bersihkan_field_add_pajak()
                setelah_dialog()
            dialog.bind(on_dismiss=on_tutup)

        dialog.open()

class EditPajak(Screen):
    def bersihkan_field_edit_pajak(self):
        fields = [
            'jenis_pajak', 'persen_pajak'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def isi_data_edit_pajak(self, data):
        self.bersihkan_field_edit_pajak()
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
        # HANDLING ERRORS
        if not data['jenis_pajak']:
            self.tampilkan_dialog("Jenis Pajak wajib diisi!")
            return
        if not data['persen_pajak'] or not data['persen_pajak'].isdigit() or not (0 <= int(data['persen_pajak']) <= 30):
            self.tampilkan_dialog("Persen Pajak harus diisi dan harus berupa angka!(0-30%)")
            return
        #______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
        try:
            MDApp.get_running_app().db.edit_pajak( 
                data['jenis_pajak'],
                data['persen_pajak']
                )

            rows = MDApp.get_running_app().db.get_all_pajak()
            SessionCache.set_data_pajak(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_pajak', 'right')

            self.bersihkan_field_edit_pajak()
            self.tampilkan_dialog("Data berhasil diperbarui!", setelah_dialog=setelah_ditutup)

        except Exception as e:
            self.tampilkan_dialog(f"Error saat update: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        # Pastikan tetap dijalankan meskipun user tidak klik tombol
        if setelah_dialog:
            dialog.bind(on_dismiss=lambda *args: setelah_dialog())

        dialog.open()

#---------------------------------------------------------------------------------------------#

class DataPelanggan(Screen):
    def on_enter(self):
        self.selected_rows = set()
        self.checkbox_refs = {}
        self.load_table_data()
        self.show_table(self._rows)

    def load_table_data(self):
        self._rows = SessionCache.get_data_pelanggan()

    def show_table(self, rows):
        grid = self.ids.grid_pelanggan
        grid.clear_widgets()
        grid.cols = 6

        self.selected_rows.clear()
        self.checkbox_refs.clear()

        headers = ["ID", "Nama", "Nomer Telefon", "Alamat", "Poin", "Pilih"]
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
        db = MDApp.get_running_app().db
        if not self.selected_rows:
            toast("Belum ada yang dipilih")
            return
        ids = list(self.selected_rows)
        pesan_list = []
        for i, id_ in enumerate(ids, 1):
            nama = db.get_nama_pelanggan_by_id(id_)
            nama = nama or "Tidak ditemukan"
            pesan_list.append(f"{i}. {id_} - {nama}")
        pesan_konfirmasi = "Yakin ingin menghapus data berikut?\n\n" + "\n".join(pesan_list)

        def confirm_hapus():
            db = MDApp.get_running_app().db
            deleted = 0
            for kode in ids:
                kode_bersih = self.bersihkan_field(kode)
                try:
                    if db.hapus_pelanggan(kode_bersih):
                        deleted += 1
                    else:
                        toast(f"Gagal hapus {kode_bersih}")
                except Exception as e:
                    toast(f"Error: {str(e)}")

            if deleted > 0:
                toast(f"{deleted} data berhasil dihapus")
                rows = db.get_all_pelanggan()
                SessionCache.set_data_pelanggan(rows)
                self.reload_table(rows)
                self.reset_centang()

        def batal_hapus():
            self.reset_centang()

        self.tampilkan_dialog(pesan_konfirmasi, on_yes=confirm_hapus, on_no=batal_hapus)

    def edit_data_pelanggan(self):
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
                "id": data_row[0],
                "nama_pelanggan": self.bersihkan_field(data_row[1]),
                "nomor_telfon": self.bersihkan_field(data_row[2]),
                "alamat": self.bersihkan_field(data_row[3]),
                "poin": data_row[4],
            }
            screen_edit = self.manager.get_screen('edit_pelanggan')
            screen_edit.isi_data_edit_pelanggan(data)
            MDApp.get_running_app().change_screen('edit_pelanggan', 'left')
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
        self.ids.grid_pelanggan.clear_widgets()

    def on_leave(self):
        self.clear_table()

class InsertPelanggan(Screen):
    def bersihkan_field_add_pelanggan(self):
        fields = [
            'nama_pelanggan', 'nomor_telfon', 'alamat'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""

    def get_form_values(self):
        fields = [
            'nama_pelanggan', 'nomor_telfon', 'alamat'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values

    def simpan_data_pelanggan(self):
        data = self.get_form_values()
        # HANDLING ERRORS
        if not data['nama_pelanggan']:
            self.tampilkan_dialog("Nama Pelanggan wajib diisi!")
            return
        nomor = data['nomor_telfon']
        if not nomor:
            self.tampilkan_dialog("Nomor Telepon wajib diisi!")
            return
        nomor_bersih = re.sub(r'[^\d+]', '', nomor)
        if nomor_bersih.startswith('+62'):
            nomor_normal = nomor_bersih
        elif nomor_bersih.startswith('62'):
            nomor_normal = '+' + nomor_bersih
        elif nomor_bersih.startswith('08'):
            nomor_normal = '+62' + nomor_bersih[1:]
        else:
            self.tampilkan_dialog("Nomor Telepon harus diawali dengan 08, 62, atau +62")
            return
        if not re.fullmatch(r'\+62\d{8,13}', nomor_normal):
            self.tampilkan_dialog("Format Nomor Telepon tidak valid! Contoh: 08123456789 atau +628123456789")
            return
        data['nomor_telfon'] = nomor_normal
        if not data['alamat']:
            self.tampilkan_dialog("Alamat wajib diisi!")
            return
        #_______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
        try:
            MDApp.get_running_app().db.tambah_pelanggan(
                data['nama_pelanggan'], 
                data['nomor_telfon'],
                data['alamat'],
                )

            rows = MDApp.get_running_app().db.get_all_pelanggan()
            SessionCache.set_data_pelanggan(rows)
            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_pelanggan', 'right'))

        except Exception as e:
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        dialog = None

        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            def on_tutup(*args):
                self.bersihkan_field_add_pelanggan()
                setelah_dialog()
            dialog.bind(on_dismiss=on_tutup)

        dialog.open()

class EditPelanggan(Screen):
    def bersihkan_field_edit_pelanggan(self):
        fields = [
            'nama_pelanggan', 'nomor_telfon', 'alamat'
        ]
        for field in fields:
            text_input = self.ids.get(field)
            if text_input:
                text_input.text = ""
                
    def get_form_values(self):
        fields = [
            'id', 'nama_pelanggan', 'nomor_telfon', 'alamat', 'poin'
        ]
        values = {}
        for field in fields:
            text_input = self.ids.get(field)
            values[field] = text_input.text if text_input else ""

        return values

    def isi_data_edit_pelanggan(self, data):
        self.bersihkan_field_edit_pelanggan()
        self._set_numeric_field('id', data, 'id')
        self._set_text_field('nama_pelanggan', data, 'nama_pelanggan')
        self._set_numeric_field('nomor_telfon', data, 'nomor_telfon')
        self._set_text_field('alamat', data, 'alamat')
        self._set_numeric_field('poin', data, 'poin')

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
    
    def simpan_edit_pelanggan(self):
        data = self.get_form_values()
        # HANDLING ERRORS
        if not data['nama_pelanggan']:
            self.tampilkan_dialog("Nama Pelanggan wajib diisi!")
            return
        
        nomor = data['nomor_telfon']
        if not nomor:
            self.tampilkan_dialog("Nomor Telepon wajib diisi!")
            return
        nomor_bersih = re.sub(r'[^\d+]', '', nomor)
        if nomor_bersih.startswith('+62'):
            nomor_normal = nomor_bersih
        elif nomor_bersih.startswith('62'):
            nomor_normal = '+' + nomor_bersih
        elif nomor_bersih.startswith('08'):
            nomor_normal = '+62' + nomor_bersih[1:]
        else:
            self.tampilkan_dialog("Nomor Telepon harus diawali dengan 08, 62, atau +62")
            return
        if not re.fullmatch(r'\+62\d{8,13}', nomor_normal):
            self.tampilkan_dialog("Format Nomor Telepon tidak valid! Contoh: 08123456789 atau +628123456789")
            return
        data['nomor_telfon'] = nomor_normal
        if not data['alamat']:
            self.tampilkan_dialog("Alamat wajib diisi!")
            return
        #_______________________________________________________________________________________#
        # Jika semua validasi lolos, simpan data
        try:
            MDApp.get_running_app().db.edit_pelanggan(
                data['id'],
                data['nama_pelanggan'], 
                data['nomor_telfon'],
                data['alamat'],
                data['poin'],
                )

            rows = MDApp.get_running_app().db.get_all_pelanggan()
            SessionCache.set_data_pelanggan(rows)

            def setelah_ditutup():
                MDApp.get_running_app().change_screen('data_pelanggan', 'right')

            self.bersihkan_field_edit_pelanggan()
            self.tampilkan_dialog("Data berhasil diperbarui!", setelah_dialog=setelah_ditutup)

        except Exception as e:
            self.tampilkan_dialog(f"Error saat update: {str(e)}")

    def tampilkan_dialog(self, pesan, setelah_dialog=None):
        def tutup_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            text=pesan,
            buttons=[MDFlatButton(text="OK", on_release=tutup_dialog)],
        )

        if setelah_dialog:
            dialog.bind(on_dismiss=lambda *args: setelah_dialog())

        dialog.open()

#---------------------------------------------------------------------------------------------#

class Kasir(Screen):
    hasil_pencarian = ListProperty()
    daftar_belanja = ListProperty()
    total_akhir = NumericProperty(0)
    kembalian = NumericProperty(0)
    poin_pelanggan = NumericProperty(0)
    is_kredit = BooleanProperty(False)
    is_non_tunai = BooleanProperty(False)
    terpending = None
    nama_pelanggan_aktif = StringProperty('')
    diskon_dari_poin = BooleanProperty(False)
    #METHODS#
    @property
    def pembulatan(self):
        return MDApp.get_running_app().settings_manager.get("pembulatan")
    @property
    def pembagian_perpoin(self):
        return MDApp.get_running_app().settings_manager.get("pembagian_perpoin")
    #INIT#
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)
        self.no_ref_sedang_diedit = None
        self.mode_edit = False
        self.last_diskon_input = ''

    def on_pre_enter(self):
        if not getattr(self, 'mode_edit', False):
            self.ids.diskon_rp.text = ''
            self.ids.diskon_persen.text = ''
            self.ids.ongkir_input.text = ''
            self.ids.uang_pelanggan_input.text = ''
            self.reset_form_kasir()
            self.update_totals()
    #KASIR#
    def update_totals(self):
        if hasattr(self, '_updating_diskon'):
            return
        self._updating_diskon = True
        try:
            total_belanja = sum(item['total'] for item in self.daftar_belanja)
        except:
            total_belanja = 0
        diskon_rp_text = self.ids.diskon_rp.text.strip()
        diskon_persen_text = self.ids.diskon_persen.text.strip()
        diskon_rp = get_digits_only(diskon_rp_text)
        diskon_persen = 0
        if self.last_diskon_input == 'persen' and diskon_persen_text:
            diskon_persen = int(diskon_persen_text)
            if diskon_persen > 100:
                diskon_persen = 100
                self.ids.diskon_persen.text = "100"
            diskon_rp = int(total_belanja * (diskon_persen / 100))
            self.ids.diskon_rp.text = f"{diskon_rp:,}".replace(",", ".")
        elif self.last_diskon_input == 'persen' and not diskon_persen_text:
            diskon_rp = 0
            self.ids.diskon_rp.text = ''
        elif self.last_diskon_input == 'rp' and diskon_rp_text:
            if not self.diskon_dari_poin:
                diskon_persen = round((diskon_rp / total_belanja) * 100) if total_belanja else 0
                self.ids.diskon_persen.text = str(diskon_persen)
            else:
                diskon_persen = 0
        elif self.last_diskon_input == 'rp' and not diskon_rp_text:
            diskon_persen = 0
            self.ids.diskon_persen.text = ''
        #LOGIKA POIN NANTI MASUK DISINI UNTUK PENGURANGAN POIN
        total_setelah_diskon = int(round((max(total_belanja - diskon_rp, 0))/float(self.pembulatan))*self.pembulatan)
        ongkir = get_digits_only(self.ids.ongkir_input.text)
        total_setelah_ongkir = int(round((max(total_setelah_diskon + ongkir, 0))/float(self.pembulatan))*self.pembulatan)
        self.total_akhir = total_setelah_ongkir
        # Jika checkbox aktif, maka diskon ini berasal dari poin
        if self.diskon_dari_poin and self.nama_pelanggan_aktif:
            if diskon_rp > self.poin_pelanggan:
                self.tampilkan_popup("Diskon poin melebihi poin pelanggan, menggunakan poin maksimum.")
                diskon_rp = 0
                self.ids.diskon_rp.text = ''
            else:
                self.ids.total_setelah_diskon.text = f"Total Setelah Diskon (Poin) = Rp{total_setelah_diskon:,.0f}".replace(",", ".")
        else:
            self.ids.total_setelah_diskon.text = f"Total Setelah Diskon = Rp{total_setelah_diskon:,.0f}".replace(",", ".")
        self.ids.total_setelah_ongkir.text = f"Total Setelah Ongkir = Rp{total_setelah_ongkir:,.0f}".replace(",", ".")
        uang_pelanggan = get_digits_only(self.ids.uang_pelanggan_input.text)
        kembalian = uang_pelanggan - total_setelah_ongkir
        self.kembalian = max(0, kembalian)
        self.ids.kembalian_label.text = f"Kembalian     : Rp{self.kembalian:,.0f}".replace(",", ".")
        if self.diskon_dari_poin:
            # Saat diskon dari poin aktif, hanya aktifkan input RP
            self.ids.diskon_rp.disabled = False
            self.ids.diskon_persen.disabled = True
        else:
            if self.last_diskon_input == 'rp' and diskon_rp_text:
                self.ids.diskon_persen.disabled = True
                self.ids.diskon_rp.disabled = False
            elif self.last_diskon_input == 'persen' and diskon_persen_text:
                self.ids.diskon_rp.disabled = True
                self.ids.diskon_persen.disabled = False
            else:
                self.ids.diskon_rp.disabled = False
                self.ids.diskon_persen.disabled = False
        del self._updating_diskon

    def tambah_ke_keranjang(self, nama, satuan, harga, plu):
        db = MDApp.get_running_app().db
        stok_obat = db.stok_obat(plu)
        stok_min = db.stok_min_obat(plu)
        if stok_obat <= stok_min:
            pesan = (f"Stok {nama} sudah mencapai batas minimum.\n"
                    f"Stok saat ini: {stok_obat}, batas minimum: {stok_min}")
            if stok_obat == 0:
                pesan += "\n⚠️ Stok 0 — pertimbangkan substitusi atau konfirmasi ke gudang."
            self.tampilkan_popup(pesan)
        try:
            harga_int = int(harga)
        except (TypeError, ValueError):
            harga_int = 0  # fallback aman
        harga_bulat = int(round(harga_int / self.pembulatan) * self.pembulatan)
        self.daftar_belanja.append({
            'plu': plu,
            'nama': nama,
            'satuan': satuan,
            'harga': harga_bulat,
            'qty': 1,
            'diskon': 0,
            'total': harga_bulat,
        })
        self.update_totals()
        self.refresh_keranjang()

    def update_item(self, index, qty_str, diskon_str):
        try:
            item = self.daftar_belanja[index]
            harga = int(round(item['harga'] / self.pembulatan) * self.pembulatan)
            qty = int(qty_str.strip()) if qty_str.strip().isdigit() else 1
            diskon = int(diskon_str.strip()) if diskon_str.strip().isdigit() else 0
            qty = max(min(qty, 999), 1)
            diskon = max(min(diskon, 100), 0)
            db = MDApp.get_running_app().db
            stok_obat = db.stok_obat(item['plu'])
            stok_min_obat = db.stok_min_obat(item['plu'])
            stok_sem = stok_obat - qty
            if qty > stok_obat:
                self.tampilkan_popup(
                    f"Qty yang dimasukkan ({qty}) melebihi stok ({stok_obat}). "
                    f"Qty disesuaikan ke stok maksimum."
                )
                qty = stok_obat
            if stok_sem < stok_min_obat:
                self.tampilkan_popup(f"Stok obat ini sudah-\nmencapai batas minimum.\nstok ketika dikurangi: {stok_sem}\nstok obat ini : {stok_obat}")
            total = round((harga * qty) * (1 - (diskon / 100)) / self.pembulatan) * self.pembulatan
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
        tanggal_input = self.ids.input_tanggal_tempo.text
        tanggal_tempo = date_only(tanggal_input)
        if kredit and not tanggal_tempo:
            self.tampilkan_popup("Format tanggal salah!\nGunakan format YYYY-MM-DD")
            return
        if self.is_non_tunai == 0:
            cara_bayar = "Tunai"
        else:
            cara_bayar = "Non Tunai"
        jenis_pelanggan = self.ids.jenis_pelanggan_spinner.text
        nama_kasir = "User_percobaan"
        tanggal = now.strftime("%Y-%m-%d")

        try:
            if self.diskon_dari_poin == True and self.nama_pelanggan_aktif:
                diskon = int(get_digits_only(self.ids.diskon_rp.text))
                db.pengurangan_poin_pelanggan(pelanggan, diskon)
            else:
                diskon = int(get_digits_only(self.ids.diskon_rp.text))
        except ValueError as e:
            print(f"Error parsing diskon: {e}")
            diskon = 0
        try:
            ongkir = int(get_digits_only(self.ids.ongkir_input.text))
        except ValueError as e:
            print(f"Error parsing ongkir: {e}")
            ongkir = 0
        try:
            pembayaran = int(get_digits_only(self.ids.uang_pelanggan_input.text))
        except ValueError as e:
            print(f"Error parsing pembayaran: {e}")
            pembayaran = 0
        total = self.total_akhir
        if self.mode_edit:
            db.pengurangan_poin_transaksi(no_ref)
            eligible_new = pelanggan is not None
            poin_baru = (total // self.pembagian_perpoin) if eligible_new else 0
            if eligible_new and poin_baru > 0:
                db.tambah_poin_pelanggan(pelanggan, poin_baru)
            db.edit_transaksi(no_ref, tanggal=tanggal, id_pelanggan=pelanggan, kredit=kredit, tanggal_tempo=tanggal_tempo, cara_bayar=cara_bayar, jenis_pelanggan=jenis_pelanggan, diskon_toko=diskon, ongkir=ongkir, total_penjualan=total, pembayaran=pembayaran, nama_kasir=nama_kasir, poin_didapat=poin_baru)
            db.hapus_data_transaksi_item(no_ref)
        else:
            eligible = pelanggan is not None
            poin_baru = (total // self.pembagian_perpoin) if eligible else 0
            if eligible and poin_baru > 0:
                db.tambah_poin_pelanggan(pelanggan, poin_baru)
            db.new_transaksi(no_ref, tanggal, pelanggan, kredit, tanggal_tempo, cara_bayar,
                            jenis_pelanggan, diskon, ongkir, total, pembayaran, nama_kasir, poin_baru)

        for item in self.daftar_belanja:
            db.stok_pengurangan_obat(item['plu'], item['qty'])
            db.new_transaksi_item(no_ref, item['nama'], item['satuan'], item['harga'],
                                item['qty'], item['diskon'], item['total'])
            
        stok_obat = db.stok_obat(item['plu'])
        stok_min_obat = db.stok_min_obat(item['plu'])
        if stok_obat <= stok_min_obat:
            self.tampilkan_popup(
                f"Stok {item['nama']} sudah mencapai batas minimum.\n"
                f"Stok saat ini: {stok_obat}, batas minimum: {stok_min_obat}"
            )
        self.daftar_belanja.clear()
        self.refresh_keranjang()
        self.update_totals()
        self.mode_edit = False
        self.no_ref_sedang_diedit = None
        self.reset_form_kasir()

        self.tampilkan_popup("Transaksi berhasil disimpan!")

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
        self.is_non_tunai = transaksi[5]
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
        self.last_diskon_input = ''
        self.is_non_tunai = False
        self.is_kredit = False
        self.nama_pelanggan_aktif = ''
        self.ids.input_tanggal_tempo.disabled = True
        self.daftar_belanja.clear()
        self.refresh_keranjang()
        self.total_akhir = 0
        self.kembalian = 0
        self.mode_edit = False
        self.update_totals()

    def hapus_transaksi(self, no_ref):
        db = MDApp.get_running_app().db
        db.pengurangan_poin_transaksi(no_ref)
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

    def pending_transaksi(self):
        if self.terpending:
            self.tampilkan_popup("Masih ada transaksi yang terpending")
            return
        if not self.daftar_belanja:
            self.tampilkan_popup("Keranjang belanja masih kosong")
            return
        now = datetime.now()
        try:
            data_transaksi = {
                "tanggal": now.strftime("%Y-%m-%d"),
                "pelanggan": self.ids.label_nama_pelanggan.text.strip(),
                "kredit": self.is_kredit,
                "tanggal_tempo": self.ids.input_tanggal_tempo.text.strip(),
                "cara_bayar": "Non Tunai" if self.is_non_tunai else "Tunai",
                "jenis_pelanggan": self.ids.jenis_pelanggan_spinner.text,
                "diskon": self.ids.diskon_rp.text,
                "ongkir": self.ids.ongkir_input.text,
                "bayar": self.ids.uang_pelanggan_input.text,
            }

            # Simpan ke memori
            self.terpending = {
                'transaksi': data_transaksi,
                'items': self.daftar_belanja.copy()
            }

            self.tampilkan_popup("Transaksi dipending!")
            self.daftar_belanja.clear()
            self.refresh_keranjang()
            self.reset_form_kasir()

        except Exception as e:
            self.tampilkan_popup(f"Error saat pending: {str(e)}")

    def reload_pending(self):
        if not self.terpending:
            self.tampilkan_popup("Tidak ada transaksi pending untuk dimuat.")
            return

        data = self.terpending
        transaksi = data['transaksi']

        self.ids.label_nama_pelanggan.text = transaksi['pelanggan']
        self.is_kredit = transaksi['kredit']
        self.ids.input_tanggal_tempo.text = transaksi['tanggal_tempo']
        self.ids.jenis_pelanggan_spinner.text = transaksi['jenis_pelanggan']
        self.ids.diskon_rp.text = transaksi['diskon']
        self.ids.ongkir_input.text = transaksi['ongkir']
        self.ids.uang_pelanggan_input.text = transaksi['bayar']

        self.daftar_belanja.clear()
        self.daftar_belanja.extend(data['items'])

        self.refresh_keranjang()
        self.update_totals()
        self.tampilkan_popup("Transaksi pending berhasil dimuat!")
        self.terpending = None
    #UTILS#
    def on_diskon_rp_checkbox(self, active):
        if getattr(self, '_updating_checkbox', False):
            return

        if active:
            if self.nama_pelanggan_aktif:
                self.diskon_dari_poin = True
                self.update_totals()
            else:
                self.diskon_dari_poin = False
                self._updating_checkbox = True
                self.ids.diskon_rp_checkbox.active = False
                self._updating_checkbox = False
                self.update_totals()
                self.tampilkan_popup("Diskon dari poin hanya berlaku\nuntuk pelanggan terdaftar")
        else:
            self.diskon_dari_poin = False
            self.update_totals()

    def update_time(self, dt):
        current_time = datetime.now().strftime('%Y-%m-%d || %H:%M:%S')
        time_label = self.ids.get('time_label')
        if time_label:
            time_label.text = f'{current_time}'

    def generate_no_ref(self):
        last = MDApp.get_running_app().db.automatis_no_ref()
        if last and last[0].isdigit():
            last_number = int(last[0])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{new_number:07d}"

    def toggle_kredit(self, value):
        self.is_kredit = value
        if not value:
            self.ids.input_tanggal_tempo.text = ''

    def toggle_non_tunai(self, value):
        self.is_non_tunai = value

    def periksa_pelanggan_kosong(self, input_widget):
        if not input_widget.focus and input_widget.text.strip() == "":
            self.ids.label_nama_pelanggan.text = "Umum"
            self.nama_pelanggan_aktif = "Umum"

    def cari_pelanggan(self, keyword):
        hasil = MDApp.get_running_app().db.search_data_pelanggan(keyword)
        if hasil:
            self.tampilkan_popup_pelanggan(hasil)
        else:
            self.tampilkan_popup("pelanggan tidak ditemukan")

    def pilih_pelanggan(self, btn, data, popup):
        self.ids.label_nama_pelanggan.text = data[1]
        self.ids.input_nama_pelanggan.text = ''
        self.ids.label_poin_pelanggan.text = f"Poin: {self.poin_pelanggan}"
        self.nama_pelanggan_aktif = data[1]
        popup.dismiss()
    #POPUPS#
    def tampilkan_popup_obat(self, hasil_pencarian):
        layout = Factory.PopupLayout()
        tombol_layout = layout.ids.tombol_layout

        for obat in hasil_pencarian:
            nama, satuan, harga, plu = obat
            btn = Button(
                text=f"{nama} ({satuan}) - Rp{harga}",
                size_hint_y=None,
                height=40
            )

            btn.bind(on_release=lambda btn, data=obat: (self.tambah_ke_keranjang(data[0], data[1], data[2], data[3]), popup.dismiss()))
            tombol_layout.add_widget(btn)

        popup = Popup(
            title="Pilih Obat",
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        popup.open()

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
            btn.bind(on_release=lambda btn: self.pilih_pelanggan(btn, pelanggan, popup))
            tombol_layout.add_widget(btn)
        popup.open()

    def tampilkan_popup(self, pesan):
        popup = Popup(
            title="Info",
            content=Label(text=pesan),
            size_hint=(None, None),
            size=(300, 150)
        )
        popup.open()

    def open_cara_bayar_popup(self):
        popup = Popup(
            title='Informasi',
            content=Label(text='Menu Cara Bayar'),
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True
        )
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

class SettingsDooka(Screen):
    #METHODS#
    @property
    def pembulatan(self):
        return MDApp.get_running_app().settings_manager.get("pembulatan")
    @property
    def pembagian_perpoin(self):
        return MDApp.get_running_app().settings_manager.get("pembagian_perpoin")
    #INIT#
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    #UTILS#
    def ubah_pembulatan(self, nilai_baru):
        MDApp.get_running_app().settings_manager.set("pembulatan", nilai_baru)
    def ubah_pembagian_perpoin(self, nilai_baru):
        MDApp.get_running_app().settings_manager.set("pembagian_perpoin", nilai_baru)

#---------------------------------------------------------------------------------------------#

class WindowsManager(ScreenManager):
    pass

#---------------------------------------------------------------------------------------------#

class DookaApp(MDApp):
    def build(self):
        Window.size = (1200, 800)
        Window.set_icon("assets\image\DOOKA_Logo_besar.png")
        self.formatter = FormatHelper() #digunakan didalam file kv
        # Inisialisasi database
        self.db = DatabaseObat("database/dooka_user.db")
        # Inisialisasi json settings manager
        settings_path = os.path.join("assets", "json", "setting.json")
        self.settings_manager = SettingsManager(settings_path)
        # Inisialisasi session cache
        if not SessionCache.get_data_obat():
            SessionCache.set_data_obat(self.db.get_all_obat())
        if not SessionCache.get_data_golongan():
            SessionCache.set_data_golongan(self.db.get_all_golongan())
        if not SessionCache.get_data_pajak():
            SessionCache.set_data_pajak(self.db.get_all_pajak())
        if not SessionCache.get_data_pelanggan():
            SessionCache.set_data_pelanggan(self.db.get_all_pelanggan())

        return Builder.load_file('user_interface/gui.kv')

    def on_stop(self):
        if hasattr(self, "db"):
            self.db.close_connection()
        self.settings_manager.save()

    def change_screen(self, screen_name, direction):
        self.root.transition.direction = direction
        self.root.current = screen_name