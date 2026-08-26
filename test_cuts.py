import tempfile
import threading
import unittest
from pathlib import Path
import os
from unittest.mock import patch

from app import find_ffmpeg, find_magick, ConverterApp
from discord_export import run_command
from media_cutter import cut_media, parse_timecode


class CutMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.ffmpeg = find_ffmpeg()
        self.magick = find_magick()
        if not self.ffmpeg or not self.magick:
            self.skipTest("ImageMagick e FFmpeg são necessários")

    def test_parse_timecode(self):
        self.assertEqual(parse_timecode("12.5"), 12.5)
        self.assertEqual(parse_timecode("00:01:02.500"), 62.5)
        self.assertIsNone(parse_timecode(""))
        with self.assertRaises(ValueError):
            parse_timecode("-1")

    def test_video_copy_without_recompression(self):
        source = self.directory / "video.mp4"
        run_command([self.ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                     "-i", "testsrc2=size=160x90:rate=30:duration=2", "-y", str(source)], threading.Event())
        original = source.read_bytes()
        result, summary = cut_media(self.ffmpeg, source, self.directory, "trecho", 0.5, 1.5)
        self.assertEqual(result.suffix, ".mp4")
        self.assertIn("sem recompressão", summary)
        self.assertTrue(result.is_file())
        self.assertEqual(source.read_bytes(), original)

    def test_audio_copy_and_gif_animation(self):
        audio = self.directory / "audio.wav"
        run_command([self.ffmpeg, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                     "-i", "sine=frequency=440:duration=2", "-c:a", "pcm_s16le", "-y", str(audio)], threading.Event())
        audio_cut, audio_summary = cut_media(self.ffmpeg, audio, self.directory, "som", 0.25, 1.25)
        self.assertEqual(audio_cut.suffix, ".wav")
        self.assertIn("sem recompressão", audio_summary)

        gif = self.directory / "animado.gif"
        run_command([self.magick, "-delay", "10", "-size", "80x40", "xc:red",
                     "-delay", "10", "-size", "80x40", "xc:blue", "-loop", "0", str(gif)], threading.Event())
        gif_cut, gif_summary = cut_media(self.ffmpeg, gif, self.directory, "gif-corte", 0, 0.2)
        self.assertEqual(gif_cut.suffix, ".gif")
        self.assertIn("GIF recodificado", gif_summary)
        self.assertTrue(gif_cut.is_file())

    def test_invalid_range_does_not_publish(self):
        source = self.directory / "video.mp4"
        source.write_bytes(b"placeholder")
        with self.assertRaises(ValueError):
            cut_media(self.ffmpeg, source, self.directory, "falha", 5, 4)
        self.assertFalse((self.directory / "falha.mp4").exists())

    def test_cut_tab_layout_and_saved_folder(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.directory)}):
            app = ConverterApp()
            app.withdraw()
            try:
                self.assertEqual(len(app.notebook.tabs()), 3)
                tab = app.cut_tab
                saved = self.directory / "cortes"
                tab.folder.set(str(saved))
                tab.save_folder()
                tab.folder.set(tab.app._saved_output_dir("cortes"))
                self.assertEqual(tab.folder.get(), str(saved))
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
