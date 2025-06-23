# DEXPI-Connect (Master Thesis code dump)

This repo holds everything used in my master thesis on a **graph-centric, DEXPI-based approach to P&ID engineering design**.

## What’s here

| Folder / file            | What it contains |
|--------------------------|------------------|
| **Final Network Graphs** | Interactive HTML files showing the full “high-level” knowledge graphs generated from each DEXPI file. Open them in any browser. |
| **Graph_Isomorphism**    | HTML files with the smaller piping sub-graphs that were detected as repeating patterns (graph-isomorphism results). |
| **P&ID**                 | Images (SVG/PNG) of the P&IDs that were automatically reconstructed from the DEXPI data. |
| **Spagetti**             | All code. `Main.py` runs the whole pipeline. Inside this folder, **Process_dexpi/** contains the step-by-step scripts used in the thesis, including `elementsearch.py` for quick XML lookup. |

## 📊 Viewing the HTML graph files

Both **Final Network Graphs** and **Graph_Isomorphism** contain ready-made, self-contained HTML visualisations.  
Download them to your computer and open them in any modern browser—no server, plugins, or internet connection required.

| Folder | File pattern | What it shows | How to open |
|--------|--------------|---------------|-------------|
| `Final Network Graphs/` | `*.html` | **Full knowledge graph** for each DEXPI file. Zoom, pan, and click any node to inspect its tag, ISO 15926 class, system, etc. | ① Clone the repo *or* click the file in GitHub → **Download raw**.<br>② Double-click the saved HTML (or drag it into a browser window). |
| `Graph_Isomorphism/` | `*.html` | **Repeated piping sub-graphs** (modules found via graph-isomorphism). Click a card to highlight every occurrence in the drawing. | Same steps as above—works offline in Chrome, Edge, Firefox, Safari. |


