"""
The code mainly refers to the open source code in
	- https://github.com/lihongxun945/gobang
	- https://github.com/int8/monte-carlo-tree-search/blob/master/mctspy/tree/nodes.py
"""

from copy import deepcopy

from state import TwoPlayerGameState
import time
import random

MAX_BOARD = 20
SHAPE_SCORE = dict(
	ONE=10,
	TWO=100,
	THREE=1000,
	FOUR=100000,
	FIVE=10000000,
	BLOCKED_ONE=1,
	BLOCKED_TWO=10,
	BLOCKED_THREE=100,
	BLOCKED_FOUR=20000
)


class GomokuState(TwoPlayerGameState):

	x = 1
	o = -1

	def __init__(self, width=MAX_BOARD, height=MAX_BOARD):
		self.board = [[0 for i in range(width)] for j in range(height)]
		self.width = width
		self.height = height

		self.chess = {GomokuState.x:[], GomokuState.o:[]}

		self._free = self.width * self.height
		self._next_player = GomokuState.x
		self._game_result = None

	@property
	def last_player(self):
		return GomokuState.x if self.next_player == GomokuState.o else GomokuState.o
	
	@property
	def next_player(self):
		return self._next_player

	@property
	def game_result(self):
		return self._game_result

	def is_game_over(self):
		return self.game_result is not None

	def make_move(self, move):
		x, y = move
		player = self.next_player
		assert self.is_free(x, y)

		new_state = deepcopy(self)

		new_state.board[x][y] = player
		new_state.chess[player].append((x, y))
		new_state._next_player = self.last_player
		new_state._free -= 1

		if new_state.check_win(x, y, player):
			new_state._game_result = player
		if new_state._free == 0:
			new_state._game_result = 0

		return new_state

	def get_actions(self):
		actions = []
		for i in range(self.width):
			for j in range(self.height):
				if self.board[i][j] == 0:
					actions.append((i, j))
		return actions
	
	def is_free(self, x, y):
		return x >= 0 and y >= 0 and x < self.width and y < self.height and self.board[x][y] == 0

	def check_win(self, x, y, player):
		count = [1, 1, 1, 1]
		active = [True, True, True, True]
		for i in range(1, 5):
			if x - i >= 0 and self.board[x - i][y] == player and active[0]:
				count[0] += 1
			else:
				active[0] = False
			if y - i >= 0 and self.board[x][y - i] == player and active[1]:
				count[1] += 1
			else:
				active[1] = False
			if x - i >= 0 and y - i >= 0 and self.board[x - i][y - i] == player and active[2]:
				count[2] += 1
			else:
				active[2] = False
			if x - i >= 0 and y + i < self.height and self.board[x - i][y + i] == player and active[3]:
				count[3] += 1
			else:
				active[3] = False
		
		active = [True, True, True, True]
		for i in range(1, 5):
			if x + i < self.width and self.board[x + i][y] == player and active[0]:
				count[0] += 1
			else:
				active[0] = False
			if y + i < self.height and self.board[x][y + i] == player and active[1]:
				count[1] += 1
			else:
				active[1] = False				
			if x + i < self.height and y + i < self.width and self.board[x + i][y + i] == player and active[2]:
				count[2] += 1
			else:
				active[2] = False				
			if x + i < self.height and y - i > 0 and self.board[x + i][y - i] == player and active[3]:
				count[3] += 1
			else:
				active[3] = False

		return count[0] >= 5 or count[1] >= 5 or count[2] >= 5 or count[3] >= 5

	def pprint(self):
		# Pretty print
		print("{:2s}".format("GG") + " ".join(["{:2d}".format(x + 1) for x in range(self.width)]))
		num2sign = {0:'-', GomokuState.x:'X', GomokuState.o:'O'}
		for i in range(self.height):
			print("{:2d} ".format(i + 1) +  " ".join(["{:2s}".format(num2sign[self.board[i][j]]) for j in range(self.width)]))
			

class OnlyNeighborGomokuState(GomokuState):
	def __init__(self, *args, **kwargs):
		super(OnlyNeighborGomokuState, self).__init__(*args, **kwargs)
		self._active = [[False for _ in range(self.width)] for _ in range(self.height)]

	def get_actions(self):
		actions = [(x, y) for x in range(self.width) for y in range(self.height) if self._active[x][y]]
		return actions if actions else [(self.width // 2, self.height // 2)]

	def make_move(self, move, inplace=False):
		x, y = move

		player = self.next_player
		assert self.is_free(x, y)

		new_state = self if inplace else deepcopy(self)

		new_state.board[x][y] = player
		new_state.chess[player].append((x, y))
		new_state._next_player = self.last_player
		new_state._free -= 1
		new_state._update_neighbor(x, y)

		if new_state.check_win(x, y, player):
			new_state._game_result = player
		if new_state._free == 0:
			new_state._game_result = 0

		return new_state

	def _update_neighbor(self, x, y):
		self._active[x][y] = False
		for i, j in [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
					 (x - 1, y),                 (x + 1, y),
					 (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]:
			if self.is_free(i, j):
				self._active[i][j] = True


def load_opening(state, openings):
	for i in range(0, len(openings), 2):
		state = state.make_move((openings[i] + state.height // 2, openings[i + 1] + state.width // 2), inplace=True)
	state.pprint()
	return state


if __name__ == '__main__':
	num2sign = {0:'-', GomokuState.x:'X', GomokuState.o:'O'}
	state = OnlyNeighborGomokuState(8, 8)

	opening = []
	# opening = [-2,-10,-1,-9,0,-10,-1,-8]
	# opening = [7,5,7,6,5,4,6,4,4,6,4,5,6,7,5,7,3,6]
	# opening = [-9,0,-6,0,-5,2,-4,1,-4,0,-3,2,-2,3,-5,1,-6,1,-7,-1,-8,-2,-2,1,-3,1,-4,3,-1,0,-5,-1,-8,-1]
	state = load_opening(state, opening)
	
	from mcts import *
	best_node = MCTSNode(state)
	# best_node = AlphaNode(state, p=1)

	for _ in range(36):
		tick = time.time()
		_, best_node = mcts(best_node, 5000)
		best_node.parent = None
		# for action, child in best_node.children.items():
		# 	print(action, '->', '{}/{}'.format(child.q, child.n))
		best_node.state.pprint()
		print(best_node.state.chess[best_node.state.last_player][-1], "Time: {:.2f}".format(time.time() - tick))
		if best_node.state.is_game_over():
			print("Winner: ", num2sign[best_node.state.game_result])
			break