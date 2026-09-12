# Importamos las herramientas necesarias de Flask y Python
from datetime import date
import random
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Inicialización de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vida_saludable.db'
app.config['SECRET_KEY'] = 'clave_secreta_vitalilab'

db = SQLAlchemy(app)

# ==========================================
# MODELOS DE BASE DE DATOS
# ==========================================
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(200), nullable=False)
  role = db.Column(db.String(20), default='user')
  is_verified = db.Column(db.Boolean, default=False)
  verification_code = db.Column(db.String(6), nullable=True)

class DailyChecklist(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date = db.Column(db.String(10), nullable=False)

class Announcement(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150), nullable=False)
  content = db.Column(db.Text, nullable=False)

with app.app_context():
  db.create_all()

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
      flash('Este correo ya está registrado.', 'danger')
      return redirect(url_for('register'))

    code = str(random.randint(100000, 999999))
    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        verification_code=code,
        is_verified=False,
    )
    db.session.add(new_user)
    db.session.commit()

    session['temp_user_id'] = new_user.id
    flash(f'Registro exitoso. Tu código de verificación es: {code}', 'info')
    return redirect(url_for('verify_email'))

  return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify_email():
  if 'temp_user_id' not in session:
    return redirect(url_for('register'))

  if request.method == 'POST':
    entered_code = request.form['code']
    user = User.query.get(session['temp_user_id'])

    if user and user.verification_code == entered_code:
      user.is_verified = True
      user.verification_code = None
      db.session.commit()
      session.pop('temp_user_id', None)
      flash('¡Correo verificado con éxito! Ya puedes iniciar sesión.', 'success')
      return redirect(url_for('login'))
    else:
      flash('Código incorrecto. Inténtalo de nuevo.', 'danger')

  return render_template('completar_perfil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
      if not user.is_verified:
        flash('Debes verificar tu correo antes de iniciar sesión.', 'warning')
        return redirect(url_for('login'))

      session['user_id'] = user.id
      session['role'] = user.role
      flash('¡Bienvenido de nuevo a VitaliLab!', 'success')
      return redirect(url_for('perfil'))
    else:
      flash('Correo o contraseña incorrectos.', 'danger')

  return render_template('login.html')

@app.route('/perfil')
def perfil():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  return render_template('perfil.html')

@app.route('/checklist', methods=['GET', 'POST'])
def checklist():
  if 'user_id' not in session:
    return redirect(url_for('login'))

  current_user_id = session['user_id']
  today_str = date.today().strftime('%Y-%m-%d')

  existing_check = DailyChecklist.query.filter_by(
      user_id=current_user_id, date=today_str
  ).first()

  if request.method == 'POST':
    if existing_check:
      flash('Ya has completado tu checklist el día de hoy.', 'warning')
      return redirect(url_for('checklist'))

    new_check = DailyChecklist(user_id=current_user_id, date=today_str)
    db.session.add(new_check)
    db.session.commit()
    flash('¡Checklist guardado correctamente por hoy!', 'success')
    return redirect(url_for('checklist'))

  return render_template('cuidarte_info.html', already_checked=bool(existing_check))

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
  if 'user_id' not in session or session.get('role') != 'admin':
    flash('Acceso denegado. Solo los administradores pueden ver esta página.', 'danger')
    return redirect(url_for('perfil'))

  if request.method == 'POST':
    title = request.form['title']
    content = request.form['content']

    new_announcement = Announcement(title=title, content=content)
    db.session.add(new_announcement)
    db.session.commit()
    flash('Comunicado publicado exitosamente.', 'success')
    return redirect(url_for('admin_panel'))

  users = User.query.all()
  announcements = Announcement.query.all()
  return render_template('fundamentos_info.html', users=users, announcements=announcements)

if __name__ == '__main__':
  app.run(debug=True)