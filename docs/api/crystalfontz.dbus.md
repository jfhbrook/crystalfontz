# crystalfontz.dbus

The `crystalfontz` library includes a DBus service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients - including `crystalfontzctl` - can connect to the service.

Note that the DBus interface uses DBus compatible types, rather than the standard `crystalfontz` domain objects. To map between `crystalfontz` domain objects and DBus types, use [the `crystalfontz.dbus.domain` module](./crystalfontz.dbus.domain.md).

For information on the service daemon and CLI client, visit [the main DBus documentation](../dbus.md).

::: crystalfontz.dbus
