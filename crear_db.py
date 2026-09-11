import sqlite3

def inicializar_bd():
    conexion = sqlite3.connect('vida_saludable.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            edad INTEGER,
            grado TEXT,
            agua INTEGER DEFAULT 0,
            racha INTEGER DEFAULT 0,
            puntos INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retos_diarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            fecha TEXT,
            agua_cumplida BOOLEAN DEFAULT 0,
            dormir_cumplido BOOLEAN DEFAULT 0,
            entrenamiento_cumplido BOOLEAN DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("Base de datos creada y actualizada con éxito.")

if __name__ == '__main__':
    inicializar_bd()