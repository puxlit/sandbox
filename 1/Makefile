SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt

.SUFFIXES:

check: trebuchet.py
	python3 -m doctest -v trebuchet.py

clean:
	rm -f part_1_answer.txt part_1_input.txt

part_1_answer.txt: trebuchet.py part_1_input.txt
	python3 trebuchet.py part_1_input.txt >$@

part_1_input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/1/input'

.PHONY: all check clean
