all: build-front

.PHONY:
changelog:
	git-chglog --next-tag "Unreleased" --output CHANGELOG.md
