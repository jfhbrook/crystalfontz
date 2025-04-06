# DBus Access and Permissions

When running services under the `system` bus, care must be taken to manage access policies. Dbus does this primarily with [an XML-based policy language](https://dbus.freedesktop.org/doc/dbus-daemon.1.html). Systemd additionally manages access to privileged methods, seemingly with the intent of delegating to polkit.

By default, Dbus is configured with the following policies:

- The root user may own the bus, and send and receive messages from `org.jfhbrook.crystalfontz`
- Users in the `crystalfontz` Unix group may additionally send and receive messages from `org.jfhbrook.crystalfontz`
- Select methods which may be destructive or affect availability are marked with the `org.freedesktop.systemd1.Privileged` annotation, and will require `sudo` to execute

This means that, if the service is running, `sudo crystalfontzctl` commands should always work; and that if your user is in the `crystalfontz` Unix group, Dbus will allow for unprivileged `crystalfontzctl` commands as well. You can create this group and add yourself to it by running:

```bash
sudo groupadd crystalfontz
sudo usermod -a -G crystalfontz "${USER}"
```
