import sqlite3

def inicializar_bd():
    conexion = sqlite3.connect('vida_saludable.db')
    cursor = conexion.cursor()
    
    # Eliminamos la tabla anterior para evitar conflictos
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    
    # Creamos la tabla completa compatible con tu perfil y comunidad
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            edad INTEGER DEFAULT 0,
            grado TEXT DEFAULT 'Comunidad General',
            vasos_agua INTEGER DEFAULT 0,
            peso REAL DEFAULT 0,
            altura REAL DEFAULT 0,
            imc REAL DEFAULT 0,
            racha INTEGER DEFAULT 0,
            puntos INTEGER DEFAULT 0,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("¡Base de datos creada y optimizada correctamente!")

if __name__ == '__main__':
    inicializar_bd()