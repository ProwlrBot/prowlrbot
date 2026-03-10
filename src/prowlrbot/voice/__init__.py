# -*- coding: utf-8 -*-
"""Voice interaction module for ProwlrBot dashboard.

Provides speech-to-text transcription and text-to-speech synthesis
with pluggable backends:

- **Transcription**: OpenAI Whisper API, local Whisper CLI, or browser
  Speech Recognition API (client-side).
- **Synthesis**: OpenAI TTS API or browser Speech Synthesis API
  (client-side).

Usage::

    from prowlrbot.voice.transcriber import WhisperTranscriber, TranscriberConfig
    from prowlrbot.voice.synthesizer import TextToSpeech, SynthesizerConfig
"""

from .transcriber import TranscriberConfig, WhisperTranscriber
from .synthesizer import SynthesizerConfig, TextToSpeech

__all__ = [
    "TranscriberConfig",
    "WhisperTranscriber",
    "SynthesizerConfig",
    "TextToSpeech",
]
