"""
Represent entities in the crystalfontz domain model with dbus-compatible types, and
map between the crystalfontz and dbus domains.

While these classes don't all implement the same protocols, they do follow
a number of important conventions.

## Naming Conventions

In general classes corresponding to entities share their names, but with a postfix
naming convention.

Dbus types corresponding to entities in the crystalfontz domain have `T` appended
to them. For instance, the dbus type corresponding to `Optional[bytes]` is `OptBytesT`,
which corresponds to the "ay" dbus type signature. This applies to more complex
entities as well - for instance, the dbus type corresponding to the `Versions` response
is `VersionsT`.

Mappers - classes that map between entities and dbus types - have `M` appended to
their names. For intance, the mapper for `Optional[bytes]` and `OptBytesT` is called
`OptBytesM`.

## `pack` methods and `none` properties

Mappers which support it have a `pack` class method, which takes objects from the
crystalfontz domain and converts them into dbus data types. For instance, `OptBytesM`
packs an `Optional[bytes]` value into a `OptBytesT`.

Additionally, mappers representing optional data have a property called `none`,
which contains the value that the dbus client canonically interprets as `None`.
For instance, `TimeoutM.none` is equal to `-1.0`. Note that, in this case,
the dbus client treats any value less than 0 as `None`.

As a user, you would typically use these APIs when constructing arguments for the
dbus client. For example, if you were to call `dbus_client.ping`, it would look like
this:

```py
pong: PongT = await dbus_client.ping(
    b"Hello world!", TimeoutM.pack(timeout), RetryTimesM.pack(retry_times)
)
```

## `unpack` methods

Dbus client methods will not only *be called* with dbus-compatible types, but
will return dbus-compatible types as well. Sometimes these are sensible - in fact,
most methods return `None`. However, for non-trivial response types, you will likely
want to *unpack* them back into the crystalfontz domain. For example, the `ping`
command returns a `PongT`, and you will probably want to unpack it into a `Pong`
object:

```py
print(PongM.unpack(pong).response)
```
"""

from typing import List

from crystalfontz.dbus.domain.base import (
    OptBytesM,
    OptBytesT,
    OptFloatM,
    OptFloatT,
    OptStrM,
    OptStrT,
    RetryTimesM,
    RetryTimesT,
    TimeoutM,
    TimeoutT,
)
from crystalfontz.dbus.domain.config import ConfigM, ConfigT
from crystalfontz.dbus.domain.cursor import CursorStyleM, CursorStyleT
from crystalfontz.dbus.domain.device import DeviceStatusM, DeviceStatusT
from crystalfontz.dbus.domain.gpio import OptGpioSettingsM, OptGpioSettingsT
from crystalfontz.dbus.domain.keys import (
    KeypadBrightnessM,
    KeypadBrightnessT,
    KeyPressT,
    KeyStatesT,
    KeyStateT,
)
from crystalfontz.dbus.domain.lcd import LcdRegisterM, LcdRegisterT
from crystalfontz.dbus.domain.response import (
    DowDeviceInformationM,
    DowDeviceInformationT,
    DowTransactionResultM,
    DowTransactionResultT,
    GpioReadM,
    GpioReadT,
    KeyActivityReportM,
    KeyActivityReportT,
    KeypadPolledM,
    KeypadPolledT,
    LcdMemoryM,
    LcdMemoryT,
    PongM,
    PongT,
    TemperatureReportM,
    TemperatureReportT,
    VersionsM,
    VersionsT,
)
from crystalfontz.dbus.domain.temperature import (
    TemperatureDisplayItemM,
    TemperatureDisplayItemT,
    TemperatureUnitT,
)

__all__: List[str] = [
    "ConfigM",
    "ConfigT",
    "CursorStyleM",
    "CursorStyleT",
    "DeviceStatusM",
    "DeviceStatusT",
    "DowDeviceInformationM",
    "DowDeviceInformationT",
    "DowTransactionResultM",
    "DowTransactionResultT",
    "GpioReadM",
    "GpioReadT",
    "KeyActivityReportM",
    "KeyActivityReportT",
    "KeypadBrightnessM",
    "KeypadBrightnessT",
    "KeypadPolledM",
    "KeypadPolledT",
    "KeyPressT",
    "KeyStateT",
    "KeyStatesT",
    "LcdMemoryM",
    "LcdMemoryT",
    "LcdRegisterM",
    "LcdRegisterT",
    "OptBytesM",
    "OptBytesT",
    "OptGpioSettingsM",
    "OptGpioSettingsT",
    "OptFloatM",
    "OptFloatT",
    "OptStrM",
    "OptStrT",
    "PongM",
    "PongT",
    "RetryTimesM",
    "RetryTimesT",
    "TemperatureUnitT",
    "TemperatureDisplayItemM",
    "TemperatureDisplayItemT",
    "TemperatureReportM",
    "TemperatureReportT",
    "TimeoutM",
    "TimeoutT",
    "VersionsM",
    "VersionsT",
]
