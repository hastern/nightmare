


#include <stdio.h>
#include <assert.h>

int main(int argc, char * argv[]) {

	char * str = "SEGFAULT";

	switch (argv[1][0]) {
		case '1': assert(1==0); break;
		case '2': *str = 'F'; break;
	}

	return 0;
}




