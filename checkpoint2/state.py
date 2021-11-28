"""
An abstract base class for any game
"""
from abc import ABC, abstractmethod

class TwoPlayerGameState(ABC):

	@property
	@abstractmethod
	def last_player(self):
		pass

	@property
	@abstractmethod
	def next_player(self):
		pass

	@abstractmethod
	def game_result(self):
		pass

	@abstractmethod
	def get_actions(self):
		pass

	@abstractmethod
	def make_move(self, *args):
		pass

	@abstractmethod
	def is_game_over(self, *args):
		pass