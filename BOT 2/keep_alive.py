import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Un servidor web ultraligero nativo de Python (Sin Flask)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot encendido y puerto abierto para Render!")

def run():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
