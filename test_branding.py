import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import APP_NAME, ConverterApp, tk


class BrandingTests(unittest.TestCase):
    def test_name_icon_and_existing_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            legacy = Path(folder) / "VS Conversor"
            legacy.mkdir()
            expected = str(Path(folder) / "Minhas imagens")
            (legacy / "preferencias.json").write_text(json.dumps({
                "gif_fps": 60, "pastas_destino": {"imagens": expected}
            }), encoding="utf-8")
            with patch.dict(os.environ, {"LOCALAPPDATA": folder}):
                icon_calls = []
                original = tk.Tk.iconbitmap

                def record_icon(window, bitmap=None, default=None):
                    icon_calls.append(bitmap)
                    return original(window, bitmap, default)

                with patch.object(tk.Tk, "iconbitmap", record_icon):
                    app = ConverterApp()
                app.withdraw()
                try:
                    app.update_idletasks()
                    self.assertEqual(APP_NAME, "Vsy Converter")
                    self.assertEqual(app.title(), APP_NAME)
                    self.assertEqual(app.output_dir.get(), expected)
                    self.assertEqual(app.gif_fps.get(), 60)
                    self.assertEqual(len(icon_calls), 1)
                    self.assertTrue(Path(icon_calls[0]).is_file())
                finally:
                    app.destroy()


if __name__ == "__main__":
    unittest.main()
