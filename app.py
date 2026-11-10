import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Lokasi penyimpanan file JSON di dalam Docker Named Volume
DATA_DIR = os.environ.get("DATA_DIR", "/var/lib/backend_data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")
PORT = 5000


def load_tasks():
    """Membaca daftar tugas dari file tasks.json."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks):
    """Menyimpan daftar tugas ke dalam file tasks.json."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


class TaskAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        """Fungsi bantu untuk mengirim respon JSON beserta header CORS."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        # Mengizinkan Frontend (index.html) mengakses API dari port berbeda
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        """Menangani preflight request CORS dari browser."""
        self._send_json(200, {"status": "ok"})

    def do_GET(self):
        """GET /tasks -> Mengambil seluruh daftar tugas kelompok."""
        parsed = urlparse(self.path)
        if parsed.path == "/tasks":
            tasks = load_tasks()
            self._send_json(200, {
                "status": "success",
                "count": len(tasks),
                "data": tasks
            })
        elif parsed.path == "/health":
            self._send_json(200, {"status": "healthy"})
        else:
            self._send_json(404, {
                "status": "error",
                "message": "Endpoint tidak ditemukan. Gunakan /tasks"
            })

    def do_POST(self):
        """POST /tasks -> Menambahkan tugas baru ke dalam daftar."""
        parsed = urlparse(self.path)
        if parsed.path != "/tasks":
            self._send_json(404, {
                "status": "error",
                "message": "Endpoint tidak ditemukan. Gunakan POST /tasks"
            })
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json(400, {
                "status": "error",
                "message": "Body request tidak boleh kosong"
            })
            return

        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json(400, {
                "status": "error",
                "message": "Format JSON tidak valid"
            })
            return

        title = str(body.get("title", "")).strip()
        assignee = str(body.get("assignee", "")).strip()
        priority = str(body.get("priority", "Normal")).strip()
        note = str(body.get("note", "")).strip()

        if not title or not assignee:
            self._send_json(400, {
                "status": "error",
                "message": "Nama tugas (title) dan penanggung jawab (assignee) wajib diisi"
            })
            return

        tasks = load_tasks()
        new_task = {
            "title": title,
            "assignee": assignee,
            "priority": priority,
            "note": note
        }
        tasks.append(new_task)
        save_tasks(tasks)

        self._send_json(201, {
            "status": "success",
            "message": "Tugas berhasil ditambahkan",
            "data": new_task
        })

    def do_DELETE(self):
        """DELETE /tasks?index=X -> Menghapus tugas berdasarkan nomor index."""
        parsed = urlparse(self.path)
        if parsed.path != "/tasks":
            self._send_json(404, {
                "status": "error",
                "message": "Endpoint tidak ditemukan. Gunakan DELETE /tasks?index=X"
            })
            return

        query_params = parse_qs(parsed.query)
        if "index" not in query_params:
            self._send_json(400, {
                "status": "error",
                "message": "Parameter query 'index' wajib disertakan (contoh: /tasks?index=0)"
            })
            return

        try:
            index = int(query_params["index"][0])
        except ValueError:
            self._send_json(400, {
                "status": "error",
                "message": "Parameter 'index' harus berupa angka bulat"
            })
            return

        tasks = load_tasks()
        if index < 0 or index >= len(tasks):
            self._send_json(404, {
                "status": "error",
                "message": f"Tugas dengan index {index} tidak ditemukan"
            })
            return

        deleted_task = tasks.pop(index)
        save_tasks(tasks)

        self._send_json(200, {
            "status": "success",
            "message": f"Tugas '{deleted_task.get('title')}' berhasil dihapus/diselesaikan",
            "deleted": deleted_task
        })


if __name__ == "__main__":
    print(f"Server Backend berjalan di http://0.0.0.0:{PORT}")
    print(f"Menyimpan data ke: {DATA_FILE}")
    server = HTTPServer(("0.0.0.0", PORT), TaskAPIHandler)
    server.serve_forever()

