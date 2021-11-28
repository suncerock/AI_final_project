"""
The code mainly refers to the open source code in
	- https://github.com/lihongxun945/gobang
	- https://github.com/int8/monte-carlo-tree-search/blob/master/mctspy/tree/nodes.py
"""

from copy import deepcopy

from state import TwoPlayerGameState
import time
import random
import math

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

	def make_move(self, move, inplace=False):
		x, y = move
		player = self.next_player
		assert self.is_free(x, y)

		new_state = self if inplace else deepcopy(self)

		new_state.board[x][y] = player
		new_state.chess[player].append((x, y))
		new_state._next_player = self.last_player
		new_state._free -= 1

		if new_state.check_win(x, y, player):
			new_state._game_result = player
		elif new_state._free == 0:
			new_state._game_result = 0

		return new_state

	def get_actions(self):
		actions = []
		for i in range(self.width):
			for j in range(self.height):
				if self.board[i][j] == 0:
					actions.append((i, j))
		return [(1 / len(actions), action[1]) for action in actions]
	
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

	def pprint(self, fix_index=0):
		# Pretty print
		print("{:2s}".format("GG") + " ".join(["{:2d}".format(x + fix_index) for x in range(self.width)]))
		num2sign = {0:'-', GomokuState.x:'X', GomokuState.o:'O'}
		for i in range(self.height):
			print("{:2d} ".format(i + fix_index) +  " ".join(["{:2s}".format(num2sign[self.board[i][j]]) for j in range(self.width)]))
			

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

class ScoreGomokuState(GomokuState):
	def __init__(self, *args, **kwargs):
		super(ScoreGomokuState, self).__init__(*args, **kwargs)
		self._active = [[False for _ in range(self.width)] for _ in range(self.height)]
		self._score = {
			GomokuState.x: [[False for _ in range(self.width)] for _ in range(self.height)],
			GomokuState.o: [[False for _ in range(self.width)] for _ in range(self.height)]
		}
		self._init_score()

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
		# if not inplace:
		new_state._update_score(x, y)

		if new_state.check_win(x, y, player):
			new_state._game_result = player
		if new_state._free == 0:
			new_state._game_result = 0

		return new_state

	def _init_score(self):
		for j in range(self.width):
			for i in range(self.height):
				if i == 0 and j == 0 or i == self.height and j == 0 or i == 0 and j == self.width or i == self.height and j == self.width:
					self._score[GomokuState.x][j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"]
					self._score[GomokuState.o][j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"]
				elif i == 0 or j == 0 or i == self.height or j == self.width:
					self._score[GomokuState.x][j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"] + SHAPE_SCORE["ONE"]
					self._score[GomokuState.o][j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"] + SHAPE_SCORE["ONE"]
				else:
					self._score[GomokuState.x][j][i] = 4 * SHAPE_SCORE["ONE"]
					self._score[GomokuState.o][j][i] = 4 * SHAPE_SCORE["ONE"]
		return

	def get_actions(self, max_action=10):
		from heapq import heappush, heappop
		actions = []
		for x in range(self.width):
			for y in range(self.height):
				if self._active[x][y]:
					heappush(actions, (self._score[self.next_player][x][y] + self._score[self.last_player][x][y], (x, y)))
					if len(actions) > max_action:
						_ = heappop(actions)

		if len(actions) == 0:
			return [(1, (self.width // 2, self.height // 2))]
		else:
			tick = time.time()
			score_max = max(action[0] for action in actions)
			scores = [math.exp(actions[i][0] - score_max) for i in range(len(actions))]
			sum_scores = sum(scores)
			return [(scores[i] / sum_scores, actions[i][1]) for i in range(len(actions))]

	def update_point(self, x, y, player):
		opponent = GomokuState.x if player == GomokuState.o else GomokuState.o
		result, radius = 0, 15

		count, block, empty = 1, 0, -1
		for j in range(y + 1, y + radius + 1):
			if j >= self.height or self.board[x][j] == opponent:
				block += 1
				break
			if self.board[x][j] == 0:
				if empty == -1 and j < self.height - 1 and self.board[x][j + 1] == player:
					empty = count
					continue
				else:
					break
			if self.board[x][j] == player:
				count += 1

		for j in range(y - 1, y - radius - 1, -1):
			if j < 0 or self.board[x][j] == opponent:
				block += 1
				break
			if self.board[x][j] == 0:
				if empty == -1 and j > 0 and self.board[x][j - 1] == player:
					empty = 0
					continue
				else:
					break
			if self.board[x][j] == player:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(x + 1, x + radius + 1):
			if i >= self.width or self.board[i][y] == opponent:
				block += 1
				break
			if self.board[i][y] == 0:
				if empty == -1 and i < self.width - 1 and self.board[i + 1][y] == player:
					empty = count
					continue
				else:
					break
			if self.board[i][y] == player:
				count += 1
		for i in range(x - 1, x - radius - 1, -1):
			if i < 0 or self.board[i][y] == opponent:
				block += 1
				break
			if self.board[i][y] == 0:
				if empty == -1 and i > 0 and self.board[i - 1][y] == player:
					empty = 0
					continue
				else:
					break
			if self.board[i][y] == player:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(1, radius + 1):
			if x + i >= self.width or y + i >= self.height or self.board[x + i][y + i] == opponent:
				block += 1
				break
			if self.board[x + i][y + i] == 0:
				if empty == -1 and x + i < self.width - 1 and y + i < self.height - 1 and self.board[x + i + 1][y + i + 1] == player:
					empty = count
					continue
				else:
					break
			if self.board[x + i][y + i] == player:
				count += 1
		for i in range(1, radius + 1):
			if x - i < 0 or y - i < 0 or self.board[x - i][y - i] == opponent:
				block += 1
				break
			if self.board[x - i][y - i] == 0:
				if empty == -1 and x - i > 0 and y - i > 0 and self.board[x - i - 1][y - i - 1] == player:
					empty = 0
					continue
				else:
					break
			if self.board[x - i][y - i] == player:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(1, radius + 1):
			if x + i >= self.width or y - i < 0 or self.board[x + i][y - i] == opponent:
				block += 1
				break
			if self.board[x + i][y - i] == 0:
				if empty == -1 and x + i < self.width - 1 and y - i > 0 and self.board[x + i + 1][y - i - 1] == player:
					empty = count
					continue
				else:
					break
			if self.board[x + i][y - i] == player:
				count += 1
		for i in range(1, radius + 1):
			if x - i < 0 or y + i >= self.height or self.board[x - i][y + i] == opponent:
				block += 1
				break
			if self.board[x - i][y + i] == 0:
				if empty == -1 and x - i > 0 and y + i < self.height - 1 and self.board[x - i - 1][y + i + 1] == player:
					empty = 0
					continue
				else:
					break
			if self.board[x - i][y + i] == player:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		return result

	def _update_score(self, x, y):
		radius = 4
		def update(x, y):
			self._score[GomokuState.o][x][y] = self.update_point(x, y, GomokuState.o) if self.board[x][y] != GomokuState.x else 0
			self._score[GomokuState.x][x][y] = self.update_point(x, y, GomokuState.x) if self.board[x][y] != GomokuState.o else 0

		for i in range(-radius, radius + 1):
			if y + i < 0:
				continue
			if y + i >= self.height:
				break
			update(x, y + i)

		for i in range(-radius, radius + 1):
			if x + i < 0:
				continue
			if x + i >= self.width:
				break
			update(x + i, y)

		for i in range(-radius, radius + 1):
			if x + i < 0 or y + i < 0:
				continue
			if x + i >= self.width or y + i >= self.width:
				break
			update(x + i, y + i)

		for i in range(-radius, radius + 1):
			if x + i < 0 or y - i >= self.width:
				continue
			if x + i >= self.width or y - i < 0:
				break
			update(x + i, y - i)

	def _update_neighbor(self, x, y):
		self._active[x][y] = False
		for i, j in [(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
					 (x - 1, y),                 (x + 1, y),
					 (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)]:
			if self.is_free(i, j):
				self._active[i][j] = True
		return

	def _count_to_score(self, count, block, empty):
		if empty <= 0:
			if count >= 5:
				return SHAPE_SCORE["FIVE"]  # X X X X X
			if block == 0:
				if count == 1:
					return SHAPE_SCORE["ONE"]  # O X O
				elif count == 2:
					return SHAPE_SCORE["TWO"]  # O X X O
				elif count == 3:
					return SHAPE_SCORE["THREE"]  # O X X X O
				elif count == 4:
					return SHAPE_SCORE["FOUR"]  # O X X X X O
			if block == 1:
				if count == 1:
					return SHAPE_SCORE["BLOCKED_ONE"]  # - X O
				elif count == 2:
					return SHAPE_SCORE["BLOCKED_TWO"]  # - X X O
				elif count == 3:
					return SHAPE_SCORE["BLOCKED_THREE"]  # - X X X O
				elif count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X X O
		elif empty == 1 or empty == count - 1:
			if count >= 6:
				return SHAPE_SCORE["FIVE"]  # X O X X X X X
			if block == 0:
				if count == 2:
					return SHAPE_SCORE["TWO"] / 2  # O X O X O
				if count == 3:
					return SHAPE_SCORE["THREE"]
				# return SHAPE_SCORE["THREE"] + SHAPE_SCORE['BLOCKED_ONE']  # O X O X X O
				if count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]
				# return SHAPE_SCORE["BLOCKED_FOUR"] + SHAPE_SCORE['BLOCKED_ONE']  # O X O X X X O
				if count == 5:
					return SHAPE_SCORE["FOUR"]  # O X O X X X X O
			if block == 1:
				if count == 2:
					return SHAPE_SCORE["BLOCKED_TWO"]  # - X O X O
				if count == 3:
					return SHAPE_SCORE["BLOCKED_THREE"]  # - X O X X O / - X X O X O
				if count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X O X X X O / - X X X O X O
				if count == 5:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X O X X X X O / - X X X X O X

		elif empty == 2 or empty == count - 2:
			if count >= 7:
				return SHAPE_SCORE["FIVE"]  # X X O X X X X X
			if block == 0:
				if count == 3:
					return SHAPE_SCORE["THREE"]  # O X X O X O
				if count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # O X X O X X O
				if count == 5:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # O X X O X X X O
				if count == 6:
					return SHAPE_SCORE["FOUR"]  # O X X O X X X X O

			if block == 1:
				if count == 3:
					return SHAPE_SCORE["BLOCKED_THREE"]  # - X X O X O
				if count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X O X X O
				if count == 5:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X O X X X O / - X X X O X X
				if count == 6:
					return SHAPE_SCORE["FOUR"]  # - X X O X X X X O / - X X X X O X X O

			if block == 2:
				return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X O X X - / # - X X O X X X - / # - X X O X X X X -

		elif empty == 3 or empty == count - 3:
			if count >= 8:
				return SHAPE_SCORE["FIVE"]  # X X X O X X X X X
			if block == 0:
				if count == 4:
					return SHAPE_SCORE["THREE"]
				# return SHAPE_SCORE["THREE"] + SHAPE_SCORE["BLOCKED_ONE"]  # O X X X O X O
				if count == 5:
					return SHAPE_SCORE["THREE"]
				# return SHAPE_SCORE["THREE"] + SHAPE_SCORE["BLOCKED_TWO"]  # O X X X O X X O
				if count == 6:
					return SHAPE_SCORE["BLOCKED_FOUR"]
				# return SHAPE_SCORE["BLOCKED_FOUR"] + SHAPE_SCORE["BLOCKED_THREE"]  # O X X X O X X X O
				if count == 7:
					return SHAPE_SCORE["FOUR"]
			# return SHAPE_SCORE["FOUR"] + SHAPE_SCORE["BLOCKED_THREE"]  # O X X X O X X X X O

			if block == 1:
				if count == 4:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X O X O
				if count == 5:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X O X X O
				if count == 6:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X O X X X O
				if count == 7:
					return SHAPE_SCORE["FOUR"]  # - X X X O X X X X O

			if block == 2:
				return SHAPE_SCORE["BLOCKED_FOUR"]

		elif empty == 4 or empty == count - 4:
			if count >= 9:
				return SHAPE_SCORE["FIVE"]  # X X X X O X X X X X
			if block == 0:
				return SHAPE_SCORE[
					"FOUR"]  # O X X X X O X O / O X X X X O X X O / O X X X X O X X X O / O X X X X O X X X X X O

			if block == 1:
				if count == 5:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X X O X O / - X O X X X X O
				if count == 6:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X X O X X O / - X X O X X X X O
				if count == 7:
					return SHAPE_SCORE["BLOCKED_FOUR"]  # - X X X X O X X X O / - X X X O X X X X O
				if count == 8:
					return SHAPE_SCORE["FOUR"]  # - X X X X O X X X O / - X X X O X X X X O

			if block == 2:
				return SHAPE_SCORE["BLOCKED_FOUR"]

		elif empty == 5 or empty == count - 5:
			return SHAPE_SCORE["FIVE"]

		return 0

	def get_utility(self, player):
		score = 0
		opponent = GomokuState.x if player == GomokuState.o else GomokuState.o
		for chess in self.chess[player]:
			score += self._score[player][chess[0]][chess[1]]
		for chess in self.chess[opponent]:
			score -= self._score[player][chess[0]][chess[1]]
		return 1 / (1 + math.exp(-score))

def load_opening(state, openings):
    for i in range(0, len(openings), 2):
        state = state.make_move((openings[i] + state.height // 2, openings[i + 1] + state.width // 2), inplace=True)
    state.pprint()
    return state


if __name__ == '__main__':
	num2sign = {0:'-', GomokuState.x:'X', GomokuState.o:'O'}
	state = ScoreGomokuState(8, 8)

	# opening = []
	opening = [-2, -2, -1, -2, -2, -1, -1, -1, -2, 0]
	# opening = [-2,-10,-1,-9,0,-10,-1,-8]
	# opening = [7,5,7,6,5,4,6,4,4,6,4,5,6,7,5,7,3,6]
	# opening = [-9,0,-6,0,-5,2,-4,1,-4,0,-3,2,-2,3,-5,1,-6,1,-7,-1,-8,-2,-2,1,-3,1,-4,3,-1,0,-5,-1,-8,-1]
	state = load_opening(state, opening)

	from mcts import *
	best_node = MCTSNode(state)

	for _ in range(36):
		tick = time.time()
		_, best_node = mcts(best_node, 200)
		best_node.parent = None
		best_node.state.pprint()
		print(best_node.state.chess[best_node.state.last_player][-1], "Time: {:.2f}".format(time.time() - tick))
		if best_node.state.is_game_over():
			print("Winner: ", num2sign[best_node.state.game_result])
			break