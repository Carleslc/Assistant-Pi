#!/usr/bin/env python3
"""Offline wake-word + speech-to-text check with Vosk on the Voice HAT microphone.

Two recognizers share one live microphone stream:
  - kws: restricted grammar with the wake phrases only (cheap and robust keyword spotting)
  - stt: free English dictation, to see general recognition quality and the real-time factor
The speaker plays test phrases with pico2wave, so it is a real acoustic loop and no
human is needed. You can also speak yourself ("Ok Google", "Hey Google").

Usage (from the repository root):
    python3 tests/wake_test.py [--seconds 22] [--model models/vosk-model-small-en-us-0.15]
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time

from vosk import KaldiRecognizer, Model, SetLogLevel

RATE = 16000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL = os.path.join(ROOT, 'models', 'vosk-model-small-en-us-0.15')
WAKE = ['ok google', 'hey google']
PHRASES = ['Ok Google', 'What is the weather like today?', 'Hey Google']
TTS_VOLUME = 40  # pico2wave volume markup (0-100). Above ~50 pico2wave clips (audible crackle).


def say(text):
    markup = '<volume level="%d">%s</volume>' % (TTS_VOLUME, text)
    subprocess.call(['pico2wave', '-l', 'en-US', '-w', '/tmp/wake_say.wav', markup])
    subprocess.call(['aplay', '-q', '/tmp/wake_say.wav'])


def play_script():
    time.sleep(2.0)
    for phrase in PHRASES:
        print('>>> speaker: %s' % phrase, flush=True)
        say(phrase)
        time.sleep(1.5)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--seconds', type=float, default=22)
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--no-speaker', action='store_true', help='only listen (speak yourself)')
    args = parser.parse_args()

    SetLogLevel(-1)
    t0 = time.time()
    model = Model(args.model)
    print('model load %.1fs' % (time.time() - t0))
    kws = KaldiRecognizer(model, RATE, json.dumps(WAKE + ['[unk]']))
    stt = KaldiRecognizer(model, RATE)

    rec = subprocess.Popen(['arecord', '-q', '-f', 'S16_LE', '-r', str(RATE), '-c', '1', '-t', 'raw'],
                           stdout=subprocess.PIPE)
    speaker = None
    if not args.no_speaker:
        speaker = threading.Thread(target=play_script)
        speaker.start()

    wakes, audio_s, cpu_s = [], 0.0, 0.0
    end = time.time() + args.seconds
    try:
        while time.time() < end:
            chunk = rec.stdout.read(4000)  # 125 ms
            audio_s += len(chunk) / (2 * RATE)
            c0 = time.process_time()
            if kws.AcceptWaveform(chunk):
                text = json.loads(kws.Result())['text']
                if any(w in text for w in WAKE):
                    wakes.append(text)
                    print('*** WAKE detected: %r' % text, flush=True)
            if stt.AcceptWaveform(chunk):
                text = json.loads(stt.Result())['text']
                if text:
                    print('--- stt: %r' % text, flush=True)
            cpu_s += time.process_time() - c0
    finally:
        rec.kill()
        if speaker:
            speaker.join()

    print('audio %.1fs, cpu %.1fs, RTF %.2f (both recognizers)' % (audio_s, cpu_s, cpu_s / audio_s))
    print('WAKE_OK' if wakes else 'WAKE_MISS', len(wakes))
    return 0 if wakes else 1


if __name__ == '__main__':
    sys.exit(main())
