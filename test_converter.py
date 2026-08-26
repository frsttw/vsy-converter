import os
import gc
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from app import ConverterApp
from discord_export import run_command, Cancelled


class ConverterTests(unittest.TestCase):
    def setUp(self):
        gc.collect()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'LOCALAPPDATA': self.temp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app = ConverterApp()
        self.app.withdraw()
        self.addCleanup(self.app.destroy)

    def result(self):
        events = []
        while not self.app.events.empty():
            events.append(self.app.events.get_nowait())
        return events[-1][1]

    def test_conversion_collision_and_source_snapshot(self):
        source = self.directory / 'original.png'
        run_command([self.app.magick, '-size', '40x30', 'xc:purple', str(source)], threading.Event())
        original = source.read_bytes()
        self.app.files = []
        for _ in range(2):
            self.app._convert_all(self.directory, None, ('png', '90', True, 30), (source,))
            _, errors, converted, cancelled = self.result()
            self.assertEqual(errors, [])
            self.assertEqual(converted, 1)
            self.assertFalse(cancelled)
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue((self.directory / 'original (2).png').is_file())
        self.assertTrue((self.directory / 'original (3).png').is_file())
        self.assertFalse(list(self.directory.glob('.vsy-*')))

    def test_video_60fps(self):
        if not self.app.ffmpeg:
            self.skipTest('FFmpeg não instalado')
        source = self.directory / 'video.mp4'
        run_command([self.app.ffmpeg, '-loglevel', 'error', '-f', 'lavfi', '-i',
                     'testsrc2=size=160x90:rate=60:duration=1', '-y', str(source)], threading.Event())
        self.app._convert_all(self.directory, '120x120', ('gif', '90', True, 60), (source,))
        _, errors, converted, _ = self.result()
        self.assertEqual(errors, [])
        self.assertEqual(converted, 1)
        info = run_command([self.app.magick, 'identify', '-ping', '-format', '%W %H %T\n',
                            str(self.directory / 'video.gif')], threading.Event()).splitlines()
        self.assertEqual(len(info), 60)
        self.assertTrue(all(row.startswith('120 67 ') or row.startswith('120 68 ') for row in info))
        self.assertLessEqual(abs(sum(int(row.split()[2]) for row in info) - 100), 2)

    def test_cancel_running_process(self):
        cancelled = threading.Event()
        with self.assertRaises(Cancelled):
            run_command([sys.executable, '-c', 'import time; time.sleep(10)'], cancelled,
                        lambda elapsed: cancelled.set())

    def test_empty_destination_and_small_window(self):
        self.app.files = [self.directory / 'test.png']
        self.app.output_dir.set('')
        with patch('app.messagebox.showwarning') as warning:
            self.app.start_conversion()
        warning.assert_called_once()
        self.assertFalse(self.app.conversion_busy)
        self.app.deiconify()
        self.app.geometry('900x620')
        for index, button in ((0, self.app.convert_button), (1, self.app.discord_tab.export_button)):
            self.app.notebook.select(index)
            self.app.update()
            self.assertLessEqual(button.winfo_rooty() + button.winfo_height(),
                                 self.app.winfo_rooty() + self.app.winfo_height())


if __name__ == '__main__':
    unittest.main()
