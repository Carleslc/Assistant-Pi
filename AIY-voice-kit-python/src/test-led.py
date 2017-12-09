#!/usr/bin/env python3

import aiy.voicehat

statuses = ["starting", "ready", "listening", "thinking", "stopping", "power-off", "error"]

if __name__ == '__main__':
    status_ui = aiy.voicehat.get_status_ui()
    for status in statuses:
        print(status)
        status_ui.status(status)
        input('Press Enter to change LED status...')
    print('-> Goodbye!')