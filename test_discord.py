import os
import subprocess
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from app import find_magick, ConverterApp
from discord_export import convert_image, PRESETS, Cancelled


class DiscordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.magick = find_magick()
        if not self.magick:
            self.skipTest("ImageMagick não instalado")
        self.source = self.directory / "imagem teste.png"
        self.run_magick("-size", "300x120", "xc:red", str(self.source))

    def run_magick(self, *args):
        return subprocess.check_output([self.magick, *args], text=True, creationflags=0x08000000)

    def test_static_dimensions_fit_collision_and_original(self):
        original = self.source.read_bytes()
        for kind in PRESETS:
            for fit in ("crop", "contain"):
                path, summary = convert_image(self.magick, self.source, self.directory, kind, fit, "AUTO")
                p = PRESETS[kind]
                self.assertEqual(self.run_magick("identify", "-format", "%wx%h", str(path)), f"{p.width}x{p.height}")
                self.assertLess(path.stat().st_size, p.max_bytes)
                again, _ = convert_image(self.magick, self.source, self.directory, kind, fit, "AUTO")
                self.assertNotEqual(again, path)
        self.assertEqual(self.source.read_bytes(), original)

    def test_gif_preserves_frames_and_timing(self):
        gif = self.directory / "animado.gif"
        self.run_magick("-delay", "10", "-size", "80x60", "xc:red", "-delay", "20", "-size", "80x60", "xc:blue", "-loop", "0", str(gif))
        for kind in PRESETS:
            path, _ = convert_image(self.magick, gif, self.directory, kind, "crop", "AUTO")
            self.assertEqual(path.suffix, ".gif")
            self.assertEqual(self.run_magick("identify", "-format", "%T\n", str(path)), "10\n20\n")
        path, summary = convert_image(self.magick, gif, self.directory, "avatar", "contain", "PNG")
        self.assertIn("primeiro quadro", summary)
        self.assertEqual(self.run_magick("identify", "-format", "%n", str(path)), "1")

    def test_oversized_is_not_published(self):
        destination = self.directory / "saida"
        with patch.dict(PRESETS, {"banner": replace(PRESETS["banner"], max_bytes=1)}):
            with self.assertRaisesRegex(RuntimeError, "acima da margem"):
                convert_image(self.magick, self.source, destination, "banner", "crop", "PNG")
        self.assertEqual(list(destination.iterdir()), [])

    def test_cancel(self):
        event = threading.Event()
        event.set()
        with self.assertRaises(Cancelled):
            convert_image(self.magick, self.source, self.directory, "avatar", "crop", "AUTO", event)

    def test_tab_and_separate_folders(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.directory)}):
            app = ConverterApp()
            try:
                self.assertEqual(len(app.notebook.tabs()), 2)
                tab = app.discord_tab
                tab.folder.set(str(self.directory / "avatars"))
                tab.save_folder()
                tab.kind.set("banner")
                tab.target_changed()
                tab.folder.set(str(self.directory / "banners"))
                tab.save_folder()
                tab.kind.set("avatar")
                tab.target_changed()
                self.assertEqual(tab.folder.get(), str(self.directory / "avatars"))
                app.notebook.select(tab)
                app.update()
                self.assertLessEqual(tab.export_button.winfo_rooty() + tab.export_button.winfo_height(), app.winfo_rooty() + app.winfo_height())
            finally:
                app.destroy()

    def test_export_through_tab_worker(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.directory)}):
            app = ConverterApp()
            app.withdraw()
            try:
                tab = app.discord_tab
                tab.source.set(str(self.source))
                tab.folder.set(str(self.directory / "ui-export"))
                tab.start()
                def check():
                    if tab.busy:
                        app.after(50, check)
                    else:
                        app.quit()
                app.after(50, check)
                timeout = app.after(15000, app.quit)
                app.mainloop()
                app.after_cancel(timeout)
                self.assertFalse(tab.busy)
                self.assertIsNotNone(tab.result)
                self.assertTrue(tab.result.is_file())
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
