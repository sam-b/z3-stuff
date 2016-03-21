from z3 import *
import z3
import sys

polynomial = 0xEDB88320

def crc32(data,size,prev=0):
	crc = prev ^ 0xFFFFFFFF
	for i in range(0,size,8):
		crc = crc ^ (z3.LShR(data,i) & 0xFF)
		for _ in range(8):
			crc = If(crc & 1 == BitVecVal(1, size), z3.LShR(crc,1) ^ polynomial, z3.LShR(crc,1))
	return crc ^ 0xFFFFFFFF



if __name__ == "__main__":
	if len(sys.argv) < 3 :
		print "Usage: crc.py target_crc input_length_in_bytes"
	print "Target: " + sys.argv[1]
	print "length in bytes: " + sys.argv[2]
	size = int(sys.argv[2]) * 8
	target = int(sys.argv[1],16)
	s = z3.Solver()
	data = z3.BitVec('data',size)
	s.add(crc32(data,size) == target)
	if s.check() == z3.sat:
		print hex(int(str(s.model()[data])))
	else:
		print "unsat :("

