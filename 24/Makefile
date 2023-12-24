SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: never_tell_me_the_odds.py
	python3 -m doctest -v never_tell_me_the_odds.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/24/input'

part_1_answer.txt: never_tell_me_the_odds.py input.txt
	python3 never_tell_me_the_odds.py 1 input.txt >$@

part_2_answer.txt: never_tell_me_the_odds.py input.txt
	python3 never_tell_me_the_odds.py 2 input.txt >$@

.PHONY: all check clean clobber
