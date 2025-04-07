# DBus API Overview

The `crystalfontz` library includes a DBus service and client. This service allows for multitenancy on Linux - the centralized service controls the serial bus, and clients - including `crystalfontzctl` - can connect to the service.

The DBus APIs largely depend on the [sdbus](https://pypi.org/project/sdbus/) Python library, which in turn depends on the [sd-bus](https://www.freedesktop.org/software/systemd/man/latest/sd-bus.html) library. This means that, effectively, the DBus API is only available on Linux. `sdbus` is therefore an optional dependency, under the `dbus` extra.

As a consequence, the DBus API is (unlike the primary `crystalfontz` API) not re-exported at the top level. This is to make it viable to run unit tests for parts of the DBus API which don't strictly depend on `sdbus`, namely tests for `crystalfontz.dbus.domain`.

For information on the DBus service and client CLI, check out [the core DBus documentation](../../dbus/index.md).

## crystalfontz.dbus.client

This module contains the core `DbusClient` class. This class is used for interacting with a live DBus service. This is where most users will want to start.

For more information, view the API docs for [`crystalfontz.dbus.client`](./crystalfontz.dbus.client.md).

## crystalfontz.dbus.domain

The DBus interface uses DBus compatible types, rather than the standard `crystalfontz` domain objects. The domain module contains type aliases and mapper classes for converting to and from `crystalfontz` domain objects and DBus types. While not strictly necessary for using the client, it's highly recommended.

For more information, view the API docs for [`crystalfontz.dbus.domain`](./crystalfontz.dbus.domain.md).

## crystalfontz.dbus.report

Like the main serial client in [`crystalfontz`](../crystalfontz.md), the `DbusInterface` and `DbusClient` classes may accept `ReportHandlers` - objects which handle key activity and temperature reports from the device. Particularly relevant are the `DbusClientReportHandler` and its subclasses.

For more information, view the API docs for [`crystalfontz.dbus.report`](./crystalfontz.dbus.report.md).

## crystalfontz.dbus.effects

This module contains abstractions for running effects with DBus. The core of this is a class implementing the `crystalfontz.effects.EffectClient` protocol. Note that the `DbusClient` doesn't implement effect convenience methods the same way the main `Client` does.

For more information, view the API docs for [`crystalfontz.dbus.effects`](./crystalfontz.dbus.effects.md).

## crystalfontz.dbus.config

Configuration for the DBus service is a little different than for the serial client. This is because the DBus service doesn't live reload a config after it changes. In other words, if you edit the config file, the DBus service's loaded config will show drift. This module helps track the drift between these sources.

For more information, view the API docs for [`crystalfontz.dbus.config`](./crystalfontz.dbus.config.md).

## crystalfontz.dbus.service

This module contains abstractions for running the DBus service. It will typically be used through [the service CLI](../../dbus/service.md). But this module may be useful for users wishing to embed it in another program.

For more information, view the API docs for [`crystalfontz.dbus.service`](./crystalfontz.dbus.service.md).

## crystalfontz.dbus.select

This module contains convenience functions for configuring which bus the program uses.

For more information, view the API docs for [`crystalfontz.dbus.select`](./crystalfontz.dbus.select.md).

## crystalfontz.dbus.interface

This module contains the core `DbusInterface` class. This is used directly when serving the interface, and subclassed by the client.

For more information, view the API docs for [`crystalfontz.dbus.interface`](./crystalfontz.dbus.interface.md).

