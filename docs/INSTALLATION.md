# Installation details

## Offline installation

Inspect and extract the prepared source bundle, then copy its
`zelport.integration` directory to
`~/.config/omarchy/plugins/zelport.integration/`. `manifest.json` must be
directly inside that directory. Validate and enable the installed copy:

```sh
omarchy plugin validate .
omarchy-shell shell rescanPlugins
omarchy plugin enable zelport.integration
```

## Keyboard shortcut

On Omarchy installations that use Lua configuration, add the optional
**Super + Alt + Z** shortcut to `~/.config/hypr/bindings.lua`:

```lua
o.bind("SUPER + ALT + Z", "Zelport Integration", "omarchy-shell shell toggle zelport.integration '{}'")
```

Check for conflicts first. Zelport Integration never changes keyboard
configuration itself.
