# EC API


## Install requirements

* Python 3.12
* [uv](https://docs.astral.sh/uv/)

## Installation

This section assumes a working python 3.12 environment with uv installed.

* `cp ec_api/settings/local.py.example ec_api/settings/local.py`
* Install Python dependencies: `uv sync --all-groups --all-packages`
* Run the test suite: `pytest`
* Run lint checks: `ruff .`
* Auto-format: `ruff format .`

## Run application

- `./scripts/startapp.sh`

## Pre-commit

Using a pre-commit hook is suggested when working on this project to catch
code standard issues before committing them.

Install the hooks with:

`pre-commit install`


[![codecov](https://codecov.io/gh/DemocracyClub/ec-api-proxy/branch/hotfix/dependency-upgrades/graph/badge.svg?token=M9VDGSYISQ)](https://codecov.io/gh/DemocracyClub/ec-api-proxy)
