# graphicsDisplay.py
# ------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from graphicsUtils import *
import math, time
import tkinter as tk
from game import Directions

# 与启动器 / 游戏窗口一致的街机配色
_UI_BG         = "#000000"
_UI_CARD       = "#18181B"
_UI_CARD_INNER = "#222226"
_UI_BORDER     = "#2e2e38"
_UI_ACCENT     = "#FFFF3D"
_UI_ACCENT_HOV = "#FFFF80"
_UI_CYAN       = "#00FFFF"
_UI_BLUE       = "#0033FF"
_UI_HEADING    = "#e8e8f0"
_UI_SUB        = "#9090b0"
_UI_LOSE       = "#FF3333"
_UI_LOSE_HOV   = "#FF6666"
_UI_LOSE_DIM   = "#4a1515"


def _ui_rounded_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    points = [
        x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
        x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def _ui_draw_decor_dots(canvas, accent, w, h, margin=14):
    """首页风格彩色装饰点。"""
    dots = [
        (margin + 18, margin + 22, _UI_CYAN, 5),
        (w - margin - 18, margin + 22, _UI_BLUE, 5),
        (margin + 12, h - margin - 18, accent, 4),
        (w - margin - 12, h - margin - 18, _UI_CYAN, 4),
    ]
    ids = []
    for x, y, color, r in dots:
        ids.append(canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=''))
    return ids


def _ui_draw_pacman_icon(canvas, cx, cy, r=30):
    """吃豆人朝右，嘴朝东（与游戏中 East 朝向一致）。"""
    x0, y0, x1, y1 = cx - r - 1, cy - r - 1, cx + r, cy + r
    mouth_span = 70
    canvas.create_arc(
        x0, y0, x1, y1, start=mouth_span / 2, extent=360 - mouth_span,
        fill=_UI_ACCENT, outline='', style='pieslice',
    )
    canvas.create_arc(
        x0, y0, x1, y1, start=360 - mouth_span / 2, extent=mouth_span,
        fill=_UI_BG, outline='', style='pieslice',
    )
    eye_x, eye_y = cx - r * 0.22, cy - r * 0.42
    canvas.create_oval(eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4, fill=_UI_BG, outline='')


def _ui_draw_ghost_icon(canvas, cx, cy, scale=28):
    """失败弹窗幽灵：与对局中红色幽灵同款造型。"""
    draw_game_ghost_icon(canvas, cx, cy, ghost_index=0, unit=scale * 0.4)


def show_arcade_outcome_dialog(parent, outcome, score):
    """街机风结果弹窗：圆角卡片、图标、得分区与圆角按钮。"""
    is_win = outcome == 'win'
    accent = _UI_ACCENT if is_win else _UI_LOSE
    accent_hov = _UI_ACCENT_HOV if is_win else _UI_LOSE_HOV
    title_text = '游戏通关' if is_win else '游戏失败'
    msg_text = '恭喜清空迷宫！' if is_win else '被幽灵抓住了…'
    badge = 'VICTORY' if is_win else 'GAME OVER'

    dlg_w, dlg_h = 420, 380
    dlg = tk.Toplevel(parent)
    dlg.title(title_text)
    dlg.configure(bg=_UI_BG)
    dlg.resizable(False, False)
    dlg.transient(parent)
    dlg.grab_set()

    cvs = tk.Canvas(dlg, width=dlg_w, height=dlg_h, bg=_UI_BG, highlightthickness=0)
    cvs.pack()

    m = 12
    _ui_rounded_rect(cvs, m - 2, m - 2, dlg_w - m + 2, dlg_h - m + 2, radius=20,
                     fill='#0d0d10', outline='')
    _ui_rounded_rect(cvs, m, m, dlg_w - m, dlg_h - m, radius=18,
                     fill=_UI_CARD, outline=_UI_BORDER)
    _ui_rounded_rect(cvs, m, m, dlg_w - m, m + 6, radius=18, fill=accent, outline='')
    cvs.create_rectangle(m, m + 4, dlg_w - m, m + 8, fill=accent, outline='')

    cx = dlg_w // 2
    _ui_draw_decor_dots(cvs, accent, dlg_w, dlg_h, m)

    icon_y = 78
    _ui_rounded_rect(cvs, cx - 44, icon_y - 44, cx + 44, icon_y + 44, radius=44,
                     fill=_UI_CARD_INNER, outline=_UI_BORDER)
    if is_win:
        _ui_draw_pacman_icon(cvs, cx, icon_y, 26)
    else:
        _ui_draw_ghost_icon(cvs, cx, icon_y, 24)

    cvs.create_text(cx, 138, text=badge, font=('Consolas', 10, 'bold'), fill=accent)
    cvs.create_text(cx, 168, text=title_text, font=('Microsoft YaHei', 24, 'bold'), fill=accent)
    cvs.create_text(cx, 198, text=msg_text, font=('Microsoft YaHei', 11), fill=_UI_SUB)

    pill_y1, pill_y2 = 218, 278
    pill_x1, pill_x2 = cx - 118, cx + 118
    _ui_rounded_rect(cvs, pill_x1, pill_y1, pill_x2, pill_y2, radius=14,
                     fill=_UI_CARD_INNER, outline='#3a3a48')
    cvs.create_text(cx, pill_y1 + 22, text='最终得分', font=('Microsoft YaHei', 9), fill=_UI_SUB)
    cvs.create_text(cx, pill_y1 + 48, text=str(score), font=('Consolas', 28, 'bold'),
                    fill=accent if is_win else _UI_HEADING)

    btn_y1, btn_y2 = dlg_h - m - 58, dlg_h - m - 14
    btn_x1, btn_x2 = cx - 92, cx + 92
    btn_rect = _ui_rounded_rect(cvs, btn_x1, btn_y1, btn_x2, btn_y2, radius=22,
                                fill=accent, outline='')
    btn_text = cvs.create_text(cx, (btn_y1 + btn_y2) // 2, text='确  定',
                               font=('Microsoft YaHei', 12, 'bold'), fill='#000000')
    def on_enter(_):
        cvs.itemconfig(btn_rect, fill=accent_hov)
        cvs.configure(cursor='hand2')

    def on_leave(_):
        cvs.itemconfig(btn_rect, fill=accent)
        cvs.configure(cursor='')

    def on_ok(_=None):
        dlg.destroy()

    for item in (btn_rect, btn_text):
        cvs.tag_bind(item, '<Enter>', on_enter)
        cvs.tag_bind(item, '<Leave>', on_leave)
        cvs.tag_bind(item, '<Button-1>', on_ok)

    dlg.bind('<Return>', on_ok)
    dlg.bind('<Escape>', on_ok)

    dlg.update_idletasks()
    px = parent.winfo_rootx() + max(0, (parent.winfo_width() - dlg_w) // 2)
    py = parent.winfo_rooty() + max(0, (parent.winfo_height() - dlg_h) // 2)
    dlg.geometry(f'{dlg_w}x{dlg_h}+{px}+{py}')
    dlg.focus_set()
    dlg.wait_window()

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero written or rewritten for cs188, UC Berkeley.
# Some code from a Pacman implementation by LiveWires, and used / modified with permission.

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = formatColor(0,0,0)
WALL_COLOR = formatColor(0.0/255.0, 51.0/255.0, 255.0/255.0)
INFO_PANE_COLOR = formatColor(.4,.4,0)
SCORE_COLOR = formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 2
PACMAN_CAPTURE_OUTLINE_WIDTH = 4

GHOST_COLORS = []
GHOST_COLORS.append(formatColor(.9,0,0)) # Red
GHOST_COLORS.append(formatColor(0,.3,.9)) # Blue
GHOST_COLORS.append(formatColor(.98,.41,.07)) # Orange
GHOST_COLORS.append(formatColor(.1,.75,.7)) # Green
GHOST_COLORS.append(formatColor(1.0,0.6,0.0)) # Yellow
GHOST_COLORS.append(formatColor(.4,0.13,0.91)) # Purple

TEAM_COLORS = GHOST_COLORS[:2]

GHOST_SHAPE = [
    ( 0,    0.3 ),
    ( 0.25, 0.75 ),
    ( 0.5,  0.3 ),
    ( 0.75, 0.75 ),
    ( 0.75, -0.5 ),
    ( 0.5,  -0.75 ),
    (-0.5,  -0.75 ),
    (-0.75, -0.5 ),
    (-0.75, 0.75 ),
    (-0.5,  0.3 ),
    (-0.25, 0.75 )
  ]
GHOST_SIZE = 0.65
SCARED_COLOR = formatColor(1,1,1)

GHOST_VEC_COLORS = [colorToVector(c) for c in GHOST_COLORS]


def draw_game_ghost_icon(canvas, cx, cy, ghost_index=0, unit=11, direction=Directions.EAST):
    """
    与 PacmanGraphics.drawGhost 相同的轮廓、配色与眼睛偏移。
    unit 对应游戏中的 gridSize * GHOST_SIZE，供启动器等 Tk Canvas 复用。
    """
    colour = GHOST_COLORS[ghost_index] if ghost_index < len(GHOST_COLORS) else GHOST_COLORS[0]
    coords = [(cx + x * unit, cy + y * unit) for x, y in GHOST_SHAPE]
    canvas.create_polygon(coords, fill=colour, outline=colour)

    dx, dy = 0, 0
    if direction == Directions.NORTH:
        dy = -0.2
    elif direction == Directions.SOUTH:
        dy = 0.2
    elif direction == Directions.EAST:
        dx = 0.2
    elif direction == Directions.WEST:
        dx = -0.2

    white = formatColor(1.0, 1.0, 1.0)
    black = formatColor(0.0, 0.0, 0.0)
    eye_r = unit * 0.2
    pupil_r = unit * 0.08
    for ex_mult in (-0.3, 0.3):
        ex = cx + unit * (ex_mult + dx / 1.5)
        ey = cy - unit * (0.3 - dy / 1.5)
        canvas.create_oval(ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r, fill=white, outline=white)
    for ex_mult in (-0.3, 0.3):
        ex = cx + unit * (ex_mult + dx)
        ey = cy - unit * (0.3 - dy)
        canvas.create_oval(ex - pupil_r, ey - pupil_r, ex + pupil_r, ey + pupil_r, fill=black, outline=black)


PACMAN_COLOR = formatColor(255.0/255.0,255.0/255.0,61.0/255)
PACMAN_SCALE = 0.5
#pacman_speed = 0.25

# Food
FOOD_COLOR = formatColor(1,1,1)
FOOD_SIZE = 0.1

# Laser
LASER_COLOR = formatColor(1,0,0)
LASER_SIZE = 0.02

# Capsule graphics
CAPSULE_COLOR = formatColor(1,1,1)
CAPSULE_SIZE = 0.25

# Drawing walls
WALL_RADIUS = 0.15

class InfoPane:
    def __init__(self, layout, gridSize):
        self.gridSize = gridSize
        self.width = (layout.width) * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT

        # 根据窗口宽度自适应字体大小
        if self.width < 200:
            self.fontSize = 10
        elif self.width < 300:
            self.fontSize = 14
        elif self.width < 450:
            self.fontSize = 18
        else:
            self.fontSize = 24

        self.scoreColor = SCORE_COLOR          # 浅灰色分数
        self.timerColor = formatColor(.4, 1.0, .4)  # 亮绿色计时器
        self.drawPane()

    def toScreen(self, pos, y=None):
        if y is None:
            x, y = pos
        else:
            x = pos
        x = self.gridSize + x  # 左边距
        y = self.base + y
        return x, y

    def drawPane(self):
        # 分数 —— 左侧
        self.scoreText = text(
            self.toScreen(0, 0), self.scoreColor,
            "Score: 0", "Times", self.fontSize, "bold"
        )
        # 计时器 —— 右侧
        timerWidth = 8.5 * self.gridSize
        timerX = self.width - timerWidth
        if timerX < self.gridSize * 5:
            timerX = self.gridSize * 5
        self.timerText = text(
            self.toScreen(timerX, 0), self.timerColor,
            "Time: 00:00", "Times", self.fontSize, "bold"
        )

    def updateScore(self, score):
        changeText(self.scoreText, "Score: %d" % score)

    def updateTimer(self, elapsed):
        """更新计时器，elapsed 单位为秒。"""
        m = int(elapsed) // 60
        s = int(elapsed) % 60
        changeText(self.timerText, "Time: %02d:%02d" % (m, s))

    def initializeGhostDistances(self, distances):
        self.ghostDistanceText = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = text( self.toScreen(self.width//2 + self.width//8 * i, 0), GHOST_COLORS[i+1], d, "Times", size, "bold")
            self.ghostDistanceText.append(t)

    def setTeam(self, isBlue):
        text = "RED TEAM"
        if isBlue: text = "BLUE TEAM"
        self.teamText = text( self.toScreen(300, 0  ), PACMAN_COLOR, text, "Times", self.fontSize, "bold")

    def updateGhostDistances(self, distances):
        if len(distances) == 0: return
        if 'ghostDistanceText' not in dir(self): self.initializeGhostDistances(distances)
        else:
            for i, d in enumerate(distances):
                changeText(self.ghostDistanceText[i], d)

    def drawGhost(self):
        pass

    def drawPacman(self):
        pass

    def drawWarning(self):
        pass

    def clearIcon(self):
        pass

    def updateMessage(self, message):
        pass

    def clearMessage(self):
        pass


class PacmanGraphics:
    def __init__(self, zoom=1.0, frameTime=0.0, capture=False):
        self.have_window = 0
        self.currentGhostImages = {}
        self.pacmanImage = None
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.capture = capture
        self.frameTime = frameTime
        self.startTime = None
        self._gameOutcome = None  # ('win'|'lose', score) 游戏结束时用于弹窗
        self._defer_refresh = True  # 每回合合并为一次画布刷新，不改变画面样式
        self._last_timer_sec = -1

    def checkNullDisplay(self):
        return False

    def initialize(self, state, isBlue = False):
        self.isBlue = isBlue
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state
        self.startTime = time.time()  # 记录游戏开始时间

    def startGraphics(self, state):
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridSize)
        self.currentState = layout

    def drawDistributions(self, state):
        walls = state.layout.walls
        dist = []
        for x in range(walls.width):
            distx = []
            dist.append(distx)
            for y in range(walls.height):
                ( screen_x, screen_y ) = self.to_screen( (x, y) )
                block = square( (screen_x, screen_y),
                                0.5 * self.gridSize,
                                color = BACKGROUND_COLOR,
                                filled = 1, behind=2)
                distx.append(block)
        self.distributionImages = dist

    def drawStaticObjects(self, state):
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        refresh()

    def drawAgentObjects(self, state):
        self.agentImages = [] # (agentState, image)
        for index, agent in enumerate(state.agentStates):
            if agent.isPacman:
                image = self.drawPacman(agent, index)
                self.agentImages.append( (agent, image) )
            else:
                image = self.drawGhost(agent, index)
                self.agentImages.append( (agent, image) )
        refresh()

    def swapImages(self, agentIndex, newState):
        """
          Changes an image from a ghost to a pacman or vis versa (for capture)
        """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage: remove_from_screen(item)
        if newState.isPacman:
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image )
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image )
        refresh()

    def update(self, newState):
        agentIndex = newState._agentMoved
        agentState = newState.agentStates[agentIndex]

        if self.agentImages[agentIndex][0].isPacman != agentState.isPacman: self.swapImages(agentIndex, agentState)
        prevState, prevImage = self.agentImages[agentIndex]
        if agentState.isPacman:
            self.animatePacman(agentState, prevState, prevImage)
        else:
            self.moveGhost(agentState, agentIndex, prevState, prevImage)
        self.agentImages[agentIndex] = (agentState, prevImage)

        if newState._foodEaten != None:
            self.removeFood(newState._foodEaten, self.food)
        if newState._capsuleEaten != None:
            self.removeCapsule(newState._capsuleEaten, self.capsules)
        self.infoPane.updateScore(newState.score)
        if self.startTime is not None:
            elapsed = time.time() - self.startTime
            sec = int(elapsed)
            if sec != self._last_timer_sec:
                self.infoPane.updateTimer(elapsed)
                self._last_timer_sec = sec
        if self._defer_refresh:
            # 吃豆人开平滑动画时，每帧已在 animatePacman 内刷新
            pacman_animated = agentState.isPacman and (self.frameTime > 0.01 or self.frameTime < 0)
            if not pacman_animated:
                refresh()
        if 'ghostDistances' in dir(newState):
            self.infoPane.updateGhostDistances(newState.ghostDistances)
        if newState._win:
            self._gameOutcome = ('win', int(newState.score))
        elif newState._lose:
            self._gameOutcome = ('lose', int(newState.score))

    def make_window(self, width, height):
        grid_width = (width-1) * self.gridSize
        grid_height = (height-1) * self.gridSize
        screen_width = 2*self.gridSize + grid_width
        screen_height = 2*self.gridSize + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                       screen_height,
                       BACKGROUND_COLOR,
                       "CS188 Pacman")

    def drawPacman(self, pacman, index):
        position = self.getPosition(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(pacman))

        width = PACMAN_OUTLINE_WIDTH
        outlineColor = PACMAN_COLOR
        fillColor = PACMAN_COLOR

        if self.capture:
            outlineColor = TEAM_COLORS[index % 2]
            fillColor = GHOST_COLORS[index]
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        return [circle(screen_point, PACMAN_SCALE * self.gridSize,
                       fillColor = fillColor, outlineColor = outlineColor,
                       endpoints = endpoints,
                       width = width)]

    def getEndpoints(self, direction, position=(0,0)):
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi* pos)

        delta = width / 2
        if (direction == 'West'):
            endpoints = (180+delta, 180-delta)
        elif (direction == 'North'):
            endpoints = (90+delta, 90-delta)
        elif (direction == 'South'):
            endpoints = (270+delta, 270-delta)
        else:
            endpoints = (0+delta, 0-delta)
        return endpoints

    def movePacman(self, position, direction, image):
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints( direction, position )
        r = PACMAN_SCALE * self.gridSize
        moveCircle(image[0], screenPosition, r, endpoints)
        if not self._defer_refresh:
            refresh()

    def animatePacman(self, pacman, prevPacman, image):
        if self.frameTime < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1
        if self.frameTime > 0.01 or self.frameTime < 0:
            fx, fy = self.getPosition(prevPacman)
            px, py = self.getPosition(pacman)
            frames = 4.0
            for i in range(1, int(frames) + 1):
                pos = px * i / frames + fx * (frames - i) / frames, py * i / frames + fy * (frames - i) / frames
                self.movePacman(pos, self.getDirection(pacman), image)
                if self._defer_refresh:
                    refresh()
                sleep_light(abs(self.frameTime) / frames)
        else:
            self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)

    def getGhostColor(self, ghost, ghostIndex):
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghostIndex]

    def drawGhost(self, ghost, agentIndex):
        pos = self.getPosition(ghost)
        dir = self.getDirection(ghost)
        (screen_x, screen_y) = (self.to_screen(pos) )
        coords = []
        for (x, y) in GHOST_SHAPE:
            coords.append((x*self.gridSize*GHOST_SIZE + screen_x, y*self.gridSize*GHOST_SIZE + screen_y))

        colour = self.getGhostColor(ghost, agentIndex)
        body = polygon(coords, colour, filled = 1)
        WHITE = formatColor(1.0, 1.0, 1.0)
        BLACK = formatColor(0.0, 0.0, 0.0)

        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        leftEye = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        rightEye = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2, WHITE, WHITE)
        leftPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        rightPupil = circle((screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08, BLACK, BLACK)
        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        return ghostImageParts

    def moveEyes(self, pos, dir, eyes):
        (screen_x, screen_y) = (self.to_screen(pos) )
        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        moveCircle(eyes[0],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[1],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy/1.5)), self.gridSize*GHOST_SIZE*0.2)
        moveCircle(eyes[2],(screen_x+self.gridSize*GHOST_SIZE*(-0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)
        moveCircle(eyes[3],(screen_x+self.gridSize*GHOST_SIZE*(0.3+dx), screen_y-self.gridSize*GHOST_SIZE*(0.3-dy)), self.gridSize*GHOST_SIZE*0.08)

    def moveGhost(self, ghost, ghostIndex, prevGhost, ghostImageParts):
        old_x, old_y = self.to_screen(self.getPosition(prevGhost))
        new_x, new_y = self.to_screen(self.getPosition(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghostImagePart in ghostImageParts:
            move_by(ghostImagePart, delta)

        if ghost.scaredTimer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghostIndex]
        edit(ghostImageParts[0], ('fill', color), ('outline', color))
        self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[-4:])
        if not self._defer_refresh:
            refresh()

    def getPosition(self, agentState):
        if agentState.configuration == None: return (-1000, -1000)
        return agentState.getPosition()

    def getDirection(self, agentState):
        if agentState.configuration == None: return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self):
        import graphicsUtils
        if graphicsUtils.user_closed_graphics():
            graphicsUtils.end_graphics()
            return
        if self._gameOutcome:
            outcome, score = self._gameOutcome
            parent = graphicsUtils._root_window
            if parent is not None:
                show_arcade_outcome_dialog(parent, outcome, score)
        end_graphics()

    def to_screen(self, point):
        ( x, y ) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height  - y)*self.gridSize
        return ( x, y )

    # Fixes some TK issue with off-center circles
    def to_screen2(self, point):
        ( x, y ) = point
        #y = self.height - y
        x = (x + 1)*self.gridSize
        y = (self.height  - y)*self.gridSize
        return ( x, y )

    def drawWalls(self, wallMatrix):
        wallColor = WALL_COLOR
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.width: wallColor = TEAM_COLORS[0]
            if self.capture and (xNum * 2) >= wallMatrix.width: wallColor = TEAM_COLORS[1]

            for yNum, cell in enumerate(x):
                if cell: # There's a wall here
                    pos = (xNum, yNum)
                    screen = self.to_screen(pos)
                    screen2 = self.to_screen2(pos)

                    # draw each quadrant of the square based on adjacent walls
                    wIsWall = self.isWall(xNum-1, yNum, wallMatrix)
                    eIsWall = self.isWall(xNum+1, yNum, wallMatrix)
                    nIsWall = self.isWall(xNum, yNum+1, wallMatrix)
                    sIsWall = self.isWall(xNum, yNum-1, wallMatrix)
                    nwIsWall = self.isWall(xNum-1, yNum+1, wallMatrix)
                    swIsWall = self.isWall(xNum-1, yNum-1, wallMatrix)
                    neIsWall = self.isWall(xNum+1, yNum+1, wallMatrix)
                    seIsWall = self.isWall(xNum+1, yNum-1, wallMatrix)

                    # NE quadrant
                    if (not nIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (0,91), 'arc')
                    if (nIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (eIsWall) and (not neIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (180,271), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # NW quadrant
                    if (not nIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (90,181), 'arc')
                    if (nIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5)-1)), wallColor)
                    if (not nIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                    if (nIsWall) and (wIsWall) and (not nwIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (270,361), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(-1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(-1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-2)*WALL_RADIUS+1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(-0.5))), wallColor)

                    # SE quadrant
                    if (not sIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (270,361), 'arc')
                    if (sIsWall) and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*WALL_RADIUS, 0)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (eIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5+1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (eIsWall) and (not seIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*2*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (90,181), 'arc')
                        line(add(screen, (self.gridSize*2*WALL_RADIUS-1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*0.5, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

                    # SW quadrant
                    if (not sIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (180,271), 'arc')
                    if (sIsWall) and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, 0)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5)+1)), wallColor)
                    if (not sIsWall) and (wIsWall):
                        # horizontal line
                        line(add(screen, (0, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5)-1, self.gridSize*(1)*WALL_RADIUS)), wallColor)
                    if (sIsWall) and (wIsWall) and (not swIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize*(-2)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS)), WALL_RADIUS * self.gridSize-1, wallColor, wallColor, (0,91), 'arc')
                        line(add(screen, (self.gridSize*(-2)*WALL_RADIUS+1, self.gridSize*(1)*WALL_RADIUS)), add(screen, (self.gridSize*(-0.5), self.gridSize*(1)*WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(2)*WALL_RADIUS-1)), add(screen, (self.gridSize*(-1)*WALL_RADIUS, self.gridSize*(0.5))), wallColor)

    def isWall(self, x, y, walls):
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    def drawFood(self, foodMatrix ):
        foodImages = []
        color = FOOD_COLOR
        for xNum, x in enumerate(foodMatrix):
            if self.capture and (xNum * 2) <= foodMatrix.width: color = TEAM_COLORS[0]
            if self.capture and (xNum * 2) > foodMatrix.width: color = TEAM_COLORS[1]
            imageRow = []
            foodImages.append(imageRow)
            for yNum, cell in enumerate(x):
                if cell: # There's food here
                    screen = self.to_screen((xNum, yNum ))
                    dot = circle( screen,
                                  FOOD_SIZE * self.gridSize,
                                  outlineColor = color, fillColor = color,
                                  width = 1)
                    imageRow.append(dot)
                else:
                    imageRow.append(None)
        return foodImages

    def drawCapsules(self, capsules ):
        capsuleImages = {}
        for capsule in capsules:
            ( screen_x, screen_y ) = self.to_screen(capsule)
            dot = circle( (screen_x, screen_y),
                              CAPSULE_SIZE * self.gridSize,
                              outlineColor = CAPSULE_COLOR,
                              fillColor = CAPSULE_COLOR,
                              width = 1)
            capsuleImages[capsule] = dot
        return capsuleImages

    def removeFood(self, cell, foodImages ):
        x, y = cell
        remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell, capsuleImages ):
        x, y = cell
        remove_from_screen(capsuleImages[(x, y)])

    def drawExpandedCells(self, cells):
        """
        Draws an overlay of expanded grid positions for search agents
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen( cell)
            cellColor = formatColor(*[(n-k) * c * .5 / n + .25 for c in baseColor])
            block = square(screenPos,
                     0.5 * self.gridSize,
                     color = cellColor,
                     filled = 1, behind=2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                refresh()

    def clearExpandedCells(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                remove_from_screen(cell)


    def updateDistributions(self, distributions):
        "Draws an agent's belief distributions"
        # copy all distributions so we don't change their state
        distributions = map(lambda x: x.copy(), distributions)
        if self.distributionImages == None:
            self.drawDistributions(self.previousState)
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                weights = [dist[ (x,y) ] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0,0.0,0.0]
                colors = GHOST_VEC_COLORS[1:] # With Pacman
                if self.capture: colors = GHOST_VEC_COLORS
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3) for c,g in zip(color, gcolor)]
                changeColor(image, formatColor(*color))
        refresh()

class FirstPersonPacmanGraphics(PacmanGraphics):
    def __init__(self, zoom = 1.0, showGhosts = True, capture = False, frameTime=0):
        PacmanGraphics.__init__(self, zoom, frameTime=frameTime)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state, isBlue = False):

        self.isBlue = isBlue
        PacmanGraphics.startGraphics(self, state)
        # Initialize distribution images
        walls = state.layout.walls
        dist = []
        self.layout = state.layout

        # Draw the rest
        self.distributionImages = None  # initialize lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def lookAhead(self, config, state):
        if config.getDirection() == 'Stop':
            return
        else:
            pass
            # Draw relevant ghosts
            allGhosts = state.getGhostStates()
            visibleGhosts = state.getVisibleGhosts()
            for i, ghost in enumerate(allGhosts):
                if ghost in visibleGhosts:
                    self.drawGhost(ghost, i)
                else:
                    self.currentGhostImages[i] = None

    def getGhostColor(self, ghost, ghostIndex):
        return GHOST_COLORS[ghostIndex]

    def getPosition(self, ghostState):
        if not self.showGhosts and not ghostState.isPacman and ghostState.getPosition()[1] > 1:
            return (-1000, -1000)
        else:
            return PacmanGraphics.getPosition(self, ghostState)

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0
import os

def saveFrame():
    "Saves the current graphical output as a postscript file"
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT: return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR): os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name) # writes the current canvas
