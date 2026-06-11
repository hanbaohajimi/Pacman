# pacman_launcher.py
# 吃豆人 AI 实验 —— GUI 启动器
# 提供图形化首页、模式选择、实验数据对比。

import sys
import os
import subprocess
import tkinter as tk
from tkinter import font as tkfont

_LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAUNCHER_DIR not in sys.path:
    sys.path.insert(0, _LAUNCHER_DIR)
from graphicsDisplay import draw_game_ghost_icon

# ---------- 配置 ----------
PACMAN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pacman.py")
PYTHON = sys.executable

# ---------- 实验数据 ----------
# (地图, 算法, 路径代价, 扩展节点数, 运行时间ms, 类别)
BENCHMARK = [
    ("tinyMaze",     "DFS",              10,   15,    2,  "blind"),
    ("tinyMaze",     "BFS",               8,   15,    3,  "blind"),
    ("tinyMaze",     "UCS",               8,   15,    3,  "blind"),
    ("tinyMaze",     "A* (曼哈顿)",        8,   14,    2,  "astar"),
    ("mediumMaze",   "DFS",             130,  146,   12,  "blind"),
    ("mediumMaze",   "BFS",              68,  269,   18,  "blind"),
    ("mediumMaze",   "UCS",              68,  269,   18,  "blind"),
    ("mediumMaze",   "A* (曼哈顿)",       68,  221,   15,  "astar"),
    ("bigMaze",      "DFS",             210,  390,   28,  "blind"),
    ("bigMaze",      "BFS",             210,  620,   42,  "blind"),
    ("bigMaze",      "UCS",             210,  620,   41,  "blind"),
    ("bigMaze",      "A* (曼哈顿)",      210,  549,   35,  "astar"),
    ("mediumCorners","A* (corners)",    106,  774,   38,  "multidot"),
    ("trickySearch", "A* (food)",        60, 4137,  185,  "multidot"),
]

MAP_NAMES = {
    "tinyMaze": "tinyMaze  小迷宫",
    "mediumMaze": "mediumMaze  中等迷宫",
    "bigMaze": "bigMaze  大迷宫",
    "mediumCorners": "mediumCorners  四角问题",
    "trickySearch": "trickySearch  全图吃豆",
}

# ---------- 模式数据 ----------
SECTIONS = {
    "keyboard": ("键盘操作",     "自由操控吃豆人，体验不同地图",         "⌨"),
    "blind":    ("盲目搜索算法",  "BFS / DFS / UCS 经典图搜索",        "◇"),
    "astar":    ("A* 启发式搜索", "可采纳启发式引导，高效最优路径",      "★"),
    "multidot": ("多点任务搜索",  "四角 / 全图吃豆，状态空间复杂",      "◆"),
    "bonus":    ("动态幽灵对抗",  "动态避障 / Alpha-Beta 博弈",         "⚡"),
}

# 预计算性能数据分组（静态数据，避免每次 refresh 重复计算）
_BENCHMARK_GROUPS = {}
for _r in BENCHMARK:
    _BENCHMARK_GROUPS.setdefault(_r[0], []).append(_r)

MODES = [
    ("小迷宫 (tinyMaze)",
     ["-l", "tinyMaze", "-p", "KeyboardAgent"],
     "小巧迷宫，适合初次上手体验", "tinyMaze", "keyboard"),
    ("小型经典 (smallClassic)",
     ["-l", "smallClassic", "-p", "KeyboardAgent"],
     "缩小版经典地图，难度适中", "smallClassic", "keyboard"),
    ("中等经典 (mediumClassic)",
     ["-l", "mediumClassic", "-p", "KeyboardAgent"],
     "标准经典地图，含幽灵追逐与道具", "mediumClassic", "keyboard"),
    ("大型经典 (originalClassic)",
     ["-l", "originalClassic", "-p", "KeyboardAgent"],
     "Berkeley 原版大型经典布局，挑战升级", "originalClassic", "keyboard"),
    ("BFS 广度优先搜索",
     ["-l", "mediumMaze", "-p", "SearchAgent", "-a", "fn=bfs"],
     "队列 FIFO — 层序遍历，保证找到最短路径", "mediumMaze", "blind"),
    ("DFS 深度优先搜索",
     ["-l", "mediumMaze", "-p", "SearchAgent", "-a", "fn=dfs"],
     "栈 LIFO — 一条路走到黑，路径通常非最优", "mediumMaze", "blind"),
    ("UCS 一致代价搜索",
     ["-l", "mediumMaze", "-p", "SearchAgent", "-a", "fn=ucs"],
     "优先队列按 g(n) 扩展，边权不同时仍最优", "mediumMaze", "blind"),
    ("A* + 曼哈顿 (中等迷宫)",
     ["-l", "mediumMaze", "-p", "SearchAgent", "-a", "fn=astar,heuristic=manhattanHeuristic"],
     "曼哈顿距离启发式，f(n)=g(n)+h(n) 引导搜索", "mediumMaze", "astar"),
    ("A* + 曼哈顿 (大迷宫)",
     ["-l", "bigMaze", "-z", "0.65", "-p", "SearchAgent", "-a", "fn=astar,heuristic=manhattanHeuristic"],
     "大迷宫下检验启发式的剪枝效率", "bigMaze", "astar"),
    ("A* 四角问题 (mediumCorners)",
     ["-l", "mediumCorners", "-p", "AStarCornersAgent"],
     "走遍四角，MST 下界启发式保证可采纳性", "mediumCorners", "multidot"),
    ("A* 四角问题 (tinyCorners)",
     ["-l", "tinyCorners", "-p", "AStarCornersAgent"],
     "小地图四角问题，适合快速演示", "tinyCorners", "multidot"),
    ("A* 吃光所有豆 (trickySearch)",
     ["-l", "trickySearch", "-p", "AStarFoodSearchAgent"],
     "多豆子搜索，mazeDistance 启发式", "trickySearch", "multidot"),
    ("A* 吃光所有豆 (multiFoodTest)",
     ["-l", "multiFoodTest", "-p", "AStarFoodSearchAgent"],
     "约 10 颗豆的小型多豆地图，A* 数秒内可完成规划", "multiFoodTest", "multidot"),
    ("A* 单豆批改 (testSearch)",
     ["-l", "testSearch", "-p", "AStarFoodSearchAgent"],
     "Berkeley 批改用单豆地图，仅 1 颗豆，快速验证路径", "testSearch", "multidot"),
    ("动态避障 (幽灵躲避)",
     ["-l", "smallClassic", "-p", "DynamicAvoidanceAgent"],
     "每步 A*：主动吃能量豆，惊吓后追击幽灵加分", "smallClassic", "bonus"),
    ("Alpha-Beta 对抗搜索",
     ["-l", "mediumClassic", "-z", "0.55", "-p", "AlphaBetaPacmanAgent"],
     "Minimax + α-β：吃能量豆后追击变白幽灵", "mediumClassic", "bonus"),
]

# ---------- 颜色 (Retro-Futurism Arcade Palette) ----------
# 参考 ui-ux-pro-max: Arcade & Retro Game 色彩方案
BG_ROOT       = "#0F172A"   # 深蓝黑背景（替代纯黑）
BG_PAGE       = "#0F172A"
BG_CARD       = "#192134"   # 深蓝紫卡片
BG_CARD_HOVER = "#1F2A45"   # 卡片悬停变亮
BG_TOPBAR     = "#0B1220"   # 顶栏略深于页面
FG_TITLE      = "#FBBF24"   # 琥珀金标题（保留 Pacman 黄）
FG_HEADING    = "#F1F5F9"   # 标题文字（slate-100）
FG_TEXT       = "#E2E8F0"   # 正文（slate-200）
FG_SUB        = "#94A3B8"   # 辅助文字（slate-400）
FG_TAG        = "#64748B"   # 标签（slate-500）
ACCENT        = "#DC2626"   # 霓虹红 — 主 CTA（ui-ux-pro-max Arcade primary）
ACCENT_HOVER  = "#EF4444"   # 霓虹红悬停
ACCENT_BLUE   = "#2563EB"   # 霓虹蓝 — 次级强调
BLUE_HOVER    = "#3B82F6"   # 蓝色悬停
SCORE_GREEN   = "#22C55E"   # 街机绿 — 最优值/得分
BTN_TEXT      = "#FFFFFF"   # 按钮文字
SCROLL_BG     = "#0F172A"

SEC_COLORS = {
    "keyboard": "#FBBF24",  # 琥珀金 — 玩家操控
    "blind":    "#22D3EE",  # 青色 — 盲目搜索
    "astar":    "#DC2626",  # 霓虹红 — A* 智能
    "multidot": "#F97316",  # 暖橙 — 多点任务
    "bonus":    "#8B5CF6",  # 紫罗兰 — 幽灵对抗
}

# ============================================================
_rr_counter = 0


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """圆角矩形（矩形 + 四角圆弧），避免 smooth polygon 在圆角处露底、涂色不均。"""
    global _rr_counter
    _rr_counter += 1
    tag = f"rounded_rect_{_rr_counter}"

    fill = kwargs.pop("fill", "") or ""
    outline = kwargs.pop("outline", "") or ""
    width = int(kwargs.pop("width", 1) or 0)

    r = min(radius, max(0, (x2 - x1) // 2), max(0, (y2 - y1) // 2))
    corners = [
        (x1, y1, 90),
        (x2 - 2 * r, y1, 0),
        (x2 - 2 * r, y2 - 2 * r, 270),
        (x1, y2 - 2 * r, 180),
    ]

    fill_tag = f"{tag}__fill"
    outline_tag = f"{tag}__outline"

    if fill:
        body = {"fill": fill, "outline": "", "width": 0, "tags": (tag, fill_tag)}
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **body)
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **body)
        for ax, ay, start in corners:
            canvas.create_arc(
                ax, ay, ax + 2 * r, ay + 2 * r,
                start=start, extent=90, style="pieslice", **body,
            )

    if outline:
        lw = max(1, width)
        edge = {"tags": (tag, outline_tag)}
        for x_start, x_end, y in ((x1 + r, x2 - r, y1), (x1 + r, x2 - r, y2)):
            canvas.create_line(x_start, y, x_end, y, fill=outline, width=lw, **edge)
        for y_start, y_end, x in ((y1 + r, y2 - r, x1), (y1 + r, y2 - r, x2)):
            canvas.create_line(x, y_start, x, y_end, fill=outline, width=lw, **edge)
        for ax, ay, start in corners:
            canvas.create_arc(
                ax, ay, ax + 2 * r, ay + 2 * r,
                start=start, extent=90, style="arc",
                outline=outline, width=lw, fill="", tags=(tag, outline_tag),
            )

    return tag


def configure_rounded_rect(canvas, tag, *, fill=None, outline=None):
    """按图元类型更新圆角矩形填充/描边，避免对 line 使用 outline 选项报错。"""
    if fill is not None:
        for item in canvas.find_withtag(f"{tag}__fill"):
            canvas.itemconfig(item, fill=fill)
    if outline is not None:
        for item in canvas.find_withtag(f"{tag}__outline"):
            if canvas.type(item) == "line":
                canvas.itemconfig(item, fill=outline)
            elif canvas.type(item) == "arc":
                canvas.itemconfig(item, outline=outline)


HOME_ICON_SIZE = 36
HOME_GHOST_UNIT = 11


def draw_pacman_icon(canvas, cx, cy, r=14, fill=FG_TITLE, bg=BG_PAGE):
    """绘制朝右的经典吃豆人（实心饼形 + 张嘴 + 眼睛）。"""
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    mouth = 62
    canvas.create_arc(
        x0, y0, x1, y1, start=mouth / 2, extent=360 - mouth,
        fill=fill, outline="", style="pieslice",
    )
    canvas.create_arc(
        x0, y0, x1, y1, start=360 - mouth / 2, extent=mouth,
        fill=bg, outline="", style="pieslice",
    )
    ex, ey = cx - r * 0.22, cy - r * 0.4
    er = max(2, int(r * 0.2))
    canvas.create_oval(ex - er, ey - er, ex + er, ey + er, fill=bg, outline="")


def draw_pellet_icon(canvas, cx, cy):
    """绘制小豆（实心光点，非空心圆环）。"""
    canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#4a4a58", outline="")
    canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#FFF4D6", outline="")
    canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill="#FFFFFF", outline="")


# ---------- 共享 UI 工厂函数 ----------
def _build_topbar(parent, title, ctrl):
    """统一的顶栏：标题 + 返回首页按钮 + 分隔线。"""
    bar = tk.Frame(parent, bg=BG_TOPBAR, height=60)
    bar.pack(fill="x"); bar.pack_propagate(False)
    tk.Label(bar, text=f"  {title}", font=("Microsoft YaHei", 16, "bold"),
             fg=FG_TITLE, bg=BG_TOPBAR).pack(side="left", padx=22, pady=12)
    bk = tk.Button(bar, text="返回首页", font=("Microsoft YaHei", 10, "bold"),
                   bg=BG_TOPBAR, fg=FG_SUB, activebackground=BG_TOPBAR,
                   activeforeground="#fff", relief="flat", cursor="hand2",
                   borderwidth=0, command=lambda: ctrl.show_frame("HomePage"))
    bk.pack(side="right", padx=22, pady=12)
    bk.bind("<Enter>", lambda e: bk.configure(fg="#fff"))
    bk.bind("<Leave>", lambda e: bk.configure(fg=FG_SUB))
    tk.Frame(parent, bg="#1E293B", height=1).pack(fill="x")


def _build_scroll_area(parent, width=None):
    """统一的滚动区域：返回 (canvas, scrollbar, inner_frame)。"""
    outer = tk.Frame(parent, bg=BG_PAGE); outer.pack(fill="both", expand=True)
    cvs = tk.Canvas(outer, bg=BG_PAGE, highlightthickness=0, bd=0)
    scl = tk.Scrollbar(outer, orient="vertical", command=cvs.yview, width=8)
    scl.configure(bg=SCROLL_BG, troughcolor=BG_PAGE, activebackground="#3a3a60", borderwidth=0)
    inr = tk.Frame(cvs, bg=BG_PAGE)
    inr.bind("<Configure>", lambda e: cvs.configure(scrollregion=cvs.bbox("all")))
    win_kw = {"window": inr, "anchor": "nw"}
    if width is not None:
        win_kw["width"] = width
    cvs.create_window((0, 0), **win_kw)
    cvs.configure(yscrollcommand=scl.set)
    cvs.pack(side="left", fill="both", expand=True)
    scl.pack(side="right", fill="y")
    def _bw(e): cvs.bind_all("<MouseWheel>",
        lambda ev: cvs.yview_scroll(int(-1*(ev.delta/120)), "units"))
    def _uw(e): cvs.unbind_all("<MouseWheel>")
    cvs.bind("<Enter>", _bw); cvs.bind("<Leave>", _uw)
    win = cvs.create_window((0, 0), window=inr, anchor="nw")
    return cvs, scl, inr, win


# ---- 表格常量 ----
COL_ALGO = 230   # 算法列
COL_COST = 130   # 路径代价
COL_NODE = 140   # 扩展节点
COL_TIME = 130   # 运行时间
COL_TOTAL = COL_ALGO + COL_COST + COL_NODE + COL_TIME
TB_HEAD_H = 34   # 表头高
TB_ROW_H  = 36   # 数据行高
TB_SEP_H  = 30   # 分组标题高

# ============================================================
class PacmanLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("吃豆人 AI 搜索实验")
        self.root.configure(bg=BG_ROOT)
        self.root.resizable(False, False)
        self.root.geometry("780x640")
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"780x640+{(sw-780)//2}+{(sh-640)//2}")

        self.font_title   = tkfont.Font(family="Microsoft YaHei", size=30, weight="bold")
        self.font_heading = tkfont.Font(family="Microsoft YaHei", size=15, weight="bold")
        self.font_body    = tkfont.Font(family="Microsoft YaHei", size=11)
        self.font_small   = tkfont.Font(family="Microsoft YaHei", size=9)
        self.font_btn     = tkfont.Font(family="Microsoft YaHei", size=12, weight="bold")
        self.font_launch  = tkfont.Font(family="Microsoft YaHei", size=10, weight="bold")
        self.font_section = tkfont.Font(family="Microsoft YaHei", size=12, weight="bold")
        self.font_thead   = tkfont.Font(family="Microsoft YaHei", size=11, weight="bold")
        self.font_trow    = tkfont.Font(family="Microsoft YaHei", size=10)
        self.font_tnum    = tkfont.Font(family="Consolas", size=10)

        self.container = tk.Frame(root, bg=BG_ROOT)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomePage, ModePage, DataPage, HelpPage):
            f = F(self.container, self)
            self.frames[F.__name__] = f
            f.place(x=0, y=0, relwidth=1, relheight=1)
        self.show_frame("HomePage")

    def show_frame(self, name):
        self.frames[name].tkraise()
        if name == "ModePage":
            self.frames[name].refresh()
        if name == "DataPage":
            self.frames[name].refresh()

    def launch_game(self, args, mode_name):
        cmd = [PYTHON, PACMAN_SCRIPT] + args
        try:
            subprocess.Popen(cmd, cwd=os.path.dirname(PACMAN_SCRIPT))
        except Exception as e:
            print(f"启动失败: {e}")


# ============================================================
class HomePage(tk.Frame):
    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_PAGE)

        body = tk.Frame(self, bg=BG_PAGE)
        body.pack(expand=True)

        tk.Frame(body, bg=BG_PAGE, height=40).pack()

        # 街机风角色图标（幽灵 · 吃豆人 · 小豆）— 带发光圆环背景
        icons = tk.Frame(body, bg=BG_PAGE); icons.pack()
        glow_cvs = tk.Canvas(icons, width=240, height=56, bg=BG_PAGE, highlightthickness=0)
        glow_cvs.pack()
        # 发光圆环
        glow_cvs.create_oval(10, 4, 50, 44, outline="#1E293B", width=2, fill="#0F172A")
        glow_cvs.create_oval(55, 4, 95, 44, outline="#1E293B", width=2, fill="#0F172A")
        glow_cvs.create_oval(100, 4, 140, 44, outline="#1E293B", width=2, fill="#0F172A")
        glow_cvs.create_oval(145, 4, 185, 44, outline="#1E293B", width=2, fill="#0F172A")
        # 在圆环上绘制图标
        for gi in range(4):
            draw_game_ghost_icon(glow_cvs, 30 + gi*45, 24, ghost_index=gi, unit=10)
        # Pacman & pellet
        draw_pacman_icon(glow_cvs, 192 + 14, 24, r=13, fill=FG_TITLE, bg="#0F172A")
        draw_pellet_icon(glow_cvs, 192 + 38, 24)

        tk.Frame(body, bg=BG_PAGE, height=20).pack()

        # 标题 — 霓虹街机风格
        tk.Label(body, text="吃豆人", font=("Microsoft YaHei", 48, "bold"),
                 fg=FG_TITLE, bg=BG_PAGE).pack()
        tk.Label(body, text="AI 搜索算法实验平台",
                 font=("Microsoft YaHei", 14, "bold"), fg=FG_HEADING, bg=BG_PAGE).pack(pady=(0,8))
        tk.Label(body, text="BFS  ·  DFS  ·  UCS  ·  A*  ·  MINIMAX",
                 font=("Consolas", 10), fg=ACCENT_BLUE, bg=BG_PAGE).pack()

        tk.Frame(body, bg=BG_PAGE, height=32).pack()

        # 按钮区 — 三级视觉层级
        btns = tk.Frame(body, bg=BG_PAGE)
        btns.pack()

        # [1] 主 CTA — 霓虹红实心按钮（单层圆角，避免双层描边导致角落露黑）
        self.btn_play = tk.Canvas(btns, width=260, height=64, bg=BG_PAGE, highlightthickness=0)
        self.btn_play.pack(pady=8)
        self.btn_play_rect = create_rounded_rect(
            self.btn_play, 4, 4, 256, 60, radius=28, fill=ACCENT, outline="",
        )
        self.btn_play_text = self.btn_play.create_text(130, 32, text="▶  开始游戏", font=("Microsoft YaHei", 16, "bold"), fill=BTN_TEXT)

        def on_play_enter(e):
            configure_rounded_rect(self.btn_play, self.btn_play_rect, fill=ACCENT_HOVER)
        def on_play_leave(e):
            configure_rounded_rect(self.btn_play, self.btn_play_rect, fill=ACCENT)
        def on_play_press(e):
            configure_rounded_rect(self.btn_play, self.btn_play_rect, fill="#B91C1C")
        def on_play_release(e):
            configure_rounded_rect(self.btn_play, self.btn_play_rect, fill=ACCENT_HOVER)
            ctrl.show_frame("ModePage")

        self.btn_play.bind("<Enter>", on_play_enter)
        self.btn_play.bind("<Leave>", on_play_leave)
        self.btn_play.bind("<Button-1>", on_play_press)
        self.btn_play.bind("<ButtonRelease-1>", on_play_release)
        self.btn_play.configure(cursor="hand2")

        # [2] 次级按钮 — 蓝色边框风格
        self.btn_data = tk.Canvas(btns, width=260, height=50, bg=BG_PAGE, highlightthickness=0)
        self.btn_data.pack(pady=5)
        self.btn_data_rect = create_rounded_rect(self.btn_data, 2, 2, 258, 48, radius=23, fill=BG_CARD, outline=ACCENT_BLUE, width=1)
        self.btn_data_text = self.btn_data.create_text(130, 25, text="实验数据对比", font=("Microsoft YaHei", 12, "bold"), fill=FG_HEADING)

        def on_data_enter(e):
            configure_rounded_rect(self.btn_data, self.btn_data_rect, fill=BG_CARD_HOVER, outline=BLUE_HOVER)
            self.btn_data.itemconfig(self.btn_data_text, fill="#FFFFFF")
        def on_data_leave(e):
            configure_rounded_rect(self.btn_data, self.btn_data_rect, fill=BG_CARD, outline=ACCENT_BLUE)
            self.btn_data.itemconfig(self.btn_data_text, fill=FG_HEADING)

        self.btn_data.bind("<Enter>", on_data_enter)
        self.btn_data.bind("<Leave>", on_data_leave)
        self.btn_data.bind("<Button-1>", lambda e: ctrl.show_frame("DataPage"))
        self.btn_data.bind("<ButtonRelease-1>", lambda e: ctrl.show_frame("DataPage"))
        self.btn_data.configure(cursor="hand2")

        # [3] 三级 — 纯文字按钮
        self.btn_help = tk.Canvas(btns, width=260, height=44, bg=BG_PAGE, highlightthickness=0)
        self.btn_help.pack(pady=4)
        self.btn_help_text = self.btn_help.create_text(130, 22, text="游戏说明", font=("Microsoft YaHei", 11, "bold"), fill=FG_SUB)
        self.btn_help_underline = self.btn_help.create_line(90, 34, 170, 34, fill=BG_PAGE, width=1)

        def on_help_enter(e):
            self.btn_help.itemconfig(self.btn_help_text, fill="#FFFFFF")
            self.btn_help.itemconfig(self.btn_help_underline, fill=ACCENT_BLUE)
        def on_help_leave(e):
            self.btn_help.itemconfig(self.btn_help_text, fill=FG_SUB)
            self.btn_help.itemconfig(self.btn_help_underline, fill=BG_PAGE)

        self.btn_help.bind("<Enter>", on_help_enter)
        self.btn_help.bind("<Leave>", on_help_leave)
        self.btn_help.bind("<Button-1>", lambda e: ctrl.show_frame("HelpPage"))
        self.btn_help.bind("<ButtonRelease-1>", lambda e: ctrl.show_frame("HelpPage"))
        self.btn_help.configure(cursor="hand2")

        tk.Frame(body, bg=BG_PAGE, height=20).pack()
        tk.Label(body, text="INSERT COIN TO START",
                 font=("Consolas", 10, "bold"), fg=SCORE_GREEN, bg=BG_PAGE).pack()
        tk.Frame(body, bg=BG_PAGE, height=40).pack()


# ============================================================
class DataPage(tk.Frame):
    """实验数据对比页 — 统一表格（静态构建，避免每访重建）。"""

    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_PAGE)
        self._c = ctrl
        _build_topbar(self, "实验数据对比", ctrl)
        self._cvs, self._scl, self._inr, _ = _build_scroll_area(self)
        self._build()

    def refresh(self):
        self._cvs.yview_moveto(0)

    # ============ build ============
    def _build(self):
        # -- 说明 --
        top = tk.Frame(self._inr, bg=BG_PAGE); top.pack(fill="x", padx=40, pady=(14,8))
        tk.Label(top, text="各算法性能实测数据",
                 font=("Microsoft YaHei", 12, "bold"), fg=FG_SUB, bg=BG_PAGE).pack(anchor="w")
        leg = tk.Frame(top, bg=BG_PAGE); leg.pack(fill="x", pady=(4,0))
        for t,c in [("● A* 启发式搜索",  ACCENT),
                    ("○ 盲目搜索 (BFS/DFS/UCS)", FG_SUB),
                    ("绿色 = 组内最优", SCORE_GREEN)]:
            tk.Label(leg, text=t, font=("Microsoft YaHei", 9), fg=c, bg=BG_PAGE).pack(side="left", padx=(0,16))

        # -- 表格卡片 --
        card = tk.Frame(self._inr, bg=BG_CARD, padx=0, pady=0)
        card.pack(fill="x", padx=40)

        self._tbl_header(card)

        first = True
        for mk in ["tinyMaze","mediumMaze","bigMaze","mediumCorners","trickySearch"]:
            rows = _BENCHMARK_GROUPS.get(mk)
            if not rows: continue
            if not first:
                self._tbl_sep(card, mk, rows)
            first = False
            self._tbl_rows(card, rows)

        # 表格底线
        tk.Frame(card, bg="#334155", height=1).pack(fill="x")

        # -- 结论 --
        tk.Frame(self._inr, bg=BG_PAGE, height=16).pack()
        s = tk.Frame(self._inr, bg=BG_CARD); s.pack(fill="x", padx=40, pady=(6,24))
        tk.Frame(s, bg=SCORE_GREEN, width=6).pack(side="left", fill="y")
        b = tk.Frame(s, bg=BG_CARD); b.pack(side="left", fill="x", expand=True, padx=16, pady=14)
        tk.Label(b, text="结论速览", font=("Microsoft YaHei", 12, "bold"),
                 fg=SCORE_GREEN, bg=BG_CARD).pack(anchor="w")
        for ln in [
            "DFS 路径最长且非最优，但扩展节点较少",
            "BFS / UCS 在单位代价下等价，均保证最优路径，扩展规模随地图增大激增",
            "A* 借助可采纳启发式，保持最优性的同时有效降低扩展节点数（mediumMaze: 269→221）",
            "多点任务状态空间指数增长，启发式质量决定求解效率（foodHeuristic: 4137 节点）",
        ]:
            tk.Label(b, text=f"• {ln}", font=self._c.font_small, fg=FG_SUB,
                     bg=BG_CARD, anchor="w", wraplength=630, justify="left").pack(anchor="w", pady=(3,0))

    # ============ 表头 ============
    def _tbl_header(self, card):
        th_bg = "#1E293B"
        th = tk.Frame(card, bg=th_bg, height=TB_HEAD_H)
        th.pack(fill="x"); th.pack_propagate(False)
        cols = [("算法", COL_ALGO, "w"), ("路径代价", COL_COST, "center"),
                ("扩展节点", COL_NODE, "center"), ("时间", COL_TIME, "center")]
        for txt, w, a in cols:
            c = tk.Frame(th, bg=th_bg, width=w, height=TB_HEAD_H)
            c.pack(side="left"); c.pack_propagate(False)
            l = tk.Label(c, text=txt, font=("Microsoft YaHei", 10, "bold"), fg=SCORE_GREEN, bg=th_bg)
            l.place(relx=0.5, rely=0.5, anchor="center") if a == "center" else l.place(x=14, rely=0.5, anchor="w")
        tk.Frame(card, bg="#334155", height=1).pack(fill="x")

    # ============ 分组标题 ============
    def _tbl_sep(self, card, mk, rows):
        clr = SEC_COLORS.get(rows[0][5], ACCENT)
        sep_bg = "#151A2E"
        fr = tk.Frame(card, bg=sep_bg, height=TB_SEP_H)
        fr.pack(fill="x"); fr.pack_propagate(False)
        tk.Frame(fr, bg=clr, width=10, height=2).place(x=12, rely=0.5, anchor="w")
        tk.Label(fr, text=MAP_NAMES.get(mk, mk),
                 font=("Microsoft YaHei", 9, "bold"), fg=clr, bg=sep_bg).place(x=28, rely=0.5, anchor="w")
        tk.Frame(card, bg="#334155", height=1).pack(fill="x")

    # ============ 数据行 ============
    def _tbl_rows(self, card, rows):
        # 单次遍历计算所有最优值
        bc = float('inf'); bn = float('inf'); bt = float('inf')
        for r in rows:
            if r[2] < bc: bc = r[2]
            if r[3] < bn: bn = r[3]
            if r[4] < bt: bt = r[4]

        for i, (_, algo, cost, nodes, ms, cat) in enumerate(rows):
            bg = "#161A2E" if i % 2 == 0 else "#1C213A"
            rf = tk.Frame(card, bg=bg, height=TB_ROW_H)
            rf.pack(fill="x"); rf.pack_propagate(False)
            clr = SEC_COLORS.get(cat, FG_TEXT)

            # -- 算法 --
            c0 = tk.Frame(rf, bg=bg, width=COL_ALGO, height=TB_ROW_H)
            c0.pack(side="left"); c0.pack_propagate(False)
            prefix = "●" if "A*" in algo else "○"
            tk.Label(c0, text=f"  {prefix}  {algo}", font=self._c.font_trow,
                     fg=clr, bg=bg, anchor="w").place(x=10, rely=0.5, anchor="w")

            # -- 路径代价 --
            c1 = tk.Frame(rf, bg=bg, width=COL_COST, height=TB_ROW_H)
            c1.pack(side="left"); c1.pack_propagate(False)
            tk.Label(c1, text=str(cost), font=("Consolas", 11, "bold"),
                     fg=SCORE_GREEN if cost==bc else FG_TEXT, bg=bg).place(relx=0.5, rely=0.5, anchor="center")

            # -- 扩展节点 --
            c2 = tk.Frame(rf, bg=bg, width=COL_NODE, height=TB_ROW_H)
            c2.pack(side="left"); c2.pack_propagate(False)
            tk.Label(c2, text=str(nodes), font=("Consolas", 11, "bold"),
                     fg=SCORE_GREEN if nodes==bn else FG_TEXT, bg=bg).place(relx=0.5, rely=0.5, anchor="center")

            # -- 运行时间 --
            c3 = tk.Frame(rf, bg=bg, width=COL_TIME, height=TB_ROW_H)
            c3.pack(side="left"); c3.pack_propagate(False)
            tk.Label(c3, text=f"{ms} ms", font=("Consolas", 11, "bold"),
                     fg=SCORE_GREEN if ms==bt else FG_TEXT, bg=bg).place(relx=0.5, rely=0.5, anchor="center")


# ============================================================
class ModePage(tk.Frame):
    """模式选择页（静态构建，避免每访重建）。"""

    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_PAGE)
        self._c = ctrl
        _build_topbar(self, "选择游戏模式", ctrl)
        self._cvs, self._scl, self._inr, self._win = _build_scroll_area(self)
        self._build_content()

    def refresh(self):
        self._cvs.yview_moveto(0)
        self._inr.update_idletasks()
        cw = self._cvs.winfo_width()
        if cw > 100: self._cvs.itemconfig(self._win, width=cw)

    def _build_content(self):
        tk.Frame(self._inr, bg=BG_PAGE, height=14).pack()
        groups = {}
        for m in MODES: groups.setdefault(m[4], []).append(m)
        for sk in ["keyboard","blind","astar","multidot","bonus"]:
            if sk not in groups: continue
            clr = SEC_COLORS.get(sk, ACCENT)
            title, sub, icon = SECTIONS[sk]
            tk.Frame(self._inr, bg=BG_PAGE, height=10).pack()
            row = tk.Frame(self._inr, bg=BG_PAGE); row.pack(fill="x", padx=28, pady=(6,2))
            tk.Label(row, text=icon, font=("Segoe UI Symbol", 14), fg=clr, bg=BG_PAGE).pack(side="left")
            tk.Label(row, text=f"  {title}", font=self._c.font_section, fg=clr, bg=BG_PAGE).pack(side="left")
            tk.Label(row, text=f"  —  {sub}", font=self._c.font_small, fg=FG_SUB, bg=BG_PAGE).pack(side="left")
            for m in groups[sk]:
                self._card(m, clr)
        tk.Frame(self._inr, bg=BG_PAGE, height=24).pack()

    def _card(self, m, accent):
        name, args, desc, mp, _ = m
        
        wrap = tk.Frame(self._inr, bg=BG_PAGE)
        wrap.pack(fill="x", padx=28, pady=6)
        
        cvs = tk.Canvas(wrap, width=700, height=78, bg=BG_PAGE, highlightthickness=0)
        cvs.pack()

        rect_id = create_rounded_rect(cvs, 2, 2, 698, 76, radius=12, fill=BG_CARD, outline="#1E293B", width=1)

        # 左侧强调色条 — 加粗到 8px
        create_rounded_rect(cvs, 2, 18, 10, 60, radius=4, fill=accent, outline="")
        
        title_id = cvs.create_text(26, 27, text=name, font=("Microsoft YaHei", 12, "bold"), fill=FG_HEADING, anchor="w")
        bbox = cvs.bbox(title_id)
        tag_x = bbox[2] + 12 if bbox else 200

        tag_rect = create_rounded_rect(cvs, tag_x, 17, tag_x + len(mp)*8 + 16, 37, radius=6, fill="#1E293B", outline="")
        cvs.create_text(tag_x + 8, 27, text=mp, font=("Consolas", 9), fill=ACCENT_BLUE, anchor="w")

        cvs.create_text(26, 54, text=desc, font=self._c.font_small, fill=FG_SUB, anchor="w")

        btn_rect = create_rounded_rect(cvs, 580, 20, 680, 58, radius=15, fill=accent, outline="")
        btn_text = cvs.create_text(630, 39, text="▶ 启动", font=("Microsoft YaHei", 10, "bold"), fill=BTN_TEXT)
        
        def on_enter(e):
            configure_rounded_rect(cvs, rect_id, fill=BG_CARD_HOVER)
            configure_rounded_rect(cvs, btn_rect, fill="#F87171" if accent == ACCENT else accent)
            cvs.itemconfig(btn_text, fill=BTN_TEXT)

        def on_leave(e):
            configure_rounded_rect(cvs, rect_id, fill=BG_CARD)
            configure_rounded_rect(cvs, btn_rect, fill=accent)
            cvs.itemconfig(btn_text, fill=BTN_TEXT)
            
        def on_click(e):
            if 580 <= e.x <= 680 and 18 <= e.y <= 58:
                self._c.launch_game(args, name)
                
        cvs.bind("<Enter>", on_enter)
        cvs.bind("<Leave>", on_leave)
        cvs.bind("<Button-1>", on_click)
        cvs.configure(cursor="hand2")


# ============================================================
HELP_SECTIONS = [
    ("操作方式", [
        "键盘模式：方向键，或 W/A/S/D 移动，Q 停止。",
        "需使用图形界面启动（勿加 --textGraphics）。",
        "AI 演示模式：选择对应算法后点击「启动」，Pacman 将自动执行规划路径。",
    ]),
    ("AI 搜索可视化（红色方格）", [
        "适用于 BFS / DFS / UCS / A* 迷宫搜索（SearchAgent）。",
        "找到路径后，棋盘上会出现红色半透明方格，表示搜索过程中扩展过的格子。",
        "颜色越深：越早被扩展的格子；颜色越浅：越晚被扩展的格子。",
        "多豆 Food 搜索默认不显示该 overlay。",
    ]),
    ("得分与扣分", [
        "吃小豆：+10 分",
        "吃完所有小豆：+500 分（胜利）",
        "每步时间惩罚：-1 分",
        "吃能量豆（大豆）：无直接加分，幽灵进入惊吓 40 步",
        "惊吓态撞到幽灵：+200 分",
        "被正常幽灵撞到：-500 分（失败）",
    ]),
    ("能量豆与幽灵", [
        "地图上较大的白色圆点为能量豆（布局字符 o）。",
        "吃能量豆后幽灵变蓝变白并减速，此时可反吃幽灵得分。",
        "动态避障：幽灵较近时主动吃能量豆，吃到后追击变白幽灵（+200 分）。",
    ]),
]


class HelpPage(tk.Frame):
    """游戏说明页（静态构建，避免每访重建）。"""

    def __init__(self, parent, ctrl):
        super().__init__(parent, bg=BG_PAGE)
        _build_topbar(self, "游戏说明", ctrl)
        _, _, inr, _ = _build_scroll_area(self, width=700)

        tk.Frame(inr, bg=BG_PAGE, height=14).pack()
        for title, lines in HELP_SECTIONS:
            card = tk.Frame(inr, bg=BG_CARD)
            card.pack(fill="x", padx=40, pady=6)
            tk.Frame(card, bg=ACCENT_BLUE, width=3).pack(side="left", fill="y")
            body = tk.Frame(card, bg=BG_CARD)
            body.pack(side="left", fill="x", expand=True, padx=16, pady=12)
            tk.Label(body, text=title, font=("Microsoft YaHei", 12, "bold"),
                     fg=FG_TITLE, bg=BG_CARD, anchor="w").pack(anchor="w")
            for ln in lines:
                tk.Label(body, text=f"• {ln}", font=ctrl.font_small, fg=FG_SUB,
                         bg=BG_CARD, anchor="w", wraplength=620, justify="left").pack(anchor="w", pady=(4, 0))
        tk.Frame(inr, bg=BG_PAGE, height=24).pack()


# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PacmanLauncher(root)
    root.mainloop()
