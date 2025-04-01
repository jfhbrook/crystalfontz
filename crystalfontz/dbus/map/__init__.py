"""
Map values between crystalfontz's domain model and dbus types.

While these classes don't all implement the same protocols, they do follow
a number of important conventions.

## Naming Conventions

Mappers have `M` appended to their class names. For example, the mapper for `bytes`
is called `BytesM`.

Otherwise, classes corresponding to a type share their names. For example, the mapper
for a `Versions` response is named `VersionsM`.

## `pack` methods and `none` properties

Mappers which support it have a `pack` class method, which takes objects from the
crystalfontz domain and convert them into dbus data types. For instance, `BytesM`
packs a `bytes` value into a `List[int]`, which corresponds to the `ay` dbus type.

Additionally, mappers representing optional data have a property called `none`,
which contains the value that the dbus client canonically interprets as `None`.
For instance, `TimeoutM.none` is equal to `-1.0`. Note that, in this case,
the dbus client treats any value less than 0 as `None`.

As a user, you would typically use these APIs when constructing arguments for the
dbus client. For example, if you were to call `dbus_client.ping`, it would look like
this:

```py
pong: List[int] = await dbus_client.ping(
    BytesM.pack(b"Hello world!"), TimeoutM.none, RetryTimesM.none
)
```

## `unpack` methods

Many dbus client methods return sensible values - in fact, most methods return `None`.
However, for non-trivial response types, you may wish to unpack the responses
back into the crystalfontz domain. For example, the `ping` command returns a
`List[int]`, and you will probably want to convert it back into a `Pong` object:

```py
print(PongM.unpack(pong).response)
```

Alternately, the `Pong` response is simple enough that calling `BytesM.unpack` is
sufficient. But there may be stronger motivations for other response types, which have
more complicated structures or rich reprs.

## `t` property

The `t` property encodes the dbus signature corresponding to the type. Users will
typically not need to use this property, but it may be considered as documentation.
"""

from typing import List

from crystalfontz.dbus.map.base import (
    BytesM,
    BytesT,
    OptBytesM,
    OptBytesT,
    OptPosFloatM,
    OptPosFloatT,
    RetryTimesM,
    RetryTimesT,
    TimeoutM,
    TimeoutT,
)
from crystalfontz.dbus.map.config import ConfigM, ConfigT
from crystalfontz.dbus.map.cursor import CursorStyleM, CursorStyleT
from crystalfontz.dbus.map.keys import KeyPressT, KeyStatesT, KeyStateT
from crystalfontz.dbus.map.lcd import LcdRegisterM, LcdRegisterT
from crystalfontz.dbus.map.response import (
    DowDeviceInformationM,
    DowDeviceInformationT,
    DowTransactionResultM,
    DowTransactionResultT,
    KeypadPolledM,
    KeypadPolledT,
    LcdMemoryM,
    LcdMemoryT,
    PongM,
    PongT,
    VersionsM,
    VersionsT,
)
from crystalfontz.dbus.map.temperature import (
    TemperatureDisplayItemM,
    TemperatureDisplayItemT,
    TemperatureUnitT,
)

__all__: List[str] = [
    "BytesM",
    "BytesT",
    "ConfigM",
    "ConfigT",
    "CursorStyleM",
    "CursorStyleT",
    "DowDeviceInformationM",
    "DowDeviceInformationT",
    "DowTransactionResultM",
    "DowTransactionResultT",
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
    "OptPosFloatM",
    "OptPosFloatT",
    "PongM",
    "PongT",
    "RetryTimesM",
    "RetryTimesT",
    "TemperatureUnitT",
    "TemperatureDisplayItemM",
    "TemperatureDisplayItemT",
    "TimeoutM",
    "TimeoutT",
    "VersionsM",
    "VersionsT",
]
