SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: cubes.py
	python3 -m doctest -v cubes.py

clean:
	rm -f input.txt part_1_answer.txt part_2_answer.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/2/input'

part_1_answer.txt: cubes.py input.txt
	python3 cubes.py 1 input.txt >$@

part_2_answer.txt: cubes.py input.txt
	python3 cubes.py 2 input.txt >$@

.PHONY: all check clean
