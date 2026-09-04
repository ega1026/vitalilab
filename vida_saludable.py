import os
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_vitalilab'

def conectar_db():
    conexion = sqlite3.connect('vida_saludable.db')
    conexion.row_factory = sqlite3.Row
    return conexion

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        nombre_usuario = request.form['nombre'].strip()
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre_usuario,))
        usuario = cursor.fetchone()
        conexion.close()
        
        if usuario:
            session['usuario_id'] = usuario['id']
            return redirect(url_for('perfil'))
        else:
            error = "Usuario no encontrado. Puedes registrarte abajo."
            
    return render_template('login.html', error=error)

@app.route('/registro', methods=['POST'])
def registro():
    nombre_usuario = request.form.get('nombre', '').strip()
    edad = request.form.get('edad', 15)
    grado = request.form.get('grado', 'General')
    
    if not nombre_usuario:
        return render_template('login.html', error="El nombre de usuario no puede estar vacío.")
        
    conexion = conectar_db()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre_usuario,))
        existente = cursor.fetchone()
        if existente:
            conexion.close()
            return render_template('login.html', error="El usuario ya existe. Inicia sesión.")
            
        cursor.execute("INSERT INTO usuarios (nombre, edad, grado, agua) VALUES (?, ?, ?, 0)", (nombre_usuario, edad, grado))
        conexion.commit()
        nuevo_id = cursor.lastrowid
        conexion.close()
        
        session['usuario_id'] = nuevo_id
        return redirect(url_for('perfil'))
    except Exception as e:
        conexion.close()
        return render_template('login.html', error=f"Error al registrar: {str(e)}")

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