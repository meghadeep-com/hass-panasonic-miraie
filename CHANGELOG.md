# Changelog

All notable changes to this fork are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This is the `meghadeep-com` fork of `chrissmartin/hass-panasonic-miraie`,
maintained independently since upstream went quiet (its last real commit was
2025-05-23). The entries below cover every release cut from this fork; versions
up to and including 0.7.0 were released by upstream and are not repeated here.

## [1.1.1] - 2026-10-01

### Fixed

- Entities no longer go stale. The four climate entities shared a single
  class-level update lock, so each refresh cycle only one AC won the lock and
  the other three hit `locked()` and skipped their periodic REST refresh
  entirely, leaving them on whatever MQTT last pushed until the device next
  published a change. The update and command locks and the per-entity state
  counters are now per-instance, so every AC refreshes independently.
- The MQTT handler no longer reconnects on an idle connection. MirAIe only
  publishes to `/state` when something changes, so a quiet house was silent and
  the old "no inbound message for 45s = stale" rule reconnected roughly every
  minute, churning the socket and dropping messages. Liveness now relies on the
  protocol-level keepalive, which surfaces a genuinely dead socket as an error
  in the message loop and reconnects there.
- State updates now honour the device's `onlineStatus` instead of forcing
  availability to `True` on every update, so an offline unit goes unavailable
  rather than showing its last values as if they were live.

### Added

- This changelog.

## [1.1.0] - 2026-09-28

### Changed

- The vertical and horizontal swing dropdowns now get their own per-position
  icons via `icons.json`, so the two controls are visually distinguishable in
  the climate card instead of both showing the same grey dot.

## [1.0.3] - 2026-09-28

### Changed

- Dropped the model-specific digit from the Converti preset labels (now
  "Converti 90%" rather than "Converti7 90%"), since the same capacity field is
  branded differently across models. Preset keys are unchanged for automation
  compatibility.

## [1.0.2] - 2026-09-28

### Fixed

- Buzzer and Display state is now populated rather than sitting at `unknown`;
  the parser's allowlist was missing those fields.
- Platforms now skip fields a given model does not report instead of creating
  dead entities that sit at `unavailable`.

## [1.0.1] - 2026-09-28

### Changed

- Took over maintainership: removed upstream's donation links, funding config
  and codeowners in favour of this fork's.

## [1.0.0] - 2026-09-28

### Added

- Exposed the app's remaining controls as their own entities beyond the climate
  card: switches (Powerful / Eco / Clean / Display / Buzzer), a number entity
  for Converti capacity, and sensors (room temperature, WiFi signal, filter
  dust level, operating hours).

## [0.7.2] - 2026-09-28

### Fixed

- Louver / swing control now actually works. The firmware silently discards
  string-typed louver values, so positions are now sent as integers (0 =
  continuous swing, 1-5 = fixed position), and state parsing was fixed to
  compare against integers rather than strings. This resolves upstream's
  long-standing swing-control bug.

## [0.7.1] - 2026-09-28

First release cut from this fork, rescuing the integration on current Home
Assistant.

### Fixed

- Resolved the `AttributeError` that crashed the climate entity on current
  Home Assistant and blocked the integration from loading at all.

### Added

- First release to ship the Converti7, nanoe G, powerful-mode and economy-mode
  control services. These were written upstream but never included in a tagged
  release before upstream stalled.

[1.1.1]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.1.1
[1.1.0]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.1.0
[1.0.3]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.0.3
[1.0.2]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.0.2
[1.0.1]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.0.1
[1.0.0]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v1.0.0
[0.7.2]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v0.7.2
[0.7.1]: https://github.com/meghadeep-com/hass-panasonic-miraie/releases/tag/v0.7.1
