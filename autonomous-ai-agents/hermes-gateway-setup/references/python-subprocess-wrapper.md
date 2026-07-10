# Python Subprocess Wrapper for Gateway Setup

Use this pattern when the piped `echo` approach times out before the user scans the QR code. The wrapper keeps stdin open so the `hermes gateway setup` process stays alive.

## Minimal Script

```python
import subprocess
import sys
import time
import re
import os

proc = subprocess.Popen(
    ['hermes', 'gateway', 'setup'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

# Feed initial answers with delays
for answer in ['n', '3', 'y']:
    proc.stdin.write(answer + '\n')
    proc.stdin.flush()
    time.sleep(1)

# Read output to extract QR URL
qr_url = None
start = time.time()
while time.time() - start < 15:
    line = proc.stdout.readline()
    if not line:
        time.sleep(0.5)
        continue
    print(line, end='', flush=True)
    match = re.search(r'https://liteapp\.weixin\.qq\.com/q/[^\s]+', line)
    if match:
        qr_url = match.group(0)

print(f"\n=== QR URL: {qr_url or 'NOT FOUND'} ===")

# Wait for QR scan (up to 5 minutes)
try:
    proc.wait(timeout=300)
    remaining = proc.stdout.read()
    if remaining:
        print(remaining)
except subprocess.TimeoutExpired:
    proc.kill()
```

## Key Points

- `subprocess.PIPE` for stdin keeps the pipe **open** after the initial inputs, unlike `echo -e "..." |` which closes stdin after sending.
- 1-second delays between inputs prevent curses from buffering them at the wrong prompt.
- The script reads stdout line-by-line in real time (prints to its own stdout for capture).
- After finding the QR URL, it switches to `proc.wait()` — no more stdout reads, just waits for the wizard to complete or timeout.
- The process is killed after 5 minutes to prevent orphan processes.

## QR Code PNG Generation

If the user cannot see the ASCII QR code, generate a PNG:

```python
import qrcode
qr_url = "https://liteapp.weixin.qq.com/q/..."
img = qrcode.make(qr_url)
img.save(os.path.expanduser("~/wechat_qr.png"))
print(f"QR image saved to ~/wechat_qr.png")
```

Requires `pip install qrcode` (also needs `Pillow` as a dependency of `qrcode`).
