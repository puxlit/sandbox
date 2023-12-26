SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt input_visualisation.dot input_visualisation.svg

.SUFFIXES:

check: snowverload.py
	python3 -m doctest -v snowverload.py

clean:
	rm -f part_1_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/25/input'

part_1_answer.txt: snowverload.py input.txt
	python3 snowverload.py 1 input.txt >$@

input_visualisation.dot: input_to_visualisation.sed input.txt
	sed -E -f input_to_visualisation.sed input.txt >$@

input_visualisation.svg: input_visualisation.dot
	dot -Tsvg -o $@ $<

.PHONY: all check clean clobber
