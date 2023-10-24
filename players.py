import random
import time
import pygame
import math
import numpy as np
from copy import deepcopy

class connect4Player(object):
	def __init__(self, position, seed=0):
		self.position = position
		self.opponent = None
		self.seed = seed
		random.seed(seed)

	def play(self, env, move):
		move = [-1]

class human(connect4Player):

	def play(self, env, move):
		move[:] = [int(input('Select next move: '))]
		while True:
			if int(move[0]) >= 0 and int(move[0]) <= 6 and env.topPosition[int(move[0])] >= 0:
				break
			move[:] = [int(input('Index invalid. Select next move: '))]

class human2(connect4Player):

	def play(self, env, move):
		done = False
		while(not done):
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

				if event.type == pygame.MOUSEMOTION:
					pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
					posx = event.pos[0]
					if self.position == 1:
						pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
					else: 
						pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
				pygame.display.update()

				if event.type == pygame.MOUSEBUTTONDOWN:
					posx = event.pos[0]
					col = int(math.floor(posx/SQUARESIZE))
					move[:] = [col]
					done = True

class randomAI(connect4Player):

	def play(self, env, move):
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		move[:] = [random.choice(indices)]

class stupidAI(connect4Player):

	def play(self, env, move):
		possible = env.topPosition >= 0
		indices = []
		for i, p in enumerate(possible):
			if p: indices.append(i)
		if 3 in indices:
			move[:] = [3]
		elif 2 in indices:
			move[:] = [2]
		elif 1 in indices:
			move[:] = [1]
		elif 5 in indices:
			move[:] = [5]
		elif 6 in indices:
			move[:] = [6]
		else:
			move[:] = [0]

class minimaxAI(connect4Player):	
    # python main.py -p1 minimaxAI -p2 stupidAI -limit_players 1,2 -verbose True -seed 0
    # python main.py -p1 human -p2 minimaxAI -limit_players 2 -verbose True -seed 0
	
	def play(self, env, move):	
		env.visualize = True		
		env = deepcopy(env)	
		move_hist = [0]
		move_hist[0] = 3
    
		#Hardcode first move 1 if we are player 1 or 2
		if not np.any(env.board) or np.sum(env.board) == 1:
			move[:] = [3]
			move_hist[0] = 3 
			print("here:", move)
		
		else:
			if self.position == 2: player = 1 
			else: player = 1

			value, move_hist[0] = self.miniMax(env, 3, player, move_hist) 
			print("Value:", value)
			print("Move:", move_hist[0])
			move[:] = [move_hist[0]]
		
  
	def miniMax(self, env, depth, player, move_hist):
		possible = env.topPosition >= 0
  
		p_moves = []
		for i, p in enumerate(possible):
			if p: p_moves.append(i)
		#print(p_moves)
  
		if depth == 0 or env.gameOver(move_hist[0], player):
			return self.evaluation(env.board), None
    
		#print("history", move_hist[0])

		if player == 1:
			best_move = None
			max_val = -math.inf
			for move in p_moves:
				#print("P1")
				result, _ = self.miniMax(self.simulateMove(deepcopy(env), move, player), depth - 1, 2, move_hist)
				if result > max_val:
					max_val = result
					best_move = move
			#print("best move:", best_move)
			return max_val, best_move
    
		if player == 2:
			best_move = None
			min_val = math.inf
			for move in p_moves:
				#print("P2")
				result, _ = self.miniMax(self.simulateMove(deepcopy(env), move, player), depth - 1, 1, move_hist)
				if result < min_val:
					min_val = result
					best_move = move
			#print("best move:", best_move)
			return min_val, best_move
		
  
	def evaluation(self, board):
		value = 0
		board = np.array(board)
		weights = np.array([[0, 1, 2, 3, 2, 1, 0], 
                      		[1, 2, 3, 4, 3, 2, 1], 
                        	[2, 3, 4, 5, 4, 3, 2], 
                         	[3, 4, 5, 6, 5, 4, 3], 
                          	[2, 3, 4, 5, 4, 3, 2], 
                           	[1, 2, 3, 4, 3, 2, 1]])

		#Initial board weights
		board[board == 2] = -1
		temp = board * weights
		value = temp.sum()
  
		#Series checker
		#print(np.count_nonzero(np.diff(board, axis = 1) == 0, axis = 1) + 1)
		for i in range(board.shape[0]):
			for j in range(board.shape[1] - 2):
				if board[i, j] == board[i, j + 1]:
					value += 10 if board[i, j] == 1 else -15
     
		for i in range(board.shape[0] - 2):
			for j in range(board.shape[1]):
				if board[i, j] == board[i + 1, j]:
					value += 10 if board[i, j] == 1 else -15
     
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row + 1, col + 1]:
					value += 20 if board[row, col] == 1 else -30
     
		for row in range(3, board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row - 1, col + 1]:
					value += 20 if board[row, col] == 1 else -30
  
		#Win condition checker, horizontal
		for row in range(board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row, col+1] == board[row, col+2] == board[row, col+3] != 0:
					if board[row, col] == 1:
						value += 1000
					else:
						value -= 1000

		#vertical
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1]):
				if board[row, col] == board[row+1, col] == board[row+2, col] == board[row+3, col] != 0:
					if board[row, col] == 1:
						value += 1000
					else:
						value -= 1000
		#diagonal top-bottom
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row+1, col+1] == board[row+2, col+2] == board[row+3, col+3] != 0:
					if board[row, col] == 1:
						value += 1000
					else:
						value -= 1000
		#diagonal bottom-top
		for row in range(3, board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row-1, col+1] == board[row-2, col+2] == board[row-3, col+3] != 0:
					if board[row, col] == 1:
						value += 1000
					else:
						value -= 1000
		#print("value:", value)
		return value		

	def simulateMove(self, env, move, player):
		#print(player)
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		#print(env.board)
		#print("one:", np.count_nonzero(env.board == 1))
		#print("two:", np.count_nonzero(env.board == 2))
		#print("top:", env.topPosition)
		#print("player:", player)
		#print("Move:", move_hist[0])
		return env


class alphaBetaAI(connect4Player):

	def play(self, env, move):	
		env.visualize = True		
		env = deepcopy(env)	
		move_hist = [0]
		move_hist[0] = 3
    
		#Hardcode first move 1 if we are player 1 or 2
		if not np.any(env.board) or np.sum(env.board) == 1:
			move[:] = [3]
			move_hist[0] = 3 
		
		else:
			if self.position == 2: player = 1 
			else: player = 1

			value, move_hist[0] = self.miniMax(env, 4, -math.inf, math.inf, player, move_hist) 
			move[:] = [move_hist[0]]
		
  
	def miniMax(self, env, depth, alpha, beta, player, move_hist):
		possible = env.topPosition >= 0
  
		p_moves = []
		for i, p in enumerate(possible):
			if p: p_moves.append(i)
		#print(p_moves)
  
		if depth == 0 or env.gameOver(move_hist[0], player):
			return self.evaluation(env.board), None
    
		#print("history", move_hist[0])

		if player == 1:
			best_move = None
			max_val = -math.inf
			for move in p_moves:
				#print("P1")
				result, _ = self.miniMax(self.simulateMove(deepcopy(env), move, player), depth - 1, alpha, beta, 2, move_hist)				
				if result > max_val:
					alpha = max(alpha, result)
					max_val = result
					best_move = move
				if beta <= alpha:
					break
			#print("best move:", best_move)
			return max_val, best_move
    
		if player == 2:
			best_move = None
			min_val = math.inf
			for move in p_moves:
				#print("P2")
				result, _ = self.miniMax(self.simulateMove(deepcopy(env), move, player), depth - 1, alpha, beta, 1, move_hist)				
				if result < min_val:
					beta = min(beta, result)
					min_val = result
					best_move = move
				if beta <= alpha:
					break
			#print("best move:", best_move)
			return min_val, best_move
		
  
	def evaluation(self, board):
		value = 0
		board = np.array(board)
		weights = np.array([[0, 1, 2, 3, 2, 1, 0], 
                      		[1, 2, 3, 4, 3, 2, 1], 
                        	[2, 3, 4, 5, 4, 3, 2], 
                         	[3, 4, 5, 6, 5, 4, 3], 
                          	[2, 3, 4, 5, 4, 3, 2], 
                           	[1, 2, 3, 4, 3, 2, 1]])

		#Initial board weights
		board[board == 2] = -1
		temp = board * weights
		value = temp.sum()
  
		#Series checker
		#print(np.count_nonzero(np.diff(board, axis = 1) == 0, axis = 1) + 1)
		for i in range(board.shape[0]):
			for j in range(board.shape[1] - 2):
				if board[i, j] == board[i, j + 1]:
					value += 10 if board[i, j] == 1 else -15
     
		for i in range(board.shape[0] - 2):
			for j in range(board.shape[1]):
				if board[i, j] == board[i + 1, j]:
					value += 10 if board[i, j] == 1 else -15
     
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row + 1, col + 1]:
					value += 20 if board[row, col] == 1 else -30
     
		for row in range(3, board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row - 1, col + 1]:
					value += 20 if board[row, col] == 1 else -30
  
		#Win condition checker, horizontal
		for row in range(board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row, col+1] == board[row, col+2] == board[row, col+3] != 0:
					if board[row, col] == 1:
						value += 100000
					else:
						value -= 100000

		#vertical
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1]):
				if board[row, col] == board[row+1, col] == board[row+2, col] == board[row+3, col] != 0:
					if board[row, col] == 1:
						value += 100000
					else:
						value -= 100000
		#diagonal top-bottom
		for row in range(board.shape[0] - 3):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row+1, col+1] == board[row+2, col+2] == board[row+3, col+3] != 0:
					if board[row, col] == 1:
						value += 100000
					else:
						value -= 100000
		#diagonal bottom-top
		for row in range(3, board.shape[0]):
			for col in range(board.shape[1] - 3):
				if board[row, col] == board[row-1, col+1] == board[row-2, col+2] == board[row-3, col+3] != 0:
					if board[row, col] == 1:
						value += 100000
					else:
						value -= 100000
		return value		

	def simulateMove(self, env, move, player):
		#print(player)
		env.board[env.topPosition[move]][move] = player
		env.topPosition[move] -= 1
		#print(env.board)
		#print("one:", np.count_nonzero(env.board == 1))
		#print("two:", np.count_nonzero(env.board == 2))
		#print("top:", env.topPosition)
		#print("player:", player)
		#print("Move:", move_hist[0])
		return env


SQUARESIZE = 100
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)