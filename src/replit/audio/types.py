# flake8: noqa
from typing import List
from typing_extensions import TypedDict
from enum import Enum


class ReaderType(Enum):
    "An Enum for the types of sources."

    def __str__(self) -> str:
        return self._value_

    def __repr__(self) -> str:
        return f"ReaderType.{self._name_}"

    wav_file = "wav"
    "ReaderType : The type for a .wav file."
    aiff_file = "aiff"
    "ReaderType : The type for a .aiff file."
    mp3_file = "mp3"
    "ReaderType : The type for a .mp3 file."
    tone = "tone"
    "ReaderType : The type for a generated tone."


class WaveType(Enum):
    "The different wave shapes that can be used for tone generation."

    def __str__(self) -> str:
        return self._value_

    WaveSine = 0
    "WaveType : The WaveSine wave shape."
    WaveTriangle = 1
    "WaveType : The Triangle wave shape."
    WaveSaw = 2
    "WaveType : The Saw wave shape."
    WaveSqr = 3
    "WaveType : The Square wave shape."


file_types: List[ReaderType] = [
    ReaderType.aiff_file,
    ReaderType.wav_file,
    ReaderType.mp3_file,
]
"The different file types for sources in a list."


class RequestArgs(TypedDict, total=False):
    "The additional arguments for a request that are type-specific."
    Pitch: float
    "float : The pitch/frequency of the tone. Only used if the request type is tone."
    Seconds: float

    "float : The duration for the tone to be played. Only used if the request type is tone."
    WaveType: WaveType or int
    "WaveType : The wave type of the tone. Only used if the request type is tone."
    Path: str
    "str : The path to the file to be read. Only used if the request is for a file type."


class RequestData(TypedDict):
    "A request to pid1 for a source to be played."
    ID: int
    "int : The ID of the source. Only used for updating a pre-existing source."
    Paused: bool or None
    "bool or None : Wether the source with the provided ID should be paused or not.  Can only be used when updating a source."
    Volume: float
    "float : The volume the source should be played at. (1 being 100%)"
    DoesLoop: bool
    "bool : Wether the source should loop / repeat or not. Defaults to false."
    LoopCount: int
    "int : How many times the source should loop / repeat.  Defaults to 0."
    Name: str
    "str : The name of the source."
    Type: ReaderType or str
    "ReaderType : The type of the source."
    Args: RequestArgs
    "RequestArgs : The additional arguments for the source."


class SourceData(TypedDict):
    """A source's raw data, as a payload."""

    Name: str
    "str : The name of the source."
    Type: str
    "str : The type of the source."
    Volume: float
    "float : The volume of the source."
    Duration: int
    "int : The duration of the source in milliseconds."
    Remaining: int
    "int : How many more milliseconds the source will be playing."
    Paused: bool
    "bool : Wether the source is paused or not."
    Loop: int
    "int : How many times the source will loop. If 0, the source will not repeat itself."
    ID: int
    "int : The ID of the source."
    EndTime: str
    "str : The estimated timestamp for when the source will finish playing."
    StartTime: str
    "str : When the source started playing."
    Request: RequestData
    "RequestData : The request used to create the source."


class AudioStatus(TypedDict):
    "The raw data read from /tmp/audioStatus.json."
    Sources: List[SourceData] or None
    "List[SourceData] : The sources that are know to the audio manager."
    Running: bool
    "bool : Wether the audio manager knows any sources or not."
    Disabled: bool
    "bool : Wether the audio manager is disabled or not."
