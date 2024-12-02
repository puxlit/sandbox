SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt

.SUFFIXES:

check: red_nosed_reports.py
	python3 -m doctest -v red_nosed_reports.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt input.txt.gpg

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2024/day/2/input'

input.txt.gpg: input.txt
	gpg --encrypt --default-recipient-self --output $@ --throw-keyids $<

part_1_answer.txt: red_nosed_reports.py input.txt
	python3 red_nosed_reports.py 1 input.txt >$@

part_2_answer.txt: red_nosed_reports.py input.txt
	python3 red_nosed_reports.py 2 input.txt >$@

.PHONY: all check clean clobber
