"""
Gomoku for DATA130008 2021 Fall
Midterm2: Monte Carlo Tree Search
Author: Yiwei Ding (18307110009)
The code is mainly based on pbrain-pyrandom by Jan Stransky (https://github.com/stranskyjan/pbrain-pyrandom)
The utility function and the get action function 
	refers to the open source code in https://github.com/lihongxun945/gobang
"""

import time

from gomoku import *
from mcts import *
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = \
	"""
	name = Monte Carlo Tree Search
	author = Jan Stransky, Yiwei Ding
	"""

MAX_BOARD = 50

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
DEBUG_LOGFILE = "E:/AI_final_project/log.txt"
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
class GameController():
	def __init__(self):
		self.root = None

	def move_or_create(self, x, y):
		if (x, y) in self.root.children:
			self.root = self.root.children[(x, y)]
			self.root.parent = None
		else:
			self.root = AlphaNode(self.root.state.make_move((x, y), inplace=True))

	def brain_init(self):
		self.board = OnlyNeighborGomokuState(pp.width, pp.height)
		self.root = AlphaNode(self.board, p=1)
		if pp.width < 5 or pp.height < 5:
			pp.pipeOut("ERROR size of the board")
			return
		if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
			pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
			return
		pp.pipeOut("OK")

	def brain_restart(self):
		del self.board
		del self.root
		self.board = OnlyNeighborGomokuState(pp.width, pp.height)
		self.root = AlphaNode(self.board)
		pp.pipeOut("OK")

	def brain_my(self, x, y):
		try:
			logDebug("Moving {}, {}".format(x, y))
			self.move_or_create(x, y)
			logDebug("Moved {}, {}".format(x, y))
		except:
			logTraceBack()
			pp.pipeOut("ERROR my move [{},{}]".format(x, y))

	def brain_opponents(self, x, y):
		try:
			self.move_or_create(x, y)
		except:
			logTraceBack()
			pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

	def brain_block(self, x, y):
		try:
			self.move_or_create(x, y)
		except:
			pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

	def brain_takeback(self, x, y):
		try:
			self.move_or_create(x, y)
			return 0
		except:
			return 2

	def brain_turn(self):
		try:
			if pp.terminateAI:
				return

			(x, y), _ = mcts(self.root, 2200)

			if pp.terminateAI:
				return

			pp.do_mymove(x, y)
		except:
			logTraceBack()

	def brain_end(self):
		pass
		
#################################################################

controller = GameController()

# "overwrites" functions in pisqpipe module

pp.brain_init = controller.brain_init
pp.brain_restart = controller.brain_restart
pp.brain_my = controller.brain_my
pp.brain_opponents = controller.brain_opponents
pp.brain_block = controller.brain_block
pp.brain_takeback = controller.brain_takeback
pp.brain_turn = controller.brain_turn
pp.brain_end = controller.brain_end
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