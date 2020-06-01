# This repository is archived.
Please go to [BazaJayGee66's repository](https://github.com/BazaJayGee66/homeassistant_cololight) for continued support and updates. 



---



# Home Assistant LifeSmart Cololight

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

Custom component to support [LifeSmart Cololight](http://www.cololight.com/) in Home Assistant

## Installation


### HACS

1. In HACS go to the tab "Settings"
2. Add this repository as custom repository. Category is "Integration".
3. Switch to the tab "Integrations"
4. Install like any other custom integration.
5. Restart Home Assistant

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called cololight.
4. Download all the files from the cololight/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

## Configuration

### Options

| Name                        | Type   | Required | Default   | Description                             |
| --------------------------- | ------ | -------- | --------- | --------------------------------------- |
| platform                    | string | ✔        |           | cololight                               |
| host                        | string | ✔        |           | IP address of your Cololight            |
| name                        | string | ✖        | ColoLight | Name of your entity                     |
| custom_effects              | map    | ✖        |           | List of custom effects to add to entity |
| custom_effects:name         | string | ✔        |           | Name of custom effect                   |
| custom_effects:color_scheme | string | ✔        |           | Color Scheme of effect                  |
| custom_effects:color        | string | ✔        |           | Color of effect                         |
| custom_effects:cycle_speed  | int    | ✔        |           | Cycle speed of effect (1 - 32)          |
| custom_effects:mode         | int    | ✔        |           | [Mode](MODES.md) of effect (1 - 27)     |

Add a light to your configuration:

```yaml
light:
  - platform: cololight
    name: my_cololight
    host: 192.168.1.100
    custom_effects:
      - name: My Cool Effect
        color_scheme: Mood
        color: Gold
        cycle_speed: 10
        mode: 1
      - name: My Other Effect
        color_scheme: Breath
        color: Red, Green, Blue
        cycle_speed: 10
        mode: 1
```

## Credits

Thanks to ["Projekt: ColoLight in FHEM"](https://haus-automatisierung.com/projekt/2019/04/05/projekt-cololight-fhem.html) for discovering how to talk with the Cololight

## Tests:

This section talks to how to setup and run test to ensure any development changes do not break the component.

**Prerequisites**

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- Docker
  - For Linux, macOS, or Windows 10 Pro/Enterprise/Education use the [current release version of Docker](https://docs.docker.com/install/)
  - Windows 10 Home requires [WSL 2](https://docs.microsoft.com/windows/wsl/wsl2-install) and the current Edge version of Docker Desktop (see instructions [here](https://docs.docker.com/docker-for-windows/wsl-tech-preview/)). This can also be used for Windows Pro/Enterprise/Education.
- [Visual Studio code](https://code.visualstudio.com/)
- [Remote - Containers (VSC Extension)][extension-link]

[More info about requirements and devcontainer in general](https://code.visualstudio.com/docs/remote/containers#_getting-started)

[extension-link]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers

**Getting started:**

1. Clone the repository to your computer.
2. Open the repository using Visual Studio code.

When you open this repository with Visual Studio code you are asked to "Reopen in Container", this will start the build of the container.

_If you don't see this notification, open the command palette and select `Remote-Containers: Reopen Folder in Container`._

**Running Tests:**

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
