# org.jfhbrook.crystalfontz (/)

## Interface: org.jfhbrook.crystalfontz

### Method: ClearScreen

**Arguments:** `d`, `x`

**Returns:** `void`

### Method: ConfigureKeyReporting

**Arguments:** `ay`, `ay`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: ConfigureWatchdog

**Arguments:** `y`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: DetectBaudRate

**Arguments:** `d`, `x`

**Returns:** `q`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: DetectDevice

**Arguments:** `d`, `x`

**Returns:** `(sssqqqqq)`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: DowTransaction

**Arguments:** `y`, `q`, `ay`, `d`, `x`

**Returns:** `q`

### Method: Ping

**Arguments:** `ay`, `d`, `x`

**Returns:** `ay`

### Method: PollKeypad

**Arguments:** `d`, `x`

**Returns:** `((bbb))`

### Method: ReadDowDeviceInformation

**Arguments:** `y`, `d`, `x`

**Returns:** `t`

### Method: ReadGpio

**Arguments:** `y`, `d`, `x`

**Returns:** `y`

### Method: ReadLcdMemory

**Arguments:** `q`, `d`, `x`

**Returns:** `ay`

### Method: ReadStatus

**Arguments:** `d`, `x`

**Returns:** `ay`

### Method: ReadUserFlashArea

**Arguments:** `d`, `x`

**Returns:** `ay`

### Method: RebootLcd

**Arguments:** `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: ResetHost

**Arguments:** `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SendCommandToLcdController

**Arguments:** `b`, `y`, `d`, `x`

**Returns:** `void`

### Method: SendData

**Arguments:** `y`, `y`, `ay`, `d`, `x`

**Returns:** `void`

### Method: SetAtxPowerSwitchFunctionality

**Arguments:** `(aybbbd)`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SetBacklight

**Arguments:** `d`, `d`, `d`, `x`

**Returns:** `void`

### Method: SetBaudRate

**Arguments:** `q`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SetContrast

**Arguments:** `d`, `d`, `x`

**Returns:** `void`

### Method: SetCursorPosition

**Arguments:** `y`, `y`, `d`, `x`

**Returns:** `void`

### Method: SetCursorStyle

**Arguments:** `q`, `d`, `x`

**Returns:** `void`

### Method: SetGpio

**Arguments:** `y`, `y`, `q`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SetLine1

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Method: SetLine2

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Method: SetSpecialCharacterData

**Arguments:** `y`, `t`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SetSpecialCharacterEncoding

**Arguments:** `s`, `y`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: SetupLiveTemperatureDisplay

**Arguments:** `y`, `y`, `n`, `y`, `y`, `b`, `d`, `x`

**Returns:** `void`

### Method: SetupTemperatureReporting

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: ShutdownHost

**Arguments:** `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: StoreBootState

**Arguments:** `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Method: TestConnection

**Arguments:** `d`, `x`

**Returns:** `b`

### Method: Versions

**Arguments:** `d`, `x`

**Returns:** `s`

### Method: WriteUserFlashArea

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

**Annotations:**

- org.freedesktop.systemd1.Privileged: `true`

### Property: Config

**Type:** `(sssssqdx)`

**Access:** `read`

**Annotations:**

- org.freedesktop.DBus.Property.EmitsChangedSignal: `false`

### Signal: KeyActivityReports

**Type**: `y`

### Signal: TemperatureReports

**Type**: `d`

