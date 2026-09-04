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
    if request.method == 'POST':
        nombre_usuario = request.form['nombre']
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre_usuario,))
        usuario = cursor.fetchone()
        conexion.close()
        
        if usuario:
            session['usuario_id'] = usuario['id']
            return redirect(url_for('perfil'))
        else:
            return render_template('login.html', error="Usuario no encontrado")
            
    return render_template('login.html')

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