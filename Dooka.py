from database import db
from user_interface.ui_dooka_kivy import DookaApp

if __name__ == "__main__":
    database = db.DatabaseObat("database/dooka_user.db")

    DookaApp().run()

    database.close_connection()