'''
The code heavily relies on the implementation by Ruipu Luo and Qingwen Liu (elearning, lab 2 template)
'''

import time
from copy import deepcopy

class MinimaxAgent(object):
	def __init__(self, board, max_depth=4):
		self.board = board
		self.max_depth = max_depth
		self.node_count = 0
		self.copy_time = 0

	def max_value(self, board, alpha, beta, depth):
		if depth >= self.max_depth:
			return board.get_utility(), None
		v = float("-inf")
		for a in board.get_actions():
			tick = time.time()
			new_board = deepcopy(board)
			self.copy_time += time.time() - tick
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
			tick = time.time()
			new_board = deepcopy(board)
			self.copy_time += time.time() - tick
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
		v, action = self.max_value(self.board, float("-inf"), float("inf"), depth=0)
		return action