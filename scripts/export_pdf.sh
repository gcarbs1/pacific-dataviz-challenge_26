#!/bin/sh
# Rebuild the poster and export it as a vector A4 PDF (text and artwork stay
# vector, so the quality is resolution-independent).
#
#   scripts/export_pdf.sh
#
set -e
cd "$(dirname "$0")/.."

.venv/bin/python scripts/build_a4.py

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu \
  --virtual-time-budget=8000 \
  --no-pdf-header-footer \
  --print-to-pdf="viz/where-the-rain-went-a4.pdf" \
  "file://$PWD/viz/a4.html"

echo "wrote viz/where-the-rain-went-a4.pdf"
