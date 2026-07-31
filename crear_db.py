import sqlite3

def crear_base_datos():
    conexion = sqlite3.connect("vida_saludable.db")
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            grado TEXT NOT NULL,
            vasos_agua INTEGER NOT NULL,
            peso REAL DEFAULT 0,
            altura REAL DEFAULT 0,
            imc REAL DEFAULT 0
        )
    """)
    
    conexion.commit()
    conexion.close()
    print("Base de datos y tabla perfiles creadas correctamente.")

if __name__ == "__main__":
    crear_base_datos()