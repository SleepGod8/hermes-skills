"""
世界征服者4 - 征服模式自动扩张脚本 (MuMu模拟器)
=================================================
原理：ADB 截图 → 图像识别 → 自动点击 → 循环
需要先截图按钮模板放入 templates/ 文件夹

运行方式: python wc4_conquest.py
依赖: pip install opencv-python pillow numpy
"""

import subprocess
import time
import os
import sys
from pathlib import Path
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

# ============================================================
# 配置区（按实际情况修改）
# ============================================================

# MuMu 模拟器 ADB 连接地址（MuMu 12 常用 127.0.0.1:16384 或 127.0.0.1:7555）
ADB_HOST = "127.0.0.1:16384"

# ADB 路径（如果系统 PATH 里没有 adb，填完整路径）
ADB_PATH = "adb"

# 模板图片文件夹
TEMPLATE_DIR = Path(__file__).parent / "templates"

# 点击间隔（秒）
CLICK_INTERVAL = 0.5
ACTION_WAIT = 2.0
MAX_LOOPS = 999

# ============================================================
# ADB 基础操作
# ============================================================

def adb(cmd: str, timeout: int = 15) -> str:
    """执行 ADB 命令"""
    full_cmd = f'{ADB_PATH} -s {ADB_HOST} {cmd}'
    try:
        r = subprocess.run(full_cmd, shell=True, capture_output=True,
                          text=True, timeout=timeout, encoding="utf-8", errors="ignore")
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"[警告] ADB 超时: {cmd[:50]}")
        return ""

def adb_connect() -> bool:
    """连接 MuMu 模拟器"""
    print(f"[连接] 尝试连接 {ADB_HOST}...")
    result = adb("connect " + ADB_HOST)
    print(f"  {result}")
    devices = adb("devices")
    return ADB_HOST.replace(":", "-") in devices or "device" in devices

def click(x: int, y: int):
    """点击屏幕坐标"""
    adb(f"shell input tap {x} {y}")
    time.sleep(CLICK_INTERVAL)

def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    """滑动"""
    adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
    time.sleep(CLICK_INTERVAL)

def screenshot() -> np.ndarray:
    """截取模拟器屏幕，返回 OpenCV 格式图片"""
    proc = subprocess.run(
        f'{ADB_PATH} -s {ADB_HOST} exec-out screencap -p',
        shell=True, capture_output=True, timeout=10
    )
    img = Image.open(BytesIO(proc.stdout))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def get_screen_size() -> tuple:
    """获取屏幕分辨率"""
    out = adb("shell wm size")
    try:
        size_str = out.split(":")[-1].strip()
        w, h = size_str.split("x")
        return int(w), int(h)
    except:
        return 1920, 1080

# ============================================================
# 图像识别
# ============================================================

def find_template(screen: np.ndarray, template_name: str, threshold: float = 0.8) -> tuple | None:
    """在屏幕中查找模板图片，返回中心坐标 (x,y) 或 None"""
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        print(f"[警告] 模板不存在: {template_path}")
        return None
    template = cv2.imread(str(template_path))
    if template is None:
        return None
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        h, w = template.shape[:2]
        return (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return None

def wait_and_click(template_name: str, timeout: float = 10.0, threshold: float = 0.8) -> bool:
    """等待模板出现并点击"""
    start = time.time()
    while time.time() - start < timeout:
        pos = find_template(screenshot(), template_name, threshold)
        if pos:
            click(*pos)
            print(f"  点击 {template_name} @ {pos}")
            return True
        time.sleep(0.5)
    print(f"  超时: 未找到 {template_name}")
    return False

def is_on_screen(template_name: str, threshold: float = 0.8) -> bool:
    """检查模板是否在当前屏幕上"""
    return find_template(screenshot(), template_name, threshold) is not None

# ============================================================
# 游戏操作（世界征服者4 示例）
# ============================================================

def is_in_battle() -> bool:
    """判断是否在战斗/大地图界面"""
    return is_on_screen("end_turn.png", 0.75) or is_on_screen("next_turn.png", 0.75)

def end_turn():
    """结束回合"""
    if wait_and_click("end_turn.png", timeout=5):
        time.sleep(ACTION_WAIT)
    elif wait_and_click("next_turn.png", timeout=2):
        time.sleep(ACTION_WAIT)

def select_city():
    """点击最近的己方城市"""
    pos = find_template(screenshot(), "friendly_city.png", 0.7)
    if pos:
        click(*pos)
        time.sleep(1)
        return True
    return False

def produce_unit(unit_type: str = "infantry"):
    """在城市中生产部队"""
    unit_btns = {
        "infantry": "btn_infantry.png",
        "tank": "btn_tank.png",
        "artillery": "btn_artillery.png",
        "navy": "btn_navy.png",
    }
    btn = unit_btns.get(unit_type, "btn_infantry.png")
    if wait_and_click(btn, timeout=3):
        wait_and_click("btn_produce.png", timeout=2)
        return True
    return False

def find_nearest_enemy() -> tuple | None:
    """找到最近的敌方单位或城市"""
    for template in ["enemy_unit.png", "enemy_city.png", "enemy_red.png"]:
        pos = find_template(screenshot(), template, 0.7)
        if pos:
            return pos
    return None

def move_to_enemy():
    """移动到敌方附近"""
    enemy_pos = find_nearest_enemy()
    if enemy_pos:
        click(*enemy_pos)
        time.sleep(1)
        wait_and_click("btn_move.png", timeout=3)
        return True
    return False

def attack():
    """攻击当前目标"""
    wait_and_click("btn_attack.png", timeout=3)

def handle_popups():
    """处理弹窗"""
    for popup in ["btn_ok.png", "btn_confirm.png", "btn_close.png", "btn_skip.png"]:
        pos = find_template(screenshot(), popup, 0.75)
        if pos:
            click(*pos)
            print(f"  关闭弹窗: {popup}")
            time.sleep(0.5)

# ============================================================
# 征服模式主循环
# ============================================================

def conquest_loop(max_turns: int = 1000):
    """征服模式自动扩张主循环"""
    print(f"\n{'='*50}")
    print(f"  世界征服者4 - 征服模式自动扩张")
    print(f"  模拟器: {ADB_HOST}")
    print(f"  最大回合: {max_turns}")
    print(f"{'='*50}\n")

    screen_w, screen_h = get_screen_size()
    print(f"[信息] 屏幕分辨率: {screen_w} x {screen_h}")

    turn = 0
    no_progress_count = 0

    while turn < max_turns:
        turn += 1
        print(f"\n--- 回合 {turn} ---")

        handle_popups()
        time.sleep(ACTION_WAIT)

        if not is_in_battle():
            print("[警告] 似乎不在战斗界面，尝试返回...")
            wait_and_click("btn_back.png", timeout=3)
            time.sleep(ACTION_WAIT)
            continue

        print("[行动] 检查己方城市...")
        cities_produced = 0
        for _ in range(20):
            if select_city():
                if produce_unit("tank"):
                    cities_produced += 1
                elif produce_unit("infantry"):
                    cities_produced += 1
                wait_and_click("btn_close.png", timeout=2)
            else:
                break
        print(f"  本回合产出: {cities_produced} 个城市")

        print("[行动] 部署部队...")
        moves = 0
        for _ in range(30):
            if move_to_enemy():
                moves += 1
                attack()
                time.sleep(ACTION_WAIT)
            else:
                break
        print(f"  本回合移动/攻击: {moves} 次")

        handle_popups()
        print("[行动] 结束回合...")
        end_turn()

        if cities_produced == 0 and moves == 0:
            no_progress_count += 1
        else:
            no_progress_count = 0

        if no_progress_count >= 5:
            print("\n[提示] 连续 5 回合无行动，可能游戏结束")
            break

    print(f"\n完成！共执行 {turn} 回合")


# ============================================================
# 简易模式：纯坐标点击（不需要模板匹配）
# ============================================================

def simple_conquest_loop(city_coords: list = None, turns: int = 500):
    """纯坐标点击模式 - 不需要截图模板"""
    print("\n=== 简易征服模式 ===")
    print("前提：已手动进入征服模式大地图")

    screen_w, screen_h = get_screen_size()

    if city_coords is None:
        city_coords = [
            (screen_w//4, screen_h//3),
            (screen_w//3, screen_h//2),
            (screen_w//5, screen_h//2 + 100),
        ]

    for turn in range(turns):
        print(f"\n--- 回合 {turn + 1} ---")
        for i, (cx, cy) in enumerate(city_coords):
            print(f"  城市 {i+1}: 点击 ({cx}, {cy})")
            click(cx, cy)
            time.sleep(1.5)
            click(screen_w // 2, screen_h - 150)
            time.sleep(1)
            click(screen_w // 3, screen_h - 250)
            time.sleep(0.5)
            click(screen_w // 2, screen_h - 100)
            time.sleep(0.5)
            click(screen_w - 50, 50)
            time.sleep(0.5)

        print("  结束回合")
        click(screen_w - 80, screen_h - 80)
        time.sleep(3)


# ============================================================
# 坐标录制工具
# ============================================================

def record_clicks():
    """坐标录制模式"""
    print("\n=== 坐标录制模式 ===")
    print("输入坐标来点击，Ctrl+C 停止。\n")
    while True:
        try:
            x = int(input("X坐标: "))
            y = int(input("Y坐标: "))
            click(x, y)
            print(f"  → 已点击 ({x}, {y})")
        except (ValueError, KeyboardInterrupt):
            print("\n录制结束")
            break


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════╗")
    print("║  世界征服者4 - 自动扩张脚本      ║")
    print("║  MuMu 模拟器版                   ║")
    print("╚══════════════════════════════════╝")
    print()
    print("模式选择：")
    print("  1 = 简易模式（纯坐标点击）")
    print("  2 = 模板匹配模式（需要截图模板）")
    print("  3 = 坐标录制工具")
    print("  0 = 退出")

    try:
        choice = input("请选择模式 [1/2/3/0]: ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "0"

    if choice == "0":
        print("再见~")
        sys.exit(0)

    if not adb_connect():
        print("\n[错误] 无法连接 MuMu 模拟器！")
        print("请检查：")
        print("  1. MuMu 模拟器是否正在运行")
        print("  2. ADB 端口是否正确（修改 ADB_HOST）")
        print("  常见 MuMu 12 端口: 16384, 7555, 21503")
        sys.exit(1)

    if choice == "1":
        simple_conquest_loop(turns=500)
    elif choice == "2":
        max_t = input("最大回合数 [默认 500]: ").strip()
        max_t = int(max_t) if max_t else 500
        conquest_loop(max_turns=max_t)
    elif choice == "3":
        record_clicks()
