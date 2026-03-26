#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
PIP_BIN="$ROOT_DIR/.venv/bin/pip"
MKDOCS_BIN="$ROOT_DIR/.venv/bin/mkdocs"
SITE_DIR="$ROOT_DIR/.pdf-build/site"
HTML_DIR="$ROOT_DIR/.pdf-build/html"
OUTPUT_PDF="$ROOT_DIR/pdf/capstone-documentation.pdf"
CHROMIUM_BIN="${CHROMIUM_BIN:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)}"

if [[ -z "${CHROMIUM_BIN:-}" ]]; then
  echo "Chromium or Chrome is required to build the PDF." >&2
  exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  python3 -m venv "$ROOT_DIR/.venv"
fi

"$PYTHON_BIN" -m pip install --upgrade pip >/dev/null
"$PIP_BIN" install mkdocs mkdocs-material beautifulsoup4 >/dev/null

rm -rf "$ROOT_DIR/.pdf-build"
mkdir -p "$ROOT_DIR/.pdf-build" "$ROOT_DIR/pdf"

"$MKDOCS_BIN" build --clean -q -d "$SITE_DIR"
"$PYTHON_BIN" "$ROOT_DIR/scripts/build_combined_html.py" --site-dir "$SITE_DIR" --output-dir "$HTML_DIR"

PUPPETEER_SKIP_DOWNLOAD=1 \
PUPPETEER_EXECUTABLE_PATH="$CHROMIUM_BIN" \
  npx -y pagedjs-cli "$HTML_DIR/combined-paged.html" -o "$OUTPUT_PDF" >/dev/null

rm -rf "$ROOT_DIR/.pdf-build"

echo "Built PDF: $OUTPUT_PDF"
