from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService

ROOT = Path(__file__).resolve().parent

semantic_db = SemanticDB.from_file(str(Path(__file__).resolve().parents[1] / "configs/semanticdb.sample.json"))
logger = AuditLogger(store=AuditStore())
pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
service = AuditReplayService(logger)


class UIHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, code: int = 200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in {"/", "/index.html"}:
            html = (ROOT / "index.html").read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        if self.path.startswith("/replay"):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            actor_role = q.get("actor_role", ["admin"])[0]
            sort_order = q.get("sort_order", ["desc"])[0]
            limit = int(q.get("limit", ["20"])[0])
            offset = int(q.get("offset", ["0"])[0])
            trace_id = q.get("trace_id", [None])[0]
            resp = service.replay_safe(actor="u_admin", actor_role=actor_role, scope_to_actor=False, sort_by="logged_at", sort_order=sort_order, limit=limit, offset=offset, trace_id=trace_id)
            return self._send_json(resp)
        self._send_json({"code": "NOT_FOUND", "message": "not found"}, 404)

    def do_POST(self):
        if self.path != "/query":
            return self._send_json({"code": "NOT_FOUND", "message": "not found"}, 404)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        req = json.loads(body)
        question = req.get("question", "今年销售额")
        role = req.get("role", "analyst")
        result = pipeline.run(question, role=role)
        self._send_json({"code": "OK", "result": result})


def run_ui_server(host: str = "127.0.0.1", port: int = 8010):
    server = HTTPServer((host, port), UIHandler)
    print(f"UI server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_ui_server()
