#!/usr/bin/env python3

import os.path
import logging
import time
import argparse
import aiy.audio
import aiy.voicehat
import aiy.i18n
import cloudspeechrecognizer
from logging import info

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

lang = 'en-US' # es-ES

COMMANDS = {
    'repeat': 'repeat',
    'change language to': 'change_language'
}

END_COMMAND = 'goodbye'

def set_args():
    global args
    parser = argparse.ArgumentParser(description="Custom Assistant")
    parser.add_argument("--with-google", action='store_true', help='embed Google Assistant')
    args = parser.parse_args()

def main():
    try:
        start()
        loop()
        teardown()
    except Exception as e:
        error(e)

def start():
    global status_ui
    status_ui = None
    info('Starting...')
    status_ui = aiy.voicehat.get_status_ui()
    status_ui.status('starting')
    setup()
    status_ui.status('ready')
    # TODO: play beep sound
    info('Started')

def setup():
    global recognizer
    aiy.i18n.set_language_code(lang)
    info('Language: ' + aiy.i18n.get_language_code())

    recognizer = cloudspeechrecognizer.get_recognizer()
    recognizer.expect_phrases(['change language to', 'goodbye'])

    if args.with_google:
        info('Google Assistant is enabled')
    else:
        info('Google Assistant is NOT enabled')

def loop():
    global status_ui
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()
    end = False

    while not end:
        info('Press the button and speak')
        button.wait_for_press()
        info('Listening...')
        status_ui.status('listening')
        text = recognizer.recognize()
        status_ui.status('thinking')
        if not text:
            info('Sorry, I did not hear you.')
        else:
            info('You said "' + text + '"')
            if text == END_COMMAND:
                end = True
            for command, callback_name in COMMANDS.items():
                if command in text:
                    callback = globals()[callback_name]
                    callback(text)
                    break
        if not end:
            status_ui.status('ready')

def teardown():
    global status_ui
    try_do(lambda: aiy.audio.say('Goodbye!'))
    status_ui.status('power-off')
    info('Goodbye!')

def error(e):
    global status_ui
    info('Something was wrong')
    logging.exception(e)
    info('Terminating...')
    if status_ui:
        status_ui.status('error')
        time.sleep(3)
    teardown()
    exit(1)

# TODO: Move UTILS to another file
# TODO: Refactor COMMANDS to use Command class

# COMMANDS

def repeat(text):
    to_repeat = remove(text, 'repeat')
    aiy.audio.say(to_repeat)

def change_language(text):
    new_lang = remove(text, 'change language to')
    # TODO
    aiy.audio.say(new_lang)

# UTILS

def remove(text, substring):
    return text.replace(substring, '', 1).strip()

def try_do(something):
    try:
        something()
    except Exception:
        pass

if __name__ == '__main__':
    set_args()
    main()