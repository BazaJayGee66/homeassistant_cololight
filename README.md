# Home Assistant LifeSmart Cololight

[![Build status](https://badge.buildkite.com/03f664e487145ff4bfd75d66c94e6cecb26051e7479ccb0279.svg)](https://buildkite.com/goodwin/homeassistant-cololight)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

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
3. Download `cololight.zip` [release version](https://github.com/BazaJayGee66/homeassistant_cololight/releases), and unzip to custom_components directory

```sh
wget https://github.com/BazaJayGee66/homeassistant_cololight/releases/download/v1.2.3/cololight.zip
unzip cololight.zip -d /path/to/custom_components
rm cololight.zip
```

4. Restart Home Assistant

## Configuration

### Config Flow - UI

In Configuration/Integrations click on the + button, select LifeSmart Cololight and configure the options on the form.

Default Effects can be selected when creating the entity.

Custom effects can be added/deleted in configuration options once the entity has been created.

### configuration.yaml

#### Options

| Name                        | Type   | Required | Default   | Description                             |
| --------------------------- | ------ | -------- | --------- | --------------------------------------- |
| platform                    | string | ✔        |           | cololight                               |
| host                        | string | ✔        |           | IP address of your Cololight            |
| name                        | string | ✖        | ColoLight | Name of your entity                     |
| default_effects             | list   | ✖        | All       | Default Cololight effects to add        |
| custom_effects              | map    | ✖        |           | List of custom effects to add to entity |
| custom_effects:name         | string | ✔        |           | Name of custom effect                   |
| custom_effects:color_scheme | string | ✔        |           | Color Scheme of effect                  |
| custom_effects:color        | string | ✔        |           | Color of effect                         |
| custom_effects:cycle_speed  | int    | ✔        |           | Cycle speed of effect (1 - 32)          |
| custom_effects:mode         | int    | ✔        |           | [Mode](MODES.md) of effect (1 - 27)     |

> Valid default_effects:
> ["80s Club", "Cherry Blossom", "Cocktail Parade", "Instagrammer", "Pensieve", "Savasana", "Sunrise", "The Circus", "Unicorns", "Christmas", "Rainbow Flow", "Music Mode", "Good Effect"]

#### Example

Add a light to your configuration:

```yaml
light:
  - platform: cololight
    name: my_cololight
    host: 192.168.1.100
    default_effects:
      - 80s Club
      - Cherry Blossom
      - Cocktail Parade
      - Instagrammer
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

## Feature Requests/Issue

Please create an issue [here](https://github.com/BazaJayGee66/homeassistant_cololight/issues)

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
