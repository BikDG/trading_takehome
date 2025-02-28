#!/bin/bash

python -m venv .venv
. .venv/bin/activate && pip install -r scripts/requirements.txt
