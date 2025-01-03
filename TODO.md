# TODO

### Basic Commands

- [x] ping
- [x] get versions
- [x] set line 1, set line 2
- [x] clear screen
- [x] set contrast
- [x] set backlight
- [x] set cursor style
- [x] set cursor position
- [x] reboot, reset or power off
  - (only tested reboot)
- [x] poll keypad
- [x] poke
- [x] send data to LCD
- [x] set special character data
- [x] set baud rate
- [x] store boot state
- [-] configure key reporting
- [-] setup temperature reporting
- [ ] set atx power switch functionality
- [ ] watchdoge
- [ ] read status
  - Specific to firmware of CFA533

## Features/Improvements

- [x] Marquee and screensaver
- [x] Set device based on version output
- [x] Lock when running command
- [-] Make character ROM device specific
  - Half done, still need to implement trie
- [x] Trim/pad special characters
- [ ] Compare temperature reporting to CFA555 and CFA633
- [ ] Load special characters from image files
- [ ] Retry a few times if packet if fails to respond within 250ms

### Obscure Commands

- CFA631 key legends
- read user flash
- write user flash
- read DOW
- DOW transactions
- send raw data to LCD
- set gpio
- read gpio


### Long Tail

- [ ] CLI tool
- [ ] Awaitable for close or exception
