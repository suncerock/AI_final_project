import numpy as np

from state import TwoPlayerGameState


class TicTacToeGameState(TwoPlayerGameState):

	x = 1
	o = -1

	def __init__(self, state, next_player=1):
		self.board = state
		self.board_size = state.shape[0]
		self._next_player = next_player

	@property
	def last_player(self):
		return -1 * self._next_player

	@property
	def next_player(self):
		return self._next_player

	@property
	def game_result(self):
		# check if game is over
		rowsum = np.sum(self.board, 0)
		colsum = np.sum(self.board, 1)
		diag_sum_tl = self.board.trace()
		diag_sum_tr = self.board[::-1].trace()

		player_one_wins = any(rowsum == self.board_size)
		player_one_wins += any(colsum == self.board_size)
		player_one_wins += (diag_sum_tl == self.board_size)
		player_one_wins += (diag_sum_tr == self.board_size)

		if player_one_wins:
			return self.x

		player_two_wins = any(rowsum == -self.board_size)
		player_two_wins += any(colsum == -self.board_size)
		player_two_wins += (diag_sum_tl == -self.board_size)
		player_two_wins += (diag_sum_tr == -self.board_size)

		if player_two_wins:
			return self.o

		if np.all(self.board != 0):
			return 0.

		# if not over - no result
		return None

	def is_game_over(self):
		return self.game_result is not None

	def is_move_legal(self, move):
		x_coordinate, y_coordinate, value = move

		# check if inside the board on x-axis
		x_in_range = (0 <= x_coordinate < self.board_size)
		if not x_in_range:
			return False

        # check if inside the board on y-axis
		y_in_range = (0 <= y_coordinate < self.board_size)
		if not y_in_range:
			return False

		# finally check if board field not occupied yet
		return self.board[x_coordinate, y_coordinate] == 0

	def make_move(self, move, inplace=False):
		x_coordinate, y_coordinate, value = move
		if not self.is_move_legal(move):
			raise ValueError(
				"move {0} on board {1} is not legal". format(move, self.board)
			)
		new_board = np.copy(self.board)
		new_board[x_coordinate, y_coordinate] = value
		if self.next_player == TicTacToeGameState.x:
			next_player = TicTacToeGameState.o
		else:
			next_player = TicTacToeGameState.x

		return TicTacToeGameState(new_board, next_player)

	def get_actions(self):
		indices = np.where(self.board == 0)
		return [
			(coords[0], coords[1], self.next_player)
			for coords in list(zip(indices[0], indices[1]))
		]


if __name__ == '__main__':
	state = np.zeros((3, 3))
	initial_board_state = TicTacToeGameState(state = state, next_player=1)

	from mcts import *
	best_node = MCTSNode(initial_board_state)

	for _ in range(36):
		best_node = mcts(best_node, 5000)
		print(best_node.state.board)
		if best_node.state.is_game_over():
			print("Winner: ", best_node.state.game_result)
			break