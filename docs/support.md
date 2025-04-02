# Support

## Devices

* `CFA533`: Most features have been tested with a real CFA533.
* `CFA633`: The CFA633 has **not** been tested. However, the documentation for the CFA533 includes some details on how the CFA633 differs from the CFA533, such that I have _ostensive_ support for it. Feel free to try it out, but be aware that it may have bugs.
* Other devices: Crystalfontz has other devices, but I haven't investigated them. As such, these other devices are currently unsupported. However, it's believed that it would be easy to add support for a device, by reading through its data sheet and implementing device-specific functionality in `crystalfontz.device`.

## Features

The basic features have all been tested with a real CFA533. However, there are a number of features when have **not** been tested, as I'm not using them. These features tend to be related to the CFA533's control unit capabilities:

* ATX power supply control functionality
* DOW and temperature related functionality
* GPIO pin related functionality
* Watchdog timer

These features have been filled in, they type check, and they _probably_ work, mostly. But it's not viable for me to test them. If you're in a position where you need these features, give them a shot and let me know if they work for you!
