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

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install mkdocs mkdocs-material
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

## Project Structure

- `mkdocs.yml`: MkDocs configuration and navigation
- `docs/`: Markdown source files for the documentation
