import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_vitalilab'

def conectar_db():
    conexion = sqlite3.connect('vida_saludable.db')
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_bd():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
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
            nivel TEXT DEFAULT 'Novato Saludable',
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conexion.commit()
    conexion.close()

inicializar_bd()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/imc-info')
def imc_page():
    return render_template('imc_info.html')

@app.route('/cuidarte-info')
def cuidarte_page():
    return render_template('cuidarte_info.html')

@app.route('/fundamentos-info')
def fundamentos_page():
    return render_template('fundamentos_info.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ? AND contrasena = ?", (correo, contrasena))
        usuario = cursor.fetchone()
        conexion.close()
        
        if usuario:
            session['usuario_id'] = usuario['id']
            return redirect(url_for('perfil'))
        else:
            error = "Correo o contraseña incorrectos."
            
    return render_template('login.html', error=error)

@app.route('/registro', methods=['POST'])
def registro():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    contrasena = request.form.get('contrasena', '').strip()
    
    if not nombre or not correo or not contrasena:
        return render_template('login.html', error="Todos los campos son obligatorios.")
        
    conexion = conectar_db()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
        if cursor.fetchone():
            conexion.close()
            return render_template('login.html', error="Este correo ya está registrado.")
            
        cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contrasena, edad, grado, vasos_agua, racha, puntos, nivel) 
            VALUES (?, ?, ?, 0, 'Comunidad General', 0, 0, 0, 'Novato Saludable')
        ''', (nombre, correo, contrasena))
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        
        session['usuario_id'] = nuevo_id
        return redirect(url_for('perfil'))
    except Exception as e:
        conexion.close()
        return render_template('login.html', error=f"Error al registrar: {str(e)}")

@app.route('/actualizar_retos', methods=['POST'])
def actualizar_retos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    usuario_id = session['usuario_id']
    agua = 1 if 'agua' in request.form else 0
    dormir = 1 if 'dormir' in request.form else 0
    entrenamiento = 1 if 'entrenamiento' in request.form else 0
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    puntos_ganados = (agua + dormir + entrenamiento) * 15
    
    cursor.execute("SELECT puntos, racha FROM usuarios WHERE id = ?", (usuario_id,))
    actual = cursor.fetchone()
    
    nuevos_puntos = actual['puntos'] + puntos_ganados
    nueva_racha = actual['racha'] + 1
    
    nuevo_nivel = 'Novato Saludable'
    if nuevos_puntos >= 100:
        nuevo_nivel = 'Guerrero Vital'
    if nuevos_puntos >= 250:
        nuevo_nivel = 'Leyenda Fit'

    cursor.execute('''
        UPDATE usuarios 
        SET puntos = ?, racha = ?, nivel = ? 
        WHERE id = ?
    ''', (nuevos_puntos, nueva_racha, nuevo_nivel, usuario_id))
    
    conexion.commit()
    conexion.close()
    
    return redirect(url_for('perfil'))

@app.route('/perfil')
def perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['usuario_id'],))
    usuario = cursor.fetchone()
    conexion.close()
    
    return render_template('perfil.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)