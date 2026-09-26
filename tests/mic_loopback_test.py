#!/usr/bin/env python3
"""Microphone check using the original AIY API (aiy.audio).

Records 7 s: the first ~3 s are silence, then the speaker says a test phrase.
Compares the RMS level of both parts: a working mic shows a much louder second part.

Usage (from the repository root):
    python3 tests/mic_loopback_test.py
"""
import sys
import threading
import time
import wave

import numpy as np

import _path  # noqa: F401  (adds AIY-voice-kit-python/src to sys.path)
import aiy.audio

OUT = '/tmp/mic_test.wav'
MIN_RATIO = 3.0


def rms(x):
    return float(np.sqrt(np.mean(x ** 2))) if x.size else 0.0


def main():
    speaker = threading.Thread(target=lambda: (
        time.sleep(3.5), aiy.audio.say('Testing the microphone, one two three, testing')))
    speaker.start()
    # The AIY recorder is a one-shot thread: record only once per process.
    aiy.audio.record_to_wave(OUT, 7)
    speaker.join()

    with wave.open(OUT) as w:
        rate = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)
    quiet, loud = a[int(0.3 * rate):int(3.0 * rate)], a[int(4.0 * rate):]
    ratio = rms(loud) / max(rms(quiet), 1e-9)

    print('recording: %s (%d Hz, %.1f s)' % (OUT, rate, a.size / rate))
    print('silence rms=%.1f peak=%d' % (rms(quiet), np.abs(quiet).max()))
    print('speech  rms=%.1f peak=%d' % (rms(loud), np.abs(loud).max()))
    print('ratio   %.1fx' % ratio)
    ok = rms(loud) > MIN_RATIO * max(rms(quiet), 1.0)
    print('MIC_OK' if ok else 'MIC_SUSPECT')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
