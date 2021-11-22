"""
Author: @suncerock

An implementation of Monte Carlo Tree Search
The code mainly refers to the open-source code in 
	- https://github.com/haroldsultan/MCTS/blob/master/mcts.py
	- https://github.com/int8/monte-carlo-tree-search/blob/master/mctspy/tree/nodes.py
"""


import math
import random
from copy import deepcopy
from collections import defaultdict


class MCTSNode(object):
	def __init__(self, state, parent=None):
		self.state = state
		self.children = []
		self.parent = parent

		self._number_of_visits = 0
		self._results = defaultdict(int)
		self._untried_actions = None

	@property
	def untried_actions(self):
		if self._untried_actions is None:
			self._untried_actions = self.state.get_actions()
		return self._untried_actions

	@property
	def q(self):
		wins = self._results[self.parent.state.next_player]
		loses = self._results[self.parent.state.last_player]
		return wins - loses

	@property
	def n(self):
		return self._number_of_visits

	def expand(self):
		action = self.untried_actions.pop()
		next_state = self.state.make_move(action)
		child_node = MCTSNode(next_state, parent=self)
		self.children.append(child_node)
		return child_node

	def is_terminal_node(self):
		return self.state.is_game_over()

	def rollout(self):
		current_rollout_state = self.state
		while not current_rollout_state.is_game_over():
			possible_moves = current_rollout_state.get_actions()
			action = self.rollout_policy(possible_moves)
			current_rollout_state = current_rollout_state.make_move(action)
		return current_rollout_state.game_result

	def backpropagate(self, result):
		self._number_of_visits += 1
		self._results[result] += 1
		if self.parent:
			self.parent.backpropagate(result)

	def rollout_policy(self, possible_moves):
		# print(possible_moves)
		return possible_moves[random.randint(0, len(possible_moves) - 1)]

	def is_fully_expanded(self):
		return len(self.untried_actions) == 0

	def best_child(self, c=1):
		w = -1
		best_child = None
		for child in self.children:
			s = child.q / child.n + c * math.sqrt(2 * math.log(self.n) / child.n)
			if s > w:
				w = s
				best_child = child
		return best_child


def mcts(tree, simulation=20):
	for _ in range(0, simulation):
		cur = tree
		while not cur.is_terminal_node():
			if cur.is_fully_expanded():
				cur = cur.best_child()
			else:
				cur = cur.expand()
				break

		reward = cur.rollout()
		cur.backpropagate(reward)
	best_child = tree.best_child()
	if best_child.state.last_player == 1:
		return best_child.state.chess1[-1]
	else:
		return best_child.state.chess2[-1]
		