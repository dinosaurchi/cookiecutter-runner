# An inline runner for cookiecutter template

## Preparation

After installation, `poetry` can be used globally

Download and install `python3.7`

```sh
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.7
```

Install `pipx` to support running binaries packages (`poetry`)

```sh
$ python3 -m pip install --user pipx
$ python3 -m pipx ensurepath
```

Install `poetry`

```sh
$ pipx install -r poetry.req.txt
```

## Git-hooks setup (optional)

If you create a new project based on this source code without using this project `.git`, you have to install the `pre-commit` to the `git-hooks`
```sh
$ poetry run pre-commit install --install-hooks
```

## Setup development environment

Install all packages (including `dev` packages)
```sh
$ make install
```
- The environment directory will be generated at `.venv` directory
- Now, we can have the same mechanism to `yarn` with `node_modules` directory in `typescript/javascript`

To add new package
```sh
$ poetry add package_name
```

## Code linting and checking

Check the code styles, type declarations:
```sh
$ make lint.check
$ make type.check
$ make check # Check both
```

To check the coding convention:
```sh
$ make lint.analyze
```

Before committing your code, please run the following to reformat the source code:
```sh
$ make lint
```
- It is supposed to fix all of the styling problems and reformat your code to the standard
- You can modify the standards in `.pylintrc`, `isort` and `mypy` in `setup.cfg`

Sometime, you should run the package-check to inspect security vulnerabilities in package and its dependencies
```sh
$ make package-check
```
- It is not obligated but you should pay attention to it when deploying to outside world

## Run python script

Enter to the virtual environment
```sh
$ poetry shell
(py-template) $ python your_script.py
```

Or your can run with `poetry run` (not recommended)
```sh
$ poetry run python your_script.py
```

Note that, do not use `poetry run` as a production shortcut, as when build the container (docker), we will run in docker environment, and thus, simply run as a normal python program
```sh
$ python your_script.py
```

As `poetry` supports using `poetry run` without creating virtual environment (set `virtualenvs.create` to `false`), we can use `poetry run` inside docker

## Write tests

A python module file to be considered as a testing module:
- File name must be matched with pattern: `*_test_unit.py` or `*_test_integ.py`
- Module functions are considered as a test case if function name matched pattern: `test_*`

## Run test and test coverage report

```sh
$ make test # all tests
$ make test.unit # unit tests
$ make test.integ # integration tests
```

To run the test coverage report:
```sh
$ make test.coverage
```

## Reuse heavy python packages

`poetry` cached your downloaded packages thus we do not need to worry about space comsumption

## Build docker image

```sh
$ make docker.build
```

## Run Github Actions locally

It is to make sure our code will pass the CI beforing pushing to the remote repo
- Save running time
- Save monthly Github resource (about 2000 - 3000 minutes per month) for Github Actions

Run:
```sh
$ make github.actions.check
```