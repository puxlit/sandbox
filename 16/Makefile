SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: the_floor_will_be_lava.py
	python3 -m doctest -v the_floor_will_be_lava.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/16/input'

part_1_answer.txt: the_floor_will_be_lava.py input.txt
	python3 the_floor_will_be_lava.py 1 input.txt >$@

part_2_answer.txt: the_floor_will_be_lava.py input.txt
	python3 the_floor_will_be_lava.py 2 input.txt >$@

.PHONY: all check clean clobber
