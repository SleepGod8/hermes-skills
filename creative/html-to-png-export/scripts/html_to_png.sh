#!/usr/bin/env bash
# html_to_png.sh — Convert a local HTML file to PNG via headless Chrome (Windows git-bash).
# Usage: bash html_to_png.sh <input.html> [output.png] [window_width] [window_height]
# Example: bash html_to_png.sh E:/ai1/nl2sql-flowchart.html E:/ai1/out.png 1200 1500
# Notes: Chrome may exit code 2 on success; success is verified by output file existence.
set -u

INPUT="$1"
OUTPUT="${2:-${INPUT%.html}.png}"
WIDTH="${3:-1200}"
HEIGHT="${4:-1500}"

# Locate a Chromium-based browser
CHROME=""
for cand in \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Microsoft/Edge/Application/msedge.exe"; do
  if [ -f "$cand" ]; then CHROME="$cand"; break; fi
done

if [ -z "$CHROME" ]; then
  echo "ERROR: no Chrome/Edge found" >&2
  exit 1
fi

# Convert to file:// URL (accepts E:/path or /e/path or E:\\path forms)
WINPATH=$(cygpath -w "$INPUT" 2>/dev/null || echo "$INPUT")
FILEURL="file:///${WINPATH//\\//}"

"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 \
  --window-size="${WIDTH},${HEIGHT}" \
  --virtual-time-budget=8000 \
  --screenshot="$(cygpath -w "$OUTPUT" 2>/dev/null || echo "$OUTPUT")" \
  "$FILEURL" >/dev/null 2>&1

# Chrome exits non-zero on success sometimes — verify by file
if [ -s "$OUTPUT" ]; then
  echo "OK: $OUTPUT ($(stat -c%s "$OUTPUT") bytes)"
  python -c "from PIL import Image; im=Image.open(r'$OUTPUT'); print('Dimensions:', im.size)" 2>/dev/null \
    || python -c "import struct;f=open(r'$OUTPUT','rb');d=f.read(33);print('Dimensions:', struct.unpack('>II', d[16:24]))" 2>/dev/null \
    || true
else
  echo "ERROR: output file missing/empty" >&2
  exit 1
fi
