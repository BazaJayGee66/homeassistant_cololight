# Contributing

Contributions are more than welcome.

To get up and running, fellow the below process:

- Fork the git repository.
- Write the code for new feature or bug fix.
- Ensure tests work.
- Create a Pull Request against the master branch.

## Prerequisites

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Docker
  - For Linux, macOS, or Windows 10 Pro/Enterprise/Education use the [current release version of Docker](https://docs.docker.com/install/)
  - Windows 10 Home requires [WSL 2](https://docs.microsoft.com/windows/wsl/wsl2-install) and the current Edge version of Docker Desktop (see instructions [here](https://docs.docker.com/docker-for-windows/wsl-tech-preview/)). This can also be used for Windows Pro/Enterprise/Education.
- [Visual Studio code](https://code.visualstudio.com/)
- [Remote - Containers (VSC Extension)](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

[More info about requirements and devcontainer in general](https://code.visualstudio.com/docs/remote/containers#_getting-started)

## Getting started

1. Clone the repository to your computer.
2. Open the repository using Visual Studio code.

When you open this repository with Visual Studio code you are asked to "Reopen in Container", this will start the build of the container.

_If you don't see this notification, open the command palette and select `Remote-Containers: Reopen Folder in Container`._

## Tests

Open a terminal in Visual Studio code within the Remote-Containers session.
Tests can then be run using pytest.

Run all test:

```
pytest
```

Run individual test:

```
pytest tests/test_light.py::test_turn_on
```
