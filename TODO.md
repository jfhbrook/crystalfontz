# TODO

### The Basics

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
- [-] store boot state
- [x] poke
- [x] send data to LCD

## Features/Improvements

- [x] Marquee and screensaver
- [x] Set device based on version output
- [-] Lock when running command
- [ ] Make character ROM device specific
- [ ] Retry a few times if packet if fails to respond within 250ms

### More Interesting Commands

- [ ] set baud rate
- [ ] set special character data
- [ ] configure key reporting
- [ ] set up temperature reporting
- [ ] set atx power switch
- [ ] read status

### Obscure Commands

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
