




.PHONY: test, docs


test: 
	@python3 test.py

docs:
	@cd ./docs && make

docs-%:

	@echo $(shell echo $@ | cut -c6-)
	@cd ./docs && make $(shell echo $@ | cut -c6-)
