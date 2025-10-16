from datetime import datetime
from kivy.clock import Clock
# from kivymd.uix.dialog import MDDialog
# from kivymd.uix.button import MDFlatButton

class FormatHelper:
    @staticmethod
    def intonly_format(widget):
        def _sanitize(dt):
            digits_only = ''.join(filter(str.isdigit, widget.text))
            if not digits_only:
                widget.text = ''
                return
            formatted = "{:,}".format(int(digits_only)).replace(",", ".")
            if widget.text != formatted:
                widget.text = formatted
                Clock.schedule_once(lambda dt2: setattr(widget, 'cursor', (len(formatted), 0)), 0)

        Clock.schedule_once(_sanitize, 0)

def get_digits_only(text):
    digits = ''.join(filter(str.isdigit, text))
    return int(digits) if digits else 0

def date_only(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None