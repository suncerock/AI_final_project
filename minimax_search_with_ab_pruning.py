"""
Gomoku for DATA130008 2021 Fall
Midterm1: Minimax with Alpha-Beta Pruning

Author: Yiwei Ding (18307110009)

The code is mainly based on pbrain-pyrandom by Jan Stransky (https://github.com/stranskyjan/pbrain-pyrandom)
The implementation of Alpha-Beta Pruning refers to the code by Ruipu Luo and Qingwen Liu (elearning, lab 2 template)
The utility function and the get action function 
	refers to the open source code in https://github.com/lihongxun945/gobang
"""

############ The code below are my implementation of the algorithm ###########
from copy import deepcopy
import time

class MinimaxAgent(object):
	def __init__(self, board, max_depth=5):
		self.board = board
		self.max_depth = max_depth
		self.node_count = 0

	def max_value(self, board, alpha, beta, depth):
		if depth >= self.max_depth:
			return board.get_utility(), None
		v = float("-inf")
		for a in board.get_actions():
			new_board = deepcopy(board)
			new_board.make_move(a[0], a[1], 1)
			self.node_count += 1
			move_v, move_action = self.min_value(new_board, alpha, beta, depth+1)
			if move_v > v:
				v = move_v
				action = a
			if v >= beta:
				return v, action
			alpha = max(alpha, v)
		return v, action

	def min_value(self, board, alpha, beta, depth):
		if depth >= self.max_depth:
			return board.get_utility(), None
		v = float("inf")
		for a in board.get_actions():
			new_board = deepcopy(board)
			new_board.make_move(a[0], a[1], 2)
			self.node_count += 1
			move_v, move_action = self.max_value(new_board, alpha, beta, depth+1)
			if move_v < v:
				v = move_v
				action = a
			if v <= alpha:
				return v, action
			beta = min(beta, v)
		return v, action

	def alpha_beta_search(self):
		# tick = time.time()
		v, action = self.max_value(self.board, float("-inf"), float("inf"), depth=0)
		# tock = time.time()
		return action


############# The code below are modified from pbrain-pyrandom ###############

import random
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = \
	"""
	name = min max search with alpha beta pruning
	author = Jan Stransky, Yiwei Ding
	"""

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


class Board(object):
	def __init__(self, width=MAX_BOARD, height=MAX_BOARD):
		self.board = [[0 for i in range(height)] for j in range(width)]
		self.last_player = None
		self.chess1 = []
		self.chess2 = []
		self.score1 = [[0 for i in range(height)] for j in range(width)]
		self.score2 = [[0 for i in range(height)] for j in range(width)]

	def is_free(self, x, y):
		return x >= 0 and y >= 0 and x < pp.width and y < pp.height and self.board[x][y] == 0

	def make_move(self, x, y, value):
		if not self.is_free(x, y):
			raise RuntimeError("[{}, {}] not free!".format(x, y))
		self.board[x][y] = value
		self.update_score(x, y, value)
		if value == 1:
			self.last_player = 1
			self.chess1.append((x, y))
		elif value == 2:
			self.last_player = 2
			self.chess2.append((x, y))

	def takeback(self, x, y):
		pp.pipeOut("真男人永不悔棋！")
		raise Exception("悔棋错误：不许悔棋")
		if self.is_free(x, y):
			raise RuntimeError("[{}, {}] free!".format(x, y))
		if self.board[x][y] == 1:
			self.chess1.remove((x, y))
		elif self.board[x][y] == 2:
			self.chess2.remove((x, y))
		self.board[x][y] = 0

	def __getitem__(self, index):
		x, y = index
		return self.board[x][y]

	def __repr__(self):
		s = "\t".join([" "] + [str(i) for i in range(MAX_BOARD)]) + "\n"
		for i in range(len(self.board)):
			s += "{}\t".format(i) +"\t".join([str(j) for j in self.board[i]]) + "\n"
		return s

	def get_actions(self, count_limit=20):
		fives = []
		fours1 = []
		fours2 = []
		two_blocked_fours1 = []
		two_blocked_fours2 = []
		blocked_fours1 = []
		blocked_fours2 = []
		two_threes1 = []
		two_threes2 = []
		threes1 = []
		threes2 = []
		twos1 = []
		twos2 = []
		neighbors = []

		if self.last_player is None:
			return [(pp.width // 2, pp.height // 2)]

		last_x, last_y = self.chess1[-1] if self.last_player == 1 else self.chess2[-1]
		for x in range(0, pp.width):
			for y in range(0, pp.height):
				if not self.is_free(x, y):
					continue
					
				if len(self.chess1) + len(self.chess2) < 6:
					if not self._has_neighbor(x, y, 1, 1):
						continue
				elif not self._has_neighbor(x, y, 2, 2):
					continue
				max_score = max(self.score1[x][y], self.score2[x][y])

				if max_score >= SHAPE_SCORE["FIVE"]:
					fives.append((x, y))
				elif self.score2[x][y] >= SHAPE_SCORE["FOUR"]:
					fours2.append((x, y))
				elif self.score1[x][y] >= SHAPE_SCORE["FOUR"]:
					fours1.append((x, y))
				elif self.score2[x][y] >= 2 * SHAPE_SCORE["BLOCKED_FOUR"]:
					two_blocked_fours2.append((x, y))
				elif self.score1[x][y] >= 2 * SHAPE_SCORE["BLOCKED_FOUR"]:
					two_blocked_fours1.append((x, y))
				elif self.score2[x][y] >= SHAPE_SCORE["BLOCKED_FOUR"]:
					blocked_fours2.append((x, y))
				elif self.score1[x][y] >= SHAPE_SCORE["BLOCKED_FOUR"]:
					blocked_fours1.append((x, y))
				elif self.score2[x][y] >= 2 * SHAPE_SCORE["THREE"]:
					two_threes2.append((x, y))
				elif self.score1[x][y] >= 2 * SHAPE_SCORE["THREE"]:
					two_threes1.append((x, y))
				elif self.score2[x][y] >= SHAPE_SCORE["THREE"]:
					threes2.append((x, y))
				elif self.score1[x][y] >= SHAPE_SCORE["THREE"]:
					threes1.append((x, y))
				elif self.score2[x][y] >= SHAPE_SCORE["TWO"]:
					twos2.append((x, y))
				elif self.score1[x][y] >= SHAPE_SCORE["TWO"]:
					twos1.append((x, y))
				else:
					neighbors.append((x, y))
		
		if fives:
			return fives
		if self.last_player == 1 and (fours2 or two_blocked_fours2):
			return fours2 + two_blocked_fours2
		if self.last_player == 2 and (fours1 or two_blocked_fours1):
			return fours1 + two_blocked_fours1
		if self.last_player == 1 and (fours1 or two_blocked_fours1):
			if two_blocked_fours2:
				return fours1 + two_blocked_fours2 + two_blocked_fours1 + blocked_fours2 + blocked_fours1
			if blocked_fours2:
				return fours1 + blocked_fours2 + blocked_fours1
			else:
				return fours1
		if self.last_player == 2 and (fours2 or two_blocked_fours2):
			if two_blocked_fours1:
				return fours2 + two_blocked_fours1 + two_blocked_fours2 + blocked_fours1 + blocked_fours2
			if blocked_fours1:
				return fours2 + blocked_fours1 + blocked_fours2
			else:
				return fours2

		
		if self.last_player == 1:
			result = two_threes2 + two_threes1 + blocked_fours2 + blocked_fours1 + threes2 + threes1
		if self.last_player == 2:
			result = two_threes1 + two_threes2 + blocked_fours1 + blocked_fours2 + threes1 + threes2
		# result.sort(key=lambda x:-max(self.score1[x[0]][x[1]], self.score2[x[0]][x[1]]))
		if two_threes2 or two_threes1:
			return result[:count_limit]

		if len(self.chess1) + len(self.chess2) > 10 and len(result) > 0:
			return result[:count_limit]

		twos = twos2 + twos1 if self.last_player == 1 else twos1 + twos2
		if twos:
			twos.sort(key=lambda x:-max(self.score1[x[0]][x[1]], self.score2[x[0]][x[1]]))
			result = result + twos
			return result[:count_limit]
		else:
			neighbors.sort(key=lambda x:-max(self.score1[x[0]][x[1]], self.score2[x[0]][x[1]]))
			result = result + neighbors
			return result[:count_limit]

	def update_point(self, x, y, color):
		opponent_color = 2 if color == 1 else 1
		result, radius = 0, 15

		# count: how many chess of your color
		# block: {0, 1, 2}
		count, block, empty = 1, 0, -1
		for j in range(y + 1, y + radius + 1):
			if j >= pp.height or self.board[x][j] == opponent_color:
				block += 1
				break
			if self.board[x][j] == 0:
				if empty == -1 and j < pp.height - 1 and self.board[x][j + 1] == color:
					empty = count
					continue
				else:
					break
			if self.board[x][j] == color:
				count += 1

		for j in range(y - 1, y - radius - 1, -1):
			if j < 0 or self.board[x][j] == opponent_color:
				block += 1
				break
			if self.board[x][j] == 0:
				if empty == -1 and j > 0 and self.board[x][j - 1] == color:
					empty = 0
					continue
				else:
					break
			if self.board[x][j] == color:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(x + 1, x + radius + 1):
			if i >= pp.width or self.board[i][y] == opponent_color:
				block += 1
				break
			if self.board[i][y] == 0:
				if empty == -1 and i < pp.width - 1 and self.board[i + 1][y] == color:
					empty = count
					continue
				else:
					break
			if self.board[i][y] == color:
				count += 1
		for i in range(x - 1, x - radius - 1, -1):
			if i < 0 or self.board[i][y] == opponent_color:
				block += 1
				break
			if self.board[i][y] == 0:
				if empty == -1 and i > 0 and self.board[i - 1][y] == color:
					empty = 0
					continue
				else:
					break
			if self.board[i][y] == color:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(1, radius + 1):
			if x + i >= pp.width or y + i >= pp.height or self.board[x + i][y + i] == opponent_color:
				block += 1
				break
			if self.board[x + i][y + i] == 0:
				if empty == -1 and x + i < pp.width - 1 and y + i < pp.height - 1 and self.board[x + i + 1][y + i + 1] == color:
					empty = count
					continue
				else:
					break
			if self.board[x + i][y + i] == color:
				count += 1
		for i in range(1, radius + 1):
			if x - i < 0 or y - i < 0 or self.board[x - i][y - i] == opponent_color:
				block += 1
				break
			if self.board[x - i][y - i] == 0:
				if empty == -1 and x - i > 0 and y - i > 0 and self.board[x - i - 1][y - i - 1] == color:
					empty = 0
					continue
				else:
					break
			if self.board[x - i][y - i] == color:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		count, block, empty = 1, 0, -1
		for i in range(1, radius + 1):
			if x + i >= pp.width or y - i < 0 or self.board[x + i][y - i] == opponent_color:
				block += 1
				break
			if self.board[x + i][y - i] == 0:
				if empty == -1 and x + i < pp.width - 1 and y - i > 0 and self.board[x + i + 1][y - i - 1] == color:
					empty = count
					continue
				else:
					break
			if self.board[x + i][y - i] == color:
				count += 1
		for i in range(1, radius + 1):
			if x - i < 0 or y + i >= pp.height or self.board[x - i][y + i] == opponent_color:
				block += 1
				break
			if self.board[x - i][y + i] == 0:
				if empty == -1 and x - i > 0 and y + i < pp.height - 1 and self.board[x - i - 1][y + i + 1] == color:
					empty = 0
					continue
				else:
					break
			if self.board[x - i][y + i] == color:
				count += 1
				if empty != -1:
					empty += 1

		result += self._count_to_score(count, block, empty)

		return result

	def update_score(self, x, y, color):
		# logDebug("updating score step {}".format(len(self.chess1) + len(self.chess2)))
		radius = 4

		def update(x, y):
			if self.board[x][y] != 1:
				self.score2[x][y] = self.update_point(x, y, 2)
			else:
				self.score2[x][y] == 0
			
			if self.board[x][y] != 2:
				self.score1[x][y]  = self.update_point(x, y, 1)
			else:
				self.score1[x][y]  == 0

		for i in range(-radius, radius + 1):
			if y + i < 0:
				continue
			if y + i >= pp.height:
				break
			update(x, y + i)

		for i in range(-radius, radius + 1):
			if x + i < 0:
				continue
			if x + i >= pp.width:
				break
			update(x + i, y)

		for i in range(-radius, radius + 1):
			if x + i < 0 or y + i < 0:
				continue
			if x + i >= pp.width or y + i >= pp.width:
				break
			update(x + i, y + i)
		
		for i in range(-radius, radius + 1):
			if x + i < 0 or y - i >= pp.width:
				continue
			if x + i >= pp.width or y - i < 0:
				break
			update(x + i, y - i)

	def get_utility(self):
		score = 0
		for chess in self.chess1:
			score += self.score1[chess[0]][chess[1]]
		for chess in self.chess2:
			score -= self.score2[chess[0]][chess[1]]
		return score

	def _has_neighbor(self, x, y, distance, count):
		for i in range(x - distance, x + distance + 1):
			if i < 0 or i >= pp.width:
				continue
			for j in range(y - distance, y + distance + 1):
				if j < 0 or j >= pp.height:
					continue
				if i == x and j == y:
					continue
				if self.board[i][j] != 0:
					count -= 1
		return count <= 0

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
				return SHAPE_SCORE["BLOCKED_FOUR"] # - X X O X X - / # - X X O X X X - / # - X X O X X X X -

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
				return SHAPE_SCORE["FOUR"]  # O X X X X O X O / O X X X X O X X O / O X X X X O X X X O / O X X X X O X X X X X O
			
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


board = Board()


def brain_init():
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")

def brain_restart():
	del board
	board = Board(pp.width, pp.height)
	for i in range(pp.width):
		for j in range(pp.height):
			board.board[i][j] = 0
	pp.pipeOut("OK")

def brain_my(x, y):
	try:
		board.make_move(x, y, 1)
	except:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	try:
		board.make_move(x, y, 2)
	except:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	try:
		board.make_move(x, y, 3)
	except:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	try:
		board.takeback(x, y)
		return 0
	except:
		return 2

#################### only need to modify brain turn here #####################
def brain_turn():
	try:
		if pp.terminateAI:
			return
		i = 0
		while True:
			# tick = time.time()
			agent = MinimaxAgent(board)
			x, y = agent.alpha_beta_search()
			# logDebug("{} nodes visited in {:.3f}s".format(agent.node_count, time.time() - tick))
			i += 1
			if pp.terminateAI:
				return
			if board.is_free(x,y):
				break
		if i > 1:
			pp.pipeOut("DEBUG {} coordinates didn't hit an empty field".format(i))
		pp.do_mymove(x, y)
	except:
		logTraceBack()

def brain_end():
	pass

#################### only need to modify brain end here ######################

def brain_about():
	pp.pipeOut(pp.infotext)

if DEBUG_EVAL:
	import win32gui
	def brain_eval(x, y):
		# TODO check if it works as expected
		wnd = win32gui.GetForegroundWindow()
		dc = win32gui.GetDC(wnd)
		rc = win32gui.GetClientRect(wnd)
		c = str(board[x, y])
		win32gui.ExtTextOut(dc, rc[2]-15, 3, 0, None, c, ())
		win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################

# define a file for logging ...
DEBUG_LOGFILE = "E:/AI_final_project/pbrain-pyrandom.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise


######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
	pp.brain_eval = brain_eval

def main():
	pp.main()

if __name__ == "__main__":
	try:
		main()
	except:
		logTraceBack()
