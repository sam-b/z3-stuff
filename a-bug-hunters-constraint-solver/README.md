By Sam Brown ([@\_samdb_](https://twitter.com/_samdb_))

All the code for this post can be found at: [https://github.com/sam-b/z3-stuff/tree/master/a-bug-hunters-constraint-solver](https://github.com/sam-b/z3-stuff/tree/master/a-bug-hunters-constraint-solver)

While reading [A Bug Hunters Diary](https://www.nostarch.com/bughunter) the other day I came across a problem the author had in chapter 7 (investigating an XNU kernel bug), the author could control some data which was then used in as the address passed to a call instruction. The data went through some basic transforms before it was used as an address, so in order to get it to be an address which the author/attacker controlled they wrote a simple script which brute forced the value they should place in that location as shown below.

<pre>
#include &lt;stdio.h>

#define MEMLOC 0x0041bda0
#define SEARCH_START 0x80000000
#define SEARCH_END 0xffffffff

int main(void) {

	unsigned int a,b = 0;

	for(a = SEARCH_START; a < SEARCH_END; a++ ){
		b = (a << 5) + 0x456860;
		if(b == MEMLOC){
			printf("Value: %08x\n", a);
			return 0;
		}
	}

	printf("No valid value found.\n");
	return 1;
}
</pre>

This seemed like a perfect opportunity to make use of an SMT solver (see: [https://doar-e.github.io/presentations/securityday2015/SecDay-Lille-2015-Axel-0vercl0k-Souchet.html#/](https://doar-e.github.io/presentations/securityday2015/SecDay-Lille-2015-Axel-0vercl0k-Souchet.html#/) for what is pretty much the best intro I've found), SMT solvers allow us to express 'symbolic' variables and constraints on their values. Then if its possible to find any values which satisfy the constraints, it allows us to access a model which includes possible values which satisfy them - while this particular problem is a trivial example, it is a nice short and simple opportunity to illustrate how to make use of a pretty opaque tool. 

In this case I chose to use the [Z3](https://github.com/Z3Prover/z3) constraint solver/SAT solver from Microsoft, which is open source and has great python bindings. My solution is shown below:

<pre>
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
</pre>

Obviously we could just do the math but that's far less interesting and as you can see below rewriting the brute forcer using z3 saves us a valuable 0.4 seconds :D

![runtime comparison](https://raw.githubusercontent.com/sam-b/z3-stuff/master/a-bug-hunters-constraint-solver/a_bug_hunters_screenshot.PNG)