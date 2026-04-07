# Capstone Documentation

This repository contains the MkDocs source for the Capstone documentation site and the generated PDF guides.

## Setup

Prerequisites:

- Python 3
- Node.js and `npm`

Set up the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r pdf/requirements.txt
```

Install the pinned PDF build dependency:

```bash
npm ci
```

## Common Commands

Activate the virtual environment before running these commands:

```bash
source .venv/bin/activate
```

Run the docs site locally:

```bash
mkdocs serve
```

Build the static site:

```bash
mkdocs build
```

The static site output is written to `site/`.

Build the PDF guides:

```bash
./scripts/build_pdf.sh
```

PDF build prerequisites:

- Chromium, `chromium-browser`, or Google Chrome

Generated PDFs:

- `pdf/setup-guide.pdf`
- `pdf/user-guide.pdf`

## Adding or Updating Pages

1. Create or edit Markdown files in `docs/`.
2. Add new pages to the `nav` section in `mkdocs.yml`.
3. Run `mkdocs serve` to review changes locally.
4. Run `./scripts/build_pdf.sh` if the PDF guides should be refreshed.

Example `mkdocs.yml` navigation entry:

```yaml
nav:
  - Home: index.md
  - New Page: new-page.md
```

## Project Structure

- `mkdocs.yml`: MkDocs site configuration and navigation
- `docs/`: Markdown source files
- `scripts/build_pdf.sh`: Builds the PDF guides
- `scripts/build_combined_html.py`: Prepares combined HTML used for PDF export
- `pdf/requirements.txt`: Python dependencies for PDF generation
- `package.json` and `package-lock.json`: Pinned Node dependency for PDF generation
- `pdf/setup-guide.pdf`: Generated setup guide PDF
- `pdf/user-guide.pdf`: Generated user guide PDF

## Notes

- `scripts/build_pdf.sh` bootstraps the local Python environment if needed.
- The PDF build uses the repo’s pinned `pagedjs-cli` dependency for more consistent output.
