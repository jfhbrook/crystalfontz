# org.jfhbrook.crystalfontz (/)

## Interface: org.jfhbrook.crystalfontz

### Method: ClearScreen

**Arguments:** `d`, `x`

**Returns:** `void`

### Method: ConfigureKeyReporting

**Arguments:** `ay`, `ay`, `d`, `x`

**Returns:** `void`

### Method: ConfigureWatchdog

**Arguments:** `y`, `d`, `x`

**Returns:** `void`

### Method: DetectBaudRate

**Arguments:** `d`, `x`

**Returns:** `q`

### Method: DetectDevice

**Arguments:** `d`, `x`

**Returns:** `(sssqqqqq)`

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

**Returns:** `ay`

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

### Method: ResetHost

**Arguments:** `d`, `x`

**Returns:** `void`

### Method: SendCommandToLcdController

**Arguments:** `b`, `y`, `d`, `x`

**Returns:** `void`

### Method: SendData

**Arguments:** `y`, `y`, `ay`, `d`, `x`

**Returns:** `void`

### Method: SetAtxPowerSwitchFunctionality

**Arguments:** `(aybbbd)`, `d`, `x`

**Returns:** `void`

### Method: SetBacklight

**Arguments:** `d`, `d`, `d`, `x`

**Returns:** `void`

### Method: SetBaudRate

**Arguments:** `q`, `d`, `x`

**Returns:** `void`

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

### Method: SetLine1

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Method: SetLine2

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Method: SetSpecialCharacterData

**Arguments:** `y`, `t`, `d`, `x`

**Returns:** `void`

### Method: SetSpecialCharacterEncoding

**Arguments:** `s`, `y`

**Returns:** `void`

### Method: SetupLiveTemperatureDisplay

**Arguments:** `y`, `y`, `n`, `y`, `y`, `b`, `d`, `x`

**Returns:** `void`

### Method: SetupTemperatureReporting

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Method: ShutdownHost

**Arguments:** `d`, `x`

**Returns:** `void`

### Method: StoreBootState

**Arguments:** `d`, `x`

**Returns:** `void`

### Method: TestConnection

**Arguments:** `d`, `x`

**Returns:** `b`

### Method: Versions

**Arguments:** `d`, `x`

**Returns:** `s`

### Method: WriteUserFlashArea

**Arguments:** `ay`, `d`, `x`

**Returns:** `void`

### Property: Config

**Type:** `(sssssqdx)`

**Access:** `read`

**Annotations:**

- org.freedesktop.DBus.Property.EmitsChangedSignal: `false`

