try:
    from XQlightPy.position import Position
    from XQlightPy.search import Search
    from XQlightPy.cchess import move2Iccs, Iccs2move
    from XQlightPy.play_against_ai import print_board as pb
    AI_AVAILABLE = True
    AI_IMPORT_ERROR = None
except Exception as exc:
    Position = None
    Search = None
    move2Iccs = None
    Iccs2move = None
    pb = None
    AI_AVAILABLE = False
    AI_IMPORT_ERROR = exc

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
    VOICE_IMPORT_ERROR = None
except Exception as exc:
    sr = None
    VOICE_AVAILABLE = False
    VOICE_IMPORT_ERROR = exc

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    PYAUDIO_IMPORT_ERROR = None
except Exception as exc:
    pyaudio = None
    PYAUDIO_AVAILABLE = False
    PYAUDIO_IMPORT_ERROR = exc

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
    SOUNDDEVICE_IMPORT_ERROR = None
except Exception as exc:
    sd = None
    SOUNDDEVICE_AVAILABLE = False
    SOUNDDEVICE_IMPORT_ERROR = exc
