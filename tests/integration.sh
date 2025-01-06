#!/usr/bin/env bash

set -euo pipefail

CRYSTALFONTZ_LOG_LEVEL="${CRYSTALFONTZ_LOG_LEVEL:-INFO}"
CRYSTALFONTZ_PORT="${CRYSTALFONTZ_PORT:-/dev/ttyUSB0}"

function confirm {
  read -p "${1} " -n 1 -r
  [[ "${REPLY}" =~ ^[Yy]$ ]]
}

crystalfontz backlight 0.2
crystalfontz contrast 0.9

confirm 'Did the backlight and contrast settings change?'

crystalfontz send 1 'Hello world!'

confirm 'Did the LCD display "Hello world!"?'

crystalfontz line 1 'Line 1'
crystalfontz line 2 'Line 2'

confirm 'Does the LCD display "Line 1" and "Line 2"?'

crystalfontz clear

confirm 'Did the LCD clear?'

crystalfontz cursor position 1 3
crystalfontz cursor style BLINKING_BLOCK

confirm 'Did the cursor move and start blinking?'

[[ "$(crystalfontz ping pong)" == 'pong' ]]

crystalfontz status
crystalfontz versions
crystalfontz power reboot-lcd

confirm 'Did the LCD reboot?'

crystalfontz effects marquee 1 'Josh is cool' &
PID=$!

confirm 'Is the LCD showing a marquee effect?'

kill "${PID}"

crystalfontz effects screensaver 'Josh!' &
PID=$!

confirm 'Is the LCD showing a screensaver effect?'

kill "${PID}"

# TODO: read user flash
# TODO: keypad poll
# TODO: keypad reporting
