# DBus Support

The `crystalfontz` library includes a DBus interface, service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients (including `crystalfontzctl`) can connect to the service.

For information on the API, visit the API docs for dbus:

- [`crystalfontz.dbus.interface`](../api/crystalfontz.dbus.interface.md): The core DBus interface
- [`crystalfontz.dbus.client`](../api/crystalfontz.dbus.client.md): The DBus client
- [`crystalfontz.dbus.report`](../api/crystalfontz.dbus.report.md): `ReportHandler` derived classes for use with the DBus client
- [`crystalfontz.dbus.domain`](../api/crystalfontz.dbus.domain.md): Types and classes for mapping between domain objects and DBus types
