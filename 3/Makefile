SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt

.SUFFIXES:

check: gear_ratios.py
	python3 -m doctest -v gear_ratios.py

clean:
	rm -f input.txt input.txt.gpg part_1_answer.txt

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/3/input'

input.txt.gpg: input.txt
	gpg --encrypt --default-recipient-self --output $@ --throw-keyids $<

part_1_answer.txt: gear_ratios.py input.txt
	python3 gear_ratios.py 1 input.txt >$@

.PHONY: all check clean
