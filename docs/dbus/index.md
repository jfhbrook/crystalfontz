# DBus Support

The `crystalfontz` library includes a DBus interface, service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients (including `crystalfontzctl`) can connect to the service.

For information on the API, visit the API docs for [`crystalfontz.dbus.interface`](../api/crystalfontz.dbus.interface.md) and [`crystalfontz.dbus.client`](../api/crystalfontz.dbus.client.md).
