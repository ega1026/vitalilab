import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import os

# Contraseña para acceder al panel de admin
CLAVE_ADMIN = "admin123"

def inicializar_base_datos():
    conexion = sqlite3.connect("vida_saludable.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            correo TEXT UNIQUE,
            contrasena TEXT,
            edad INTEGER DEFAULT 0,
            grado TEXT DEFAULT '',
            vasos_agua INTEGER DEFAULT 0,
            peso REAL DEFAULT 0,
            altura REAL DEFAULT 0,
            imc REAL DEFAULT 0,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexion.commit()
    conexion.close()

class MiManejador(SimpleHTTPRequestHandler):

    def do_GET(self):
        # RUTA DEL PANEL DE ADMINISTRADOR
        if self.path.startswith('/admin'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            clave = params.get('clave', [''])[0]

            # Verificación de clave
            if clave != CLAVE_ADMIN:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                html_login_admin = """
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Admin Login - VitaliLab</title>
                    <link rel="stylesheet" href="style.css">
                </head>
                <body style="display:flex; justify-content:center; align-items:center; height:100vh; background:#1e1e1e; color:white;">
                    <div style="background:#2b2b2b; padding:30px; border-radius:10px; width:300px; text-align:center;">
                        <h2>Panel de Admin</h2>
                        <form method="GET" action="/admin">
                            <input type="password" name="clave" placeholder="Contraseña de Admin" style="margin-bottom:15px;" required>
                            <button type="submit" class="btn-verde">Ingresar</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html_login_admin.encode('utf-8'))
                return

            # Si la clave es correcta, consultamos los usuarios
            conexion = sqlite3.connect("vida_saludable.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, correo, edad, grado, peso, altura, imc, vasos_agua, fecha_registro FROM perfiles ORDER BY id DESC")
            usuarios = cursor.fetchall()
            conexion.close()

            # Construcción de la tabla en HTML
            filas = ""
            for u in usuarios:
                filas += f"""
                <tr>
                    <td>{u[0]}</td>
                    <td><b>{u[1]}</b></td>
                    <td>{u[2]}</td>
                    <td>{u[3] if u[3] else '-'}</td>
                    <td>{u[4] if u[4] else '-'}</td>
                    <td>{u[5]} kg</td>
                    <td>{u[6]} cm</td>
                    <td>{u[7]}</td>
                    <td>{u[8]} vasos</td>
                    <td>{u[9]}</td>
                </tr>
                """

            html_admin = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Panel de Administración - VitaliLab</title>
                <link rel="stylesheet" href="style.css">
                <style>
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }}
                    th, td {{ padding: 12px; border: 1px solid #ddd; text-align: center; font-size: 14px; }}
                    th {{ background-color: #2ecc71; color: white; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body style="padding: 20px; background-color: #f4f7f6;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1>Panel de Control de Usuarios (Admin)</h1>
                    <a href="/index.html" class="btn btn-verde" style="width:auto; padding:8px 15px;">Ir a la Web</a>
                </div>
                <p>Total de usuarios registrados: <b>{len(usuarios)}</b></p>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre</th>
                            <th>Correo</th>
                            <th>Edad</th>
                            <th>Grado</th>
                            <th>Peso</th>
                            <th>Altura</th>
                            <th>IMC</th>
                            <th>Agua (Hoy)</th>
                            <th>Fecha Registro</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas if filas else '<tr><td colspan="10">No hay usuarios registrados aún.</td></tr>'}
                    </tbody>
                </table>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_admin.encode('utf-8'))
            return

        # Para cualquier otra ruta, usar el comportamiento estándar
        super().do_GET()

    def do_POST(self):
        longitud = int(self.headers['Content-Length'])
        datos_post = self.rfile.read(longitud).decode('utf-8')
        parametros = urllib.parse.parse_qs(datos_post)

        if self.path == '/registrar_usuario':
            try:
                nombre = parametros.get('nombre', [''])[0]
                correo = parametros.get('correo', [''])[0]
                contrasena = parametros.get('contrasena', [''])[0]
                
                conexion = sqlite3.connect("vida_saludable.db")
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO perfiles (nombre, correo, contrasena) 
                    VALUES (?, ?, ?)
                """, (nombre, correo, contrasena))
                conexion.commit()
                conexion.close()
                
                self.send_response(303)
                self.send_header('Location', '/login.html')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"Error al registrar (el correo ya existe): {str(e)}".encode('utf-8'))

        elif self.path == '/verificar_login':
            correo = parametros.get('correo', [''])[0]
            contrasena = parametros.get('contrasena', [''])[0]

            conexion = sqlite3.connect("vida_saludable.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM perfiles WHERE correo = ? AND contrasena = ?", (correo, contrasena))
            usuario = cursor.fetchone()
            conexion.close()

            if usuario:
                self.send_response(303)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                html_redirect = f"""
                <script>
                    localStorage.setItem("usuario_activo", "{correo}");
                    window.location.href = "/completar_perfil.html";
                </script>
                """
                self.wfile.write(html_redirect.encode('utf-8'))
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("Credenciales incorrectas. Regresa y prueba de nuevo.".encode('utf-8'))

        elif self.path == '/guardar_datos_adicionales':
            try:
                correo = parametros.get('correo', [''])[0]
                edad = int(parametros.get('edad', [0])[0])
                grado = parametros.get('grado', [''])[0]
                peso = float(parametros.get('peso', [0])[0])
                altura = float(parametros.get('altura', [0])[0])
                vasos = int(parametros.get('vasos', [0])[0])
                
                imc = 0
                if peso > 0 and altura > 0:
                    altura_metros = altura / 100
                    imc = round(peso / (altura_metros * altura_metros), 2)
                
                conexion = sqlite3.connect("vida_saludable.db")
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE perfiles 
                    SET edad = ?, grado = ?, vasos_agua = ?, peso = ?, altura = ?, imc = ?
                    WHERE correo = ?
                """, (edad, grado, vasos, peso, altura, imc, correo))
                conexion.commit()
                conexion.close()
                
                self.send_response(303)
                self.send_header('Location', '/index.html')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"Error al guardar datos: {str(e)}".encode('utf-8'))
        else:
            super().do_POST()

if __name__ == "__main__":
    inicializar_base_datos()
    puerto = int(os.environ.get("PORT", 8000))
    servidor = HTTPServer(('0.0.0.0', puerto), MiManejador)
    print(f"Servidor web iniciado en el puerto {puerto}")
    servidor.serve_forever()