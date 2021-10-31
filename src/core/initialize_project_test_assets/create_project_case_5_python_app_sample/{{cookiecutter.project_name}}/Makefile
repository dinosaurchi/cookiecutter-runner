# Use bash instead of shell (default)
SHELL := /bin/bash

define print_title
    echo -e "\n>>>>> $(1) <<<<<<\n"
endef

sync.version:
	$(call print_title,Sync the project to the closest git tag) && \
	echo -e "Note that if the content (hash) of git tags are identical, it will pick the alphabetical first one" && \
	echo -e "If no tag exists, it will use version 0.0.0\n" && \
	poetry version $$((git describe --tags --abbrev=0) || echo "0.0.0")
install:
	make sync.version && \
	$(call print_title,Create virtual env in the .venv in project directory with the current closest git tag) && \
	poetry install && \
	poetry update --lock && \
	poetry run pre-commit install --install-hooks
lint.analyze:
	$(call print_title,Running lint analyze) && \
	poetry run flake8
lint.check:
	$(call print_title,Running lint check with isort) && \
	poetry run isort -c --gitignore .  && \
	$(call print_title,Running lint check with black) && \
	poetry run black --check .
lint:
	$(call print_title,Linting with isort) && \
	poetry run isort --gitignore .  && \
	$(call print_title,Linting with black) && \
	poetry run black .
type.check:
	$(call print_title,Running type check) && \
	poetry run mypy
package.check:
	$(call print_title,Running package check) && \
	poetry check
check:
	$(call print_title,Running all checks) && \
	make package.check && \
	make type.check && \
	make lint.check
github.actions.check:
	$(call print_title,Preparing act to run Github Actions locally) && \
	if [ -f $$(which act) ]; then \
		echo -e "Use existing act at $$(which act)" && \
	else \
		echo -e "Installing act to run Github Actions locally" && \
		sudo curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash && \
	fi && \
	$(call print_title,Run Github Actions workflows (not using .gitignore to filter out files)) && \
	act --directory=./
test.coverage:
	$(call print_title,Run test coverage report) && \
	poetry run pytest --cov --cov-branch --cov-report=term-missing:skip-covered --cov-fail-under=100
test.unit:
	$(call print_title,Run unit tests) && \
	poetry run pytest -k test_unit
test.integ:
	$(call print_title,Run integration tests) && \
	poetry run pytest -k test_integ
test:
	$(call print_title,Run all tests);
	poetry run pytest
wheel.build:
	make sync.version && \
	$(call print_title,Build python wheel file) && \
	poetry build
docker.build:
	$(call print_title,Build docker image) && \
	source .env.docker && \
	export DOCKER_BUILDKIT=1 && \
	docker build -f ./Dockerfile -t $${IMAGE_NAME}:$${IMAGE_VERSION} .