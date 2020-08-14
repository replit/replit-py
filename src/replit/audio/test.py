# flake8: noqa
import time
import unittest
import replit
from .. import audio
from . import types

test_file = "../test.mp3"


class TestAudio(unittest.TestCase):
    def test_creation(self):
        source = audio.play_file(test_file)
        self.assertEqual(source.path, test_file)
        source.paused = True
        time.sleep(1)
        self.assertEqual(source.paused, True, "Pausing Source")

    def test_pause(self):
        source = audio.play_file(test_file)
        source.volume = 2
        time.sleep(1)
        self.assertEqual(source.volume, 2, "Volume set to 2")

        source.paused = True
        time.sleep(1)
        self.assertEqual(source.paused, True, "Pausing Source")

        source.volume = 0.2
        time.sleep(1)
        self.assertEqual(source.volume, 0.2, "Volume set to .2")

        source.paused = True
        time.sleep(1)
        self.assertEqual(source.paused, True, "Pausing Source")

    def test_loop_setting(self):
        source = audio.play_file(test_file)

        self.assertEqual(source.loops_remaining, 0, "0 loops remaining")
        source.set_loop(2)
        time.sleep(1)

        self.assertEqual(source.loops_remaining, 2, "2 loops remaining")
        source.paused = True
        time.sleep(1)
        self.assertEqual(source.paused, True, "Pausing Source")

    def test_other(self):
        source = audio.play_file(test_file)

        self.assertIsNotNone(source.end_time)
        self.assertIsNotNone(source.start_time)
        self.assertIsNotNone(source.remaining)
        source.paused = True
        time.sleep(1)
        self.assertEqual(source.paused, True, "Pausing Source")

    def test_tones(self):
        try:
            audio.play_tone(2, 400, 2)
        except TimeoutError or ValueError as e:
            self.fail(e)


if __name__ == "__main__":
    unittest.main()
