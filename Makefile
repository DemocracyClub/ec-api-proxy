.DEFAULT_GOAL := help

export SECRET_KEY?=badf00d
export DJANGO_SETTINGS_MODULE?=ec_api.settings.base_lambda
export APP_IS_BEHIND_CLOUDFRONT?=False

.PHONY: all
all: clean collectstatic lambda-layers/DependenciesLayer/requirements.txt api_endpoints/api_auth/requirements.txt api_endpoints/v1_postcode_lookup/requirements.txt ## Rebuild everything this Makefile knows how to build

.PHONY: clean
clean: ## Delete any generated static asset or req.txt files and git-restore the rendered API documentation file
	rm -rf ec_api/static_files/ lambda-layers/DependenciesLayer/requirements.txt

.PHONY: collectstatic
collectstatic: ## Rebuild the static assets
	python manage.py collectstatic --noinput --clear

lambda-layers/DependenciesLayer:
	mkdir -p $@

lambda-layers/DependenciesLayer/requirements.txt: pyproject.toml uv.lock lambda-layers/DependenciesLayer ## Update the requirements.txt file used to build this Lambda function's DependenciesLayer
	uv export --no-hashes --no-dev > lambda-layers/DependenciesLayer/requirements.txt

api_endpoints/api_auth/requirements.txt:
	uv export --no-hashes --package api_auth > api_endpoints/api_auth/requirements.txt

api_endpoints/v1_postcode_lookup/requirements.txt:
	uv export --no-hashes --package v1_postcode_lookup > api_endpoints/v1_postcode_lookup/requirements.txt

.PHONY: help
# gratuitously adapted from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## Display this help text
	@grep -E '^[-a-zA-Z0-9_/.]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%s\033[0m\n\t%s\n", $$1, $$2}'
