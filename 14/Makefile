SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: parabolic_reflector_dish.py
	python3 -m doctest -v parabolic_reflector_dish.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/14/input'

part_1_answer.txt: parabolic_reflector_dish.py input.txt
	python3 parabolic_reflector_dish.py 1 input.txt >$@

part_2_answer.txt: parabolic_reflector_dish.py input.txt
	python3 parabolic_reflector_dish.py 2 input.txt >$@

.PHONY: all check clean clobber
