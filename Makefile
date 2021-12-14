.PHONY: all environment lint start

OS ?= $(shell python -c 'import platform; print(platform.system())')
IMAGE_NAME = electionguard_web_api
AZURE_LOCATION = eastus
RESOURCE_GROUP = EG-Deploy-Demo
DEPLOY_REGISTRY = deploydemoregistry
REGISTRY_SKU = Basic
ACI_CONTEXT = egacicontext
TENANT_ID = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
GROUP_EXISTS ?= $(shell az group exists --name $(RESOURCE_GROUP))

# Supports either "guardian" or "mediator" modes
API_MODE ?= mediator
ifeq ($(API_MODE), mediator)
PORT ?= 8000
else
PORT ?= 8001
endif

all: environment lint start

environment: no-windows
	@echo 🔧 SETUP
	make install-gmp
	pip3 install 'poetry==1.1.6'
	poetry config virtualenvs.in-project true 
	poetry install

install: no-windows
	@echo 🔧 INSTALL
	poetry install

install-gmp: no-windows
	@echo 📦 Install Module
	@echo Operating System identified as $(OS)
ifeq ($(OS), Linux)
	make install-gmp-linux
endif
ifeq ($(OS), Darwin)
	make install-gmp-mac
endif

install-gmp-mac: no-windows
	@echo 🍎 MACOS INSTALL
# gmpy2 requirements
	brew install gmp || true
	brew install mpfr || true
	brew install libmpc || true

install-gmp-linux: no-windows
	@echo 🐧 LINUX INSTALL
# gmpy2 requirements
	sudo apt-get install libgmp-dev
	sudo apt-get install libmpfr-dev
	sudo apt-get install libmpc-dev

# install azure command line
install-azure-cli:
	@echo Install Azure CLI
ifeq ($(OS), Linux)
	curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
endif
ifeq ($(OS), Darwin)
	brew install azure-cli
	az upgrade
endif
ifeq ($(OS), Windows)
	Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; rm .\AzureCLI.msi
endif

# deploy to azure
deploy-azure:
	@echo Deploy to Azure
	az login --tenant $(TENANT_ID)
ifeq ($(GROUP_EXISTS), false)
	az group create -l $(AZURE_LOCATION) -n $(RESOURCE_GROUP)
endif
	az acr create --resource-group $(RESOURCE_GROUP) --name $(DEPLOY_REGISTRY) --sku $(REGISTRY_SKU)
	az acr login --name $(DEPLOY_REGISTRY)
	docker context use default
	docker build . -t $(DEPLOY_REGISTRY).azurecr.io/electionguard-api-python:latest
	docker push $(DEPLOY_REGISTRY).azurecr.io/electionguard-api-python:latest
	docker login azure --tenant-id $(TENANT_ID)
# docker context create aci $(ACI_CONTEXT)
	docker context use $(ACI_CONTEXT)
	docker compose -f docker-compose.azure.yml up
	docker logout
	docker context use default
	az logout

# Dev Server
start: no-windows
	poetry run uvicorn app.main:app --reload --port $(PORT)

start-server:
	docker compose -f docker-compose.support.yml up -d
	QUEUE_MODE=remote
	STORAGE_MODE=mongo
	poetry run uvicorn app.main:app --reload --port $(PORT)

stop:
	docker compose -f docker-compose.support.yml down

# Docker
docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker-compose up --build

docker-dev:
	docker-compose -f docker-compose.support.yml -f docker-compose.dev.yml up --build

docker-postman-test:
	@echo 🧪 RUNNING POSTMAN TESTS IN DOCKER
	docker-compose \
	-f tests/postman/docker-compose.yml up \
	--build \
	--abort-on-container-exit \
	--exit-code-from test-runner

# Linting
lint:
	@echo 💚 LINT
	@echo 1.Pylint
	poetry run pylint --extension-pkg-whitelist=pydantic app tests
	@echo 2.Black Formatting
	poetry run black --diff --check app tests
	@echo 3.Mypy Static Typing
	poetry run mypy --config-file=pyproject.toml app tests
	@echo 4.Documentation
	poetry run mkdocs build --strict

auto-lint:
	poetry run black app tests
	make lint

test-integration: no-windows
	@echo ✅ INTEGRATION TESTS
	poetry run pytest -s . -x

# Documentation
docs-serve:
	poetry run mkdocs serve

docs-build:
	poetry run mkdocs build

docs-deploy:
	@echo 🚀 DEPLOY to Github Pages
	poetry run mkdocs gh-deploy --force

docs-deploy-ci:
	@echo 🚀 DEPLOY to Github Pages
	pip install mkdocs
	mkdocs gh-deploy --force

# PRIVATE RECIPIES

no-windows:
ifeq ($(OS), Windows_NT)
	@echo Windows is not supported. Instead run this command in WSL2. For more details see README.md.
	exit 1
endif
