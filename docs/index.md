![Microsoft Defending Democracy Program: ElectionGuard](https://github.com/microsoft/electionguard-web-api/tree/main/images/electionguard-banner.svg)

#  🗳️ ElectionGuard Web API

![docker version](https://img.shields.io/docker/v/electionguard/electionguard-web-api) ![docker pulls](https://img.shields.io/docker/pulls/electionguard/electionguard-web-api) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/context:python) [![Total alerts](https://img.shields.io/lgtm/alerts/g/microsoft/electionguard-web-api.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/microsoft/electionguard-web-api/alerts/) [![Documentation Status](https://readthedocs.org/projects/electionguard-web-api/badge/?version=latest)](https://electionguard-web-api.readthedocs.io) [![license](https://img.shields.io/github/license/microsoft/electionguard-web-api)](LICENSE)


This is a python API that utilizes [`electionguard-python`](https://github.com/microsoft/electionguard-python) to perform ballot encryption, casting, spoiling, and tallying. This API is implemented using [FastAPI](https://fastapi.tiangolo.com/#interactive-api-docs
).


## 💻 Requirements

_These requirements line up with [electionguard-python](https://github.com/microsoft/electionguard-python/blob/main/README.md#-requirements)._

- [Python 3.8](https://www.python.org/downloads/) is <ins>**required**</ins> to develop this API. If developer uses multiple versions of python, [pyenv](https://github.com/pyenv/pyenv) is suggested to assist version management.
- [GNU Make](https://www.gnu.org/software/make/manual/make.html) is used to simplify the commands and GitHub Actions. This approach is recommended to simplify the command line experience. This is built in for MacOS and Linux. For Windows, setup is simpler with [Chocolatey](https://chocolatey.org/install) and installing the provided [make package](https://chocolatey.org/packages/make). The other Windows option is [manually installing make](http://gnuwin32.sourceforge.net/packages/make.htm).
- [Gmpy2](https://gmpy2.readthedocs.io/en/latest/) is used for [Arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) which
has its own [installation requirements (native C libraries)](https://gmpy2.readthedocs.io/en/latest/intro.html#installation) on Linux and MacOS.  **⚠️ Note:** _This is not required for Windows but the python package must be installed with the precompiled libraries._
- [pipenv](https://github.com/pypa/pipenv) is used to configure the python environment. Installation instructions can be found [here](https://github.com/pypa/pipenv#installation).

## 🚀 Quick Start

Using [**make**](https://www.gnu.org/software/make/manual/make.html), installation and startup can be run with one command: 

```
make
```

To start the api:
```
make start
```

## 🛠 Debugging

For local debugging with Visual Studio Code, choose the `Web API` option from the dropdown in the Run menu.  Once the server is up, you can easily hit your breakpoints.

If the code fails to run, [make sure your Python interpreter is set](https://code.visualstudio.com/docs/python/environments) to use your pipenv environment.

## 🐳 Docker
A DockerFile is available to quickly create and run a docker container.


Build docker container:
```
make docker-build
```

Run docker container:
```
make docker-run
```

## 🧪 Testing

A Postman collection is available to test the API located in the `/tests` folder. This can be imported into Postman for easy testing. This suite works on a local run server or the preconfigured docker settings.

## 📝 Documentation

**FastApi** defaultly has API documentation built in. The following is available after running:

- **[SwaggerUI](https://github.com/swagger-api/swagger-ui)** at [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

- **[ReDoc](https://github.com/Redocly/redoc)** at [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

Overviews of the API itself are available on:

- [GitHub Pages](https://microsoft.github.io/electionguard-web-api/)
- [Read the Docs](https://electionguard-web-api.readthedocs.io/)

## 🗄 Archived
As of 06/15/2020, the previous C wrapped implementation was transitioned to the python version. ElectionGuard development has transitioned to the [ElectionGuard-Python](https://github.com/microsoft/electionguard-python) Repo. The old version is available using the `dotnet-api` tag.

## 🤝 Contributing

This project encourages community contributions for development, testing, documentation, code review, and performance analysis, etc.  For more information on how to contribute, see [the contribution guidelines][Contributing]

### Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

### Reporting Issues

Please report any bugs, feature requests, or enhancements using the [GitHub Issue Tracker](https://github.com/microsoft/electionguard-web-api/issues).  Please do not report any security vulnerabilities using the Issue Tracker.  Instead, please report them to the Microsoft Security Response Center (MSRC) at [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report).  See the [Security Documentation][Security] for more information.

### Have Questions?

Electionguard would love for you to ask questions out in the open using GitHub Issues. If you really want to email the ElectionGuard team, reach out at electionguard@microsoft.com.

## License
This repository is licensed under the [MIT License]