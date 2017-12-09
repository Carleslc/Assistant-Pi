"""An API to access Google Speech recognition service. Extended from aiy/cloudspeech.py"""

import aiy.cloudspeech

class _ExtendedCloudSpeechRecognizer(aiy.cloudspeech._CloudSpeechRecognizer):

    def __init__(self, credentials_file):
        super().__init__(credentials_file)

    def expect_phrases(self, phrases):
        wrapper = lambda: None
        def get_phrases():
            return phrases
        wrapper.get_phrases = get_phrases
        self._request.add_phrases(wrapper)

def get_recognizer(credentials_file=aiy.cloudspeech.CLOUDSPEECH_CREDENTIALS_FILE):
    return _ExtendedCloudSpeechRecognizer(credentials_file)