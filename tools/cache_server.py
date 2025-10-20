"""Simple interactive cache inspector server.

Usage:
  python tools/cache_server.py --port 8000

Opens a tiny web UI at http://localhost:8000/ that lists files under trading/data/raw and allows deleting selected files.
No external dependencies.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
from pathlib import Path
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trading import cache

RAW = cache.RAW_DIR

HTML_TEMPLATE = '''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Cache Inspector</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  </head>
  <body class="p-3">
    <div class="container">
      <h3>Cache Inspector</h3>
      <p>Cache dir: %%RAW_DIR%%</p>
      <div>
        <button id="refresh" class="btn btn-sm btn-primary">Refresh</button>
        <button id="delete" class="btn btn-sm btn-danger">Delete selected</button>
      </div>
      <table class="table table-sm mt-2" id="files">
        <thead><tr><th></th><th>file</th><th>size</th><th>mtime</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <script>
      async function loadFiles(){
        const res = await fetch('/files');
        const data = await res.json();
        const tbody = document.querySelector('#files tbody');
        tbody.innerHTML = '';
        data.files.forEach(f => {
          const tr = document.createElement('tr');
          tr.innerHTML = `<td><input type="checkbox" value="${f.path}"></td><td>${f.name}</td><td>${f.size}</td><td>${f.mtime}</td>`;
          tbody.appendChild(tr);
        });
      }
      document.getElementById('refresh').addEventListener('click', loadFiles);
      document.getElementById('delete').addEventListener('click', async ()=>{
        const checks = Array.from(document.querySelectorAll('#files tbody input:checked')).map(cb => cb.value);
        if(!checks.length) return alert('No files selected');
        if(!confirm('Delete ' + checks.length + ' files?')) return;
        const res = await fetch('/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({files: checks})});
        const data = await res.json();
        alert('Deleted: ' + data.deleted.length + '\nFailed: ' + data.failed.length);
        loadFiles();
      });
      loadFiles();
    </script>
  </body>
</html>
'''

HTML = HTML_TEMPLATE.replace('%%RAW_DIR%%', str(RAW))

class Handler(BaseHTTPRequestHandler):
    def _set_json(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
            return
        if p.path == '/files':
            files = []
            for f in RAW.iterdir():
                if f.is_file():
                    files.append({'name': f.name, 'path': str(f), 'size': f.stat().st_size, 'mtime': f.stat().st_mtime})
            self._set_json()
            self.wfile.write(json.dumps({'files': files}).encode('utf-8'))
            return
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        p = urlparse(self.path)
        if p.path == '/delete':
            length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            files = data.get('files', [])
            deleted = []
            failed = []
            for f in files:
                try:
                    Path(f).unlink()
                    deleted.append(f)
                except Exception:
                    failed.append(f)
            self._set_json()
            self.wfile.write(json.dumps({'deleted': deleted, 'failed': failed}).encode('utf-8'))
            return
        self.send_response(404)
        self.end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), Handler)
    print(f'Serving cache UI on http://{args.host}:{args.port}/')
    server.serve_forever()
