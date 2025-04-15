from database import db

if __name__ == "__main__":
    database = db.Database_obat("database/kasir_dmu_user.db")
    #...
    database.close_connection()