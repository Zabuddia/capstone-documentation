# Capstone Documentation

Basic instructions for running this docs site with MkDocs.

## Prerequisites

- Python 3.10+ (or similar recent version)
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
