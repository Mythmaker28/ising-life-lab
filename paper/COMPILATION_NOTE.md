# Compilation Note

## PDF Compilation

To generate `main.pdf`, you need a LaTeX distribution installed:

### Installation Options

**Windows:**
```bash
# Install MiKTeX
# Download from: https://miktex.org/download
```

**Linux:**
```bash
sudo apt-get install texlive-full
```

**macOS:**
```bash
# Install MacTeX
# Download from: https://tug.org/mactex/
```

### Compile Command

```bash
cd paper
pdflatex main.tex
pdflatex main.tex  # Run twice for cross-references
```

### Alternative: Overleaf

If you don't want to install LaTeX locally:
1. Go to https://www.overleaf.com
2. Create new project > Upload Project
3. Upload `main.tex` and the `figures/` folder
4. Compile online

## Current Status

- ✅ Manuscript updated with realistic physics models
- ✅ All figures generated (3 PNG files in paper/figures/)
- ✅ Results from 9 systems (NV, 13C, RP)
- ⚠️ PDF not compiled (LaTeX not installed on this system)

## Manual Next Steps

After installing LaTeX, run:
```bash
cd paper
pdflatex main.tex
pdflatex main.tex
```

This will generate `main.pdf` ready for arXiv submission.

