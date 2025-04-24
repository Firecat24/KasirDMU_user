from datetime import datetime
from database.db import DatabaseObat
from threading import Thread

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


class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        current_time = datetime.now().strftime('%H:%M:%S')
        time_label = self.ids.get('time_label')
        if time_label:
            time_label.text = f'{current_time}'

class DataObat(Screen):
    def on_enter(self):
        self.ids.table_container.clear_widgets()
        Thread(target=self.load_data_in_thread).start()

    def load_data_in_thread(self):
        Clock.schedule_once(self.get_data_and_create_table, 0)

    def get_data_and_create_table(self, dt):
        rows = MDApp.get_running_app().db.get_all_obat()
        self.create_table(rows)

    def create_table(self, rows):
        if not rows:
            print("Data obat kosong!")
            return 

        column_data = [
            ("[font=Roboto][size=10sp]ID[/size][/font]", dp(20)),
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
        row_data = [
            tuple(f"[font=Roboto][size=10sp]{str(item)}[/size][/font]" for item in row) for row in rows ]
        if not row_data:
            print("Data row kosong!")
            return
        self.data_table = MDDataTable(
            size_hint=(1, 1),
            row_data=row_data,
            column_data=column_data,
            use_pagination=True,
            pagination_menu_height="140dp",
            check=True,
        )
        self.ids.table_container.add_widget(self.data_table)

    def hapus_terpilih(self):
        checked_rows = self.data_table.get_row_checks()
        if not checked_rows:
            toast("Belum ada yang dipilih")
            return

        db = MDApp.get_running_app().db
        deleted = 0

        for row in checked_rows:
            id_obat = int(row[0])
            success = db.delete_product(id_obat)
            if success:
                deleted += 1
            else:
                toast(f"Gagal hapus ID {id_obat}")

        if deleted > 0:
            toast(f"{deleted} data berhasil dihapus")
            Clock.schedule_once(lambda dt: self.on_enter(), 0.3)

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
        print("Data yang dikirim:", data)

        kode_golongan = self.kode_golongan_aktif
        nama_golongan = self.ids.dropdown_golongan.text

        kode_ppn = self.kode_pajak_aktif

        margin_data = MDApp.get_running_app().db.get_margin_golongan(kode_golongan)

        print(kode_golongan, nama_golongan)

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

            self.tampilkan_dialog("Data berhasil disimpan!", setelah_dialog=lambda: MDApp.get_running_app().change_screen('data_obat', 'left'))
        except Exception as e:
            print("Error saat menyimpan data:", str(e))
            self.tampilkan_dialog(f"Terjadi kesalahan: {str(e)}")

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

class InsertPPN(Screen):
    pass

class InsertGolonganObat(Screen):
    pass

class Kasir(Screen):
    pass

class WindowsManager(ScreenManager):
    pass

class KasirApp(MDApp):
    def build(self):
        self.db = DatabaseObat("database/kasir_dmu_user.db")
        return Builder.load_file('user_interface/gui.kv')
    
    def change_screen(self, screen_name, direction='left'):
        self.root.transition.direction = direction
        self.root.current = screen_name

    def simpan_data_obat(self):
        screen = self.root.get_screen('insert_obat')
        screen.simpan_data_obat()