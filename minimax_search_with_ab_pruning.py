"""
Gomoku for DATA130008 2021 Fall
Midterm1: Minimax with Alpha-Beta Pruning

Author: Yiwei Ding (18307110009)

The code is mainly based on pbrain-pyrandom by Jan Stransky (https://github.com/stranskyjan/pbrain-pyrandom)
The implementation of Alpha-Beta Pruning refers to the code by Ruipu Luo and Qingwen Liu (elearning, lab 2 template)
The utility function refers to the open source code in https://github.com/colingogogo/gobang_AI/blob/master/gobang_AI.py
"""

############ The code below are my implementation of the algorithm ###########
from copy import deepcopy
import time

class MinimaxAgent(object):
	def __init__(self, pp, board, max_depth=5):
		self.width = pp.width
		self.height = pp.height
		self.board = board
		self.max_depth = max_depth
		self.node_count = 0

	def max_value(self, board, alpha, beta, depth, order='NearLast', last_action=None):
		if depth >= self.max_depth:
			return board.get_utility(self.width, self.height, color=1, last_action=last_action), None
		v = float("-inf")
		for a in board.get_actions(self.width, self.height, order=order, last_action=last_action):
			new_board = deepcopy(board)
			new_board[a[0]][a[1]] = 1
			self.node_count += 1
			move_v, move_action = self.min_value(new_board, alpha, beta, depth+1, order=order, last_action=a)
			if move_v > v:
				v = move_v
				action = a
			if v >= beta:
				return v, action
			alpha = max(alpha, v)
		return v, action

	def min_value(self, board, alpha, beta, depth, order='NearLast', last_action=None):
		if depth >= self.max_depth:
			return board.get_utility(self.width, self.height, color=1, last_action=last_action), None
		v = float("inf")
		for a in board.get_actions(self.width, self.height, order=order, last_action=last_action):
			new_board = deepcopy(board)
			new_board[a[0]][a[1]] = 2
			self.node_count += 1
			move_v, move_action = self.max_value(new_board, alpha, beta, depth+1, order=order, last_action=a)
			if move_v < v:
				v = move_v
				action = a
			if v <= alpha:
				return v, action
			beta = min(beta, v)
		return v, action

	def alpha_beta_search(self):
		v, action = self.max_value(self.board, float("-inf"), float("inf"), depth=0)
		# logDebug(str(action))
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

MAX_BOARD = 100

class Board(object):
	def __init__(self):
		self.board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]

	def __getitem__(self, index):
		return self.board[index]

	def __repr__(self):
		s = "\t".join([" "] + [str(i) for i in range(MAX_BOARD)]) + "\n"
		for i in range(len(self.board)):
			s += "{}\t".format(i) +"\t".join([str(j) for j in self.board[i]]) + "\n"
		return s

	def get_actions(self, width, height, order='NearLast', last_action=None):
		actions = []
		if order == 'NearLast':
			if last_action is None:
				last_action = width // 2, height // 2
				for x in range(width):
					for y in range(height):
						if self.board[x][y] != 0:
							last_action = x, y				

			for x in range(width):
				for y in range(height):
					if self.board[x][y] == 0:
						actions.append(((x - last_action[0]) ** 2 + (y - last_action[1]) ** 2, (x, y)))
			return [x[1] for x in sorted(actions)]

		else:
			for x in range(width):
				for y in range(height):
					if self.board[x][y] == 0:
						actions.append((x, y))
			return actions

	def get_utility(self, width, height, color, last_action):
		tick = time.time()
		opponent_color = 1 if color == 2 else 2
		my_chess = []
		opponent_chess = []
		my_board = [[0 for i in range(width)] for j in range(height)]
		opponent_board = [[0 for i in range(width)] for j in range(height)]

		for i in range(width):
			for j in range(height):
				if self.board[i][j] == color:
					my_chess.append((i, j))
					my_board[i][j] = 1
				if self.board[i][j] == opponent_color:
					opponent_chess.append((i, j))
					opponent_board[i][j] = 1

		from collections import defaultdict
		shape_score = defaultdict(int)
		shape_score[(0, 1, 1, 0, 0)] = 50
		shape_score[(0, 0, 1, 1, 0)] = 50
		shape_score[(1, 1, 0, 1, 0)] = 200
		shape_score[(0, 0, 1, 1, 1)] = 500
		shape_score[(1, 1, 1, 0, 0)] = 500
		shape_score[(0, 1, 1, 1, 0)] = 5000
		shape_score[(0, 1, 0, 1, 1, 0)] = 5000
		shape_score[(0, 1, 1, 0, 1, 0)] = 5000
		shape_score[(1, 1, 1, 0, 1)] = 5000
		shape_score[(1, 1, 0, 1, 1)] = 5000
		shape_score[(1, 0, 1, 1, 1)] = 5000
		shape_score[(1, 1, 1, 1, 0)] = 5000
		shape_score[(0, 1, 1, 1, 1)] = 5000
		shape_score[(0, 1, 1, 1, 1, 0)] = 500000
		shape_score[(1, 1, 1, 1, 1)] = float("inf")

		def cal_score(pos_x, pos_y, dir_x, dir_y, score_all_arr, whose_board):
			add_score = 0
			max_score_shape = (0, None)
			for item in score_all_arr:
				for pt in item[1]:
					if pos_x == pt[0] and pos_y == pt[1] and dir_x == item[2][0] and dir_y == item[2][1]:
						return 0

			for offset in range(-5, 1):
				try:
					pos = [whose_board[pos_x + (i + offset) * dir_x][pos_y + (i + offset) * dir_y] for i in range(6)]
				except:
					continue
				tmp5 = tuple(pos[:5])
				tmp6 = tuple(pos[:6])

				if shape_score[tmp5] > max_score_shape[0] or shape_score[tmp6] > max_score_shape[0]:
					max_score_shape = (max(shape_score[tmp5], shape_score[tmp6]),
										  ((pos_x + (i + offset) * dir_x, pos_y + (i + offset) * dir_y) for i in range(5)),
										  (dir_x, dir_y))
			
			if max_score_shape[1] is not None:
				for item in score_all_arr:
					for pt1 in item[1]:
						for pt2 in max_score_shape[1]:
							if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
								add_score += item[0] + max_score_shape[0]

				score_all_arr.append(max_score_shape)
			return add_score + max_score_shape[0]

		score_all_arr = []
		my_score = 0
		for x, y in my_chess:
			my_score += cal_score(x, y, 0, 1, score_all_arr, whose_board=my_board)
			my_score += cal_score(x, y, 1, 0, score_all_arr, whose_board=my_board)
			my_score += cal_score(x, y, 1, 1, score_all_arr, whose_board=my_board)
			my_score += cal_score(x, y, -1, 1, score_all_arr, whose_board=my_board)

		score_all_arr_enemy = []
		enemy_score = 0
		for x, y in opponent_chess:
			enemy_score += cal_score(x, y, 0, 1, score_all_arr_enemy, whose_board=opponent_board)
			enemy_score += cal_score(x, y, 1, 0, score_all_arr_enemy, whose_board=opponent_board)
			enemy_score += cal_score(x, y, 1, 1, score_all_arr_enemy, whose_board=opponent_board)
			enemy_score += cal_score(x, y, -1, 1, score_all_arr_enemy, whose_board=opponent_board)
		# logDebug("Utility function calculated in {:.3f}s".format(time.time() - tick))
		return my_score - enemy_score * 0.1

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
	for x in range(pp.width):
		for y in range(pp.height):
			board[x][y] = 0
	pp.pipeOut("OK")

def isFree(x, y):
	return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0

def brain_my(x, y):
	if isFree(x,y):
		board[x][y] = 1
	else:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	if isFree(x,y):
		board[x][y] = 2
	else:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	if isFree(x,y):
		board[x][y] = 3
	else:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
		board[x][y] = 0
		return 0
	return 2

#################### only need to modify brain turn here #####################
def brain_turn():
	try:
		if pp.terminateAI:
			return
		i = 0
		while True:
			tick = time.time()
			agent = MinimaxAgent(pp, board, max_depth=1)
			x, y = agent.alpha_beta_search()
			# logDebug("{} nodes visited in {:.3f}s".format(agent.node_count, time.time() - tick))
			i += 1
			if pp.terminateAI:
				return
			if isFree(x,y):
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
		c = str(board[x][y])
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

# # use logDebug wherever
# # use try-except (with logTraceBack in except branch) to get exception info
# # an example of problematic function
# def brain_turn():
# 	logDebug("some message 1")
# 	try:
# 		logDebug("some message 2")
# 		logDebug("some message 3") # not logged, as it is after error
# 	except:
# 		logTraceBack()

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
