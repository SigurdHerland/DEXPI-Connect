# DEXPI-Connect  
*A graph-centric, DEXPI-based pipeline for smarter P&ID engineering*  
**Master’s Thesis — NTNU, 2025 — Sigurd Herland**

> Parse a raw **COMOS DEXPI** export → build a **fully connected knowledge-graph** → explore it in your browser → hand back a **re-drawn P&ID** for verification.  
> Everything that powered the thesis is here: code, graphs, images, and validation artefacts.

---

## 📑 Table of contents
1. [Why this project?](#why-this-project)
2. [Repository layout](#repository-layout)
3. [Quick start](#quick-start)
4. [Pipeline in five steps](#pipeline-in-five-steps)
5. [Validation criteria](#validation-criteria)
6. [Screenshots](#screenshots)
7. [Roadmap](#roadmap)
8. [Contributing](#contributing)
9. [Licence](#licence)
10. [Citation](#citation)

---

## Why this project?
* **DEXPI is rich –** but raw XML is hard to read and often missing links.  
* **Graphs are expressive –** once the P&ID is a graph, we can query, validate and visualise it.  
* **Engineers want trust –** they need to see that the generated graph really matches their drawing.

**DEXPI-Connect** delivers all three:

| Feature | What it gives you |
|---------|------------------|
| **Graph builder** | Extracts all lines *and* semantic objects from COMOS DEXPI and connects the dots. |
| **Connection inference** | Finds orphan valves, nozzles, off-page refs and joins them intelligently. |
| **Isomorphism search** | Detects repeated piping modules (copy-pasted skids, standard loops …). |
| **Interactive HTML** | Zero-install graph explorer – pan/zoom, highlight systems, inspect tags. |
| **P&ID regeneration** | Auto-draws centre-lines back into SVG/PNG for side-by-side QA. |
| **Validation suite** | Ten quantitative checks (semantic, topological, completeness). |

---

## Repository layout
