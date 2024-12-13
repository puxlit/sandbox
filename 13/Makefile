SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: claw_contraption.py
	python3 -m doctest -v claw_contraption.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt input.txt.gpg

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2024/day/13/input'

input.txt.gpg: input.txt
	gpg --encrypt --default-recipient-self --output $@ --throw-keyids $<

part_1_answer.txt: claw_contraption.py input.txt
	python3 claw_contraption.py 1 input.txt >$@

part_2_answer.txt: claw_contraption.py input.txt
	python3 claw_contraption.py 2 input.txt >$@

.PHONY: all check clean clobber
