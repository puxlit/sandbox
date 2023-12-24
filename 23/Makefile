SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: a_long_walk.py
	python3 -m doctest -v a_long_walk.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/23/input'

part_1_answer.txt: a_long_walk.py input.txt
	python3 a_long_walk.py 1 input.txt >$@

part_2_answer.txt: a_long_walk.py input.txt
	python3 a_long_walk.py 2 input.txt >$@

.PHONY: all check clean clobber
