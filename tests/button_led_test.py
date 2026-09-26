#!/usr/bin/env python3
"""Button + LED check using the original AIY API (aiy.voicehat).

Cycles the button LED through several states, then asks (through the speaker) to press
the button and waits up to 40 s. Always leaves the LED off on exit.

Usage (from the repository root):
    python3 tests/button_led_test.py
"""
import sys
import threading
import time

import RPi.GPIO as GPIO

import _path  # noqa: F401  (adds AIY-voice-kit-python/src to sys.path)
import aiy.audio
import aiy.voicehat

TIMEOUT_S = 40

GPIO.setwarnings(False)


def main():
    led = aiy.voicehat.get_led()
    try:
        for state in ('ON', 'BLINK', 'PULSE_QUICK', 'OFF'):
            print('LED', state, flush=True)
            led.set_state(getattr(aiy.voicehat.LED, state))
            time.sleep(1.5)

        pressed = threading.Event()
        aiy.voicehat.get_button().on_press(pressed.set)
        led.set_state(aiy.voicehat.LED.BLINK)
        aiy.audio.say('Press the button now')
        print('Waiting up to %d s for a button press...' % TIMEOUT_S, flush=True)
        ok = pressed.wait(TIMEOUT_S)
        led.set_state(aiy.voicehat.LED.ON if ok else aiy.voicehat.LED.OFF)
        aiy.audio.say('Button works' if ok else 'No button press detected')
        print('BUTTON_OK' if ok else 'BUTTON_TIMEOUT')
        return 0 if ok else 1
    finally:
        led.set_state(aiy.voicehat.LED.OFF)  # the LED driver also switches it off at exit


if __name__ == '__main__':
    sys.exit(main())
