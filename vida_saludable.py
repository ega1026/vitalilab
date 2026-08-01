import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import os

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
            imc REAL DEFAULT 0
        )
    """)
    conexion.commit()
    conexion.close()

class MiManejador(SimpleHTTPRequestHandler):
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
                
                # Redirigir al login despues de registrarse
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
                # Si las credenciales son correctas, redirigimos a completar datos inyectando el correo con script en cliente
                self.send_response(303)
                # Creamos una pequeña respuesta que guarde en localStorage y redirija
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
                
                # Al terminar de completar el perfil, vamos al index o panel principal
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