# Capstone Documentation

## Add a New Documentation Page

1. Create a new Markdown file in `docs/`:

2. Add your content to that file (start with a heading, for example `# New Page`).

3. Add the page to `nav` in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - New Page: new-page.md
```

4. Run locally and verify:

```bash
mkdocs serve
```

Basic instructions for running this docs site with MkDocs.

## Prerequisites

- Python
- `pip`
- Node.js / `npx`
- Chromium or Google Chrome

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install mkdocs mkdocs-material beautifulsoup4
```

## Run Locally

```bash
mkdocs serve
```

Then open: `http://127.0.0.1:8000`

## Build Static Site

```bash
mkdocs build
```

Build output goes to `site/`.

## Build PDF

After changing any file in `docs/` or `mkdocs.yml`, run:

```bash
./scripts/build_pdf.sh
```

The generated PDF is written to `pdf/capstone-documentation.pdf`.

## Project Structure

- `mkdocs.yml`: MkDocs configuration and navigation
- `docs/`: Markdown source files for the documentation
- `scripts/build_pdf.sh`: rebuilds the PDF export
- `pdf/capstone-documentation.pdf`: committed PDF output
