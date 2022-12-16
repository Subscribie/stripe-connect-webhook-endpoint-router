# syntax = docker/dockerfile:experimental
FROM python:3.6.8-alpine3.9

WORKDIR /usr/src/app
RUN apk add --update --no-cache build-base libffi-dev openssl-dev bash gcc
COPY . /usr/src/app/
RUN export DOCKER_BUILDKIT=1
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install uWSGI==2.0.19.1
EXPOSE 80
ENTRYPOINT [ "./entrypoint.sh" ]
