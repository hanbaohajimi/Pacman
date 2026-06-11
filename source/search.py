# search.py
# ---------
# 许可信息：可在教学用途下使用或扩展本项目，但须 (1) 不得分发或公开标准答案，
# (2) 保留本声明，(3) 注明 UC Berkeley 出处（http://ai.berkeley.edu）。
#
# 致谢：Pacman AI 项目由 UC Berkeley 开发；核心代码与自动批改主要由
# John DeNero、Dan Klein 等完成；学生端批改由 Brad Miller、Nick Hay、Pieter Abbeel 等添加。


"""
在 search.py 中实现通用搜索算法，供 searchAgents.py 中的 Pacman 代理调用。
"""

import util

class SearchProblem:
    """
    描述搜索问题的结构（抽象类），不实现具体方法。

    无需修改本类。
    """

    def getStartState(self):
        """返回搜索问题的起始状态。"""
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
        参数 state: 搜索状态

        当且仅当 state 为目标状态时返回 True。
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        参数 state: 搜索状态

        返回三元组列表 (后继状态, 动作, 步代价)，其中：
        successor 为当前状态的后继；
        action 为到达该后继所需的动作；
        stepCost 为扩展到该后继的增量代价。
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        参数 actions: 动作序列

        返回该动作序列的总代价；序列必须由合法移动组成。
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    返回能通过 tinyMaze 的动作序列；用于其他地图时结果不正确，仅适用于 tinyMaze。
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def _reconstructPath(parent, goalState):
    """根据父节点字典从目标状态回溯得到动作列表。"""
    actions = []
    state = goalState
    while parent[state][0] is not None:
        prevState, action = parent[state]
        actions.append(action)
        state = prevState
    actions.reverse()
    return actions

def depthFirstSearch(problem: SearchProblem):
    """
    深度优先搜索：优先扩展搜索树中最深的节点。

    须返回到达目标的动作列表，并实现图搜索（避免重复访问已扩展状态）。

    调试时可打印：
    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    fringe = util.Stack()  # 边界：栈（LIFO）
    fringe.push((start, []))
    visited = set()

    while not fringe.isEmpty():
        state, actions = fringe.pop()
        if state in visited:
            continue
        visited.add(state)
        if problem.isGoalState(state):
            return actions

        for successor, action, _ in problem.getSuccessors(state):
            if successor not in visited:
                fringe.push((successor, actions + [action]))

    return []

def breadthFirstSearch(problem: SearchProblem):
    """广度优先搜索：优先扩展最浅层的节点。"""
    start = problem.getStartState()
    if problem.isGoalState(start):
        return []

    fringe = util.Queue()  # 边界：队列（FIFO）
    fringe.push(start)
    visited = {start}
    parent = {start: (None, None)}

    while not fringe.isEmpty():
        state = fringe.pop()
        if problem.isGoalState(state):
            return _reconstructPath(parent, state)

        for successor, action, _ in problem.getSuccessors(state):
            if successor not in visited:
                visited.add(successor)
                parent[successor] = (state, action)
                fringe.push(successor)

    return []

def uniformCostSearch(problem: SearchProblem):
    """一致代价搜索：优先扩展累计代价 g(n) 最小的节点。"""
    start = problem.getStartState()
    fringe = util.PriorityQueue()  # 边界：优先队列（二叉堆）
    fringe.push((start, [], 0), 0)
    bestCost = {start: 0}

    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()
        # 堆中可能存在过时条目，跳过已非最优的弹出
        if cost != bestCost.get(state, float('inf')):
            continue
        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if newCost < bestCost.get(successor, float('inf')):
                bestCost[successor] = newCost
                fringe.push((successor, actions + [action], newCost), newCost)

    return []

def nullHeuristic(state, problem=None):
    """
    启发式函数：估计从当前状态到最近目标的代价。
    本函数恒为 0，即无启发信息的平凡启发式。
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """A* 搜索：优先扩展 f(n)=g(n)+h(n) 最小的节点。"""
    start = problem.getStartState()
    fringe = util.PriorityQueue()
    startPriority = heuristic(start, problem)
    fringe.push((start, [], 0), startPriority)
    bestCost = {start: 0}

    while not fringe.isEmpty():
        state, actions, cost = fringe.pop()
        if cost != bestCost.get(state, float('inf')):
            continue
        if problem.isGoalState(state):
            return actions

        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost + stepCost
            if newCost < bestCost.get(successor, float('inf')):
                bestCost[successor] = newCost
                priority = newCost + heuristic(successor, problem)
                fringe.push((successor, actions + [action], newCost), priority)

    return []


# 函数别名（命令行 fn= 参数可使用缩写）
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
