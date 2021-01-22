# flake8: noqa
"""A library to play audio in a repl."""
from datetime import datetime, timedelta
import json
from os import path
import time
from typing import Any, List, Optional

from .types import (
    AudioStatus,
    file_types,
    ReaderType,
    RequestArgs,
    RequestData,
    SourceData,
    WaveType,
)


class InvalidFileType(Exception):
    """Exception for when a requested file's type isnt valid."""

    pass


class NoSuchSourceException(Exception):
    """Exception used when a source doesn't exist."""

    pass


class Source:
    """A Source is used to get audio that is sent to the user."""

    __payload: SourceData
    _loops: bool
    _name: str

    def __init__(self, payload: SourceData, loops: bool) -> None:
        """Initialize the class.

        Args:
            payload (SourceData): The payload for the source.
            loops (bool): How many times the source should loop.
        """
        self.__payload = payload
        self._loops = loops
        self._name = payload["Name"]

    def __get_source(self) -> SourceData or None:
        source = None
        with open("/tmp/audioStatus.json", "r") as f:
            data = json.loads(f.read())
            for s in data["Sources"]:
                if s["ID"] == self.id:
                    source = s
                    break
        if source:
            self.__payload = source
        return source

    def __update_source(self, **changes: Any) -> None:
        s = self.__get_source()
        if not s:
            raise NoSuchSourceException(
                f'No player with id "{id}" found! It might be done playing.'
            )
        s.update({key.title(): changes[key] for key in changes})
        with open("/tmp/audio", "w") as f:
            f.write(json.dumps(s))
        self.__get_source()

    @property
    def name(self) -> str:
        """The name of the source."""
        return self._name

    def get_start_time(self) -> datetime:
        """When the source started plaing."""
        timestamp_str = self.__payload["StartTime"]
        timestamp = datetime.strptime(timestamp_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
        return timestamp

    start_time: datetime = property(get_start_time)
    "Property wrapper for :py:meth:`~replit.Source.get_start_time`"

    @property
    def path(self) -> str or None:
        """The path to the source, if available."""
        data = self.__payload
        if ReaderType(data["Type"]) in file_types:
            return self.__payload["Request"]["Args"]["Path"]

    @property
    def id(self) -> int:
        """The ID of the source."""
        return self.__payload["ID"]

    def get_remaining(self) -> timedelta:
        """The estimated time remaining in the source's current loop."""
        data = self.__get_source()
        if not data:
            return timedelta(milliseconds=0)

        return timedelta(milliseconds=data["Remaining"])

    remaining: int = property(get_remaining)
    "Property wrapper for :py:meth:`~replit.Source.get_remaining`"

    def get_end_time(self) -> Optional[datetime]:
        """The estimated time when the source will be done playing.

        Returns:
            Optional[datetime]: The estimated time when the source will be done playing
                or None if it is already finished.
        """
        s = self.__get_source()
        if not s:
            return None

        timestamp_str = s["EndTime"]
        timestamp = datetime.strptime(timestamp_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")
        return timestamp

    end_time: datetime or None = property(get_end_time)
    "Property wrapper for :py:meth:`~replit.Source.get_end_time`"

    @property
    def does_loop(self) -> bool:
        """Whether the source repeats itself or not."""
        return self._loops

    @property
    def duration(self) -> timedelta:
        """The duration of the source."""
        return timedelta(millaseconds=self.__payload["Duration"])

    def get_volume(self) -> float:
        """The volume the source is set to."""
        self.__get_source()
        return self.__payload["Volume"]

    def set_volume(self, volume: float) -> None:
        """Set the volume.

        Args:
            volume (float): The volume the source should be set to.
        """
        self.__update_source(volume=volume)

    volume: float = property(get_volume, set_volume)
    "Property wrapper for `replit.Source.get_volume` and `replit.Source.set_volume`"

    def get_paused(self) -> bool:
        """Whether the source is paused."""
        self.__get_source()
        return self.__payload["Paused"]

    def set_paused(self, paused: bool) -> None:
        """Change if the source is paused.

        Args:
            paused (bool): Whether the source should be paused.
        """
        self.__update_source(paused=paused)

    paused = property(get_paused, set_paused)
    "Property wrapper for `replit.Source.get_paused` and `replit.Source.set_paused`"

    def get_loops_remaining(self) -> Optional[int]:
        """The remaining amount of times the file will restart.

        Returns:
            Optional[int]: The number of loops remaining or None if the source can't be
                found, either because it has finished playing or an error occured.
        """
        if not self._loops:
            return 0

        s = self.__get_source()
        if not s:
            return None

        if s["ID"] == self.id:
            loops = s["Loop"]

            return loops

    def set_loop(self, loop_count: int) -> None:
        """Set the remaining amount of loops for the source.

        Args:
            loop_count (int): How many times the source should repeat itself. Set to a
                negative value for infinite.
        """
        does_loop = loop_count != 0
        self._loops = does_loop
        self.__update_source(doesLoop=does_loop, loopCount=loop_count)

    loops_remaining: int or None = property(get_loops_remaining)
    "Property wrapper for :py:meth:`~replit.Source.get_loops_remaining`"

    def toggle_playing(self) -> None:
        """Play/pause the source."""
        self.set_paused(not self.paused)


class Audio:
    """The basic audio manager.

    Notes
    -----
    This is not intended to be called directly, instead use :py:const:`audio`.

    Using this in addition to `audio` can cause **major** issues.
    """

    __known_ids = []
    __names_created = 0

    def __gen_name(self) -> str:
        return f"Source {time.time()}"

    def __get_new_source(self, name: str, does_loop: bool) -> Source:
        new_source = None
        timeOut = datetime.now() + timedelta(seconds=2)

        while not new_source and datetime.now() < timeOut:
            try:
                sources = AudioStatus(self.read_status())["Sources"]
                new_source = SourceData([s for s in sources if s["Name"] == name][0])
            except IndexError:
                pass
            except json.JSONDecodeError:
                pass

        if not new_source:
            raise TimeoutError("Source was not created within 2 seconds.")

        return Source(new_source, does_loop)

    def play_file(
        self,
        file_path: str,
        volume: float = 1,
        does_loop: bool = False,
        loop_count: int = 0,
        name: Optional[str] = None,
    ) -> Source:
        """Sends a request to play a file, assuming the file is valid.

        Args:
            file_path (str): The path to the file that should be played. Can be
                absolute or relative.
            volume (float): The volume the source should be played at. (1 being
                100%)
            does_loop (bool): Wether the source should repeat itself or not. Note, if
                you set this you should also set loop_count.
            loop_count (int): How many times the source should repeat itself. Set to 0
                to have the source play only once, or set to a negative value for the
                source to repeat forever.
            name (str): The name of the file. Default value is a unique name for the
                source.

        Returns:
            Source: The source created with the provided data.

        Raises:
            FileNotFoundError: If the file is not found.
            InvalidFileType: If the file type is not valid.
        """
        name = name or self.__gen_name()

        if not path.exists(file_path):
            raise FileNotFoundError(f'File "{file_path}" not found.')

        file_type = file_path.split(".")[-1]

        if ReaderType(file_type) not in file_types:
            raise InvalidFileType(f"Type {file_type} is not supported.")

        data = RequestData(
            Type=file_type,
            Volume=volume,
            DoesLoop=does_loop,
            LoopCount=loop_count,
            Name=name,
            Args=RequestArgs(Path=file_path),
        )

        with open("/tmp/audio", "w") as p:
            p.write(json.dumps(dict(data)))

        return self.__get_new_source(name, does_loop)

    def play_tone(
        self,
        duration: float,
        pitch: int,
        wave_type: WaveType,
        does_loop: bool = False,
        loop_count: int = 0,
        volume: float = 1,
        name: Optional[str] = None,
    ) -> Source:
        """Play a tone from a frequency and wave type.

        Args:
            duration (float): How long the tone should be played (in seconds).
            pitch (int): The frequency the tone should be played at.
            wave_type (WaveType): The wave shape used to generate the tone.
            does_loop (bool): Wether the source should repeat itself or not. Note, if
                you set this you should also set loop_count.
            loop_count (int): How many times the source should repeat itself. Set to 0
                to have the source play only once, or set to a negative value for the
                source to repeat forever.
            volume (float): The volume the tone should be played at (1 being 100%).
            name (str): The name of the file. Default value is a unique name for the
                source.

        Returns:
            Source: The source for the tone.
        """
        name = name or self.__gen_name()

        # ensure the wave type is valid. This will throw an error if it isn't.
        WaveType(wave_type)

        data = RequestData(
            Name=name,
            DoesLoop=does_loop,
            LoopCount=loop_count,
            Volume=volume,
            Type=str(ReaderType.tone),
            Args=RequestArgs(
                WaveType=wave_type,
                Pitch=pitch,
                Seconds=duration,
            ),
        )

        with open("/tmp/audio", "w") as f:
            f.write(json.dumps(data))

        return self.__get_new_source(name, does_loop)

    def get_source(self, source_id: int) -> Source or None:
        """Get a source by it's ID.

        Args:
            source_id (int): The ID for the source that should be found.

        Raises:
            NoSuchSourceException: If the source isnt found or there isn't any sources
                known to the audio manager.

        Returns:
            Source: The source with the ID provided.
        """
        source = None
        with open("/tmp/audioStatus.json", "r") as f:
            data = AudioStatus(json.loads(f.read()))
            if not data["Sources"]:
                raise NoSuchSourceException("No sources exist yet.")
            for s in data["Sources"]:

                if s["ID"] == int(source_id):
                    source = s
                    break
        if not source:
            raise NoSuchSourceException(f'Could not find source with ID "{source_id}"')
        return Source(source, source["Loop"])

    def read_status(self) -> AudioStatus:
        """Get the raw data for what's playing.

        This is an api call, and shouldn't be needed for general usage.

        Returns:
            AudioStatus: The contents of /tmp/audioStatus.json
        """
        with open("/tmp/audioStatus.json", "r") as f:
            data = AudioStatus(json.loads(f.read()))
            if data["Sources"] is None:
                data["Sources"]: List[SourceData] = []
            return data

    def get_playing(self) -> List[Source]:
        """Get a list of playing sources.

        Returns:
            List[Source]: A list of sources that aren't paused.
        """
        data = self.read_status()
        sources = data["Sources"]
        return [Source(s, s["Loop"]) for s in sources if not s["Paused"]]

    def get_paused(self) -> List[Source]:
        """Get a list of paused sources.

        Returns:
            List[Source]: A list of sources that are paused.
        """
        data = self.read_status()
        sources = data["Sources"]
        return [Source(s, s["Loop"]) for s in sources if s["Paused"]]

    def get_sources(self) -> List[Source]:
        """Gets all sources.

        Returns:
            List[Source]: Every source known to the audio manager, paused or playing.
        """
        data = self.read_status()
        sources = data["Sources"]
        return [Source(s, s["Loop"]) for s in sources]
