#!/usr/bin/env bash

set -euxo pipefail

CRYSTALFONTZ_LOG_LEVEL="${CRYSTALFONTZ_LOG_LEVEL:-INFO}"
CRYSTALFONTZ_PORT="${CRYSTALFONTZ_PORT:-/dev/ttyUSB0}"

export CRYSTALFONTZ_LOG_LEVEL
export CRYSTALFONTZ_PORT

function confirm {
  read -p "${1} " -n 1 -r
  [[ "${REPLY}" =~ ^[Yy]$ ]]
}

crystalfontz backlight 0.2
crystalfontz contrast 0.4

confirm 'Did the backlight and contrast settings change?'

crystalfontz send 0 0 'Hello world!'

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

crystalfontz listen &
PID=$!

confirm 'Mash some buttons. Are events showing up?'
kill "${PID}"

crystalfontz effects marquee 1 'Josh is cool' &
PID=$!

confirm 'Is the LCD showing a marquee effect?'

kill "${PID}"

crystalfontz effects screensaver 'Josh!' &
PID=$!

confirm 'Is the LCD showing a screensaver effect?'

crystalfontz listen --for 1.0
crystalfontz effects --for 1.0 marquee 1 'Josh is cool'
crystalfontz effects --for 1.0 screensaver 'Josh!'

kill "${PID}"

echo "HOORAY! All tests pass."

# TODO: read user flash
# TODO: keypad poll
# TODO: keypad reporting
