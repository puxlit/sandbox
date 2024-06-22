SHELL := /bin/sh

BASE_URL := https://jellyc.tf
API_BASE_URL := $(BASE_URL)/api/v1

SESSION_COOKIE_VALUE ?= $(shell bash -c 'read -sp "Session cookie value: " SESSION_COOKIE_VALUE; echo $$SESSION_COOKIE_VALUE')
RECIPIENT_USER_ID ?= $(shell bash -c 'read -p "Encrypted resource recipient user ID: " RECIPIENT_USER_ID; echo $$RECIPIENT_USER_ID')

# `$(wildcard)` will return nothing if <resources/challenges.json> doesn't exist, causing `$(and)` to short-circuit.
challenge_ids := $(and $(wildcard resources/challenges.json),$(shell jq --raw-output '.data[].id | select(type == "number")' resources/challenges.json))
challenge_resources := $(challenge_ids:%=resources/challenges/%.json)
resources := \
	resources/challenges.json \
	$(challenge_resources) \
	resources/scoreboard.json \
	resources/scoreboard/top/10.json \
	resources/teams/me/awards.json \
	resources/teams/me/fails.json \
	resources/teams/me/solves.json \
	resources/users/me/awards.json \
	resources/users/me/fails.json \
	resources/users/me/solves.json
encrypted_resources := $(resources:=.gpg)
# Challenge categories match /[a-z]+/, and most challenge names match /[0-9A-Z_a-z]+/, with "you're_based" and "you're_bababased?" as exceptions.
files := $(and $(wildcard $(challenge_resources)),$(shell jq --raw-output '.data | select((.category | test("^[a-z]+$$")) and (.name | test("^['"'"'0-9?A-Z_a-z]+$$"))) | . as {$$category, $$name} | .files[] | match("(?<=^/files/[0-9a-f]{32}/)[.0-9_a-z]+(?=\\?token=[-0-9A-Z_a-z]+\\.[-0-9A-Z_a-z]+\\.[-0-9A-Z_a-z]+$$)").string as $$filename | "challenges/\($$category)/\($$name)/files/\($$filename)"' $(wildcard $(challenge_resources))))

all: all-resources all-files

.SUFFIXES:

all-resources: $(encrypted_resources)

$(resources):
	mkdir -p $(@D)
	curl -b session=$(SESSION_COOKIE_VALUE) -o $@ $(API_BASE_URL)/$(@:resources/%.json=%)

$(encrypted_resources): %.json.gpg: %.json
	gpg --encrypt --hidden-recipient $(RECIPIENT_USER_ID) --output $@ $<

all-files: $(files)

# This rule is technically missing the relevant challenge resource as a prerequisite for each target.
$(files): resources/challenges.json
	mkdir -p "$(@D)"
	challenge_id=$$(jq --raw-output '.data | map(select("\(.category)/\(.name)" == "$(subst ','"'"',$(@:challenges/%/files/$(notdir $@)=%))")) | first | .id' resources/challenges.json) && \
	file_url=$$(jq --raw-output '.data.files | map(select(match("(?<=^/files/[0-9a-f]{32}/)[.0-9_a-z]+(?=\\?token=[-0-9A-Z_a-z]+\\.[-0-9A-Z_a-z]+\\.[-0-9A-Z_a-z]+$$)").string == "$(notdir $@)")) | first' resources/challenges/$${challenge_id}.json) && \
	curl -o "$@" "$(BASE_URL)$${file_url}"

.PHONY: all all-resources all-files
