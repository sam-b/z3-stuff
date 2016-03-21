from z3 import *
import sys
from itertools import cycle

#from http://stackoverflow.com/a/22549054
def abs(x):
	return If(x >= 0,x,-x)

if __name__ == "__main__":
	n = int(sys.argv[1])
	columns = [Int('col_%d' % i) for i in range(n)]
	rows = [Int('row_%d' % i) for i in range(n)]
	s = Solver()
	for i in range(n):
		s.add(columns[i] >= 0,columns[i] < n, rows[i] >= 0, rows[i] < n)
	s.add(Distinct(rows))
	s.add(Distinct(columns))
	for i in range(n - 1):
		for j in range(i + 1, n):
			s.add(abs(columns[i] - columns[j]) != abs(rows[i] - rows[j]))

	if s.check() == sat:
		m = s.model()
		colors = cycle(["\033[0;40m  \033[00m","\033[0;47m  \033[00m"])
		print_rows = []
		for i in range(n):
			print_rows.append([colors.next() for _ in xrange(n)])
			if not n % 2: colors.next()
		print_rows = cycle(print_rows)
		print_rows = [print_rows.next() for _ in xrange(n)]
		print_rows = list(reversed(print_rows))
		for x, y in zip(columns, rows):
			print_rows[m[x].as_long()][m[y].as_long()] = 'Q '
		for i in print_rows:
			out = ""
			for j in i:
				out += j
			print out
	else:
		print "unsat :("