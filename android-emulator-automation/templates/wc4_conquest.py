"""
世界征服者4 - 征服模式自动扩张脚本 (MuMu模拟器)
=================================================
原理：ADB 截图 → 图像识别 → 自动点击 → 循环
需要先截图按钮模板放入 templates/ 文件夹

运行：C:\Users\80704\AppData\Local\Python\pythoncore-3.14-64\python wc4_conquest.py
依赖：pip install opencv-python pillow numpy
"""

import subprocess, time, os, sys
from pathlib import Path
from io import BytesIO
import cv2, numpy as np
from PIL import Image

# ============================================================
# 配置区
# ============================================================

ADB_HOST = "127.0.0.1:16416"
ADB_PATH = r"C:\Users\80704\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
TEMPLATE_DIR = Path(__file__).parent / "templates"
CLICK_INTERVAL = 0.5
ACTION_WAIT = 2.0

# ============================================================
# ADB
# ============================================================

def adb(cmd, timeout=15):
    r = subprocess.run(f'{ADB_PATH} -s {ADB_HOST} {cmd}', shell=True,
        capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="ignore")
    return r.stdout.strip()

def adb_connect():
    """Try multiple common MuMu ports"""
    print(f"[连接] 扫描 MuMu 端口...")
    ports = ["16416","5557","7555","16384","21503","5555"]
    for p in ports:
        r = adb(f"connect 127.0.0.1:{p}")
        if "connected" in r.lower():
            print(f"  ✓ 127.0.0.1:{p}")
    return "device" in adb("devices")

def click(x, y):
    adb(f"shell input tap {x} {y}")
    time.sleep(CLICK_INTERVAL)

def screenshot():
    proc = subprocess.run(f'{ADB_PATH} -s {ADB_HOST} exec-out screencap -p',
        shell=True, capture_output=True, timeout=10)
    img = Image.open(BytesIO(proc.stdout))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def get_screen_size():
    try:
        w, h = adb("shell wm size").split(":")[-1].strip().split("x")
        return int(w), int(h)
    except:
        return 1920, 1080

# ============================================================
# 图像识别
# ============================================================

def find_template(screen, name, threshold=0.8):
    path = TEMPLATE_DIR / name
    if not path.exists(): return None
    tpl = cv2.imread(str(path))
    if tpl is None: return None
    result = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = tpl.shape[:2]
        return (max_loc[0]+w//2, max_loc[1]+h//2)
    return None

def wait_and_click(name, timeout=10.0, threshold=0.8):
    start = time.time()
    while time.time()-start < timeout:
        pos = find_template(screenshot(), name, threshold)
        if pos: click(*pos); return True
        time.sleep(0.5)
    return False

# ============================================================
# 游戏操作
# ============================================================

def handle_popups():
    for p in ["btn_ok.png","btn_confirm.png","btn_close.png","btn_skip.png"]:
        pos = find_template(screenshot(), p, 0.75)
        if pos: click(*pos); time.sleep(0.5)

def end_turn():
    wait_and_click("end_turn.png",5) or wait_and_click("next_turn.png",2)
    time.sleep(ACTION_WAIT)

# ============================================================
# 征服模式
# ============================================================

def conquest_loop(max_turns=1000):
    screen_w, screen_h = get_screen_size()
    print(f"屏幕: {screen_w}x{screen_h}")
    for turn in range(1, max_turns+1):
        print(f"\n--- 回合 {turn} ---")
        handle_popups(); time.sleep(ACTION_WAIT)

        for _ in range(20):
            pos = find_template(screenshot(), "friendly_city.png", 0.7)
            if not pos: break
            click(*pos); time.sleep(1)
            wait_and_click("btn_tank.png",3) or wait_and_click("btn_infantry.png",2)
            wait_and_click("btn_produce.png",2)
            wait_and_click("btn_close.png",2)

        for _ in range(30):
            enemy = find_template(screenshot(),"enemy_unit.png",0.7) or find_template(screenshot(),"enemy_city.png",0.7)
            if not enemy: break
            click(*enemy); time.sleep(1)
            wait_and_click("btn_attack.png",3) or wait_and_click("btn_move.png",3)
            time.sleep(ACTION_WAIT)

        handle_popups(); end_turn()
    print(f"\n完成！{turn} 回合")

# ============================================================
# 简易模式
# ============================================================

def simple_conquest_loop(turns=500):
    screen_w, screen_h = get_screen_size()
    for t in range(turns):
        for cx, cy in [(screen_w//4,screen_h//3),(screen_w//3,screen_h//2)]:
            click(cx,cy); time.sleep(1.5)
            click(screen_w//2,screen_h-150); time.sleep(1)
            click(screen_w//3,screen_h-250); time.sleep(0.5)
            click(screen_w//2,screen_h-100); time.sleep(0.5)
        click(screen_w-80,screen_h-80); time.sleep(3)

# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    print("\n╔══════════════════════════════╗")
    print("║  世界征服者4 - 自动扩张脚本  ║")
    print("╚══════════════════════════════╝")
    print("\n1=简易 2=模板 3=坐标录制 0=退出")
    c = input("选择: ").strip()
    if c == "0": sys.exit(0)
    if not adb_connect(): print("连接失败！"); sys.exit(1)
    if c == "1": simple_conquest_loop(500)
    elif c == "2":
        t = input("最大回合 [500]: ").strip()
        conquest_loop(int(t) if t else 500)
    elif c == "3":
        print("输入 X Y，q 退出")
        while True:
            inp = input("X Y: ").strip()
            if inp == "q": break
            try:
                x,y = map(int, inp.split())
                click(x,y); print(f"  ({x},{y})")
            except: pass
