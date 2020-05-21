import datetime
from statistics import mean

class Board:
    def __init__(self, board):
        """
        Initializes the board with given list of tiles.
        """
        self.board = board
        # actor position is determined based on the position of tile 'B'
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if board[i][j] == 'B':
                    self.actor_pos = (i, j)
        # 'r' is the default passable state
        self.passable = 'r'
        self.elapsed = []


    def print_board(self):
        print('passable: ' + self.passable)
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (i, j) == self.actor_pos:
                    print('@', end='')
                else:
                    print(self.board[i][j], end='')

            print()


    def tile_state(self, pos):
        return self.board[pos[0]][pos[1]]


    def is_tile_free(self, pos):
        """
        Determines whether the actor can enter tile at the given position
        in the current state.
        """
        if self.tile_state(pos) in [' ', 'B', 'E', 'S']:
            return True
        else:
            return self.tile_state(pos) == self.passable



    def is_move_possible(self, move):
        """
        Determine whether the given move is possible in the current state
        and at the current actor position. Returns True or False.
        Throws an error for a nonexisting move.
        """
        if move == 'move up':
            return self.is_tile_free((self.actor_pos[0 ] -1, self.actor_pos[1]))
        elif move == 'move down':
            return self.is_tile_free((self.actor_pos[0 ] +1, self.actor_pos[1]))
        elif move == 'move left':
            return self.is_tile_free((self.actor_pos[0], self.actor_pos[1 ] -1))
        elif move == 'move right':
            return self.is_tile_free((self.actor_pos[0], self.actor_pos[1 ] +1))
        elif move == 'switch':
            return self.tile_state(self.actor_pos) == 'S'
        elif move == 'finish':
            return self.tile_state(self.actor_pos) == 'E'
        else:
            raise Exception("Unknown move: " + str(move))


    all_moves = ['move up', 'move down', 'move left', 'move right', 'switch',
                 'finish']


    def reverse_move(self, move):
        """
        Determine the move that undoes the given move. All moves are reversible
        except the 'finish' move.
        """
        if move == 'move up':
            return 'move down'
        elif move == 'move down':
            return 'move up'
        elif move == 'move left':
            return 'move right'
        elif move == 'move right':
            return 'move left'
        elif move == 'switch':
            return 'switch'
        else:
            raise Exception('Move not reversible: ' + move)


    def possible_moves(self):
        """
        Calculate the list of moves an actor can perform in the current state.
        """
        return [m for m in Board.all_moves if self.is_move_possible(m)]


    def position_after_move(self, move):
        """
        Calculate the position of the actor after given move.
        """
        if move == 'move up':
            return (self.actor_pos[0 ] -1, self.actor_pos[1])
        elif move == 'move down':
            return (self.actor_pos[0 ] +1, self.actor_pos[1])
        elif move == 'move left':
            return (self.actor_pos[0], self.actor_pos[1 ] -1)
        elif move == 'move right':
            return (self.actor_pos[0], self.actor_pos[1 ] +1)
        elif move == 'switch':
            return self.actor_pos
        else:
            raise Exception('Not a move move: ' + move)


    def make_move(self, move):
        """
        Make changes in the state corresponding to the given move.
        Raises an exception when the given command does isn't equal
        to one of the valid moves moves.
        Raises an exception when the actor successfully performs the 'finish'
        move.
        Returns True if the move succeeded and False otherwise.
        """
        if not self.is_move_possible(move):
            return False

        if move[:4] == 'move':
            self.actor_pos = self.position_after_move(move)
        elif move == 'switch':
            if self.passable == 'r':
                self.passable = 'g'
            else:
                self.passable = 'r'
        elif move == 'finish':
            if self.tile_state(self.actor_pos) == 'E':
                print("Time of the whole game:", sum(self.elapsed))
                print("Mean time per action:", mean(self.elapsed))
                raise Exception("You won!")
        else:
            raise Exception("Unknown move: " + str(move))

        return True



class BacktrackingAgent:
    """
    An agent that explores the environment using backtracking.
    """
    def __init__(self, init_board = None):
        if init_board != None:
            self.set_board(init_board)


    def set_board(self, init_board):
        """
        Initializes the agent with the given board. This board is an internal
        representation that is disjoint from the one maintained in the
        environment.

        Also stores a board-like list of lists ('visited') that stores
        in which states ('r' or 'g') was the given tile visited.
        Possible values are '' (empty string) when a tile was never visited,
        'r', 'rg' or 'gr' when it was visited in the 'r' state and
        'g', 'rg' or 'gr' when it was visited in the 'g' state.

        'state_stack' holds performed moves that will be undone while
        backtracking. The 'mode' variable determines whether the agent
        currently explores forward or backtracks.
        """
        self.board = init_board
        self.visited = [['' for c in r] for r in init_board.board]
        self.state_stack = []
        self.mode = 'forward'


    def reaches_new_state(self, move):
        """
        Determines whether the given move moves the actor to an unvisited state.
        """
        pam = self.board.position_after_move(move)
        vb = self.visited[pam[0]][pam[1]]
        return self.board.passable not in vb


    def move(self, env):
        """
        Determines the next move of the actor. Uses 'env' only to retrieve
        a list of currently possible moves.
        """
        possible_moves = env.possible_moves()
        print(str(self.state_stack))
        # we want to finish as soon as it's possible
        if 'finish' in possible_moves:
            return 'finish'
        elif self.mode == 'forward':
            # if finishing is not possible and we aren't backtracking, we should
            # try moving forward
            print('going forward')
            pmoves = [m for m in possible_moves if self.reaches_new_state(m)]
            print('pmoves: ' + str(pmoves))
            # if there are no possible moves that reach a new state, we will
            # backtrack
            if len(pmoves) == 0:
                self.mode = 'backtrack'
                taken_move = self.state_stack[-1]['taken move']
                return self.board.reverse_move(taken_move)

            # otherwise go forward and record taken move and other possible
            # moves on the state stack
            self.state_stack.append({'taken move': pmoves[0],
                                     'other moves': pmoves[1:]})

            return pmoves[0]

        elif self.mode == 'backtrack':
            print('backtracking')
            print()
            # when backtracking and we have exhausted the entire state stack
            # then there is no path that leads to the end state
            if len(self.state_stack) == 0:
                raise Exception('Goal is not reachable :(')

            # if the stack is not empty, take its top element
            top = self.state_stack.pop()
            btr_possible_moves = top['other moves']
            # if there are no other possible moves at this level of backtracking
            # then backtrack futher
            if len(btr_possible_moves) == 0:
                return self.board.reverse_move(self.state_stack[-1]['taken move'])
            else:
                # if there are other options go forward
                self.mode = 'forward'
                self.state_stack.append({'taken move': btr_possible_moves[0],
                                         'other moves': btr_possible_moves[1:]})

                return btr_possible_moves[0]


    def percept(self, data):
        """
        Informs the agent about changes in the environment.
        At this moment it only tells whether the agent actually moved
        and whether the switching was successful.
        """
        if data['type'][:4] == 'move':
            pos = self.board.actor_pos
            if self.board.passable not in self.visited[pos[0]][pos[1]]:
                self.visited[pos[0]][pos[1]] += self.board.passable
            self.board.make_move(data['type'])
        elif data['type'] == 'switch':
            self.board.make_move('switch')


class Environment:
    def __init__(self, board, ai):
        self.board = board
        self.ai = ai

    def extract_player_board(self, board):
        return Board(board.board)

    def possible_moves(self):
        return self.board.possible_moves()

    def play_game(self, max_moves=100, wait_after_step=False):
        """
        Plays the game for at most max_moves. When wait_after_step is True
        then after each move of the agent the user is expected to press enter
        before the game continues.
        """
        self.ai.set_board(self.extract_player_board(self.board))

        for i in range(max_moves):
            a = datetime.datetime.now()
            print()
            print('Move ' + str(i))
            print('Possible moves: ' + str(self.board.possible_moves()))
            self.board.print_board()
            sel_move = self.ai.move(self)
            print('Move: ' + sel_move)
            result = self.board.make_move(sel_move)
            print('Move result: ' + str(result))
            self.ai.percept({'type': sel_move})
            b = datetime.datetime.now()
            delta = b - a
            self.board.elapsed.append(delta.total_seconds() * 1000)
            if wait_after_step:
                a = input()
                if a == 'F':
                    wait_after_step = False

# Two game boards for testing.
# 'W' -- Wall. Not passable.
# ' ' -- Passable space.
# 'B' -- The place where the actor begins.
# 'E' -- The place the actor needs to reach.
# 'r' -- Tiles passable when the switch is in position 'r' (default).
# 'g' -- Tiles passable when the switch is in position 'g'.
# 'S' -- Tiles with a switch (changes position between 'r' and 'g'). Requires
#        an action.
# '@' -- Current position of the actor (displayed by print_board)
# You can assume that all valid boards have walls around them.

board1 = Board([['W', 'W', 'W', 'W', 'W'],
                ['W', ' ', ' ', 'E', 'W'],
                ['W', 'g', 'W', 'W', 'W'],
                ['W', ' ', ' ', 'S', 'W'],
                ['W', 'W', 'r', 'W', 'W'],
                ['W', 'B', ' ', ' ', 'W'],
                ['W', 'W', 'W', 'W', 'W']])


board2 = Board([['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
                ['W', ' ', ' ', ' ', ' ', 'g', ' ', ' ', 'S', 'W'],
                ['W', 'W', ' ', 'W', ' ', 'W', 'W', ' ', 'W', 'W'],
                ['W', ' ', 'g', 'W', 'S', 'r', 'W', 'r', 'W', 'W'],
                ['W', 'W', ' ', 'W', 'W', ' ', 'W', ' ', 'E', 'W'],
                ['W', 'B', ' ', ' ', 'S', ' ', 'W', ' ', 'W', 'W'],
                ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W']])


# starting a game when the script runs
if __name__ == "__main__":
    env = Environment(board2, BacktrackingAgent())
    try:
        env.play_game(wait_after_step=True)
    except Exception as e:
        print('Exception happened: ' + str(e))
