[![CI](https://github.com/BazaJayGee66/homeassistant_cololight/actions/workflows/ci.yml/badge.svg)](https://github.com/BazaJayGee66/homeassistant_cololight/actions/workflows/ci.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
<img src="https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.cololight.total">

# Home Assistant Cololight

The Cololight custom integration allows you to control [LifeSmart Cololight](https://cololight.com/) devices in Home Assistant.

Supported devices include:

- Cololight Hexagon
- Cololight LED Strip
- Cololight MIX

## Installation

### Marketplace

1. Go to **Settings → Marketplace**.
2. Select **Add from link**, enter `BazaJayGee66/homeassistant_cololight`, then select **Add**.
3. Open **LifeSmart Cololight** and select **Install**.
4. Restart Home Assistant if prompted.

On Home Assistant 2026.10 or older, add `https://github.com/BazaJayGee66/homeassistant_cololight` in HACS as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (type **Integration**), download **LifeSmart Cololight**, then restart Home Assistant.

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. Download the latest [`cololight.zip`](https://github.com/BazaJayGee66/homeassistant_cololight/releases/latest/download/cololight.zip), and unzip to the `custom_components` directory.

```sh
wget https://github.com/BazaJayGee66/homeassistant_cololight/releases/latest/download/cololight.zip
unzip cololight.zip -d /path/to/custom_components
rm cololight.zip
```

4. Restart Home Assistant

## Configuration

After installation, adding Cololight to your Home Assistant instance can be done via the user interface, or by using this My button:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=cololight)

> #### Host
>
> The IP address or hostname of the Cololight (for example, `192.168.1.50`).
>
> #### Name
>
> Name to give the device in Home Assistant.
>
> #### Device
>
> The Cololight device type.

## Extra Configuration

Additional Cololight options can be configured through the Home Assistant user interface by following these steps:

1. Open your Home Assistant instance.
2. Go to [Settings → Devices & services](https://my.home-assistant.io/redirect/integrations).
3. Locate and select the **LifeSmart Cololight** integration.
4. Click the cog icon (⚙️) on the device you want to update.

<img src="images/cololight_options.png?raw=true" alt="Extra Configuration" width="500"/>

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

> #### Default effects
>
> List of default effects of the Cololight device to restore.
>
> #### Dynamic effects
>
> List of dynamic effects of the Cololight device to restore.

## Feature Requests/Issue

Please create an issue [here](https://github.com/BazaJayGee66/homeassistant_cololight/issues).

For contributing, have a look [here](CONTRIBUTING.md).

## Sponsor

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/BazaJayGee66)

## Credits

Thanks to ["Projekt: ColoLight in FHEM"](https://haus-automatisierung.com/projekt/2019/04/05/projekt-cololight-fhem.html) for discovering how to talk with the Cololight.
