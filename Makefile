.PHONY: all environment lint start

OS ?= $(shell python -c 'import platform; print(platform.system())')
WINDOWS_ERROR = ⚠️ UNSUPPORTED WINDOWS INSTALL ⚠️ 
CONTAINER_NAME = electionguard_web_api
CONTAINER_ADDRESS ?= 0.0.0.0
CONTAINER_PORT ?= 8000
IMAGE_NAME = electionguard_web_api
# Supports either "guardian" or "mediator" modes
API_MODE = mediator

all: environment lint start

environment:
	@echo 🔧 PIPENV SETUP
	make install-gmp
	pip install pipenv
	pipenv install --dev

install-gmp:
	@echo 📦 Install Module
	@echo Operating System identified as $(OS)
ifeq ($(OS), Linux)
	make install-gmp-linux
endif
ifeq ($(OS), Darwin)
	make install-gmp-mac
endif
ifeq ($(OS), Windows)
	echo $(WINDOWS_ERROR)
endif
ifeq ($(OS), Windows_NT)
	echo $(WINDOWS_ERROR)
endif

install-gmp-mac:
	@echo 🍎 MACOS INSTALL
# gmpy2 requirements
	brew install gmp || true
	brew install mpfr || true
	brew install libmpc || true

install-gmp-linux:
	@echo 🐧 LINUX INSTALL
# gmpy2 requirements
	sudo apt-get install libgmp-dev
	sudo apt-get install libmpfr-dev
	sudo apt-get install libmpc-dev

# Server
start:
	pipenv run uvicorn app.main:app --reload

# Docker
docker-build:
	DOCKER_BUILDKIT=1 docker build -t $(IMAGE_NAME) .

docker-run:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose up --build

docker-dev:
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose -f docker-compose.dev.yml up --build

# Linting
lint:
	@echo 💚 LINT
	@echo 1.Pylint
	pipenv run pylint app
	@echo 2.Black Formatting
	pipenv run black --diff --check app
	@echo 3.Mypy Static Typing
	pipenv run mypy app
	@echo 4.Documentation
	pipenv run mkdocs build --strict

auto-lint:
	pipenv run black app
	make lint 

# Documentation
docs-serve:
	pipenv run mkdocs serve

docs-build:
	pipenv run mkdocs build

docs-deploy:
	@echo 🚀 DEPLOY to Github Pages
	pipenv run mkdocs gh-deploy --force

docs-deploy-ci:
	@echo 🚀 DEPLOY to Github Pages
	pip install mkdocs
	mkdocs gh-deploy --force
