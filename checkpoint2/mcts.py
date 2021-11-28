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
	"""
	Tree node in a MCTS Tree
	Use Alpha Go and Alpha Zero style, i.e., with a prior probability

	Parameters:
		state: the game state, a TwoPlayerGameState instance (see state.py)
		p: the prior probability of its parent node visiting it (default: 1.0)
		parent: the parent node (default: None)

	Usage:
		>>> board = TwoPlayerGameState()
		>>> root = MCTSNode(board, p=1.0, parent=None)
	"""
	def __init__(self, state, p=1, parent=None):
		self.state = state
		self.children = {}
		self.parent = parent

		self._number_of_visits = 0
		self._p = float(p)
		self._q = 0
		self._untried_actions = None

	@property
	def untried_actions(self):
		if self._untried_actions is None:
			self._untried_actions = self.state.get_actions() 
		return self._untried_actions

	@property
	def p(self):
		return self._p

	@property
	def q(self):
		return self._q

	@property
	def n(self):
		return self._number_of_visits

	def expand(self):
		p, action = self.untried_actions.pop()
		next_state = self.state.make_move(action, inplace=False)
		child_node = MCTSNode(next_state, p=p, parent=self)
		self.children[action] = child_node
		return child_node

	def is_terminal_node(self):
		return self.state.is_game_over()

	def rollout(self, max_step=0):
		current_rollout_state = deepcopy(self.state)

		for step in range(max_step):
			possible_moves = current_rollout_state.get_actions()
			_, action = self.rollout_policy(possible_moves)
			current_rollout_state = current_rollout_state.make_move(action, inplace=True)

			if current_rollout_state.is_game_over():
				if current_rollout_state.game_result == self.parent.state.next_player:
					return 1
				elif current_rollout_state.game_result == self.parent.state.last_player:
					return -1
				else:
					return 0

		return self._evaluate_state(current_rollout_state, self.state.next_player)

	def backpropagate(self, reward):
		self._number_of_visits += 1
		self._q += (reward - self._q) / self._number_of_visits  # Moving Average
		if self.parent:
			self.parent.backpropagate(-reward)

	def is_fully_expanded(self):
		return len(self.untried_actions) == 0

	def rollout_policy(self, possible_moves):
		return random.choice(possible_moves)  # A very fast rollout policy

	def best_child(self, c=1.0):
		s = lambda x: x.q + c * x.p * math.sqrt(self.n) / (1 + x.n)
		best_action = max(self.children, key=lambda action:s(self.children[action]))
		return best_action, self.children[best_action]

	def _evaluate_state(self, state, player):
		return state.get_utility(player)


def mcts(tree, simulation=20):
	for _ in range(0, simulation):
		cur = tree
		while not cur.is_terminal_node():
			if cur.is_fully_expanded():
				_, cur = cur.best_child()
			else:
				cur = cur.expand()
				break
		reward = cur.rollout()
		cur.backpropagate(reward)
	best_action = max(tree.children, key=lambda action:tree.children[action].n)
	return best_action, tree.children[best_action]
		