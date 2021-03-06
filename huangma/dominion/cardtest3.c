#include "assert.h"
#include "dominion.h"
#include <stdio.h>
#include "rngs.h"
#include <stdlib.h>

int main(){
    struct gameState G;
    int k[10] = {adventurer, gardens, embargo, village, minion, mine, cutpurse,
	       sea_hag, tribute, smithy};
    initializeGame(2, k, 1 , &G);
    int r;
    int *p=0;
    printf("testing village\n");
    int hcbefore=G.handCount[whoseTurn(&G)];
    int numactions=G.numActions;
    r=cardEffect(village,1,2,3,&G,2,&p);
    assert(G.handCount[whoseTurn(&G)]==hcbefore);
    assert(G.numActions==numactions+2);
    assert(r==0);
    printf("ALL TESTS PASSED\n");
    return 0;
}
