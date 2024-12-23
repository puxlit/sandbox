#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TOTAL_DELTA_VALUES 19
#define DELTA_VALUE_TO_INDEX_OFFSET 9
#define TOTAL_DELTA_SEQUENCE_COUNTERS 130321
#define TOTAL_DELTA_SEQUENCES_PER_MONKEY 1997

#define STEP_ONE_BITMASK 0x3ffff
#define STEP_ONE_LEFT_SHIFT 6
#define STEP_TWO_RIGHT_SHIFT 5
#define STEP_THREE_BITMASK 0x1fff
#define STEP_THREE_LEFT_SHIFT 11
#define MAX_SECRET_NUMBER 0xffffff

typedef uint16_t counter_t;
#define MAX_MONKEYS 7281
_Static_assert((MAX_MONKEYS * 9) < (1 << (sizeof(counter_t) * 8)), "MAX_MONKEYS is too big, and might overflow counter_t");
#define DELTA_SEQUENCE_SALES_BYTES (TOTAL_DELTA_SEQUENCE_COUNTERS * sizeof(counter_t))

typedef uint32_t bitfield_word_t;
#define TOTAL_BITFIELD_WORDS 4073
_Static_assert(TOTAL_DELTA_SEQUENCE_COUNTERS <= (TOTAL_BITFIELD_WORDS * sizeof(bitfield_word_t) * 8), "TOTAL_BITFIELD_WORDS is too small, and cannot fit TOTAL_DELTA_SEQUENCE_COUNTERS bits");
#define WITNESSED_DELTA_SEQUENCE_IDS_BYTES (TOTAL_BITFIELD_WORDS * sizeof(bitfield_word_t))

typedef uint_fast32_t secret_t;
_Static_assert(MAX_SECRET_NUMBER < ((uint64_t)(1 << (sizeof(secret_t) * 8))), "secret_t is too small, and cannot store MAX_SECRET_NUMBER");

inline secret_t next_secret_number(secret_t secret_number) {
    secret_t next_secret_number = ((secret_number & STEP_ONE_BITMASK) << STEP_ONE_LEFT_SHIFT) ^ secret_number;
    next_secret_number = (next_secret_number >> STEP_TWO_RIGHT_SHIFT) ^ next_secret_number;
    next_secret_number = ((next_secret_number & STEP_THREE_BITMASK) << STEP_THREE_LEFT_SHIFT) ^ next_secret_number;
    return next_secret_number;
}

int main(int argc, char **argv) {
	if ((argc != 3) || strcmp(argv[1], "2")) {
		fprintf(stderr, "usage: %s 2 [input file]\n", argv[0]);
		return EXIT_FAILURE;
	}

	FILE *input_file = fopen(argv[2], "r");
	if (!input_file) {
		fprintf(stderr, "%s: %s: %s\n", argv[0], argv[2], strerror(errno));
	}

	counter_t max_delta_sequence_sales = 0;
	counter_t *delta_sequence_sales = malloc(DELTA_SEQUENCE_SALES_BYTES);
	assert(delta_sequence_sales);
	memset(delta_sequence_sales, 0, DELTA_SEQUENCE_SALES_BYTES);

	bitfield_word_t *witnessed_delta_sequence_ids = malloc(WITNESSED_DELTA_SEQUENCE_IDS_BYTES);
	assert(witnessed_delta_sequence_ids);

	uint16_t num_monkeys = 0;
	secret_t secret_number;
	int8_t prev_price, price;
	uint32_t delta_i, delta_j, delta_k, delta_l, delta_sequence_id;
	div_t bitfield_offset;
	while (fscanf(input_file, "%u", &secret_number) == 1) {
		assert((num_monkeys++) < MAX_MONKEYS);
		assert(secret_number <= MAX_SECRET_NUMBER);

		memset(witnessed_delta_sequence_ids, 0, WITNESSED_DELTA_SEQUENCE_IDS_BYTES);

		prev_price = secret_number % 10;
		secret_number = next_secret_number(secret_number);
		price = secret_number % 10;
		delta_i = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * TOTAL_DELTA_VALUES * TOTAL_DELTA_VALUES * TOTAL_DELTA_VALUES;
		prev_price = price;

		secret_number = next_secret_number(secret_number);
		price = secret_number % 10;
		delta_j = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * TOTAL_DELTA_VALUES * TOTAL_DELTA_VALUES;
		prev_price = price;

		secret_number = next_secret_number(secret_number);
		price = secret_number % 10;
		delta_k = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET) * TOTAL_DELTA_VALUES;
		prev_price = price;

		for (uint16_t i = 0; i < TOTAL_DELTA_SEQUENCES_PER_MONKEY; ++i) {
			secret_number = next_secret_number(secret_number);
			price = secret_number % 10;
			delta_l = ((price - prev_price) + DELTA_VALUE_TO_INDEX_OFFSET);
			delta_sequence_id = delta_i + delta_j + delta_k + delta_l;
			bitfield_offset = div(delta_sequence_id, sizeof(bitfield_word_t) * 8);

			if (!(witnessed_delta_sequence_ids[bitfield_offset.quot] & (1 << bitfield_offset.rem))) {
				witnessed_delta_sequence_ids[bitfield_offset.quot] |= (1 << bitfield_offset.rem);
				if (price > 0) {
					delta_sequence_sales[delta_sequence_id] += price;
					if (delta_sequence_sales[delta_sequence_id] > max_delta_sequence_sales) {
						max_delta_sequence_sales = delta_sequence_sales[delta_sequence_id];
					}
				}
			}

			prev_price = price;
			delta_i = delta_j * TOTAL_DELTA_VALUES;
			delta_j = delta_k * TOTAL_DELTA_VALUES;
			delta_k = delta_l * TOTAL_DELTA_VALUES;
		}
	}

	printf("%hu\n", max_delta_sequence_sales);
	free(witnessed_delta_sequence_ids);
	free(delta_sequence_sales);
	fclose(input_file);
	return EXIT_SUCCESS;
}
