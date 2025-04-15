from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class DataEntryApp(App):
    def build(self):
        # Create a GridLayout with 2 columns.
        self.layout = GridLayout(cols=2, padding=10, spacing=10)

        # Create input fields for each attribute in your table schema.
        self.fields = {
            "jenis": TextInput(hint_text="Jenis", multiline=False),
            "plu": TextInput(hint_text="PLU", multiline=False),
            "nama_produk": TextInput(hint_text="Nama Produk", multiline=False),
            "satuan": TextInput(hint_text="Satuan", multiline=False),
            "harga_beli": TextInput(hint_text="Harga Beli", multiline=False),
            "harga_umum": TextInput(hint_text="Harga Umum (optional)", multiline=False),
            "harga_cabang": TextInput(hint_text="Harga Cabang (optional)", multiline=False),
            "harga_halodoc": TextInput(hint_text="Harga Halodoc (optional)", multiline=False),
            "harga_karyawan": TextInput(hint_text="Harga Karyawan (optional)", multiline=False),
            "harga_bpjs": TextInput(hint_text="Harga BPJS (optional)", multiline=False),
            "kode_golongan": TextInput(hint_text="Kode Golongan", multiline=False),
            "nama_golongan": TextInput(hint_text="Nama Golongan", multiline=False), 
           # Add more fields as necessary...
           # For simplicity, only some fields are shown here.
        }

        # Add labels and text inputs to layout in two columns.
        for field_name, text_input in self.fields.items():
             self.layout.add_widget(Label(text=field_name.capitalize()))
             self.layout.add_widget(text_input)

        # Submit button spanning both columns at the bottom.
        submit_button = Button(text='Submit', size_hint=(1, 0.2))
        submit_button.bind(on_press=self.submit_data)
        self.layout.add_widget(submit_button)

        return self.layout

    def submit_data(self, instance):
        # Collecting all input values into a dictionary and printing them.
        submitted_data = {field_name: text_input.text for field_name, text_input in self.fields.items()}
        print("Submitted Data:")
        for key, value in submitted_data.items():
            print(f"{key}: {value}")

if __name__ == '__main__':
    DataEntryApp().run()
