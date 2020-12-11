from pprint import pprint
import random
import pygame
import math
import threading
import sys

class Maze(object):

	def __init__(self, width, height, start, screen):
		global grid
		self.width = width
		self.height = height
		self.start = start
		grid = [[1 for j in range(width)] for i in range(height)]
		grid[1][1] = 0
		self.visited = []

	def get_neighbour(self, x, y):
		return [i for i in [(x-2, y), (x+2, y), (x, y+2), (x, y-2)] if 0<=i[0]<height and 0<=i[1]<width]

	def generate(self, current=None):
		if not current: current = self.start
		self.visited.append(current)
		while len([i for i in self.get_neighbour(*current) if i not in self.visited]) != 0: 
			self.choice = random.choice([i for i in self.get_neighbour(*current) if i not in self.visited])
			grid[current[0]-1 if current[0]-self.choice[0] > 0 else current[0]+1 if current[0]-self.choice[0] < 0 else current[0]][current[1]-1 if current[1]-self.choice[1] > 0 else current[1]+1 if current[1]-self.choice[1] < 0 else current[1]] = 0
			grid[self.choice[0]][self.choice[1]] = 0
			print(grid)
			update()
			self.generate(self.choice)

class Node():
	"""A node class for A* Pathfinding"""

	def __init__(self, parent=None, position=None):
		self.parent = parent
		self.position = position

		self.g = 0
		self.h = 0
		self.f = 0

	def __eq__(self, other):
		return self.position == other.position


def astar(maze, start, end, screen):
	"""Returns a list of tuples as a path from the given start to the given end in the given maze"""

	# Create start and end node
	start_node = Node(None, start)
	start_node.g = start_node.h = start_node.f = 0
	end_node = Node(None, end)
	end_node.g = end_node.h = end_node.f = 0

	# Initialize both open and closed list
	open_list = []
	closed_list = []

	# Add the start node
	open_list.append(start_node)

	# Loop until you find the end
	while len(open_list) > 0:

		# Get the current node
		current_index, current_node = min(enumerate(open_list), key=lambda x: x[1].f)
		# Pop current off open list, add to closed list
		open_list.pop(current_index)
		closed_list.append(current_node)
		pygame.draw.rect(screen, (0, 255, 0), (current_node.position[0]*10, current_node.position[1]*10, 10, 10))
		pygame.display.update()  

		# Found the goal
		if current_node == end_node:
			path = []
			current = current_node
			while current is not None:
				path.append(current.position)
				current = current.parent
			screen.fill((0, 0, 0))
			update()
			for i in path:
				pygame.draw.rect(screen, (255, 0, 0), (i[0]*10, i[1]*10, 10, 10))
			pygame.display.update()
			return path[::-1] # Return reversed path

		# Generate children
		children = []
		for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

			# Get node position
			node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

			# Make sure within range
			if node_position[0] > (len(maze) - 1) or node_position[0] <= 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] <= 0:
				continue

			# Make sure walkable terrain
			if maze[node_position[0]][node_position[1]] != 0:
				continue

			# Create new node
			new_node = Node(current_node, node_position)

			# Append
			children.append(new_node)

		# Loop through children
		for child in children:


			# Child is on the closed list
			if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
				continue
					

			# Create the f, g, and h values
			child.g = current_node.g + 1
			child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
			child.f = child.g + child.h

			pygame.draw.rect(screen, (0, 0, 255), (child.position[0]*10, child.position[1]*10, 10, 10))
			pygame.display.update() 

			# Child is already in the open list
			if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
				continue

			# Add the child to the open list
			open_list.append(child) 

def update():
	for i in range(width):
		for j in range(height):
			if grid[i][j] == 0:
				pygame.draw.rect(screen, (255, 255, 255), (i*10, j*10, 10, 10))
	pygame.display.update()

sys.setrecursionlimit(100000000)
pygame.init()
width, height = 51, 51
screen = pygame.display.set_mode((width*10, height*10))

draw_maze = threading.Thread(target=Maze(width, height, (1, 1), screen).generate)
draw_maze.setDaemon(True)
draw_maze.start()
while threading.active_count() > 1: pygame.display.update()
solve_maze = threading.Thread(target=astar, args=(grid, (1, 1), (49, 49), screen,))
solve_maze.setDaemon(True)
solve_maze.start()

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
