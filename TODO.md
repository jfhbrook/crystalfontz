# TODO

- [-] Set device based on version output
- [ ] Report generator error handling

## Commands

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
- [-] poll keypad
- [-] store boot state
- [-] poke
- [ ] read status
  - [-] report status type
  - [ ] report command type
  - note, device and firmware specific

### Long Tail

- set baud rate
- set special character data
- configure key reporting
- set up temperature reporting
- read user flash
- write user flash
- read DOW
- DOW transactions
- set atx power switch
- send raw data to LCD
- set gpio
- read gpio

## Long Tail

- [ ] Debug logging
- [ ] Clean up method names
- [ ] Make character ROM device specific
- [ ] Retry a few times if packet if fails to respond within 250ms
