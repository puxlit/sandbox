SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt input_visualisation.dot input_visualisation.svg

.SUFFIXES:

check: pulse_propagation.py
	python3 -m doctest -v pulse_propagation.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/20/input'

part_1_answer.txt: pulse_propagation.py input.txt
	python3 pulse_propagation.py 1 input.txt >$@

part_2_answer.txt: pulse_propagation.py input.txt
	python3 pulse_propagation.py 2 input.txt >$@

input_visualisation.dot: input_to_visualisation.sed input.txt
	sed -E -f input_to_visualisation.sed input.txt >$@

input_visualisation.svg: input_visualisation.dot
	dot -Tsvg -o $@ $<

.PHONY: all check clean clobber
