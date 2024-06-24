#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void print_binary_digits(int value, int width) {
  // Shh... ignore the bugs here, it doesn't matter...
  for (int mask = 1 << (width - 1); mask > 0; mask >>= 1) {
    putchar(value & mask ? '1' : '0');
  }
}

int main(int argc, char **argv) {
  time_t start_timestamp = time(NULL);
  printf("t = %lu\n", start_timestamp);

  int PASSCODE_LENGTH = 6;
  int BITMASK = (1 << PASSCODE_LENGTH) - 1;
  int NUM_PHASES = 10;

  int passcode;

  int i = -5;
  while (1) {
    unsigned int seed = start_timestamp + i;
    srand(seed);
    passcode = random() & BITMASK;
    printf("For phase 1, trying seed = %u (t%+d)... does the passcode [", seed, i);
    print_binary_digits(passcode, PASSCODE_LENGTH);
    printf("] work? (y/n) ");

    char response;
    scanf(" %c", &response);
    if (response == 'y') break;

    i++;
  }

  for (i = 2; i <= NUM_PHASES; i++) {
    passcode = random() & BITMASK;
    printf("For phase %d, the passcode should be [", i);
    print_binary_digits(passcode, PASSCODE_LENGTH);
    printf("].\n");
  }

  return 0;
}
