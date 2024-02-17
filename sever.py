import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Server running on port", PORT)
    print("https://5tddfk-8000.csb.app/")
    httpd.serve_forever()
