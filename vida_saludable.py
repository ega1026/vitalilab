import os
import sqlite3
import importlib

flask_module = importlib.import_module('flask')
Flask = flask_module.Flask
render_template = flask_module.render_template
request = flask_module.request
redirect = flask_module.redirect
url_for = flask_module.url_for
session = flask_module.session

app = Flask(__name__)
app.secret_key = 'clave_secreta_vitalilab'

def conectar_db():
    conexion = sqlite3.connect('vida_saludable.db')
    conexion.row_factory = sqlite3.Row
    return conexion

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
    return render_template('fundamentos_page.html')

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
            INSERT INTO usuarios (nombre, correo, contrasena, edad, grado, vasos_agua, racha, puntos) 
            VALUES (?, ?, ?, 0, 'Comunidad General', 0, 0, 0)
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
    
    puntos_ganados = (agua + dormir + entrenamiento) * 10
    
    cursor.execute('''
        UPDATE usuarios 
        SET puntos = puntos + ?, racha = racha + 1 
        WHERE id = ?
    ''', (puntos_ganados, usuario_id))
    
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