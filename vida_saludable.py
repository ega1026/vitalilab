import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import os

# Función para asegurar que la base de datos y la tabla existan al arrancar
def inicializar_base_datos():
    conexion = sqlite3.connect("vida_saludable.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad INTEGER,
            grado TEXT,
            vasos_agua INTEGER,
            peso REAL,
            altura REAL,
            imc REAL
        )
    """)
    conexion.commit()
    conexion.close()

class MiManejador(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/registrar_perfil' or self.path == '/guardar_perfil':
            try:
                longitud = int(self.headers['Content-Length'])
                datos_post = self.rfile.read(longitud).decode('utf-8')
                parametros = urllib.parse.parse_qs(datos_post)
                
                # Obtener datos de texto
                nombre = parametros.get('nombre', [''])[0]
                grado = parametros.get('grado', [''])[0]
                
                # Obtener datos numéricos protegiendo contra errores vacíos
                try:
                    edad = int(parametros.get('edad', [0])[0])
                    peso = float(parametros.get('peso', [0])[0])
                    altura = float(parametros.get('altura', [0])[0])
                    vasos = int(parametros.get('vasos', [0])[0])
                except ValueError:
                    edad, peso, altura, vasos = 0, 0, 0, 0
                
                # Cálculo del IMC (Peso sobre altura en metros al cuadrado)
                imc = 0
                if peso > 0 and altura > 0:
                    altura_metros = altura / 100
                    imc = round(peso / (altura_metros * altura_metros), 2)
                
                # Guardar en la base de datos
                conexion = sqlite3.connect("vida_saludable.db")
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO perfiles (nombre, edad, grado, vasos_agua, peso, altura, imc) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nombre, edad, grado, vasos, peso, altura, imc))
                
                conexion.commit()
                conexion.close()
                
                # Redirigir nuevamente a la página del perfil tras guardar
                self.send_response(303)
                self.send_header('Location', '/perfil.html')
                self.end_headers()
            except Exception as e:
                # Si ocurre un error interno, responde con los detalles en texto para evitar el 502 mudo
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"Error interno en el servidor: {str(e)}".encode('utf-8'))
        else:
            super().do_POST()

if __name__ == "__main__":
    inicializar_base_datos()
    puerto = int(os.environ.get("PORT", 8000))
    servidor = HTTPServer(('0.0.0.0', puerto), MiManejador)
    print(f"Servidor web iniciado en el puerto {puerto}")
    servidor.serve_forever()