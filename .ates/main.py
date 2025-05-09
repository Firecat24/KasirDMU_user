from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRaisedButton


class MainApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("main.kv")

    def select_all_checkbox(self):
        # Mendapatkan data table
        data_table = self.root.ids.data_table
        
        # Mengubah status checkbox di seluruh baris menjadi True
        new_row_data = []
        for row in data_table.row_data:
            new_row = list(row)
            new_row[-1] = "True"  # Menandakan checkbox dicentang
            new_row_data.append(tuple(new_row))

        # Memperbarui data table dengan row data yang baru
        data_table.row_data = new_row_data

    def on_start(self):
        data_table = self.root.ids.data_table
        data_table.add_row_checkboxes()

if __name__ == "__main__":
    MainApp().run()
