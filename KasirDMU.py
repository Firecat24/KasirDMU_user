from database import db
from user_interface.ui_kasir_kivy import KasirApp

if __name__ == "__main__":
    database = db.DatabaseObat("database/kasir_dmu_user.db")

    KasirApp().run()

    database.close_connection()