# EC API


## Install requirements

* Python 3.8
* Pipenv (`pip install Pipenv`)

## Installation

This section assumes a working python 3.8 environment with Pipenv installed.

To install the project requirements:

`pipenv install`

For a developer install (or for running tests):

`pipenv install --dev`

Now create a `local.py` file in `ec_api/settings/`. Copy
`ec_api/settings/local.py.example` to get started.

## Pre-commit

Using a pre-commit hook is suggested when working on this project to catch
code standard issues before committing them.

Install the hooks with:

`pre-commit install`
