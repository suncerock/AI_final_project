"""
The code mainly refers to the open source code in https://github.com/lihongxun945/gobang
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
		self.height = height
		self.width = width

		self.last_player = None
		self.chess1 = []
		self.chess2 = []
		self.score1 = [[0 for i in range(height)] for j in range(width)]
		self.score2 = [[0 for i in range(height)] for j in range(width)]
		for j in range(width):
			for i in range(height):
				if i == 0 and j == 0 or i == self.height and j == 0 or i == 0 and j == self.width or i == self.height and j == self.width:
					self.score1[j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"]
					self.score2[j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"]
				elif i == 0 or j == 0 or i == self.height or j == self.width:
					self.score1[j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"] + SHAPE_SCORE["ONE"]
					self.score2[j][i] = 3 * SHAPE_SCORE["BLOCKED_ONE"] + SHAPE_SCORE["ONE"]
				else:
					self.score1[j][i] = 4 * SHAPE_SCORE["ONE"]
					self.score2[j][i] = 4 * SHAPE_SCORE["ONE"]

	def is_free(self, x, y):
		return x >= 0 and y >= 0 and x < self.width and y < self.height and self.board[x][y] == 0

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
		# pp.pipeOut("真男人永不悔棋！")
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
			return [(self.width // 2, self.height // 2)]

		last_x, last_y = self.chess1[-1] if self.last_player == 1 else self.chess2[-1]
		for x in range(0, self.width):
			for y in range(0, self.height):
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
				return fours1 + two_blocked_fours1 + blocked_fours2 + blocked_fours1
			else:
				return fours1 + two_blocked_fours1
		if self.last_player == 2 and (fours2 or two_blocked_fours2):
			if two_blocked_fours1:
				return fours2 + two_blocked_fours1 + two_blocked_fours2 + blocked_fours1 + blocked_fours2
			if blocked_fours1:
				return fours2 + two_blocked_fours2 + blocked_fours1 + blocked_fours2
			else:
				return fours2 + two_blocked_fours2

		
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
			if j >= self.height or self.board[x][j] == opponent_color:
				block += 1
				break
			if self.board[x][j] == 0:
				if empty == -1 and j < self.height - 1 and self.board[x][j + 1] == color:
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
			if i >= self.width or self.board[i][y] == opponent_color:
				block += 1
				break
			if self.board[i][y] == 0:
				if empty == -1 and i < self.width - 1 and self.board[i + 1][y] == color:
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
			if x + i >= self.width or y + i >= self.height or self.board[x + i][y + i] == opponent_color:
				block += 1
				break
			if self.board[x + i][y + i] == 0:
				if empty == -1 and x + i < self.width - 1 and y + i < self.height - 1 and self.board[x + i + 1][y + i + 1] == color:
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
			if x + i >= self.width or y - i < 0 or self.board[x + i][y - i] == opponent_color:
				block += 1
				break
			if self.board[x + i][y - i] == 0:
				if empty == -1 and x + i < self.width - 1 and y - i > 0 and self.board[x + i + 1][y - i - 1] == color:
					empty = count
					continue
				else:
					break
			if self.board[x + i][y - i] == color:
				count += 1
		for i in range(1, radius + 1):
			if x - i < 0 or y + i >= self.height or self.board[x - i][y + i] == opponent_color:
				block += 1
				break
			if self.board[x - i][y + i] == 0:
				if empty == -1 and x - i > 0 and y + i < self.height - 1 and self.board[x - i - 1][y + i + 1] == color:
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

	def get_utility(self):
		score = 0
		for chess in self.chess1:
			score += self.score1[chess[0]][chess[1]]
		for chess in self.chess2:
			score -= self.score2[chess[0]][chess[1]]
		return score

	def _has_neighbor(self, x, y, distance, count):
		for i in range(x - distance, x + distance + 1):
			if i < 0 or i >= self.width:
				continue
			for j in range(y - distance, y + distance + 1):
				if j < 0 or j >= self.height:
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