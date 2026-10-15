#!/bin/sh
# Rebuild the poster and export a vector A4 PDF plus a high-resolution PNG.
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

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --virtual-time-budget=8000 \
  --window-size=840,1188 \
  --force-device-scale-factor=4 \
  --screenshot="viz/where-the-rain-went-a4.png" \
  "file://$PWD/viz/a4.html?png=1"

echo "wrote viz/where-the-rain-went-a4.pdf"
echo "wrote viz/where-the-rain-went-a4.png"
