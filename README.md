# DEXPI-Connect (Master Thesis code dump)

This repo holds everything used in my master thesis on a **graph-centric, DEXPI-based approach to P&ID engineering design**.

## What’s here

| Folder / file            | What it contains |
|--------------------------|------------------|
| **Final Network Graphs** | Interactive HTML files showing the full “high-level” knowledge graphs generated from each DEXPI file. Open them in any browser. |
| **Graph_Isomorphism**    | HTML files with the smaller piping sub-graphs that were detected as repeating patterns (graph-isomorphism results). |
| **P&ID**                 | Images (SVG/PNG) of the P&IDs that were automatically reconstructed from the DEXPI data. |
| **Spagetti**             | All code. `Main.py` runs the whole pipeline. Inside this folder, **Process_dexpi/** contains the step-by-step scripts used in the thesis, including `elementsearch.py` for quick XML lookup. |

