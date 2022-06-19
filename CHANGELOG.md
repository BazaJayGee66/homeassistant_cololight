# v2.0.0

## New Features

- Support adding strip device custom effect
- Support adding strip device dynamic effects

## Fixes

- Default device to hexagon if cololight was setup prior to `v2.0.0`

## Breaking Changes

- Remove deprecated yaml configuration [#24](https://github.com/BazaJayGee66/homeassistant_cololight/issues/24)

# v1.3.2

## New Features

## Fixes

- Import pycololight, and remove class, as code has been migrated to [pycololight](https://github.com/BazaJayGee66/pycololight)

# v1.3.1

## New Features

## Fixes

- Update Update manifest.json with codeowners and issue_tracker
- Add warning for deprecated yaml configuration

# v1.3.0

## New Features

- Add polling to get light state (on/off) and brightness - Thanks [@pim12345](https://github.com/pim12345)

## Fixes

# v1.2.3

## New Features

## Fixes

- Fix issue [#13](https://github.com/BazaJayGee66/homeassistant_cololight/issues/13), where Colour Scheme "Shadow" had incorrect colours.

# v1.2.2

## New Features

## Fixes

- Fix issue [#11](https://github.com/BazaJayGee66/homeassistant_cololight/issues/11), where frequent commands could be unreliable in some cases.

# v1.2.1

## New Features

## Fixes

- Add version key to manifest.json file, as now [required](https://developers.home-assistant.io/docs/creating_integration_manifest/#version) by home assistant.

# v1.2.0

## New Features

- Allow deleting all effects through the UI, not just custom effects
- Allow restoring default effects through the UI

## Fixes

# v1.1.0

## New Features

- Select which default Cololight effects to include when creating the entity via the UI
- Set which default Cololight effects to include when creating the entity via config yaml

## Fixes

# v1.0.0

Initial Release

## New Features

- Configure through yaml config
- Configure through UI
- Brightness
- RGB Colours
- Effects
- Add custom effects

## Fixes
