![Microsoft Defending Democracy Program: ElectionGuard](https://raw.githubusercontent.com/microsoft/electionguard-web-api/main/images/electionguard-banner.svg)

# 🗳️ ElectionGuard Web API

[![docker version](https://img.shields.io/docker/v/electionguard/electionguard-web-api)](https://hub.docker.com/r/electionguard/electionguard-web-api) [![docker pulls](https://img.shields.io/docker/pulls/electionguard/electionguard-web-api)](https://hub.docker.com/r/electionguard/electionguard-web-api) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/context:python) [![Total alerts](https://img.shields.io/lgtm/alerts/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/alerts/) [![Documentation Status](https://readthedocs.org/projects/electionguard-web-api/badge/?version=latest)](https://electionguard-web-api.readthedocs.io) [![license](https://img.shields.io/github/license/microsoft/electionguard-web-api)](LICENSE)

This is a python API that provides a **thin**, **stateless** wrapper around the [`electionguard-python`](https://github.com/microsoft/electionguard-python) library to perform ballot encryption, casting, spoiling, and tallying. This API is implemented using [FastAPI](https://fastapi.tiangolo.com/#interactive-api-docs).

If you aren't familiar with ElectionGuard and its concepts, [take a stroll through the official documentation](https://microsoft.github.io/electionguard-python/) first!

## 👯‍♀️ Two APIs in One

The application can run in one of two modes:

- `guardian` mode runs features used by Guardians (key ceremony actions, partial tally decryption, etc.)
- `mediator` mode runs features used by Mediators (ballot encryption, casting, spoiling, etc.)

In practice, you will likely need to run at least one instance of each mode. We provide a single codebase and Docker image, but the mode can be set at runtime.

## 💻 Requirements

> NOTE:<br>
> 🐳 = required for running with Docker.<br>
> 🐍 = required for running with Python.

- 🐳🐍 [GNU Make](https://www.gnu.org/software/make/manual/make.html) is used to simplify the commands and GitHub Actions. This approach is recommended to simplify the command line experience. This is built in for MacOS and Linux. For Windows, setup is simpler with [Chocolatey](https://chocolatey.org/install) and installing the provided [make package](https://chocolatey.org/packages/make). The other Windows option is [manually installing make](http://gnuwin32.sourceforge.net/packages/make.htm).
- 🐍 [Python 3.8](https://www.python.org/downloads/) is <ins>**required**</ins> to develop this API. If developer uses multiple versions of python, [pyenv](https://github.com/pyenv/pyenv) is suggested to assist version management.

## 🐳 Running with Docker

### The official Docker image

We host a Docker image on both [Github Packages](https://github.com/microsoft/electionguard-web-api/packages/397920) and [DockerHub](https://hub.docker.com/r/electionguard/electionguard-web-api).

**Note:** _GitHub Packages requires authentication to retrieve the package. This requires a GitHub Access Token and using `docker login`. [Follow GitHub instructions](https://docs.github.com/en/packages/using-github-packages-with-your-projects-ecosystem/configuring-docker-for-use-with-github-packages#authenticating-with-a-personal-access-token)._

```bash
# Pull the image from DockerHub
docker pull docker.pkg.github.com/microsoft/electionguard-web-api/electionguard-web-api:main

# Start a container for the API in mediator mode, exposed on port 80 of the host machine
docker run -d -p 80:8000 --env API_MODE=mediator docker.pkg.github.com/microsoft/electionguard-web-api/electionguard-web-api:main
```

OR

```bash
# Pull the image from DockerHub
docker pull electionguard/electionguard-web-api:latest

# Start a container for the API in mediator mode, exposed on port 80 of the host machine
docker run -d -p 80:8000 --env API_MODE=mediator electionguard/electionguard-web-api:latest
```

### Developing locally with Docker

If you run Docker and want to run the code locally without Python dependencies, we provide a [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml).

Run both APIs at the same time:

```bash
make docker-run
```

Or run both APIs in development mode, with automatic reloading on file change:

```bash
make docker-dev
```

After either command, you will find the `mediator` API running at http://127.0.0.1:8000 and the `guardian` API at http://127.0.0.1:8001

## 🐍 Running with Python

### Quick Start

Using [**make**](https://www.gnu.org/software/make/manual/make.html), installation and startup can be run with one command:

To set up the environment:

```bash
make environment
```

To start the api:

```bash
make start API_MODE=mediator
```

OR

```bash
make start API_MODE=guardian
```

### Debugging

For local debugging with Visual Studio Code, choose the `Guardian Web API` or `Mediator Web API` options from the dropdown in the Run menu. Once the server is up, you can easily hit your breakpoints.

If the code fails to run, [make sure your Python interpreter is set](https://code.visualstudio.com/docs/python/environments) to use your poetry environment.

## 🧪 Testing

End-to-end integration tests can be found in the [`/tests/integration`](/tests/integration) folder.  To see them in action, run:

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
