[![Build status](https://badge.buildkite.com/03f664e487145ff4bfd75d66c94e6cecb26051e7479ccb0279.svg)](https://buildkite.com/goodwin/homeassistant-cololight)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
# Home Assistant Cololight

The Cololight custom integration allows you to control [LifeSmart Cololight](http://www.cololight.com/) devices in Home Assistnat.

Supported devices include:

- Cololight Hexagon
- Cololight LED Strip

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
wget https://github.com/BazaJayGee66/homeassistant_cololight/releases/download/v2.0.0/cololight.zip
unzip cololight.zip -d /path/to/custom_components
rm cololight.zip
```

4. Restart Home Assistant

## Configuration

After installation, adding Cololight to your Home Assistant instance can be done via the user interface, or by using this My button:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=cololight)

> #### Host
>
> The host address of the cololight device (eg, `192.168.1.50`).
>
> #### Name
>
> Name to give the device in Home Assistant.
>
> #### Device
>
> The Cololight device type.

## Extra Configuration

You can configure additional Cololight options through the integration options flow by clicking `CONFIGURE` under the integration.

<img src="images/cololight_options.png?raw=true" alt="Extra Configuratio" width="250"/>

### Create Custom Effects

Create a custom effect for the Cololight device in Home Assistant.

> #### Name
>
> Name of the effect. _(Using the same name as an existing effect, will override that effect)_
>
> #### Color Scheme
>
> Color scheme of the effect.
>
> #### Cycle Speed
>
> Cycle speed of the effect.
>
> #### Mode
>
> Mode of the effect. _(Modes can be found [here](https://github.com/BazaJayGee66/pycololight/blob/main/MODES.md))_

### Remove Effects

Remove saved effects for the Cololight device in Home Assistant.

> #### Effects
>
> List of effects to be removed.

### Restore Effects

Restore default or dynamic effects for the Cololight device in Home Assistant.

> #### Deafult effects
>
> List of deafult effects of the Cololight device to restore.
>
> #### Dynamic effects
>
> List of dynamic effects of the Cololight device to restore.

## Feature Requests/Issue

Please create an issue [here](https://github.com/BazaJayGee66/homeassistant_cololight/issues).

For contriuting, have a look [here](CONTRIBUTING.md).

## Sponsor

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/BazaJayGee66)

## Credits

Thanks to ["Projekt: ColoLight in FHEM"](https://haus-automatisierung.com/projekt/2019/04/05/projekt-cololight-fhem.html) for discovering how to talk with the Cololight.
