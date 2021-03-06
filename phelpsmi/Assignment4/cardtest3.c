#include "assert.h"
#include "dominion.h"
#include <stdio.h>
#include "rngs.h"
#include <stdlib.h>


int main (int argc, char** argv) {
	struct gameState G;
	int seed = 1;
	int result;
  int * bonus;

	printf("testing great_hall\n");
  
  int k[10] = { adventurer, council_room, feast, gardens, mine, remodel, smithy, village, baron, great_hall};

  initializeGame(2, k, seed, &G);

  G.hand[0][0] = great_hall;

  assert(G.handCount[0] == 5);
  assert(G.numActions == 1);

  assert(cardEffect(great_hall, 0, 0, 0, &G, 0, bonus) == 0);

  assert(G.handCount[0] == 5);
  assert(G.numActions == 2);
  assert(G.hand[0][0] != great_hall);


  

  printf("great_hall: PASSED\n");

}