from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty

class ObatTable(BoxLayout):
    rv_data = ListProperty()
    selected_index = NumericProperty(-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rv_data = [
            {'nama': 'Paracetamol', 'stok': 50},
            {'nama': 'Amoxicillin', 'stok': 30},
            {'nama': 'Ibuprofen', 'stok': 20},
        ]
        self.refresh_rv()

    def refresh_rv(self):
        self.ids.rv.data = [{
            'index': i,
            'data': [item['nama'], str(item['stok'])],
            'is_selected': i == self.selected_index
        } for i, item in enumerate(self.rv_data)]

    def select_row(self, index):
        self.selected_index = index
        self.refresh_rv()

    def edit_selected(self):
        if self.selected_index >= 0:
            item = self.rv_data[self.selected_index]
            print(f"Edit data: {item['nama']} (stok: {item['stok']})")
        else:
            print("Tidak ada baris yang dipilih.")

class ObatItem(BoxLayout):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.parent.select_row(self.index)
        return super().on_touch_down(touch)

class MyApp(App):
    def build(self):
        return ObatTable()