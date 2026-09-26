"""Make AIY-voice-kit-python/src importable from the tests (aiy library + assistant code)."""
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'AIY-voice-kit-python', 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
os.chdir(SRC)  # assistant.py loads its translations from ./locale
