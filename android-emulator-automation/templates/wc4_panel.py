"""
世界征服者4 - GUI 控制面板模板 (MuMu + ADB + tkinter)
========================================================
拖入用户项目目录，修改顶部的 ADB_HOST 和 ADB_PATH 即可使用。

功能：实时预览 / 点击预览=点击游戏 / 快捷按钮 / 坐标录制 / 城市列表 / 自动挂机
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess, threading, time, os
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageTk

# === 配置 ===
ADB_HOST = "127.0.0.1:16416"
ADB_PATH = r"C:\Users\...\adb.exe"

# === ADB 封装 ===
class ADB:
    def __init__(self, host=ADB_HOST, path=ADB_PATH):
        self.host = host; self.path = path
    def _run(self, cmd, timeout=10):
        r = subprocess.run(f'"{self.path}" -s {self.host} {cmd}', shell=True,
                          capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    def connect(self):
        self._run("connect "+self.host)
        return "device" in self._run("devices")
    def screenshot(self):
        proc = subprocess.run(f'"{self.path}" -s {self.host} exec-out screencap -p',
                             shell=True, capture_output=True, timeout=10)
        return Image.open(BytesIO(proc.stdout))
    def click(self, x, y):
        self._run(f"shell input tap {x} {y}"); time.sleep(0.3)
    def get_size(self):
        out = self._run("shell wm size")
        w, h = out.split(":")[-1].strip().split("x")
        return int(w), int(h)

# === GUI ===
class GamePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("游戏控制面板")
        self.root.geometry("900x700")
        self.adb = ADB()
        self.running = False
        self.city_list = []
        self._build_ui()
    
    def _build_ui(self):
        # 顶栏
        bar = tk.Frame(self.root, bg="#16213e")
        bar.pack(fill=tk.X, padx=5, pady=5)
        self.btn_conn = tk.Button(bar, text="连接模拟器", command=self.do_connect)
        self.btn_conn.pack(side=tk.LEFT)
        self.status_lbl = tk.Label(bar, text="未连接", fg="#888", bg="#16213e")
        self.status_lbl.pack(side=tk.LEFT, padx=10)
        self.btn_loop = tk.Button(bar, text="开始挂机", command=self.toggle_loop, state=tk.DISABLED)
        self.btn_loop.pack(side=tk.LEFT, padx=5)
        
        # 主区
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 左侧预览
        self.canvas = tk.Canvas(main, bg="#111", width=320, height=570)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # 右侧控制
        ctrl = tk.Frame(main, width=250, bg="#1a1a2e")
        ctrl.pack(side=tk.RIGHT, fill=tk.Y)
        # 坐标输入
        self.entry_x = tk.Entry(ctrl, width=6); self.entry_x.pack()
        self.entry_y = tk.Entry(ctrl, width=6); self.entry_y.pack()
        tk.Button(ctrl, text="点击", command=self.do_click).pack()
        # 城市列表
        self.listbox = tk.Listbox(ctrl, height=6)
        self.listbox.pack(fill=tk.X)
        tk.Button(ctrl, text="+ 城市", command=self.add_city).pack()
        tk.Button(ctrl, text="遍历", command=self.traverse).pack()
        
        # 日志
        self.log = scrolledtext.ScrolledText(self.root, height=5, bg="#111", fg="#0f0")
        self.log.pack(fill=tk.X, padx=5, pady=5)
    
    def log_msg(self, msg):
        self.log.insert(tk.END, msg+"\n"); self.log.see(tk.END)
    
    def do_connect(self):
        if self.adb.connect():
            self.status_lbl.config(text="已连接", fg="#0f0")
            self.btn_loop.config(state=tk.NORMAL)
            self.do_screenshot()
        else:
            self.status_lbl.config(text="失败", fg="#f00")
    
    def do_screenshot(self):
        img = self.adb.screenshot().resize((320, 570))
        self._img = ImageTk.PhotoImage(img)
        self.canvas.create_image(160, 285, image=self._img, anchor=tk.CENTER)
    
    def on_click(self, e):
        sx, sy = 1080/320, 1920/570
        rx, ry = int(e.x*sx), int(e.y*sy)
        self.adb.click(rx, ry)
        self.entry_x.delete(0, tk.END); self.entry_x.insert(0, str(rx))
        self.entry_y.delete(0, tk.END); self.entry_y.insert(0, str(ry))
        self.root.after(500, self.do_screenshot)
    
    def add_city(self):
        try:
            x, y = int(self.entry_x.get()), int(self.entry_y.get())
            self.listbox.insert(tk.END, f"({x},{y})")
        except: pass
    
    def traverse(self):
        items = self.listbox.get(0, tk.END)
        def _loop():
            for item in items:
                if not self.running: break
                x, y = map(int, item.strip("()").split(","))
                self.adb.click(x, y); time.sleep(2)
                self.adb.click(540, 1700); time.sleep(1)
                self.adb.click(1000, 50); time.sleep(0.5)
        threading.Thread(target=_loop, daemon=True).start()
    
    def toggle_loop(self):
        self.running = not self.running
        self.btn_loop.config(text="停止" if self.running else "开始挂机")

if __name__ == "__main__":
    tk.Tk().__class__(GamePanel).mainloop()
