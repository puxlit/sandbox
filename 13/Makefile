SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: point_of_incidence.py
	python3 -m doctest -v point_of_incidence.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/13/input'

part_1_answer.txt: point_of_incidence.py input.txt
	python3 point_of_incidence.py 1 input.txt >$@

part_2_answer.txt: point_of_incidence.py input.txt
	python3 point_of_incidence.py 2 input.txt >$@

.PHONY: all check clean clobber
