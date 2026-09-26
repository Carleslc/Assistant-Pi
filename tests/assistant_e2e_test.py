#!/usr/bin/env python3
"""End-to-end test harness for assistant.py without touching the physical button.

Replaces the Voice HAT button with a fake one that "presses" itself and then plays a
spoken command through the speaker (pico2wave), so the real microphone -> Cloud Speech ->
command dispatch -> TTS loop is exercised.

Requires ~/cloud_speech.json (Google Cloud service account with Speech-to-Text enabled).

Usage (from the repository root):
    python3 tests/assistant_e2e_test.py
"""
import subprocess
import sys
import threading
import time

import _path  # noqa: F401  (adds AIY-voice-kit-python/src to sys.path)
import aiy.voicehat

SCRIPT = ['repeat hello world', 'goodbye']


def speak(text, lang='en-US'):
    subprocess.call(['pico2wave', '-l', lang, '-w', '/tmp/e2e.wav', text])
    subprocess.call(['aplay', '-q', '/tmp/e2e.wav'])


class FakeButton:
    def __init__(self):
        self._script = iter(SCRIPT)

    def wait_for_press(self):
        try:
            phrase = next(self._script)
        except StopIteration:
            time.sleep(3600)
            return
        time.sleep(2)
        print('[e2e] button pressed, speaker says: %r' % phrase, flush=True)
        # recognizer starts listening right after wait_for_press() returns
        threading.Thread(target=lambda: (time.sleep(1.0), speak(phrase))).start()

    def on_press(self, callback):
        pass


aiy.voicehat.get_button = lambda: FakeButton()

import assistant  # noqa: E402

sys.argv = ['assistant.py']
assistant.set_args()
assistant.main()
print('[e2e] assistant exited cleanly')
