# Makefile to simplify common operations

SHELL := /bin/bash

test: src/lambda_function_test.py
	python3 -m pytest -v

upload:
	pushd script &&\
	./upload_lambda.sh &&\
	popd

.PHONY: upload