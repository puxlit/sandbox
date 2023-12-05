SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt

.SUFFIXES:

check: if_you_give_a_seed_a_fertilizer.py
	python3 -m doctest -v if_you_give_a_seed_a_fertilizer.py

clean:
	rm -f part_1_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/5/input'

part_1_answer.txt: if_you_give_a_seed_a_fertilizer.py input.txt
	python3 if_you_give_a_seed_a_fertilizer.py 1 input.txt >$@

.PHONY: all check clean clobber
