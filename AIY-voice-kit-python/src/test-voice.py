#!/usr/bin/env python3

import argparse
import aiy.audio.say as say

def set_args():
    global args
    parser = argparse.ArgumentParser(description="Test Voice")
    parser.add_argument('words', nargs='*', help='Words to say')
    parser.add_argument("--lang", help='language BCP-47 code')
    parser.add_argument("--volume", help='volume. Default: 60', type=int)
    parser.add_argument("--pitch", help='pitch. Default: 130', type=int)
    args = parser.parse_args()

if __name__ == '__main__':
    set_args()
    say(args.words, args.lang, args.volume, args.pitch)