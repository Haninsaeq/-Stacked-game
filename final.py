import heapq
from collections import deque
import random
import time

EMPTY = ' '
WALL = '\033[90m#\033[0m'
BORDER = '\033[92m*\033[0m'
BLUE = '\033[94m⬤\033[0m'
PINK = '\033[95m⬤\033[0m'
GREEN = '\033[92m⬤\033[0m'


class BoardState:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[EMPTY for _ in range(width)] for _ in range(height)]
        for i in range(width):
            self.board[0][i] = BORDER
            self.board[height-1][i] = BORDER
        for i in range(height):
            self.board[i][0] = BORDER
            self.board[i][width-1] = BORDER

    def add_walls_and_pieces(self, piece_count, wall_count, num_colors):
        self.piece_count = piece_count
        self.wall_count = wall_count

        for _ in range(wall_count):
            while True:
                x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
                if self.board[x][y] == EMPTY:
                    self.board[x][y] = WALL
                    break

        for _ in range(piece_count):
            while True:
                x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
                if self.board[x][y] == EMPTY:
                    self.board[x][y] = BLUE
                    break

        for _ in range(piece_count):
            while True:
                x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
                if self.board[x][y] == EMPTY:
                    self.board[x][y] = PINK
                    break

        if num_colors == 3:
            for _ in range(piece_count):
                while True:
                    x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
                    if self.board[x][y] == EMPTY:
                        self.board[x][y] = GREEN
                        break

    def print_board(self):
        green = '\033[92m'
        reset = '\033[0m'
        for i in range(self.height):
            for j in range(self.width):
                print(self.board[i][j], end='')
                if j < self.width - 1:
                    print(f"{green} | {reset}", end='')
            print()
            if i < self.height - 1:
                for j in range(self.width):
                    print(f"{green}---{reset}", end='')
                    if j < self.width - 1:
                        print(f"{green}+{reset}", end='')
                print()

    def can_move(self, dx, dy):
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != EMPTY and self.board[i][j] != WALL and self.board[i][j] != BORDER:
                    new_x, new_y = i + dx, j + dy
                    if 0 <= new_x < self.height and 0 <= new_y < self.width:
                        if self.board[new_x][new_y] == EMPTY or self.board[new_x][new_y] == BORDER:
                            return True
        return False

    def move_pieces(self, dx, dy):
        new_board = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        for i in range(self.width):
            new_board[0][i] = BORDER
            new_board[self.height-1][i] = BORDER
        for i in range(self.height):
            new_board[i][0] = BORDER
            new_board[i][self.width-1] = BORDER
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != EMPTY and self.board[i][j] != WALL and self.board[i][j] != BORDER:
                    new_x, new_y = i + dx, j + dy
                    if 0 <= new_x < self.height and 0 <= new_y < self.width:
                        if self.board[new_x][new_y] == EMPTY:
                            new_board[new_x][new_y] = self.board[i][j]
                        elif self.board[new_x][new_y] == self.board[i][j]:
                            new_board[new_x][new_y] = self.board[i][j]
                        else:
                            # عند الاصطدام بقطعة مختلفة أو حاجز، تبقى القطعة في مكانها
                            new_board[i][j] = self.board[i][j]
                elif self.board[i][j] == WALL or self.board[i][j] == BORDER:
                    new_board[i][j] = self.board[i][j]
        self.board = new_board

    def is_goal_state(self):
        count_blue = sum(self.board[i][j] == BLUE for i in range(self.height) for j in range(self.width))
        count_pink = sum(self.board[i][j] == PINK for i in range(self.height) for j in range(self.width))
        count_green = sum(self.board[i][j] == GREEN for i in range(self.height) for j in range(self.width))
        if count_blue == 1 and count_pink == 1 and (count_green == 0 or count_green == 1):
            return True
        return False

    def get_successors(self):
        successors = []
        for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            if self.can_move(dx, dy):
                new_state = self.copy_state()
                new_state.move_pieces(dx, dy)
                successors.append((dx, dy, new_state))  
        return successors

    def copy_state(self):
        new_state = BoardState(self.width, self.height)
        new_state.board = [row[:] for row in self.board]
        return new_state

    def hashcode(self):
        return hash(str(self.board))

    def __lt__(self, other):
        return False 

    def heuristic(self):
        count_blue = sum(self.board[i][j] == BLUE for i in range(self.height) for j in range(self.width))
        count_pink = sum(self.board[i][j] == PINK for i in range(self.height) for j in range(self.width))
        count_green = sum(self.board[i][j] == GREEN for i in range(self.height) for j in range(self.width))
        return abs(1 - count_blue) + abs(1 - count_pink) + abs(1 - count_green)
    

def bfs_search(initial_state):
    queue = deque([(initial_state, 0)])  
    visited = set()
    path = {}
    state_sequence = []

    visited.add(initial_state.hashcode())
    while queue:
        state, cost = queue.popleft() 
        if state.is_goal_state():
            solution_path = []
            while state in path:
                move, prev_state, prev_cost = path[state]
                if move:
                    solution_path.append((move, cost))
                    state_sequence.append(state)
                state = prev_state
                cost = prev_cost
            solution_path.reverse()
            state_sequence.reverse()
            return state, solution_path, len(visited), len(state_sequence), state_sequence, cost

        for dx, dy, successor in state.get_successors():
            if successor.hashcode() not in visited:
                visited.add(successor.hashcode())
                queue.append((successor, cost + 1)) 
                path[successor] = ((dx, dy), state, cost + 1)
    
    return None, [], len(visited), 0, [], 0

def dfs_search(initial_state):
    stack = [(initial_state, 0)]  
    visited = set()
    path = {}
    state_sequence = []

    visited.add(initial_state.hashcode())
    while stack:
        state, cost = stack.pop()  
        if state.is_goal_state():
            solution_path = []
            while state in path:
                move, prev_state, prev_cost = path[state]
                if move:
                    solution_path.append((move, cost))
                    state_sequence.append(state)
                state = prev_state
                cost = prev_cost
            solution_path.reverse()
            state_sequence.reverse()
            return state, solution_path, len(visited), len(state_sequence), state_sequence, cost

        for dx, dy, successor in state.get_successors():
            if successor.hashcode() not in visited:
                visited.add(successor.hashcode())
                stack.append((successor, cost + 1)) 
                path[successor] = ((dx, dy), state, cost + 1)
    
    return None, [], len(visited), 0, [], 0


def dfs_recursive(state, visited, path, cost=0):
    if state.is_goal_state():
        return state, list(path.values()), list(path.keys()), cost

    visited.add(state.hashcode())
    
    for dx, dy, successor in state.get_successors():
        if successor.hashcode() not in visited:
            path[successor] = (dx, dy, state, cost + 1)
            result, solution_path, state_sequence, result_cost = dfs_recursive(successor, visited, path, cost + 1)
            if result:
                return result, solution_path, state_sequence, result_cost
    
    return None, [], list(path.keys()), cost


def uniform_cost_search(initial_state):
    priority_queue = [(0, initial_state)]
    visited = set()
    path = {}
    state_path = {} 

    while priority_queue:
        cost, state = heapq.heappop(priority_queue)

        if state.is_goal_state():
            solution_path = []
            state_sequence = [state]
            while state in path:
                move, prev_state, prev_cost = path[state]
                if move:
                    solution_path.append((move, cost))
                    state_sequence.append(prev_state)
                state = prev_state
                cost = prev_cost
            solution_path.reverse()
            state_sequence.reverse()
            return state, solution_path, len(visited), len(state_sequence), state_sequence, cost

        visited.add(state)

        for dx, dy, successor in state.get_successors():
            if successor not in visited:
                heapq.heappush(priority_queue, (cost + 1, successor))
                path[successor] = ((dx, dy), state, cost + 1)
                state_path[successor] = state 
    return None, [], len(visited), 0, [], 0

def a_star_search(initial_state):
    priority_queue = [(0, 0, initial_state)]
    visited = set()
    path = {}
    state_path = {}
    g_costs = {initial_state: 0}

    while priority_queue:
        f_cost, g_cost, state = heapq.heappop(priority_queue)

        if state.is_goal_state():
            solution_path = []
            state_sequence = [state]
            while state in path:
                move, prev_state, prev_cost = path[state]
                if move:
                    solution_path.append((move, g_cost))
                    state_sequence.append(prev_state)
                state = prev_state
                g_cost = prev_cost
            solution_path.reverse()
            state_sequence.reverse()
            return state, solution_path, len(visited), len(state_sequence), state_sequence, g_costs[state]

        visited.add(state)

        for dx, dy, successor in state.get_successors():
            if successor not in visited:
                tentative_g_cost = g_costs[state] + 1
                h_cost = successor.heuristic()
                f_cost = tentative_g_cost + h_cost
                if successor not in g_costs or tentative_g_cost < g_costs[successor]:
                    g_costs[successor] = tentative_g_cost
                    heapq.heappush(priority_queue, (f_cost, tentative_g_cost, successor))
                    path[successor] = ((dx, dy), state, tentative_g_cost)
                    state_path[successor] = state

    return None, [], len(visited), 0, [], 0

def play_manually(initial_state):
    current_state = initial_state
    while True:
        print("Current Board:")
        current_state.print_board()
        command = input("Enter command (w/a/s/d to move, r to reset, q to quit): ")

        if command == 'q':
            break
        elif command == 'r':
            current_state = initial_state.copy_state()
            print("Game reset!")
        else:
            dx, dy = 0, 0
            if command == 'w':
                dx = -1
            elif command == 's':
                dx = 1
            elif command == 'a':
                dy = -1
            elif command == 'd':
                dy = 1
            else:
                continue

            if current_state.can_move(dx, dy):
                current_state.move_pieces(dx, dy)
                if current_state.is_goal_state():
                    print("Congratulations! You have one blue and one pink piece left! You win!")
                    current_state.print_board()
                    break
    print("Thank you for playing!")

def choose_algorithm(initial_state):
    while True:
        mode = input("Enter '1' to play manually, '2' for BFS, '3' for iterative DFS, '4' for recursive DFS, '5' for UC,'6' for A*,  'q' to quit: ")
        if mode == '1':
            play_manually(initial_state)
        elif mode == '2':
            start_time = time.time()  
            result, path, visited_nodes, solution_nodes, state_sequence, cost = bfs_search(initial_state)
            end_time = time.time() 
            total_time = end_time - start_time
        elif mode == '3':
            start_time = time.time() 
            result, path, visited_nodes, solution_nodes, state_sequence, cost = dfs_search(initial_state)
            end_time = time.time()  
            total_time = end_time - start_time
        elif mode == '4':
            start_time = time.time() 
            result, path, state_sequence, cost = dfs_recursive(initial_state, set(), {}, 0)
            visited_nodes = len(path)  
            solution_nodes = len(state_sequence)
            end_time = time.time()  
            total_time = end_time - start_time
        elif mode == '5':
            start_time = time.time()  
            result, path, visited_nodes, solution_nodes, state_sequence, cost = uniform_cost_search(initial_state)
            end_time = time.time()  
            total_time = end_time - start_time
        elif mode == '6':
            start_time = time.time()  
            result, path, visited_nodes, solution_nodes, state_sequence, cost = a_star_search(initial_state)
            end_time = time.time()  
            total_time = end_time - start_time
        elif mode == 'q':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
            continue
        
        if result:
            print("Path to solution:")
            for state in state_sequence:
                if isinstance(state, BoardState):
                    state.print_board()
                    print("------")
            print("Goal state:")
            print("Path to solution:")
            for move in path:
                print(f"Move: {move[0]} {move[1]}")
            #print("Path to solution:", path)
            print("Number of visited nodes:", visited_nodes)
            print("Number of solution nodes:", solution_nodes)
            print("Time to reach the goal: {:.2f} seconds".format(total_time))
            print("Cost to reach the goal:", cost)
        else:
            print("No solution found")

def main():
    width = int(input("Enter board width: "))
    height = int(input("Enter board height: "))
    piece_count = int(input("Enter number of pieces: "))
    wall_count = int(input("Enter number of walls: "))
    num_colors = int(input("Enter number of colors (2 or 3): "))
    initial_state = BoardState(width, height)
    initial_state.add_walls_and_pieces(piece_count, wall_count, num_colors)

    choose_algorithm(initial_state)

if __name__ == "__main__":
    main()