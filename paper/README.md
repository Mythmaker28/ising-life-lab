# arXiv Paper: Geometric Control of Biological Quantum Sensors

## Compilation

To compile the PDF:

```bash
cd paper
pdflatex main.tex
pdflatex main.tex  # Run twice for references
```

Requirements:
- pdflatex (from TeX Live, MiKTeX, or similar LaTeX distribution)
- Standard packages: amsmath, amssymb, graphicx, authblk, hyperref

## Files

- `main.tex` - Main LaTeX manuscript
- `ABSTRACT_arxiv.txt` - Plain-text abstract for arXiv submission form
- `figures/` - Publication-ready figures (PNG, 300 DPI)
  - `figure1_nv298k_p3_vs_p4.png`
  - `figure2_multi_system_comparison.png`
  - `figure3_system_properties.png`

## arXiv Submission Checklist

1. Upload `main.tex`
2. Upload all files in `figures/` directory
3. Paste contents of `ABSTRACT_arxiv.txt` into arXiv abstract field
4. Select subject: quant-ph (Quantum Physics), with possible cross-lists to physics.bio-ph (Biological Physics)

## Repository

Full code and data: https://github.com/Mythmaker28/ising-life-lab
Branch: `toolkit-core-r1`

