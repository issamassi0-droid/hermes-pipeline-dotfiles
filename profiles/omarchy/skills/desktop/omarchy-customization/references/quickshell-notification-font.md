# Quickshell Notification Font

## Default Font

Quickshell notification cards receive their font from the shell service.
The container sets `fontFamily` on the `NotificationCard` component.

## Changing the Notification Font

### Via shell.json
Edit `~/.config/omarchy/shell.json` and set `fontFamily` in the
notifications section:
```json
{
 "notifications": {
 "fontFamily": "MonoLisa"
 }
}
```

### Via plugin QML
The `NotificationCard.qml` at `~/.config/omarchy/plugins/` or
`/usr/share/omarchy/shell/plugins/notifications/components/NotificationCard.qml`
has `property string fontFamily: ""`. The service passes:
```qml
fontFamily: service.shell && service.shell.bar ? service.shell.bar.fontFamily : ""
```

## Current User Setup
- Font: **MonoLisa** (set via `omarchy font set MonoLisa`)
- The notification card uses `root.fontFamily` inherited from the shell bar

## Reference
See `references/quickshell-notification-font.md` for detailed overrides.
