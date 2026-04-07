#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_ARGS=(install --requirement "$ROOT_DIR/pdf/requirements.txt")
PAGEDJS_BIN="$ROOT_DIR/node_modules/.bin/pagedjs-cli"
SITE_DIR="$ROOT_DIR/.pdf-build/site"
HTML_SETUP_DIR="$ROOT_DIR/.pdf-build/html-setup"
HTML_USERGUIDE_DIR="$ROOT_DIR/.pdf-build/html-userguide"
OUTPUT_SETUP_PDF="$ROOT_DIR/pdf/setup-guide.pdf"
OUTPUT_USERGUIDE_PDF="$ROOT_DIR/pdf/user-guide.pdf"
CHROMIUM_BIN="${CHROMIUM_BIN:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || true)}"

cleanup() {
  rm -rf "$ROOT_DIR/.pdf-build"
}

ensure_venv() {
  if [[ ! -x "$PYTHON_BIN" ]]; then
    python3 -m venv "$VENV_DIR"
  fi

  if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
    "$PYTHON_BIN" -m ensurepip --upgrade >/dev/null
  fi
}

ensure_node_deps() {
  if [[ ! -x "$PAGEDJS_BIN" ]]; then
    PUPPETEER_SKIP_DOWNLOAD=1 npm ci --silent >/dev/null
  fi

  mkdir -p "$ROOT_DIR/node_modules/pagedjs-cli/docker-userdata"
}

if [[ -z "${CHROMIUM_BIN:-}" ]]; then
  echo "Chromium or Chrome is required to build the PDF." >&2
  exit 1
fi

ensure_venv
ensure_node_deps

"$PYTHON_BIN" -m pip install --upgrade pip >/dev/null
"$PYTHON_BIN" -m pip "${PIP_ARGS[@]}" >/dev/null

trap cleanup EXIT

cleanup
mkdir -p "$ROOT_DIR/.pdf-build" "$ROOT_DIR/pdf"

NO_MKDOCS_2_WARNING=true "$PYTHON_BIN" -m mkdocs build --clean -q -d "$SITE_DIR"

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_combined_html.py" \
  --site-dir "$SITE_DIR" \
  --output-dir "$HTML_SETUP_DIR" \
  --nav-sections "Home" "Build Order" "Reference" \
  --title "Capstone Setup Guide" \
  --description "Step-by-step setup and configuration instructions"

"$PYTHON_BIN" "$ROOT_DIR/scripts/build_combined_html.py" \
  --site-dir "$SITE_DIR" \
  --output-dir "$HTML_USERGUIDE_DIR" \
  --nav-sections "User Guide" \
  --title "Capstone User Guide" \
  --description "End-user guides for Cline, RAG Website, and OpenWebUI"

PUPPETEER_SKIP_DOWNLOAD=1 \
PUPPETEER_EXECUTABLE_PATH="$CHROMIUM_BIN" \
  "$PAGEDJS_BIN" "$HTML_SETUP_DIR/combined-paged.html" -o "$OUTPUT_SETUP_PDF" >/dev/null

PUPPETEER_SKIP_DOWNLOAD=1 \
PUPPETEER_EXECUTABLE_PATH="$CHROMIUM_BIN" \
  "$PAGEDJS_BIN" "$HTML_USERGUIDE_DIR/combined-paged.html" -o "$OUTPUT_USERGUIDE_PDF" >/dev/null

echo "Built PDF: $OUTPUT_SETUP_PDF"
echo "Built PDF: $OUTPUT_USERGUIDE_PDF"
