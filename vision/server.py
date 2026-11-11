from __future__ import annotations

import json
import os
import re
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "cache",
    "coverage",
    "data",
    "dist",
    "dist-ssr",
    "logs",
    "models",
    "sessions",
    "node_modules",
    "venv",
}
IGNORED_FILES = {".env", ".env.local", ".env.development", ".env.production"}
CODE_EXTENSIONS = {".css", ".html", ".js", ".jsx", ".py", ".ts", ".tsx"}
IMPORT_PATTERNS = (
    re.compile(r"""(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']"""),
    re.compile(r"""\bimport\s*\(\s*["']([^"']+)["']\s*\)"""),
    re.compile(r"""^\s*(?:from|import)\s+([\w.]+)""", re.MULTILINE),
)
PYTHON_IMPORT_PATTERN = re.compile(
    r"""^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))""",
    re.MULTILINE,
)
ROUTE_PATTERN = re.compile(
    r"""@router\.(?:get|post|put|patch|delete)\(\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
API_PATH_PATTERN = re.compile(
    r"""\$\{[^}]+\}/([\w.-]+)|["'`](/(?:api/)?[\w./{}-]+)["'`]"""
)
STARTED_AT = time.monotonic()


def _read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:256_000]
    except OSError:
        return ""


def _resolve_typescript_import(source: Path, target: str, known: set[str]) -> str | None:
    if not target.startswith("."):
        return None

    relative = (source.parent / target).as_posix()
    candidates = [relative]
    if not Path(relative).suffix:
        candidates.extend(relative + extension for extension in (".ts", ".tsx", ".js", ".jsx", ".css"))
        candidates.extend(
            f"{relative}/index{extension}" for extension in (".ts", ".tsx", ".js", ".jsx")
        )
    return next((candidate for candidate in candidates if candidate in known), None)


def _resolve_python_import(source: Path, target: str, known: set[str]) -> str | None:
    source_parts = list(source.with_suffix("").parts)
    if target.startswith("."):
        level = len(target) - len(target.lstrip("."))
        module = target[level:]
        base = source_parts[: max(1, len(source_parts) - level)]
        if module:
            base.extend(module.split("."))
        candidates = ["/".join(base) + ".py", "/".join(base + ["__init__.py"])]
    else:
        if not target.startswith("app."):
            return None
        base = target.replace(".", "/")
        candidates = [f"backend/{base}.py", f"backend/{base}/__init__.py"]
    return next((candidate for candidate in candidates if candidate in known), None)


def snapshot() -> dict:
    discovered: list[dict] = []
    for current, dirs, names in os.walk(ROOT, followlinks=False):
        dirs[:] = sorted(
            name for name in dirs
            if name not in IGNORED_DIRS and not (Path(current) / name).is_symlink()
        )
        for name in names:
            path = Path(current) / name
            if name in IGNORED_FILES or name.startswith(".env."):
                continue
            if path.is_symlink():
                continue
            try:
                relative = path.relative_to(ROOT).as_posix()
                stat = path.stat()
            except OSError:
                continue
            if not path.is_file():
                continue
            discovered.append({
                "path": relative,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "extension": path.suffix.lower(),
            })

    discovered.sort(key=lambda item: item["path"].casefold())
    inventory_limit = 4000
    inventory = discovered[:inventory_limit]
    known = {item["path"] for item in inventory}
    sources = [
        item for item in inventory
        if item["extension"] in CODE_EXTENSIONS and item["size"] <= 1_000_000
    ]

    nodes = []
    edges = []
    paths_by_id: dict[str, str] = {}
    source_text: dict[str, str] = {}
    graph_limit = 180
    for item in sources[:graph_limit]:
        path = item["path"]
        group = Path(path).parts[0] if len(Path(path).parts) > 1 else "root"
        nodes.append({
            "id": path,
            "label": Path(path).name,
            "path": path,
            "group": group,
            "extension": item["extension"],
            "modified": item["modified"],
        })
        paths_by_id[path] = path
        source_text[path] = _read_source(ROOT / Path(path))

    node_paths = set(paths_by_id)
    edge_keys: set[tuple[str, str, str]] = set()
    for path, text in source_text.items():
        extension = Path(path).suffix.lower()
        if extension == ".py":
            targets = (match.group(1) or match.group(2) for match in PYTHON_IMPORT_PATTERN.finditer(text))
            for target in targets:
                resolved = _resolve_python_import(Path(path), target, known)
                if resolved in node_paths and resolved != path:
                    edge_keys.add((path, resolved, "import"))
        else:
            for pattern in IMPORT_PATTERNS[:2]:
                for match in pattern.finditer(text):
                    resolved = _resolve_typescript_import(Path(path), match.group(1), known)
                    if resolved in node_paths and resolved != path:
                        edge_keys.add((path, resolved, "import"))

    backend_routes: dict[str, str] = {}
    for path, text in source_text.items():
        if not path.startswith("backend/"):
            continue
        for route in ROUTE_PATTERN.findall(text):
            backend_routes[route.rstrip("/")] = path

    for path, text in source_text.items():
        if not path.startswith("frontend/"):
            continue
        for match in API_PATH_PATTERN.finditer(text):
            route = match.group(1) or match.group(2)
            if not route.startswith("/"):
                route = "/" + route
            route_key = route.rstrip("/")
            for backend_route, backend_path in backend_routes.items():
                if route_key.endswith(backend_route) and backend_path in node_paths and backend_path != path:
                    edge_keys.add((path, backend_path, "API"))

    for source, target, kind in sorted(edge_keys):
        edges.append({"source": source, "target": target, "kind": kind})

    return {
        "nodes": nodes,
        "edges": edges,
        "omittedNodes": max(0, len(sources) - len(nodes)),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/snapshot":
            try:
                body = json.dumps(snapshot(), separators=(",", ":")).encode("utf-8")
            except Exception as error:
                body = json.dumps({"error": str(error)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        try:
            body = (Path(__file__).parent / "index.html").read_bytes()
        except OSError as error:
            self.send_error(500, str(error))
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *args: object) -> None:
        print(f"[vison] {self.address_string()} - {_format % args}")


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), DashboardHandler)
    print(f"Vison is watching {ROOT}")
    print(f"Open http://127.0.0.1:{PORT} (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Vison...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
