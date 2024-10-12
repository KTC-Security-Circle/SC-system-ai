#!/bin/bash

poetry config virtualenvs.in-project true
poetry install --no-root
poetry export -f requirements.txt -o requirements.txt --without-hashes