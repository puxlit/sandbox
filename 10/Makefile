SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: hoof_it.py
	python3 -m doctest -v hoof_it.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt input.txt.gpg

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2024/day/10/input'

input.txt.gpg: input.txt
	gpg --encrypt --default-recipient-self --output $@ --throw-keyids $<

part_1_answer.txt: hoof_it.py input.txt
	python3 hoof_it.py 1 input.txt >$@

part_2_answer.txt: hoof_it.py input.txt
	python3 hoof_it.py 2 input.txt >$@

.PHONY: all check clean clobber
