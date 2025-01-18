import http.server
import socketserver
import socket

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://{IPAddr}:{PORT}")
    httpd.serve_forever()
