SHELL = /bin/sh

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')

all: part_1_answer.txt part_2_answer.txt wet_input_visualisation.dot dry_input_visualisation.dot wet_input_visualisation.svg dry_input_visualisation.svg

.SUFFIXES:

check: a_long_walk.py
	python3 -m doctest -v a_long_walk.py

clean:
	rm -f part_1_answer.txt part_2_answer.txt

clobber: clean
	rm -f input.txt input.txt.gpg

input.txt:
	curl -b 'session=$(SESSION_COOKIE_VALUE)' -o $@ 'https://adventofcode.com/2023/day/23/input'

input.txt.gpg: input.txt
	gpg --encrypt --default-recipient-self --output $@ --throw-keyids $<

part_1_answer.txt: a_long_walk.py input.txt
	python3 a_long_walk.py 1 input.txt >$@

part_2_answer.txt: a_long_walk.py input.txt
	python3 a_long_walk.py 2 input.txt >$@

wet_input_visualisation.dot: a_long_walk.py input.txt
	python3 a_long_walk.py --visualise 1 input.txt >$@

dry_input_visualisation.dot: a_long_walk.py input.txt
	python3 a_long_walk.py --visualise 2 input.txt >$@

wet_input_visualisation.svg: wet_input_visualisation.dot
	dot -Tsvg -o $@ $<

dry_input_visualisation.svg: dry_input_visualisation.dot
	dot -Tsvg -o $@ $<

.PHONY: all check clean clobber
