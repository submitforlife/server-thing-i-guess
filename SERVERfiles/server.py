import http.server
import socketserver
import os
import json
from datetime import datetime
import mimetypes

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")  # Folder with your files

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve JSON file list
        if self.path == "/files.json":
            file_list = []
            if os.path.exists(FILES_DIR):
                for f in os.listdir(FILES_DIR):
                    full_path = os.path.join(FILES_DIR, f)
                    file_list.append({
                        "name": f,
                        "size": os.path.getsize(full_path),
                        "mtime": datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S"),
                        "ext": os.path.splitext(f)[1][1:]
                    })
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(file_list).encode("utf-8"))
            return

        # Serve all other files normally
        requested_path = self.path.lstrip("/")
        if requested_path == "":
            requested_path = "index.html"
        if os.path.exists(requested_path):
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(requested_path)
            if mime_type:
                self.send_header("Content-type", mime_type)
            else:
                self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            with open(requested_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

os.chdir(BASE_DIR)
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
