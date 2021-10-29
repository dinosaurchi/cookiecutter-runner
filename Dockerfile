# syntax=docker/dockerfile:1.0.0-experimental
FROM python:3.7
WORKDIR /usr/src
COPY . /usr/src

# check and download public key for remote hosts
RUN \
    # Install pipenv
    pip install -r ./poetry.req.txt && \
    mkdir -p -m 0600 ~/.ssh && \
    touch -m 600 ~/.ssh/known_hosts && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    ssh-keyscan gitlab.com >> ~/.ssh/known_hosts && \
    # Make sure not creating the virtual environment inside docker
    poetry config virtualenvs.create false --local

# Setup the environment
RUN --mount=type=ssh,id=gitlab_ssh_key poetry install
