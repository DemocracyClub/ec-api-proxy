# EC API


## Install requirements

* Python 3.12
* Pipenv (`pip install Pipenv`)

## Installation

This section assumes a working python 3.12 environment with Pipenv installed.

* `cp ec_api/settings/local.py.example ec_api/settings/local.py`
* Install Python dependencies:
    * `pipenv install --dev`
    * `pip install -r api_endpoints/v1_postcode_lookup/requirements.txt`
* Run the test suite: `pytest`
* Run lint checks: `ruff .`
* Auto-format: `ruff format .`

## Run application

- Frontend: `./manage.py runserver`
- API: `pipenv run start`

## Pre-commit

Using a pre-commit hook is suggested when working on this project to catch
code standard issues before committing them.

Install the hooks with:

`pre-commit install`


[![codecov](https://codecov.io/gh/DemocracyClub/ec-api-proxy/branch/hotfix/dependency-upgrades/graph/badge.svg?token=M9VDGSYISQ)](https://codecov.io/gh/DemocracyClub/ec-api-proxy)
