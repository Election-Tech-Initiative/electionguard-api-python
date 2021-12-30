![Microsoft Defending Democracy Program: ElectionGuard](https://raw.githubusercontent.com/microsoft/electionguard-web-api/main/images/electionguard-banner.svg)

# 🗳️ ElectionGuard Web API

[![docker version](https://img.shields.io/docker/v/electionguard/electionguard-web-api)](https://hub.docker.com/r/electionguard/electionguard-web-api) [![docker pulls](https://img.shields.io/docker/pulls/electionguard/electionguard-web-api)](https://hub.docker.com/r/electionguard/electionguard-web-api) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/context:python) [![Total alerts](https://img.shields.io/lgtm/alerts/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/alerts/) [![Documentation Status](https://readthedocs.org/projects/electionguard-web-api/badge/?version=latest)](https://electionguard-web-api.readthedocs.io) [![license](https://img.shields.io/github/license/microsoft/electionguard-web-api)](LICENSE)

The ElectionGuard Web API is a python-based application that provides a **thin**, **stateless** wrapper around the [`electionguard-python`](https://github.com/microsoft/electionguard-python) library to perform ballot encryption, casting, spoiling, and tallying. This API is implemented using [FastAPI](https://fastapi.tiangolo.com/#interactive-api-docs).

If you aren't familiar with ElectionGuard and its concepts, first take a stroll through [the official documentation](https://microsoft.github.io/electionguard-python/).

## 👯‍♀️ Two APIs in One

Before you begin you should be aware that the application can run in one of two modes:

- `guardian` mode runs features used by Guardians (key ceremony actions, partial tally decryption, etc.)
- `mediator` mode runs features used by Mediators (ballot encryption, casting, spoiling, etc.)

In practice, you will likely need to run at least one instance of each mode. We provide a single codebase and Docker image, but the mode can be set at runtime as described below.

## ⭐ Getting Started

This codebase can be run using one of three different approaches:

1. 🐳 Running with Docker
2. 🐳 Developing with Docker
3. 🐍 Developing with Python

## 🐳 1. Running with Docker

This approach runs an official published image. This approach is not intended for development. It works on Windows, Mac, and Linux.

For convenience the Docker image is hosted on both [Github Packages](https://github.com/microsoft/electionguard-web-api/packages/397920) and [DockerHub](https://hub.docker.com/r/electionguard/electionguard-web-api). You can choose whichever container image library works best for you.

### 1.1 Pulling from Github Packages

**Note:** _GitHub Packages requires authentication to retrieve the package. This requires a GitHub Access Token and using `docker login`. [Follow GitHub instructions](https://docs.github.com/en/packages/using-github-packages-with-your-projects-ecosystem/configuring-docker-for-use-with-github-packages#authenticating-with-a-personal-access-token)._

```bash
# Pull the image from Github
docker pull docker.pkg.github.com/microsoft/electionguard-web-api/electionguard-web-api:main

# Start a container for the API in mediator mode, exposed on port 80 of the host machine
docker run -d -p 80:8000 --env API_MODE=mediator docker.pkg.github.com/microsoft/electionguard-web-api/electionguard-web-api:main
```

### 1.2 Pulling from DockerHub

Pulling from DockerHub is simpler as it requires no additional authentication.

```bash
# Pull the image from DockerHub
docker pull electionguard/electionguard-web-api:latest

# Start a container for the API in mediator mode, exposed on port 80 of the host machine
docker run -d -p 80:8000 --env API_MODE=mediator electionguard/electionguard-web-api:latest
```

## 🐳 2. Developing with Docker

Developing with Docker is the fastest approach for getting started because it has virtually no local dependencies (e.g. Python). This approach works on Windows, Mac, and Linux. It uses a [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml).

### ✅ 2.1 Prerequisities

- [GNU Make](https://www.gnu.org/software/make/manual/make.html) is required to simplify commands and GitHub Actions. For MacOS and Linux, no action is necessary as it pre-installed. For Windows, install via [Chocolatey](https://chocolatey.org/install) and the [make package](https://chocolatey.org/packages/make), or alternately [manually install](http://gnuwin32.sourceforge.net/packages/make.htm).
- [Docker Desktop](https://www.docker.com/products/docker-desktop) is required for Docker support

### 🏃‍♀️ 2.2 Running 🏃‍♂️

To get started run both APIs at the same time:

```bash
make docker-run
```

Or run both APIs in development mode, with automatic reloading on file change:

```bash
make docker-dev
```

After either command, you will find the `mediator` API running at http://127.0.0.1:8000 and the `guardian` API at http://127.0.0.1:8001

## 🐍 3. Developing with Python

Developing with Python provides the fastest developer inner loop (speed from code changes to seeing effects of changes), but is more work to set up initially. It works on Mac and Linux. It also works via [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/about) on Windows.

### ✅ 3.1. Windows Prerequisites

On Windows you can use an IDE of your choice in Windows, and run the make and Python commands in WSL which will expose API's in Windows. Developing with Python on Windows involves the following additional setup that is not required for Linux or Mac.

1. Install [WSL 2](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Install [Ubuntu](https://www.microsoft.com/en-us/p/ubuntu/9nblggh4msv6?ocid=9nblggh4msv6_ORSEARCH_Bing&rtc=1&activetab=pivot:overviewtab) (other Linux distributions should also work with minor modifications to the instructions below)
3. Install [pyenv prerequisites](https://github.com/pyenv/pyenv/wiki#suggested-build-environment). Technically you could just install Python and it would be simpler, but this approach will provide more flexibility. To install the prerequisites:

```bash
sudo apt-get update
sudo apt-get install make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

4. Install pyenv via [pyenv-installer](https://github.com/pyenv/pyenv-installer) and add it the startup scripts:

```bash
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc
sed -Ei -e '/^([^#]|$)/ {a \
  export PYENV_ROOT="$HOME/.pyenv"
  a \
  export PATH="$PYENV_ROOT/bin:$PATH"
  a \
  ' -e ':a' -e '$!{n;ba};}' ~/.profile
echo 'eval "$(pyenv init --path)"' >>~/.profile

echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

5. Restart shell
6. Install Python 3.9 via pyenv

```bash
pyenv install 3.9.9
pyenv global 3.9.9
```

### ✅ 3.2 Mac/Linux Prerequisites

Install [Python 3.9](https://www.python.org/downloads/). We additionally recommend [pyenv](https://github.com/pyenv/pyenv) to assist with Python version management (see detailed instructions in the Windows section above starting with Step 3).

### 🏃‍♀️ 3.2 Running 🏃‍♂️

Using [**make**](https://www.gnu.org/software/make/manual/make.html), install and setup the environment:

```bash
make environment
```

Start the api as mediator

```bash
make start API_MODE=mediator
```

OR as guardian

```bash
make start API_MODE=guardian
```

### Debugging Mac/Linux

For local debugging with Visual Studio Code, choose the `Guardian Web API` or `Mediator Web API` options from the dropdown in the Run menu. Once the server is up, you can easily hit your breakpoints.

If the code fails to run, [make sure your Python interpreter is set](https://code.visualstudio.com/docs/python/environments) to use your poetry environment.

### Debugging Windows

With Visual Studio Code:

1. Install the [Remote WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) extension
2. In the bottom left click the Green Icon and "New WSL Window using Distro", select Ubuntu
3. F5
4. Choose either `Guardian Web API` or `Mediator Web API`

## 🧪 Testing

End-to-end integration tests can be found in the [`/tests/integration`](/tests/integration) folder. To see them in action, run:

```bash
make test-integration
```

A Postman collection is also available to test the API located in the [`/tests/postman`](/tests/postman) folder. You can do a few things with this:

- [Import into Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman) for easy manual testing.
- Run locally with the [Newman CLI](https://github.com/postmanlabs/newman).
- Run the APIs and tests entirely in Docker by running:
  ```bash
  make docker-postman-test
  ```

## 📝 Documentation

**FastApi** defaultly has API documentation built in. The following is available after running:

- **[SwaggerUI](https://github.com/swagger-api/swagger-ui)** at [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) or [`http://127.0.0.1:8001/docs`](http://127.0.0.1:8001/docs), depending on the API mode

- **[ReDoc](https://github.com/Redocly/redoc)** at [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc) or [`http://127.0.0.1:8001/redoc`](http://127.0.0.1:8001/redoc)

Overviews of the API itself are available on:

- [GitHub Pages](https://microsoft.github.io/electionguard-web-api/)
- [Read the Docs](https://electionguard-web-api.readthedocs.io/)

## 🗄 Archived

As of 06/15/2020, the previous C wrapped implementation was transitioned to the python version. ElectionGuard development has transitioned to the [ElectionGuard-Python](https://github.com/microsoft/electionguard-python) Repo. The old version is available using the `dotnet-api` tag.

## 🤝 Contributing

This project encourages community contributions for development, testing, documentation, code review, and performance analysis, etc. For more information on how to contribute, see [the contribution guidelines](CONTRIBUTING.md)

### Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### Reporting Issues

Please report any bugs, feature requests, or enhancements using the [GitHub Issue Tracker](https://github.com/microsoft/electionguard-web-api/issues). Please do not report any security vulnerabilities using the Issue Tracker. Instead, please report them to the Microsoft Security Response Center (MSRC) at [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report). See the [Security Documentation](SECURITY.md) for more information.

### Have Questions?

Electionguard would love for you to ask questions out in the open using GitHub Issues. If you really want to email the ElectionGuard team, reach out at electionguard@microsoft.com.

## License

This repository is licensed under the [MIT License](LICENSE)
