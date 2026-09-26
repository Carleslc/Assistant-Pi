# Assistant-Pi

Voice assistant experiments with the **Google AIY Voice Kit V1** (Voice HAT) on a Raspberry Pi 3.

The assistant code (`AIY-voice-kit-python/src`) was written in 2017-2019 against the original AIY
Python API (`aiy.audio`, `aiy.voicehat`, `aiy.i18n`, `aiy.cloudspeech`). That API was removed from
later AIY releases, so a copy of it is bundled in
[`AIY-voice-kit-python/src/aiy`](AIY-voice-kit-python/src/aiy) to keep the code running on the
**latest AIY image**.

## Requirements

- Raspberry Pi 3 + AIY Voice Kit V1 (Voice HAT, speaker, microphone board, arcade button with LED).
- SD card flashed with the last AIY system image:
  [AIY Kits Release 2021-04-02](https://github.com/google/aiyprojects-raspbian/releases/tag/v20210402)
  (Raspbian 10 Buster, Python 3.7). It already includes the Voice HAT driver, `pico2wave`, `RPi.GPIO`,
  `numpy` and the Google Cloud libraries.
- Google Cloud credentials (see [Get credentials](https://aiyprojects.withgoogle.com/voice-v1/#users-guide--get-credentials)):
  - `~/cloud_speech.json`: service account with the Speech-to-Text API enabled
    ([Change to the Cloud Speech API](https://aiyprojects.withgoogle.com/voice-v1/#custom-voice-user-interface-change-to-the-cloud-speech-api)).
    Needed by `assistant.py` and `cloudspeech_demo.py`.
  - `~/assistant.json`: OAuth client for the Google Assistant API (only for the Assistant demos of the AIY image).

## Setup

```bash
cd ~
git clone https://github.com/Carleslc/Assistant-Pi.git
cd Assistant-Pi

# The AIY 2021 image ships google-cloud-speech 2.0.0, but the AIY library in that same image
# (and its "Check Cloud" checkpoint) still uses the 1.x API. Downgrading fixes both.
sudo pip3 install "google-cloud-speech==1.3.2"

# Only for the offline wake word test
pip3 install --user vosk==0.3.45
```

Tips:

- The Voice HAT amplifier is loud. Lower the volume with `alsamixer` (30-50% is usually enough).
- `pico2wave` clips its own output above `<volume level="50">` (e.g. `aiy.audio.say(..., volume=100)`),
  which sounds like crackling on the speaker. Keep the TTS volume at 40-50 and control loudness
  with `alsamixer` instead.

## Run

Run the programs from `AIY-voice-kit-python/src`, so they use the bundled `aiy` library:

```bash
cd ~/Assistant-Pi/AIY-voice-kit-python/src
python3 assistant.py
```

Press the button and say a command:

- `repeat <text>`: says `<text>` back.
- `change language to spanish` / `english`: switches recognition and TTS language (i18n with gettext).
- `goodbye`: exits.
- `shutdown`: powers off the Raspberry Pi.

The button LED shows the assistant status (`starting`, `ready`, `listening`, `thinking`, `stopping`,
`power-off`, `error`). Try them with `python3 test-led.py`.

Other programs in the same folder:

- `python3 cloudspeech_demo.py`: press the button and say `turn on the light`, `turn off the light`,
  `blink`, `repeat <text>`, `goodbye` or `shutdown`.
- `python3 test-voice.py [--lang es-ES] [--volume 40] [--pitch 130] Hello world`: text to speech.
- `python3 test-led.py`: steps through the LED status patterns (press Enter to advance).

## Tests

Run from the repository root. Each test prints a final `*_OK` line and exits with code 0 on success.

| Test | What it checks | Command |
|---|---|---|
| Microphone | Records 3 s of silence, then the speaker talking, and compares levels | `python3 tests/mic_loopback_test.py` |
| Button + LED | LED states, then asks you to press the button (40 s) | `python3 tests/button_led_test.py` |
| Wake word (offline) | Detects "Ok Google" / "Hey Google" with [Vosk](https://alphacephei.com/vosk/), played by the speaker | `python3 tests/wake_test.py` |
| Assistant end-to-end | Runs `assistant.py` with a simulated button; the speaker says the commands | `python3 tests/assistant_e2e_test.py` |

`tests/wake_test.py --no-speaker` only listens, so you can say the wake phrase yourself.

## Repository layout

```
AIY-voice-kit-python/src/          Assistant code, demos and i18n
AIY-voice-kit-python/src/aiy/      Original AIY Python API (see below)
models/vosk-model-small-en-us-0.15 Vosk small English model for the offline wake word test
tests/                             Hardware and end-to-end tests
```

### `AIY-voice-kit-python/src/aiy`

Copy of `src/aiy` from [google/aiyprojects-raspbian](https://github.com/google/aiyprojects-raspbian)
at tag [`v20180413`](https://github.com/google/aiyprojects-raspbian/tree/v20180413/src/aiy), the last
release that includes the original API, without the Vision Kit modules. Apache License 2.0,
Copyright Google Inc.

Changes:

- `_apis/_speech.py`: also accepts `google-cloud-speech >= 2.0` (proto-plus types).
- `_drivers/_led.py`: switches the button LED off when the process exits (it could stay on).

Because this folder is found first when running from `AIY-voice-kit-python/src`, it takes precedence
over the newer `aiy` package installed in the AIY image (`~/AIY-projects-python`).

### `models/vosk-model-small-en-us-0.15`

[Vosk](https://alphacephei.com/vosk/models) small English model (Apache License 2.0), used by
`tests/wake_test.py`.
