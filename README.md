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

| Name | Type | Required | Default | Description
| --- | --- | --- | --- | ---
| platform | string | ✔ |  | cololight
| host | string | ✔ | | IP address of your Cololight
| name | string | ✖ | Cololight | name of your entity

Add a light to your configuration:

~~~ yaml
light:
  - platform: cololight
    name: my_cololight
    host: 192.168.1.100
~~~~

## Credits

Thanks to ["Projekt: ColoLight in FHEM"](https://haus-automatisierung.com/projekt/2019/04/05/projekt-cololight-fhem.html) for discovering how to talk with the Cololight
