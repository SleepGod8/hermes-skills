#!/usr/bin/env python3
"""
Extract QR URL from Heremes gateway setup for a given platform.
Usage: python extract_qr_url.py [platform_number]

Default platform_number: 3 (Weixin/WeChat)
Outputs the QR URL to stdout on success, exits with code 1 on failure.
"""
import subprocess
import sys
import re
import time

PLATFORM = sys.argv[1] if len(sys.argv) > 1 else "3"

proc = subprocess.Popen(
    ['hermes', 'gateway', 'setup'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

# Feed answers
for answer in ['n', PLATFORM, 'y']:
    proc.stdin.write(answer + '\n')
    proc.stdin.flush()
    time.sleep(1)

# Scan output for QR URL
qr_url = None
start = time.time()
while time.time() - start < 15:
    line = proc.stdout.readline()
    if not line:
        time.sleep(0.5)
        continue
    # Look for any URL that looks like a QR/auth URL
    for pattern in [
        r'https://liteapp\.weixin\.qq\.com/q/[^\s]+',
        r'https?://[^\s]+qrcode[^\s]+',
    ]:
        match = re.search(pattern, line)
        if match:
            qr_url = match.group(0)
            break
    if qr_url:
        break

if qr_url:
    print(qr_url)
    # Keep process alive for the scan
    try:
        proc.wait(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
    sys.exit(0)
else:
    proc.kill()
    print("ERROR: Could not extract QR URL from gateway setup output", file=sys.stderr)
    sys.exit(1)
