"""
Gomoku for DATA130008 2021 Fall
Midterm2: Monte Carlo Tree Search
Author: Yiwei Ding (18307110009)
The code is mainly based on pbrain-pyrandom by Jan Stransky (https://github.com/stranskyjan/pbrain-pyrandom)
The utility function and the get action function 
	refers to the open source code in https://github.com/lihongxun945/gobang
"""

import time

from gomoku import GomokuState
from mcts import *
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG

pp.infotext = \
	"""
	name = Monte Carlo Tree Search
	author = Jan Stransky, Yiwei Ding
	"""

MAX_BOARD = 50
board = GomokuState(20, 20)
def brain_init():
	# global board
	board = GomokuState(pp.width, pp.height)
	if pp.width < 5 or pp.height < 5:
		pp.pipeOut("ERROR size of the board")
		return
	if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
		pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
		return
	pp.pipeOut("OK")

def brain_restart():
	del board
	board = GomokuState(pp.width, pp.height)
	for i in range(pp.width):
		for j in range(pp.height):
			board.board[i][j] = 0
	pp.pipeOut("OK")

def brain_my(x, y):
	try:
		logDebug("Moving {}, {}".format(x, y))
		board = board.make_move((x, y))
		logDebug("Moved {}, {}".format(x, y))
	except:
		pp.pipeOut("ERROR my move [{},{}]".format(x, y))

def brain_opponents(x, y):
	try:
		board = board.make_move((x, y))
	except:
		pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))

def brain_block(x, y):
	try:
		board.make_move((x, y))
	except:
		pp.pipeOut("ERROR winning move [{},{}]".format(x, y))

def brain_takeback(x, y):
	try:
		board.takeback((x, y))
		return 0
	except:
		return 2

#################### only need to modify brain turn here #####################
def brain_turn():
	try:
		if pp.terminateAI:
			return

		root = MCTSNode(board)
		x, y = mcts(root)

		if pp.terminateAI:
			return

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