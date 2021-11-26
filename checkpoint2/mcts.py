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
		self.children = {}
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
		self.children[action] = child_node
		return child_node

	def is_terminal_node(self):
		return self.state.is_game_over()

	def rollout(self, max_step=20):
		current_rollout_state = deepcopy(self.state)

		import time
		tick = time.time()
		action_time = 0
		move_time = 0
		for step in range(max_step):
			tick_action = time.time()
			possible_moves = current_rollout_state.get_actions()
			action_time += time.time() - tick_action

			action = self.rollout_policy(possible_moves)
			
			tick_move = time.time()
			current_rollout_state = current_rollout_state.make_move(action, inplace=True)
			move_time += time.time() - tick_move

			if current_rollout_state.is_game_over():
				if current_rollout_state.game_result == self.parent.state.next_player:
					return 1
				elif current_rollout_state.game_result == self.parent.state.last_player:
					return -1
				else:
					return 0

		tock = time.time()
		# print("{} steps in {:.2f}ms! (AVG: {:.2f}ms)".format(steps, (tock - tick) * 1000, (tock - tick) / steps * 1000))
		# print("Action time {:.2f}ms, Move time {:.2f}ms".format(action_time*1000, move_time*1000))
		return self._evaluate_state(current_rollout_state)

	def backpropagate(self, result):
		self._number_of_visits += 1
		self._results[result] += 1
		if self.parent:
			self.parent.backpropagate(result)

	def rollout_policy(self, possible_moves):
		return random.choice(possible_moves)

	def is_fully_expanded(self):
		return len(self.untried_actions) == 0

	def best_child(self, c=1.4):
		s = lambda x:x.q / x.n + c * math.sqrt(2 * math.log(self.n) / x.n)
		best_action = max(self.children, key=lambda action:s(self.children[action]))
		return best_action, self.children[best_action]

	def _evaluate_state(self, state):
		return 0


class AlphaNode(MCTSNode):
	"""
	AlphaGo and AlphaZero Style MCTS Node
	"""
	def __init__(self, state, p, parent=None):
		super(AlphaNode, self).__init__(state=state, parent=parent)
		self._p = p
		self._q = 0
		
	@property
	def p(self):
		return self._p

	@property
	def q(self):
		return self._q

	def expand(self):
		action = self.untried_actions.pop()
		next_state = self.state.make_move(action)
		child_node = AlphaNode(next_state, p=1, parent=self)
		self.children[action] = child_node
		return child_node

	def backpropagate(self, reward):
		self._number_of_visits += 1
		self._q += (reward - self._q) / self._number_of_visits
		if self.parent:
			self.parent.backpropagate(-reward)

	def rollout_policy(self, possible_moves):
		return random.choice(possible_moves)

	def best_child(self, c=1.0):
		s = lambda x: x.q + c * x.p * math.sqrt(self.n) / (1 + x.n)
		best_action = max(self.children, key=lambda action:s(self.children[action]))
		return best_action, self.children[best_action]

	def _evaluate_state(self, state):
		return 0


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
		