# Pacman AI — 搜索算法实验

基于 UC Berkeley AI Pacman 框架，实现 BFS、DFS、UCS、A* 等搜索算法，并提供图形化启动器进行可视化对比。

## 快速开始

```bash
cd source
python pacman_launcher.py
```

### 环境要求

- Python 3.8 ~ 3.12
- 仅依赖 Python 标准库，无需额外安装

## 功能概览

| 模块 | 说明 |
|------|------|
| **GUI 启动器** | 图形界面，按分区浏览算法与地图，一键启动 |
| **实验数据对比** | 表格展示 BFS / DFS / UCS / A* 在不同地图下的路径代价、扩展节点、耗时 |
| **搜索可视化** | 红色半透明方格标记搜索扩展节点（颜色深浅 = 扩展先后） |
| **动态幽灵对抗** | 动态避障 + Alpha-Beta（吃能量豆后追击变白幽灵） |

## 命令行使用

```bash
# 键盘游玩
python pacman.py -l tinyMaze

# A* 搜索
python pacman.py -l mediumMaze -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic

# 四角问题
python pacman.py -l mediumCorners -p AStarCornersAgent

# 自动批改
python autograder.py --no-graphics
```

### 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-l` | 地图名 | `-l mediumMaze` |
| `-p` | 吃豆人代理 | `-p SearchAgent` |
| `-a` | 代理参数 | `-a fn=bfs` |
| `-z` | 窗口缩放 | `-z 0.65` |
| `-q` | 安静模式 | `-q` |
| `-f 0` | 最快速度 | `-f 0` |

## 项目结构

```
.
├── README.md
├── 使用说明.md
└── source/
    ├── pacman_launcher.py    # GUI 启动器
    ├── pacman.py             # 游戏主程序
    ├── search.py             # BFS / DFS / UCS / A* 实现
    ├── searchAgents.py       # 启发式与代理逻辑
    ├── ghostAgents.py        # 幽灵 AI 代理
    ├── keyboardAgents.py     # 键盘控制代理
    ├── graphicsDisplay.py    # 图形显示（含计时器）
    ├── graphicsUtils.py      # 图形工具
    ├── util.py               # 栈、队列、优先队列
    ├── autograder.py         # 自动批改
    ├── layouts/              # 地图文件
    └── test_cases/           # 批改测试用例
```

## 自动批改题目

| 题号 | 内容 |
|------|------|
| q1 | DFS |
| q2 | BFS |
| q3 | UCS |
| q4 | A* 单点 + 曼哈顿启发式 |
| q5 | Corners 问题 |
| q6 | Corners 启发式 |
| q7 | Food 启发式 |
| q8 | ClosestDot |

```bash
python autograder.py --no-graphics         # 全部题目
python autograder.py -q q4 --no-graphics   # 单题测试
```

## 得分规则

| 事件 | 分数 |
|------|------|
| 吃小豆 | +10 |
| 吃完所有小豆（胜利） | +500 |
| 每步 | -1 |
| 惊吓态撞幽灵 | +200 |
| 被正常幽灵撞到（失败） | -500 |

## 操作方式

- **键盘模式**：方向键 或 W/A/S/D 移动，Q 停止
- **AI 模式**：启动器中选择算法后点击「启动」

## 致谢

本项目基于 [UC Berkeley CS188 AI Pacman](http://ai.berkeley.edu/project_overview.html) 框架。
