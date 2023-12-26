SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt input_visualisation.dot input_visualisation.svg

.SUFFIXES:

clean:
	rm -f part_1_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/25/input'

part_1_answer.txt: input_visualisation.svg laziness.py
	sed -E -n 's/^<text text-anchor="middle" x="([0-9]+)".+$$/\1/p' input_visualisation.svg | sort -n | python3 laziness.py >$@

input_visualisation.dot: input_to_visualisation.sed input.txt
	sed -E -f input_to_visualisation.sed input.txt >$@

input_visualisation.svg: input_visualisation.dot
	dot -Tsvg -o $@ $<

.PHONY: all check clean clobber
