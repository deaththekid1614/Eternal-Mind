# Vison live project map

Vison is a standalone, read-only dashboard that maps source files and their code connections. It lives in `vision/` and does not need to be imported by the frontend or backend.

## Run

Double-click `vision/run.bat`. It starts the local Python server and opens `http://127.0.0.1:8765`. Close the command window to stop it. Python must be installed and available on `PATH`.

## How it works

- `vision/server.py` scans the repository and serves a JSON graph snapshot from `/api/snapshot`.
- The scan skips generated/dependency directories, private data folders, environment files, and symbolic links.
- It detects relative JavaScript/TypeScript imports, local Python imports, and frontend API paths that match backend routes.
- `vision/index.html` renders the graph in a full-window SVG and refreshes it every four seconds.
- Every source file is placed in a lane based on the first directory in its repository-relative path. For example, `scripts/benchmark.py` goes in `SCRIPTS` and `vision/server.py` goes in `VISION`. Each root directory gets a distinct lane; root-level source files go in `ROOT`.
- Lane grouping is derived from each node's path in the browser, not the server's optional group label, so it remains correct with an older running server.
- Resize the browser to refit the graph. Click a file node (or focus it and press Enter/Space) to highlight its direct connections.

## Add a folder

Add supported source files (`.css`, `.html`, `.js`, `.jsx`, `.py`, `.ts`, or `.tsx`) under a root directory. The map detects the directory and adds a lane automatically; no folder list or application configuration needs updating.

The scanner limits snapshots to 4,000 inventoried files and 180 source nodes. The graph reports when source nodes are omitted.
