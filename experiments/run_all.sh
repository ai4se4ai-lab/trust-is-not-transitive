#!/usr/bin/env sh
set -eu
python experiments/run.py
python scripts/process_results.py
python scripts/make_macros.py
