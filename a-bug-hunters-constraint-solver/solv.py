from z3 import *
import sys

if __name__ == "__main__":
	target = int(sys.argv[1],16)
	x = BitVec('x', 32)
	s = Solver()
	s.add(target == (x << 5) + 0x456860)
	s.add(x > 0x80000000, x < 0xffffffff)
	if s.check():
		print hex(int(str(s.model()[x])))
	else:
		print "unsat :("