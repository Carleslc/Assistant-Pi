#!/usr/bin/env python3

import os.path
import logging
import time
import argparse
import aiy.audio
import aiy.voicehat
import aiy.i18n
import cloudspeechrecognizer
import aiy.assistant.auth_helpers
from logging import info
from google.assistant.library import Assistant
from google.assistant.library.event import EventType

# TODO: Add Google Assistant with 'Ok, Google' if --with-google is set
# TODO: Set custom volume
# TODO: Internationalization script (gettext commands)
# TODO: Manga Command (download to share)
# TODO: Move UTILS to another file
# TODO: Stop audio if button is pressed while speaking
# TODO: Refactor COMMANDS to use Command class
# TODO: Alarm command
# TODO: Manga Command (send to kindle)

DEFAULT_LANGUAGE = 'en-US'

# Lazy-initialized variables
status_ui = None
recognizer = None

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

def main():
    try:
        start()
        loop()
        teardown()
    except Exception as e:
        error(e)

def set_language(lang_code):
    global recognizer, lang_codes, commands, end_command
    if recognizer:
        recognizer.reset_expected_phrases()
    aiy.i18n.set_locale_dir('locale')
    aiy.i18n.set_language_code(lang_code, gettext_install=True)
    lang_codes = {
        _('english'): 'en-US',
        _('spanish'): 'es-ES',
    }
    commands = {
        _('repeat'): 'repeat',
        _('change language to'): 'change_language',
        _('shutdown'): 'shutdown'
    }
    end_command = _('goodbye')
    command_list = list(commands.keys())
    command_list.append(end_command)
    recognizer = cloudspeechrecognizer.get_recognizer()
    recognizer.expect_phrases(command_list)
    info('Language: ' + aiy.i18n.get_language_code())
    info('Commands Available:')
    info(', '.join(recognizer.expected_phrases()))

def set_args():
    global args
    parser = argparse.ArgumentParser(description="Custom Assistant")
    parser.add_argument("--with-google", action='store_true', help='embed Google Assistant')
    args = parser.parse_args()

def start():
    global status_ui
    info('Starting...')
    status_ui = aiy.voicehat.get_status_ui()
    status_ui.status('starting')
    setup()
    status_ui.status('ready')
    aiy.audio.say(_('Hello'))
    info('Started')

def setup():
    set_language(DEFAULT_LANGUAGE)

    if args.with_google:
        info('Google Assistant is enabled')
    else:
        info('Google Assistant is NOT enabled')

def loop():
    global status_ui
    button = aiy.voicehat.get_button()
    aiy.audio.get_recorder().start()
    end = False

    while not end:
        info('Press the button and speak')
        button.wait_for_press()
        status_ui.status('listening')
        info('Listening...')
        text = recognizer.recognize()
        status_ui.status('thinking')
        valid = False
        if not text:
            info(_('Sorry, I did not understand you.'))
        else:
            info('You said "' + text + '"')
            if text == end_command:
                end = True
            for command, callback_name in commands.items():
                if command in text:
                    callback = globals()[callback_name]
                    valid = True
                    callback(text)
                    break
        if not end:
            if not valid:
                led_error()
                #aiy.audio.say(_('Sorry, I did not understand you.'))
            status_ui.status('ready')

def teardown():
    global status_ui
    if status_ui:
        status_ui.status('stopping')
    try_do(lambda: aiy.audio.say(_('Goodbye!')))
    if status_ui:
        status_ui.status('power-off')
        time.sleep(1)
        logging.debug('LED power-off')
    info('Goodbye!')

def error(e):
    global status_ui
    info('Something was wrong')
    logging.exception(e)
    info('Terminating...')
    led_error()
    teardown()
    exit(1)

def led_error():
    if status_ui:
        status_ui.status('error')
        time.sleep(3)

# COMMANDS

def repeat(text):
    to_repeat = remove(text, _('repeat'))
    if to_repeat:
        aiy.audio.say(to_repeat)

def change_language(text):
    new_lang = remove(text, _('change language to')).lower()
    lang_code = lang_codes[new_lang]
    if lang_code:
        set_language(lang_code)
        translated_new_lang = reverse_lookup(lang_codes, lang_code)
        aiy.audio.say(_('Language set to ') + translated_new_lang)
    else:
        # TODO: i18n with parameters
        aiy.audio.say(_('Language ') + new_lang + _(' is not supported'))

def shutdown(text):
    teardown()
    subprocess.call(['sudo', 'shutdown', '-h', 'now'])

# UTILS

def remove(text, substring):
    return text.replace(substring, '', 1).strip()

def try_do(something):
    try:
        something()
    except Exception:
        pass

def reverse_lookup(d, value):
    return next(k for k, v in d.items() if v == value)

if __name__ == '__main__':
    set_args()
    main()