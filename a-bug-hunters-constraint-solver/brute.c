#include <stdio.h>

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