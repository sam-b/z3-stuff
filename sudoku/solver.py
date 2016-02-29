from z3 import *
import sys

def solve(puzzle):
	grid = [Int(str(i)) for i in range(81)]
	s = Solver()

	for i in range(len(puzzle)):
		if puzzle[i] != ' ':
			s.add(grid[i] == int(puzzle[i]))

	for i in grid:
		s.add(i >0, i <10)

	for i in range(9):
		across = []
		down = []
		for j in range(9):
			down.append(grid[i+(9*j)])
			across.append(grid[(9*i)+j])
		s.add(Distinct(across))
		s.add(Distinct(down))
	for q in range(3):
		for p in range(3):
			square = []
			for i in range(3):
				for j in range(3):
					index = (q*27) + (p*3) + (i * 9) + j
					square.append(grid[index])
			s.add(Distinct(square))
	if s.check():
		return s.model()
	else:
		return None

def draw(grid):
	tmp = {}
	for i in grid:
		tmp[int(str(i))] = grid[i]
	for i in range(9):
		out = "|"
		for j in range(9):
			out += str(tmp[(9*i)+j]) + "|"
		print out

if __name__ == "__main__":	
	puzzle = "  86      6 5  1   79  4    43    6   69 17   9    24    8  43   2  3 7      95  "
	solution = solve(puzzle)
	draw(solution)