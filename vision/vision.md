# Vison: reusable live project map

Vison is a small, standalone dashboard for seeing source files grouped by their project folders and tracing recognizable code connections between them. This guide describes how this implementation works and how to reuse it in another repository.

## What it provides

- A fullscreen, browser-based SVG map with a separate lane for every top-level directory that contains supported source files.
- A `ROOT` lane for supported source files stored directly at the repository root.
- File nodes labeled with their filename and repository-relative path.
- Connection lines for detected local imports and recognized frontend-to-backend API routes.
- Periodic refresh so newly added, changed, and removed supported source files appear without a manual page reload.
- Clickable and keyboard-accessible nodes that highlight a selected file and its direct connections.
- A locally hosted, self-contained interface with no frontend package installs, external fonts, CDNs, or third-party services.

Vison is an aid for understanding a project, not a complete language parser, dependency analyzer, runtime monitor, or guarantee that every possible connection will be detected.

## Files and responsibilities

Keep the Vison folder together when moving or copying the dashboard:

| File | Responsibility |
|---|---|
| `server.py` | Finds the project root, scans source files, infers connections, returns the graph snapshot, and serves the dashboard. |
| `index.html` | Contains the dashboard styling, SVG graph renderer, interaction behavior, and periodic snapshot refresh. |
| `run.bat` | Windows launcher that starts the server from the Vison folder. |
| `vision.md` | This setup, reuse, and behavior guide. |

The server determines the project root as the parent directory of the folder containing `server.py`. For the expected layout, put the folder directly inside the project root:

```text
some-project/
├── backend/
├── frontend/
├── scripts/
└── vision/
    ├── index.html
    ├── run.bat
    ├── server.py
    └── vision.md
```

In this layout, the scan root is `some-project/`, not `some-project/vision/`.

## Run on Windows

1. Install Python 3 and ensure the `python` command is available in Command Prompt or PowerShell.
2. Put the `vision/` folder directly inside the project root.
3. Double-click `vision/run.bat`.
4. The dashboard opens at `http://127.0.0.1:8765`.
5. Keep the command window open while using the dashboard. Press Ctrl+C or close that window to stop the server.

The launcher uses `python -B server.py`; it does not install packages or create Python bytecode files. The server and graph use only the Python standard library and browser built-ins.

## Run on other operating systems

Open a terminal in the Vison folder and run:

```sh
python3 -B server.py
```

If `python3` is not the Python 3 command on that system, use its Python 3 executable instead. Open `http://127.0.0.1:8765` in a browser if it does not open automatically.

## How project lanes are determined

1. The server walks the project root and records supported source files.
2. For each file, the browser normalizes path separators and uses the first path segment as the lane name.
3. Files with the same first segment share a lane; different top-level directories always get separate lanes. For example:

   ```text
   scripts/benchmark.py  → SCRIPTS lane
   vision/server.py      → VISION lane
   frontend/src/App.tsx  → FRONTEND lane
   backend/app/main.py   → BACKEND lane
   project-config.py     → ROOT lane
   ```

4. Lane names are discovered from the graph data; there is no hardcoded list of project folders to maintain.
5. Lanes are sorted for readability, with common `frontend` and `backend` lanes first, `ROOT` next, and remaining directory names alphabetically. Each lane receives its own color.
6. If there are more lanes than fit in the viewport, the graph can scroll horizontally. The graph layout uses the available height to space nodes within each lane.

Lane grouping is about file location, not code ownership or runtime boundaries. A top-level directory gets a lane only when it contains at least one source file within the scan and graph limits.

## How connections are inferred

The server reads supported source files (up to 256 KB from each file) and applies lightweight text patterns:

- **JavaScript and TypeScript imports:** Relative `import` and `export ... from` paths are resolved against common extensions (`.ts`, `.tsx`, `.js`, `.jsx`, `.css`) and common `index` files.
- **Dynamic JavaScript imports:** Simple literal relative paths such as `import("./feature")` are recognized.
- **Python imports:** Local relative imports and imports beginning with `app.` are resolved to Python modules in the expected backend layout.
- **API routes:** Basic FastAPI-style `@router.get/post/put/patch/delete("/path")` route declarations are matched to frontend string paths. This heuristic is aimed at the conventional frontend/backend layout in this repository; change the patterns and route matching when adapting it to another framework or API convention.

An edge points from the file containing the import or API call to the file it references. Imports that cannot be resolved to a scanned source file are omitted. External packages are not displayed as nodes.

These are deliberately simple static heuristics. They may miss aliased imports, complex dynamic paths, generated routes, decorators written in an unsupported style, API URLs assembled in multiple steps, or languages and file types that are not configured. They can also mistake a string for an API path. The graph should be treated as a useful overview, not authoritative dependency data.

## Live refresh and interactions

- The page requests a fresh snapshot from `GET /api/snapshot` every four seconds.
- A browser resize redraws the graph to fit the new view.
- Select a node with a mouse click, or focus it and press Enter or Space, to emphasize its immediate connections. Select it again to clear the emphasis.
- API edges are visually distinct from import edges.
- A server-side scan error is returned as an HTTP error and shown in the graph header.
- The dashboard is read-only: it does not write to, reformat, or modify project source files.

## API and implementation details

- Dashboard: `GET /` (also serves `/index.html`).
- Graph data: `GET /api/snapshot`, returning JSON with `nodes`, `edges`, `omittedNodes`, and `generatedAt`.
- Node fields include `id`, `label`, `path`, `group`, `extension`, and `modified`. The browser derives the displayed lane from `path`, so lane placement is not dependent on the server's `group` value.
- Edge fields include `source`, `target`, and `kind` (`import` or `API`).
- The server binds to `127.0.0.1` on port `8765`; it is intended for local use, not exposure to a public network.
- The HTML is served from disk on each page request, so changes to the UI are visible after a browser refresh. The Python process must be restarted for changes to server code to take effect.

## Adapting Vison to another project

1. Copy the complete Vison folder to the root of the target repository. Do not copy only `index.html`; the server supplies the live graph data.
2. Confirm that `ROOT = Path(__file__).resolve().parent.parent` still points to the target project root. If the Vison folder is nested more deeply, adjust this expression.
3. Add source extensions to `CODE_EXTENSIONS` when the target project uses other languages. Update import resolution and graph parsing too; adding an extension alone creates a file node but does not detect that language's imports.
4. Review `IGNORED_DIRS` and `IGNORED_FILES`. Keep generated files, large dependency trees, private datasets, and secrets out of the scan. Add project-specific secret filenames or directories as needed.
5. Adapt `_resolve_typescript_import`, `_resolve_python_import`, route patterns, and API route matching to the target repository's languages, module aliases, folder structure, and framework.
6. Change `PORT` if port `8765` is already occupied. Update the printed URL in `main()` to match.
7. Start the dashboard and check representative import and API edges against the actual code. The graph only reports relationships that its configured patterns can resolve.

For good results, make the project-specific changes explicit instead of assuming Vison automatically understands every build system or framework.

## Scan scope and limits

The current implementation:

- Skips directories named `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`, `build`, `coverage`, `cache`, `data`, `dist`, `dist-ssr`, `logs`, `models`, and `sessions`.
- Skips symbolic links and environment files such as `.env`, `.env.local`, `.env.development`, `.env.production`, and files whose names start with `.env.`.
- Considers `.css`, `.html`, `.js`, `.jsx`, `.py`, `.ts`, and `.tsx` source files.
- Inventories at most 4,000 files, draws at most 180 source nodes, and reads at most 1 MB per source file for graph eligibility (the source-text parser itself reads at most 256 KB).

The ignored directory names are generic defaults, not a complete privacy policy. Review them before using Vison on a different repository. Add all project-specific sensitive locations to the skip lists and do not expose the local server to an untrusted network.

## Troubleshooting

| Symptom | Check |
|---|---|
| `python` is not recognized | Install Python 3 and add it to `PATH`, or run `server.py` with the full Python executable path. |
| Browser does not open | Open `http://127.0.0.1:8765` manually after the console prints that the server is listening. |
| Port is already in use | Stop the other local process using port `8765`, or change `PORT` in `server.py` and use the matching URL. |
| Dashboard shows a watcher error | Check that the Vison server console is still open, then refresh the page. Restart the server after changing `server.py`. |
| A folder lane is missing | Ensure the folder has a supported source file, is not ignored, and is within the 4,000-file/180-node limits. |
| A file is in the wrong lane | Confirm the path uses the expected top-level directory. Lane placement is based on the first path segment, not the server's `group` field. |
| An expected connection is missing | Check the supported import/API patterns, path aliases, file extensions, and the 256 KB read limit. Extend the relevant parser for the project's conventions. |
| The map looks unchanged after editing HTML | Refresh the browser page. HTML is read from disk for each page request. |

## Maintenance checklist

- Keep the dashboard files together under the target project root.
- Re-test the lane assignments after changing scan-root logic or graph grouping.
- Re-test representative imports and API routes after modifying language or framework patterns.
- Keep secrets and private directories excluded.
- Revisit graph scan limits if the target project is substantially larger.
- Keep this guide aligned with `server.py`, `index.html`, and the launcher whenever behavior changes.
