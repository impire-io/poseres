"""The dashboard's HTTP surface (feature 015, contracts §3; research R1/R4).

The B1 viewer's server pattern generalized: a stdlib ``ThreadingHTTPServer``
bound to 127.0.0.1 (port 0 = ephemeral), serving one self-contained page and
three JSON endpoints — ``/runs``, ``/run/<id>/state`` (everything both modes
render), and ``POST /run/<id>/ctrl`` (the control command forwarded through
the transport and the run's reply returned **verbatim** — success and every
B6 error reply alike; a transport failure or timeout becomes
``{ok: false, error}``, never a hang). The gate reads these endpoints with
urllib; a browser reads them with the page — same facts either way.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from pra.dash.model import DashboardModel

__all__ = ["start_dashboard"]


class _DashServer(ThreadingHTTPServer):
    daemon_threads = True


def start_dashboard(
    model: DashboardModel, port: int = 8600, host: str = "127.0.0.1"
) -> tuple[ThreadingHTTPServer, str]:
    """Serve the dashboard for ``model``; returns ``(server, url)``.

    Port 0 binds an ephemeral port (the URL carries the real one); a busy
    port raises ``OSError`` naming it. The server runs on a daemon thread;
    call ``shutdown()`` + ``server_close()`` when done. Binding beyond
    localhost is the operator's explicit choice via ``host``.
    """
    page = resources.files("pra.dash").joinpath("page.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 — http.server API
            if self.path in ("/", "/index.html"):
                self._reply(200, "text/html; charset=utf-8", page)
            elif self.path == "/favicon.ico":
                self._reply(204, "image/x-icon", b"")  # keep browser consoles honest-quiet
            elif self.path == "/runs":
                self._reply_json(200, model.runs_summary())
            else:
                run_id = self._run_path("state")
                if run_id is not None:
                    state = model.state_of(run_id)
                    if state is None:
                        self._reply_json(404, {"error": f"unknown run {run_id!r}"})
                    else:
                        self._reply_json(200, state)
                else:
                    self._reply_json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802 — http.server API
            run_id = self._run_path("ctrl")
            if run_id is None:
                self._reply_json(404, {"error": "not found"})
                return
            if not model.known(run_id):
                self._reply_json(404, {"error": f"unknown run {run_id!r}"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(request, dict):
                    raise ValueError
            except (ValueError, UnicodeDecodeError):
                self._reply_json(200, {"ok": False, "error": "body must be a JSON object"})
                return
            self._reply_json(200, model.control(run_id, request))

        def _run_path(self, leaf: str) -> str | None:
            parts = self.path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "run" and parts[2] == leaf:
                return parts[1]
            return None

        def _reply_json(self, code: int, obj: dict) -> None:
            self._reply(code, "application/json", json.dumps(obj).encode("utf-8"))

        def _reply(self, code: int, ctype: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:  # silence request logging
            pass

    try:
        server = _DashServer((host, port), Handler)
    except OSError as err:
        raise OSError(f"dashboard port {port} is unavailable ({err})") from err
    threading.Thread(target=server.serve_forever, daemon=True, name="pra-dash-http").start()
    real_host, real_port = server.server_address[0], server.server_address[1]
    return server, f"http://{real_host}:{real_port}/"
