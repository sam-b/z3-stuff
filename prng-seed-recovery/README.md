I've been playing with Z3 a fair bit recently (bug hunters, hackvent15) and decided to do soemthing atleast semi-useful if not still pretty simple with it. Its common knowledge that the default random number generators provided by msot languages aren't cryptographically secure and most can there future or past state calculated purely by acquiring a few outputs so I decided to try using Z3 to recover the seeds for a few of them. I started off looking at Java's util.random which is a simple Linear Congruential Generator (wikipedia link) and then I moved onto PHPs Mersienne Twister based RNG since this is more complex.

###Java util.random

First off I needed a simple Java program to print out a bunch of random numbers with a known seed for testing - 

<pre>
import java.util.Random;

public class Rand {

	public static void main(String[] args){
		Random rand = new Random();
		rand.setSeed(0x1337);
		for(int i = 0; i < 5; i++){
			System.out.println(rand.nextLong());
		}
	}
}
</pre>

This code just initialises the RNG with a seed of '0x1337' and then prints out the first five 64 bit random numbers it generates as shown:

~~~image~~~

Now since I wanted to use the python z3 bindings I needed to replicate Random() in python - this turned out to be simple as the source of Random() was publically available (http://developer.classpath.org/doc/java/util/Random-source.html), this gave me the following python implementation:

<pre>
import sys

class Rand:
	def __init__(self,seed):
		self.seed = (seed ^ 0x5DEECE66DL) & ((1L << 48) - 1)

	def output_long(self,i):
		for _ in range(i):
			self.next_long()
		return self.next_long()

	def next_long(self):
		return (self.next(32) << 32) + self.next(32)

#protected synchronized int next(int bits)
#   {
#     seed = (seed * 0x5DEECE66DL + 0xBL) & ((1L << 48) - 1);
#     return (int) (seed >>> (48 - bits));
#   }

	def next(self, bits):
		self.seed = (self.seed * 0x5DEECE66DL + 0xBL) & ((1 << 48) - 1)
		out = (self.seed >> (48 - bits)) & 0xFFFFFFFF
		if(out & 0x80000000):
			out = -0x100000000 + out
		return out

if __name__ == "__main__":
	for i in range(5):
		rand = Rand(0x1337)
		print rand.output_long(i)
</pre>

Here the __init__, next and next_long functions are straght foward re-implemtations of the same functions from the link before, the output_long() function was added so that the ith random value could be retrieved easily. Running this code it can be seen to give the same output as the java:

~~~image~~~



###PHP mt_rand()

Once I moved onto php, I again needed a simple sample script that printed out random numbers from the generator:

<pre>
<?php
	mt_srand(0x1337);
	for($i = 0; $i < 5; $i++){
		echo mt_rand();
		echo "\n";
	}
?>
</pre>

Note that the 'mt\_' functions are being used - PHP's standard rand() function also uses an LCG like Java's. The 'mt_rand()' function instead uses a Mersienne Twister based generator which has a much longer period.

The code can be seen running below - 

Now once again I needed to re-implement the RNG in python, luckily this had already been done in the 'snowflake' project. Snowflake is a framework for exploiting randomness issues in PHP applications which includes the ability to bruteforce the seed used in either mt_rand or normal rand. The re-implemented class can be found at [https://github.com/GeorgeArgyros/Snowflake/blob/master/snowflake.py](https://github.com/GeorgeArgyros/Snowflake/blob/master/snowflake.py)

<pre>
import sys

bitMask = 0xffffffff

class MtRand:

    N = 624
    M = 397

    def __init__(self, php = True):
        self.php = php
        self.twist = self.phpTwist if php else self.mtTwist
        self.seeded = False
        self.state = []
        self.next = self.N

    def phpTwist(self, m, u, v):

        """
        The invalid twist operation of the PHP generator
        """
        return (m ^ (((u) & 0x80000000)|((v) & 0x7fffffff))>>1) ^ \
            ((-((u) & 0x00000001)) & 0x9908b0df)

    def mtTwist(self, m, u, v):

        """
        The original mt twist operation
        """
        return (m ^ (((u) & 0x80000000)|((v) & 0x7fffffff))>>1) ^ \
            ((-((v) & 0x00000001)) & 0x9908b0df)

    def mtSrand(self, seed):

        """
        The default seeding procedure from the original MT code
        """

        self.seeded = True
        self.next = self.N
        self.state = [seed & bitMask]
        for i in range(1, self.N):
            s = (1812433253 * (self.state[i-1] ^ (self.state[i-1] >> 30))+ i)
            self.state.append(s & bitMask)

    def setState(self, state):
        """
        Replace existing state with another one and considers the 
        generator initialized
        """
        self.next = self.N
        self.state = state
        self.seeded = True

    def reload(self):
        """
        Generate the next N words of the internal state
        """        
        N = self.N
        M = self.M

        for i in range(N - M):
           self.state[i] = self.twist(self.state[M + i], self.state[i], 
                                       self.state[i+1])
        for i in range(i+1, N-1):
            self.state[i] = self.twist(self.state[i+(M-N)], self.state[i], 
                                       self.state[i+1])
        self.state[N-1] = self.twist(self.state[M-1], self.state[N-1],
                                     self.state[0])
        self.next = 0
        return

    def mtRand(self, min = None, max = None):
        """
        Generate a 32 bit integer
        """

        if not self.seeded:
            self.mtSrand(0xdeadbeef)     

        if self.next == self.N:
            self.reload()

        num = self.state[ self.next ]
        self.next += 1
        

        num = (num ^ (num >> 11))
        num = (num ^ ((num << 7) & 0x9d2c5680))
        num = (num ^ ((num << 15) & 0xefc60000))
        num = (num ^ (num >> 18))

        if not min and not max:
            return num
        return (min + (num*(max - min + 1)) / (1<<32))

    def phpMtRand(self, rmin = None, rmax= None):

        """
        as returned by PHP
        """
        num = self.mtRand() >> 1
        if not rmin and not rmax:
            return num
        return (rmin + (num*(rmax - rmin + 1)) / (1 <<31))

def get_val(seed,num):
    rand = MtRand()
    rand.mtSrand(seed)
    for _ in range(0,num):
        rand.phpMtRand()
    return rand.phpMtRand()

if __name__ == "__main__":
	for i in range(5):
		print get_val(0x1337,i)
</pre>

Once again the 'get_val' function has been added to make getting ith random numbers easier. When ran we can see that this code gives us the same output as the PHP so we can reasonably sure its correct:

~~~image~~~

