# searchAgents.py
# ---------------
# 许可信息：可在教学用途下使用或扩展本项目，但须 (1) 不得分发或公开标准答案，
# (2) 保留本声明，(3) 注明 UC Berkeley 出处（http://ai.berkeley.edu）。
#
# 致谢：Pacman AI 项目由 UC Berkeley 开发。


"""
本文件包含可控制 Pacman 的各类代理。运行 pacman.py 时用 -p 选择代理，用 -a 传参。

示例（深度优先搜索）：
> python pacman.py -p SearchAgent -a fn=depthFirstSearch

更多搜索策略见课程项目说明。请仅修改标有「*** YOUR CODE HERE ***」的部分。
"""

from typing import List, Tuple, Any
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
import pacman


def _manhattan(a, b):
    """两点间的曼哈顿距离。"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _closestFoodDistance(start, foodGrid, walls):
    """从 start 出发 BFS 到最近食物的真实步数。"""
    from util import Queue
    fringe = Queue()
    fringe.push((start, 0))
    visited = {start}
    while not fringe.isEmpty():
        (x, y), dist = fringe.pop()
        if foodGrid[x][y]:
            return dist
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            dx, dy = Actions.directionToVector(action)
            nx, ny = int(x + dx), int(y + dy)
            if not walls[nx][ny] and (nx, ny) not in visited:
                visited.add((nx, ny))
                fringe.push(((nx, ny), dist + 1))
    return 0

def _mstLowerBound(points, distanceFn):
    """在 distanceFn 度量下，对 points 用 Prim 算法求 MST 权重（下界）。"""
    if not points:
        return 0
    remaining = set(points)
    current = remaining.pop()
    visited = {current}
    total = 0
    while remaining:
        bestPoint = None
        bestCost = float('inf')
        for u in visited:
            for v in remaining:
                cost = distanceFn(u, v)
                if cost < bestCost:
                    bestCost = cost
                    bestPoint = v
        total += bestCost
        visited.add(bestPoint)
        remaining.remove(bestPoint)
    return total

class GoWestAgent(Agent):
    """一直向西走，直到无法继续向西的代理。"""

    def getAction(self, state):
        """接收 GameState（定义见 pacman.py），返回一个动作。"""
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# 以下部分已写好框架，但须先完成 search.py 中的搜索算法 #
#######################################################

class SearchAgent(Agent):
    """
    通用搜索代理：对给定搜索问题调用指定搜索算法，再按所得路径依次行动。

    默认对 PositionSearchProblem 运行 DFS，目标为 (1,1)。

    fn 可选：depthFirstSearch / dfs、breadthFirstSearch / bfs 等。

    注意：请勿修改 SearchAgent 类本身的代码。
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # 下列代码通过反射按名称加载搜索函数与启发式

        # 根据名称获取 search.py 中的搜索函数
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in searchAgents.py or search.py.')
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # 将搜索算法与启发式绑定为 lambda
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # 根据名称获取搜索问题类
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        代理首次看到棋盘时调用：在此计算到目标的完整路径并保存。

        参数 state: GameState 对象（见 pacman.py）
        """
        if self.searchFunction == None: raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state)  # 构造搜索问题
        self.actions  = self.searchFunction(problem)  # 求解路径
        if self.actions == None:
            self.actions = []
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state):
        """
        返回在 registerInitialState 中规划好的路径上的下一步动作；
        若无后续动作则返回 Directions.STOP。

        参数 state: GameState 对象（见 pacman.py）
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    在 Pacman 棋盘上寻路到指定坐标的问题。

    状态空间为 (x, y) 位置。本类已完整实现，请勿修改。
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        保存起点与目标。

        gameState: GameState 对象（pacman.py）
        costFn: 从状态（元组）到非负代价的函数
        goal: 目标坐标
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print('Warning: this does not look like a regular search maze')

        # 用于图形界面统计扩展节点（请勿修改）
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # 请勿修改

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # 仅用于可视化
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        返回后继状态、对应动作及代价 1。

        与 search.py 约定一致：列表元素为 (successor, action, stepCost)。
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # 记录扩展次数（请勿修改）
        self._expanded += 1  # 请勿修改
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        返回动作序列的总代价；若含非法移动则返回 999999。
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # 计算下一格并检查是否撞墙
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    位置搜索代理：代价函数惩罚棋盘西侧位置。
    进入 (x,y) 的代价为 1/2^x。
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)

class StayWestSearchAgent(SearchAgent):
    """
    位置搜索代理：代价函数惩罚棋盘东侧位置。
    进入 (x,y) 的代价为 2^x。
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    """PositionSearchProblem 的曼哈顿距离启发式。"""
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    """PositionSearchProblem 的欧几里得距离启发式。"""
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# 以下为需完成/已实现的学生代码部分                  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    须经过迷宫四个角的问题。

    需自行设计合适的状态空间与后继函数。
    """

    def __init__(self, startingGameState: pacman.GameState):
        """保存墙壁、Pacman 起点与四个角坐标。"""
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print('Warning: no food in corner ' + str(corner))
        self._expanded = 0  # 请勿修改；已扩展的搜索节点计数

    def getStartState(self):
        """返回起始状态（自定义状态空间，非完整 Pacman 状态）。"""
        return (self.startingPosition, tuple(False for _ in self.corners))

    def isGoalState(self, state: Any):
        """判断是否为已访问全部四角的目标状态。"""
        position, visitedCorners = state
        return all(visitedCorners)

    def getSuccessors(self, state: Any):
        """
        返回后继三元组列表，每步代价为 1。

        格式同 search.py：(successor, action, stepCost)。
        """

        successors = []
        position, visitedCorners = state
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            # 合法移动则加入后继；判断是否撞墙示例：
            #   x,y = currentPosition
            #   dx, dy = Actions.directionToVector(action)
            #   nextx, nexty = int(x + dx), int(y + dy)
            #   hitsWall = self.walls[nextx][nexty]

            x, y = position
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextPosition = (nextx, nexty)
                nextVisited = list(visitedCorners)
                for i, corner in enumerate(self.corners):
                    if nextPosition == corner:
                        nextVisited[i] = True
                successors.append(((nextPosition, tuple(nextVisited)), action, 1))

        self._expanded += 1  # 请勿修改
        return successors

    def getCostOfActions(self, actions):
        """
        返回动作序列代价；非法移动返回 999999（已实现）。
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)


def cornersHeuristic(state: Any, problem: CornersProblem):
    """
    CornersProblem 的启发式函数。

    参数 state: 当前搜索状态（你在问题中定义的数据结构）
    参数 problem: 本局的 CornersProblem 实例

    返回值须为从该状态到任意目标的最短路径代价的下界（可采纳；最好一致）。
    """
    corners = problem.corners  # 四个角的坐标
    walls = problem.walls  # 迷宫墙壁 Grid（见 game.py）

    position, visitedCorners = state
    remaining = [corner for corner, visited in zip(problem.corners, visitedCorners) if not visited]
    if not remaining:
        return 0
    nearest = min(_manhattan(position, corner) for corner in remaining)
    return nearest + _mstLowerBound(remaining, _manhattan)

class AStarCornersAgent(SearchAgent):
    """使用 cornersHeuristic 的 A* 四角搜索代理。"""
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    收集棋盘上所有食物（豆子）的搜索问题。

    状态为 (pacmanPosition, foodGrid)：
      pacmanPosition: (x,y) 整数坐标
      foodGrid: Grid（见 game.py），True 表示该格仍有食物
    """
    def __init__(self, startingGameState: pacman.GameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0  # 请勿修改
        self.heuristicInfo = {}  # 供启发式缓存中间结果

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        """返回后继状态、动作及代价 1。"""
        successors = []
        self._expanded += 1  # 请勿修改
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """返回动作序列总代价；非法移动返回 999999。"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # 计算下一状态并检查合法性
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    """使用 foodHeuristic 的 Food 问题 A* 代理。"""
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state: Tuple[Tuple, List[List]], problem: FoodSearchProblem):
    """
    FoodSearchProblem 的启发式函数。

    启发式应可采纳；多数可采纳启发式也一致。
    若 A* 解的代价劣于 UCS，则启发式可能不一致或不可采纳。

    状态为 (pacmanPosition, foodGrid)；可用 foodGrid.asList() 得到食物坐标列表。
    可通过 problem.walls 等访问墙壁等信息。
    可在 problem.heuristicInfo 中缓存重复计算（如迷宫距离）。
    """
    position, foodGrid = state
    foodList = foodGrid.asList()
    if not foodList:
        return 0

    if 'mazeCache' not in problem.heuristicInfo:
        problem.heuristicInfo['mazeCache'] = {}

    cache = problem.heuristicInfo['mazeCache']

    def mazeDist(a, b):
        key = (a, b) if a <= b else (b, a)
        if key not in cache:
            cache[key] = mazeDistance(a, b, problem.startingGameState)
        return cache[key]

    return max(mazeDist(position, food) for food in foodList)

class ClosestDotSearchAgent(SearchAgent):
    """通过多次搜索，每次走向当前最近的一颗豆，直至吃完所有豆。"""
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState)
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception('findPathToClosestDot returned an illegal move: %s!\n%s' % t)
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print('Path found with cost %d.' % len(self.actions))

    def findPathToClosestDot(self, gameState: pacman.GameState):
        """
        从 gameState 出发，返回到最近一颗豆的路径（动作列表）。
        """
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)

        return search.bfs(problem)

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    寻路到任意一颗食物的问题。

    与 PositionSearchProblem 类似，但目标判定不同；状态空间与后继可继承父类。

    可用于实现 findPathToClosestDot。
    """

    def __init__(self, gameState):
        """从 gameState 读取信息，一般无需修改。"""
        self.food = gameState.getFood()

        # 供 PositionSearchProblem 使用的字段
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # 请勿修改

    def isGoalState(self, state: Tuple[int, int]):
        """
        状态为 Pacman 坐标；当该格有食物时为目标。
        """
        x,y = state

        return self.food[x][y]


def _pacmanMoveTowardScaredGhosts(state):
    """
    有惊吓幽灵时，用 A* 追击变白幽灵（邻格仅未惊吓幽灵不可进入）。
    返回一步动作；无惊吓幽灵时返回 None。
    """
    legal = [a for a in state.getLegalPacmanActions() if a != Directions.STOP]
    if not legal:
        return Directions.STOP

    goals = []
    active_ghosts = []
    scared_positions = []
    for g in state.getGhostStates():
        pos = g.getPosition()
        if pos is None:
            continue
        if g.scaredTimer > 0:
            goals.append(util.nearestPoint(pos))
            scared_positions.append(pos)
        else:
            active_ghosts.append(pos)

    if not goals:
        return None

    class ScaredHuntProblem(search.SearchProblem):
        def __init__(self, gameState, goals, active_ghosts):
            self.walls = gameState.getWalls()
            self.goals = set(goals)
            self.start = gameState.getPacmanPosition()
            self.active_ghosts = active_ghosts

        def getStartState(self):
            return self.start

        def isGoalState(self, pos):
            return any(_manhattan(pos, g) <= 1 for g in self.goals)

        def getSuccessors(self, pos):
            successors = []
            for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                dx, dy = Actions.directionToVector(action)
                nx, ny = int(pos[0] + dx), int(pos[1] + dy)
                if self.walls[nx][ny]:
                    continue
                minGhost = min(
                    (_manhattan((nx, ny), g) for g in self.active_ghosts),
                    default=999,
                )
                if minGhost <= 1:
                    continue
                successors.append(((nx, ny), action, 1))
            return successors

        def getCostOfActions(self, actions):
            return len(actions)

    def heuristic(pos, problem):
        return min(_manhattan(pos, g) for g in problem.goals)

    path = search.aStarSearch(ScaredHuntProblem(state, goals, active_ghosts), heuristic)
    if path:
        return path[0]

    pac = state.getPacmanPosition()

    def fallback_score(action):
        dx, dy = Actions.directionToVector(action)
        nx, ny = int(pac[0] + dx), int(pac[1] + dy)
        if state.hasWall(nx, ny):
            return -10**9
        minActive = min((_manhattan((nx, ny), g) for g in active_ghosts), default=999)
        if minActive <= 1:
            return -10**9
        nearestScared = min(_manhattan((nx, ny), util.nearestPoint(sp)) for sp in scared_positions)
        return -nearestScared

    return max(legal, key=fallback_score)


class DynamicAvoidanceAgent(Agent):
    """
    每步重规划：未惊吓得幽灵视为危险；主动/危急时吃能量豆；
    能量豆生效后追击变白幽灵（+200 分），不再把惊吓得幽灵当障碍。
    """
    def __init__(self, dangerRadius=2, fleeRadius=4, capsuleSeekRadius=8):
        self.dangerRadius = dangerRadius
        self.fleeRadius = fleeRadius
        self.capsuleSeekRadius = capsuleSeekRadius

    def getAction(self, state):
        legal = state.getLegalPacmanActions()
        legal = [a for a in legal if a != Directions.STOP]
        if not legal:
            return Directions.STOP

        food = state.getFood().asList()
        capsules = list(state.getCapsules())
        pac = state.getPacmanPosition()
        fleeRadius = self.fleeRadius

        scared_ghosts = []
        active_ghosts = []
        for g in state.getGhostStates():
            pos = g.getPosition()
            if pos is None:
                continue
            if g.scaredTimer > 0:
                scared_ghosts.append((pos, g.scaredTimer))
            else:
                active_ghosts.append(pos)

        minActiveDist = min((_manhattan(pac, g) for g in active_ghosts), default=999)
        if scared_ghosts:
            action = _pacmanMoveTowardScaredGhosts(state)
            if action is not None:
                return action

        goals = []
        if capsules and minActiveDist <= self.capsuleSeekRadius:
            goals = [min(capsules, key=lambda c: _manhattan(pac, c))]
        elif food:
            goals = food

        if not goals:
            return Directions.STOP

        class SafeTargetProblem(search.SearchProblem):
            def __init__(self, gameState, goals, active_ghosts, flee_radius):
                self.walls = gameState.getWalls()
                self.food = gameState.getFood()
                self.goals = set(goals)
                self.start = gameState.getPacmanPosition()
                self.active_ghosts = active_ghosts
                self.flee_radius = flee_radius

            def getStartState(self):
                return self.start

            def isGoalState(self, pos):
                if pos in self.goals:
                    return True
                return self.food[pos[0]][pos[1]]

            def getSuccessors(self, pos):
                successors = []
                for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                    dx, dy = Actions.directionToVector(action)
                    nx, ny = int(pos[0] + dx), int(pos[1] + dy)
                    if self.walls[nx][ny]:
                        continue
                    minGhost = min(
                        (_manhattan((nx, ny), g) for g in self.active_ghosts),
                        default=999,
                    )
                    if minGhost <= 1:
                        continue
                    step = 1 + max(0, self.flee_radius - minGhost) * 8
                    successors.append(((nx, ny), action, step))
                return successors

            def getCostOfActions(self, actions):
                return len(actions)

        def heuristic(pos, problem):
            if problem.goals:
                return min(_manhattan(pos, g) for g in problem.goals)
            return 0

        problem = SafeTargetProblem(
            state, goals, active_ghosts, fleeRadius,
        )
        path = search.aStarSearch(problem, heuristic)
        if path:
            return path[0]

        def score(action):
            x, y = pac
            dx, dy = Actions.directionToVector(action)
            nx, ny = int(x + dx), int(y + dy)
            if state.hasWall(nx, ny):
                return -10**9
            minGhost = min((_manhattan((nx, ny), g) for g in active_ghosts), default=999)
            if minGhost <= 1:
                return -10**9
            nearestFood = min((_manhattan((nx, ny), f) for f in food), default=999)
            nearestCap = min((_manhattan((nx, ny), c) for c in capsules), default=999)
            capBonus = 0
            if capsules and minActiveDist <= self.capsuleSeekRadius:
                capBonus = -nearestCap * 5
            return minGhost * 25 - nearestFood + capBonus

        return max(legal, key=score)

class AlphaBetaPacmanAgent(Agent):
    """
    用于加分项展示的简化 Minimax / Alpha-Beta 对抗代理。
    """
    def __init__(self, depth=2):
        self.depth = depth

    def getAction(self, state):
        hunt = _pacmanMoveTowardScaredGhosts(state)
        if hunt is not None:
            return hunt

        def evalState(s):
            if s.isWin():
                return 10**9
            if s.isLose():
                return -10**9
            pac = s.getPacmanPosition()
            food = s.getFood().asList()
            ghostStates = s.getGhostStates()
            score = float(s.getScore())

            scared = [g for g in ghostStates if g.scaredTimer > 0 and g.getPosition() is not None]
            active = [g for g in ghostStates if g.scaredTimer == 0 and g.getPosition() is not None]

            if scared:
                for g in scared:
                    pos = g.getPosition()
                    d = max(_manhattan(pac, pos), 0.1)
                    score += 300.0 / (1 + d)
                    score += min(g.scaredTimer, 40) * 3.0
                    if d <= 1.0:
                        score += 180.0
            elif food:
                nearestFood = min(_manhattan(pac, f) for f in food)
                score += 40.0 / (1 + nearestFood)
                score -= 8 * len(food)
                score -= 0.2 * sum(_manhattan(pac, f) for f in food[: min(len(food), 6)])

            capsules = s.getCapsules()
            if capsules and not scared:
                minActive = min(
                    (_manhattan(pac, g.getPosition()) for g in active),
                    default=999,
                )
                if minActive <= 8:
                    nearestCap = min(_manhattan(pac, c) for c in capsules)
                    score += 55.0 / (1 + nearestCap)

            for g in active:
                pos = g.getPosition()
                d = _manhattan(pac, pos)
                if d < 0.7:
                    return -10**9
                score -= 80.0 / max(d, 0.5)
                if d <= 2:
                    score -= 50 * (3 - d)
            return score

        def alphabeta(s, depth, agentIndex, alpha, beta):
            if depth == self.depth or s.isWin() or s.isLose():
                return evalState(s), None
            numAgents = s.getNumAgents()
            legal = s.getLegalActions(agentIndex)
            if not legal:
                return evalState(s), None

            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth

            if agentIndex == 0:
                bestScore, bestAction = float('-inf'), legal[0]
                for action in legal:
                    succ = s.generateSuccessor(agentIndex, action)
                    score, _ = alphabeta(succ, nextDepth, nextAgent, alpha, beta)
                    if score > bestScore:
                        bestScore, bestAction = score, action
                    alpha = max(alpha, bestScore)
                    if alpha >= beta:
                        break
                return bestScore, bestAction

            bestScore, bestAction = float('inf'), legal[0]
            for action in legal:
                succ = s.generateSuccessor(agentIndex, action)
                score, _ = alphabeta(succ, nextDepth, nextAgent, alpha, beta)
                if score < bestScore:
                    bestScore, bestAction = score, action
                beta = min(beta, bestScore)
                if alpha >= beta:
                    break
            return bestScore, bestAction

        return alphabeta(state, 0, 0, float('-inf'), float('inf'))[1]

def mazeDistance(point1: Tuple[int, int], point2: Tuple[int, int], gameState: pacman.GameState) -> int:
    """
    返回两点在迷宫中的最短步数（使用已实现的 BFS）。

    gameState 可为任意局面；忽略其中 Pacman 的当前位置。

    示例：mazeDistance((2,4), (5,6), gameState)
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1)
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
