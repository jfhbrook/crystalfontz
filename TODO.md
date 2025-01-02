# TODO

## High Priority

- [ ] Write character table abstraction
- [ ] Write device abstraction

## Commands

### The Basics

- [x] ping
- [x] get versions
- [x] set line 1, set line 2
- [ ] clear screen
- [ ] read status
  - [-] report status type
  - [ ] report command type
  - note, device and firmware specific
- [ ] set contrast
- [ ] set backlight
- [ ] set cursor style
- [ ] set cursor position
- [ ] poll keypad
- [ ] reboot, reset or power off
- [ ] store boot state
- [ ] poke

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

- [ ] Retry a few times if packet if fails to respond within 250ms
