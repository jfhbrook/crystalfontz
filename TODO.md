# TODO

## Features/Improvements

- [ ] Manually test features
  - [ ] key reporting (configure and log)
  - [ ] temperature reporting (configure and log)
  - [ ] live temperature display
  - [ ] read user flash area
- [ ] Stub unimplemented commands
  - [ ] Read DOW
  - [ ] Arbitrary DOW transactions
  - [ ] Set GPIO
  - [ ] Read GPIO
- [ ] Implement trie for character rom - makes general across devices
- [ ] Add character encoding to ROM when adding character
- [ ] Compare temperature reporting to CFA555 and CFA633
- [ ] Retry a few times if packet if fails to respond within 250ms
- [ ] Load special characters from image files
- [ ] CLI tool
- [ ] Convenience exports in `__init__.py`
- [ ] Do up documentation
- [ ] Open source release

### Future Tickets

- [ ] Awaitable for close or exception
- [ ] Test writing to user flash area
- [ ] Test sending commands directly to LCD controller
- [ ] Test ATX power switch functionality
- [ ] Test watchdog functionality
- [ ] Read DOW
- [ ] Arbitrary DOW transactions
- [ ] Set gpio
- [ ] Read gpio
- [ ] CFA631 key legends
- [ ] Generalize plusdeck integration test framework, write proper integration tests
