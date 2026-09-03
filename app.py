from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
import threading
import tempfile
import queue
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from discord_tab import DiscordTab
from cut_tab import CutTab
from discord_export import run_command, Cancelled, find_video_engine
from ui_layout import lock_controls
from startup import is_enabled, set_enabled


APP_NAME = "Vsy Converter"
BG = "#09090d"
PANEL = "#12121a"
PANEL_ALT = "#181822"
TEXT = "#f3efff"
MUTED = "#aaa2bd"
PURPLE = "#a855f7"
MAGENTA = "#ec4899"
GREEN = "#55f991"
OUTPUT_FORMATS = ("JPG", "PNG", "WEBP", "AVIF", "GIF", "BMP", "TIFF", "ICO", "PDF")
GIF_FPS_OPTIONS = (10, 15, 24, 30, 50, 60)
FORMAT_CATEGORIES = {
    "PDF": "documentos",
}
FILE_TYPES = [
    ("Todos os formatos compatíveis", "*.jpg *.jpeg *.jpe *.jfif *.png *.apng *.webp *.avif *.gif *.bmp *.dib *.tif *.tiff *.ico *.heic *.heif *.svg *.psd *.xcf *.ppm *.pgm *.pbm *.pnm *.tga *.dds *.dng *.cr2 *.cr3 *.nef *.arw *.orf *.rw2 *.raf *.pdf *.mp4 *.m4v *.mkv *.mov *.avi *.webm *.wmv *.flv *.f4v *.mpeg *.mpg *.mpe *.mpv *.mts *.m2ts *.ts *.vob *.ogv *.ogg *.3gp *.3g2 *.asf *.rm *.rmvb *.divx *.xvid *.mxf *.dv *.qt *.y4m *.amv *.mjpeg *.mjpg *.nut"),
    ("Todos os vídeos", "*.mp4 *.m4v *.mkv *.mov *.avi *.webm *.wmv *.flv *.f4v *.mpeg *.mpg *.mpe *.mpv *.mts *.m2ts *.ts *.vob *.ogv *.ogg *.3gp *.3g2 *.asf *.rm *.rmvb *.divx *.xvid *.mxf *.dv *.qt *.y4m *.amv *.mjpeg *.mjpg *.nut"),
    ("Todas as imagens", "*.jpg *.jpeg *.jpe *.jfif *.png *.apng *.webp *.avif *.gif *.bmp *.dib *.tif *.tiff *.ico *.heic *.heif *.svg *.psd *.xcf *.ppm *.pgm *.pbm *.pnm *.tga *.dds *.dng *.cr2 *.cr3 *.nef *.arw *.orf *.rw2 *.raf"),
    ("Todos os arquivos", "*.*"),
]
VIDEO_EXTENSIONS = {
    ".mp4", ".m4v", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".flv", ".f4v",
    ".mpeg", ".mpg", ".mpe", ".mpv", ".mts", ".m2ts", ".ts", ".vob", ".ogv",
    ".ogg", ".3gp", ".3g2", ".asf", ".rm", ".rmvb", ".divx", ".xvid", ".mxf",
    ".dv", ".qt", ".y4m", ".amv", ".mjpeg", ".mjpg", ".nut",
}


def find_magick() -> str | None:
    found = shutil.which("magick")
    if found:
        return found
    program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    matches = sorted(program_files.glob("ImageMagick-*\\magick.exe"), reverse=True)
    return str(matches[0]) if matches else None


def find_ffmpeg() -> str | None:
    return find_video_engine()


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        icon_path = Path(__file__).resolve().parent / "assets" / "vs-conversor.ico"
        if icon_path.is_file():
            self.iconbitmap(str(icon_path))
        self.geometry(f"1100x{min(900, self.winfo_screenheight() - 100)}")
        self.minsize(900, 620)
        self.conversion_busy = False
        self.cancelled = threading.Event()
        self.events = queue.Queue()
        self.files: list[Path] = []
        self.magick = find_magick()
        self.ffmpeg = find_ffmpeg()
        self.config_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "VS Conversor"
        self.config_file = self.config_dir / "preferencias.json"
        self.preferences = self._load_preferences()
        self.output_format = tk.StringVar(value="JPG")
        self._active_category = self._current_category()
        self.output_dir = tk.StringVar(value=self._saved_output_dir(self._active_category))
        self.quality = tk.IntVar(value=90)
        self.gif_fps = tk.IntVar(value=self.preferences.get("gif_fps", 30))
        self.resize_enabled = tk.BooleanVar(value=False)
        self.width = tk.StringVar()
        self.height = tk.StringVar()
        self.keep_metadata = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Pronto para converter.")
        self.startup_enabled = tk.BooleanVar(value=is_enabled())
        self._build_ui()
        self.poll_id = self.after(150, self._poll_conversion)
        self.protocol("WM_DELETE_WINDOW", self._close)
        if not self.magick:
            self.after(200, lambda: messagebox.showerror(APP_NAME, "ImageMagick não foi encontrado. Reinstale-o e abra o aplicativo novamente."))

    def _build_ui(self) -> None:
        from ui_layout import build_ui
        build_ui(self, DiscordTab, CutTab, OUTPUT_FORMATS, GIF_FPS_OPTIONS)

    def _close(self):
        if self.discord_tab.busy or self.cut_tab.busy or self.conversion_busy:
            if messagebox.askyesno(APP_NAME, "Cancelar a conversão em andamento e fechar?"):
                self.discord_tab.cancelled.set()
                self.cut_tab.cancelled.set()
                self.cancelled.set()
                self._wait_close()
        else:
            self.destroy()

    def _wait_close(self):
        if self.discord_tab.busy or self.cut_tab.busy or self.conversion_busy:
            self.after(150, self._wait_close)
        else:
            self.destroy()

    def _quality_changed(self, _value: str) -> None:
        self.quality_label.configure(text=f"{round(self.quality.get())}%")

    def toggle_startup(self):
        try:
            set_enabled(self.startup_enabled.get())
            self.status.set("Inicialização do Windows atualizada.")
        except OSError as exc:
            self.startup_enabled.set(not self.startup_enabled.get())
            messagebox.showerror(APP_NAME, f"Não foi possível atualizar a inicialização do Windows.\n\n{exc}")

    def destroy(self):
        self.cancelled.set()
        if hasattr(self, 'poll_id'):
            self.after_cancel(self.poll_id)
        super().destroy()

    @staticmethod
    def _format_category(output_format: str) -> str:
        return FORMAT_CATEGORIES.get(output_format.upper(), "imagens")

    def _current_category(self) -> str:
        if any(path.suffix.lower() in VIDEO_EXTENSIONS for path in self.files):
            return "videos"
        return self._format_category(self.output_format.get())

    def _load_preferences(self) -> dict:
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def _saved_output_dir(self, category: str) -> str:
        saved = self.preferences.get("pastas_destino", {}).get(category)
        if isinstance(saved, str) and saved.strip():
            return saved
        if category == "documentos":
            return str(Path.home() / "Documents" / "Documentos convertidos")
        if category == "videos":
            return str(Path.home() / "Videos" / "GIFs convertidos")
        if category == "cortes":
            return str(Path.home() / "Videos" / "Cortes")
        if category.startswith("discord_"):
            return str(Path.home() / "Pictures" / "Discord" / ("Avatares" if category == "discord_avatar" else "Capas"))
        return str(Path.home() / "Pictures" / "Imagens convertidas")

    def _save_current_destination(self) -> None:
        destination = self.output_dir.get().strip()
        if not destination:
            return
        folders = self.preferences.setdefault("pastas_destino", {})
        folders[self._active_category] = destination
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(self.preferences, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _save_gif_fps(self) -> None:
        self.preferences["gif_fps"] = int(self.gif_fps.get())
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(self.preferences, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def _format_changed(self, _event=None) -> None:
        self._save_current_destination()
        self._active_category = self._current_category()
        self.output_dir.set(self._saved_output_dir(self._active_category))

    def _sync_destination_category(self) -> None:
        category = self._current_category()
        if category != self._active_category:
            self._save_current_destination()
            self._active_category = category
            self.output_dir.set(self._saved_output_dir(category))

    def _toggle_resize(self) -> None:
        state = "normal" if self.resize_enabled.get() else "disabled"
        self.width_entry.configure(state=state)
        self.height_entry.configure(state=state)

    def add_files(self) -> None:
        selected = filedialog.askopenfilenames(title="Escolha os arquivos", filetypes=FILE_TYPES)
        known = {str(p).lower() for p in self.files}
        for item in selected:
            if item.lower() not in known:
                self.files.append(Path(item))
                known.add(item.lower())
        self._refresh_list()
        self._sync_destination_category()

    def remove_selected(self) -> None:
        selected = set(self.file_list.curselection())
        self.files = [path for index, path in enumerate(self.files) if index not in selected]
        self._refresh_list()
        self._sync_destination_category()

    def clear_files(self) -> None:
        self.files.clear()
        self._refresh_list()
        self._sync_destination_category()

    def _refresh_list(self) -> None:
        self.file_list.delete(0, "end")
        for path in self.files:
            self.file_list.insert("end", str(path))
        self.file_count.configure(text=f"{len(self.files)} arquivo{'s' if len(self.files) != 1 else ''}")

    def choose_output(self) -> None:
        selected = filedialog.askdirectory(title="Escolha a pasta de destino", initialdir=self.output_dir.get())
        if selected:
            self.output_dir.set(selected)
            self._save_current_destination()

    def _resize_geometry(self) -> str | None:
        if not self.resize_enabled.get():
            return None
        width, height = self.width.get().strip(), self.height.get().strip()
        if not width and not height:
            raise ValueError("Informe a largura, a altura ou as duas.")
        if (width and not width.isdigit()) or (height and not height.isdigit()):
            raise ValueError("Largura e altura precisam ser números inteiros.")
        if (width and int(width) < 1) or (height and int(height) < 1):
            raise ValueError("Largura e altura precisam ser maiores que zero.")
        return f"{width}x{height}"

    def start_conversion(self) -> None:
        if self.conversion_busy:
            return
        if not self.magick:
            messagebox.showerror(APP_NAME, "ImageMagick não foi encontrado.")
            return
        if not self.files:
            messagebox.showinfo(APP_NAME, "Adicione pelo menos um arquivo para converter.")
            return
        has_video = any(path.suffix.lower() in VIDEO_EXTENSIONS for path in self.files)
        if has_video and self.output_format.get().upper() != "GIF":
            messagebox.showwarning(APP_NAME, "Vídeos podem ser convertidos para GIF. Selecione GIF como formato de saída.")
            return
        if has_video and not self.ffmpeg:
            messagebox.showerror(APP_NAME, "O componente FFmpeg não foi encontrado. Reinstale o Vsy Converter.")
            return
        try:
            geometry = self._resize_geometry()
        except ValueError as exc:
            messagebox.showwarning(APP_NAME, str(exc))
            return
        if not self.output_dir.get().strip():
            messagebox.showwarning(APP_NAME, "Escolha uma pasta de destino.")
            return
        destination = Path(self.output_dir.get().strip())
        self._save_current_destination()
        self.convert_button.configure(state="disabled")
        self.cancel_button.configure(state='normal')
        self.cancelled.clear()
        self.conversion_busy = True
        lock_controls(self.converter_content, True)
        self.progress.configure(mode='indeterminate', value=0)
        self.progress.start(12)
        self.status.set("Iniciando...")
        self._save_gif_fps()
        settings = (self.output_format.get().lower(), str(round(self.quality.get())), self.keep_metadata.get(), int(self.gif_fps.get()))
        threading.Thread(target=self._convert_all, args=(destination, geometry, settings, tuple(self.files)), daemon=True).start()

    @staticmethod
    def _unique_output(directory: Path, stem: str, extension: str) -> Path:
        candidate = directory / f"{stem}.{extension}"
        number = 2
        while candidate.exists():
            candidate = directory / f"{stem} ({number}).{extension}"
            number += 1
        return candidate

    def cancel_conversion(self):
        self.cancelled.set()
        self.status.set("Cancelando… Os arquivos originais serão preservados.")

    def _convert_all(self, destination, geometry, settings, sources):
        errors = []
        converted = 0
        extension, quality, keep_metadata, gif_fps = settings
        try:
            destination.mkdir(parents=True, exist_ok=True)
            for index, source in enumerate(sources, 1):
                if self.cancelled.is_set():
                    raise Cancelled()
                prefix = f"Arquivo {index}/{len(sources)} · {source.name}"
                self.events.put(("status", prefix))
                with tempfile.TemporaryDirectory(prefix='.vsy-convert-', dir=destination) as temp:
                    output = Path(temp) / ("resultado." + extension)
                    is_video = source.suffix.lower() in VIDEO_EXTENSIONS
                    if is_video:
                        scale = "scale='min(960,iw)':-2:flags=lanczos"
                        if geometry:
                            width, height = geometry.split('x', 1)
                            scale = f"scale={width or '-2'}:{height or '-2'}:flags=lanczos"
                            if width and height:
                                scale += ':force_original_aspect_ratio=decrease'
                        graph = f"fps={gif_fps},{scale},split[a][b];[a]palettegen=stats_mode=single[p];[b][p]paletteuse=new=1:dither=bayer"
                        command = [self.ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                                   '-i', str(source), '-filter_complex_threads', '2', '-filter_complex',
                                   graph, '-loop', '0', str(output)]
                    else:
                        command = [self.magick, str(source)]
                        if geometry:
                            command += ['-resize', geometry]
                        command += ['-quality', quality]
                        if not keep_metadata:
                            command += ['-strip']
                        if extension in {'jpg', 'jpeg'}:
                            command += ['-background', 'white', '-alpha', 'remove', '-alpha', 'off']
                        command += [str(output)]
                    try:
                        run_command(command, self.cancelled,
                                    lambda elapsed: self.events.put(('status', f'{prefix} · {elapsed:.0f}s')))
                        if self.cancelled.is_set():
                            raise Cancelled()
                        generated = sorted(Path(temp).glob('resultado*.' + extension))
                        if not generated:
                            raise RuntimeError('O conversor não gerou um arquivo de saída.')
                        for item in generated:
                            stem = source.stem if len(generated) == 1 else source.stem + item.stem.removeprefix('resultado')
                            target = self._unique_output(destination, stem, extension)
                            # No Windows rename nunca substitui um arquivo existente.
                            while True:
                                try:
                                    item.rename(target)
                                    break
                                except FileExistsError:
                                    target = self._unique_output(destination, stem, extension)
                        converted += 1
                    except Cancelled:
                        raise
                    except Exception as exc:
                        errors.append(f'{source.name}: {exc}')
        except Cancelled:
            pass
        except Exception as exc:
            errors.append(str(exc))
        finally:
            self.events.put(('done', (destination, errors, converted, self.cancelled.is_set())))

    def _poll_conversion(self):
        while not self.events.empty():
            event, value = self.events.get_nowait()
            if event == 'status':
                self.status.set(value)
            else:
                self._finished(*value)
        self.poll_id = self.after(150, self._poll_conversion)

    def _finished(self, destination, errors, converted, cancelled=False):
        self.conversion_busy = False
        lock_controls(self.converter_content, False)
        self.progress.stop()
        self.progress.configure(mode='determinate', maximum=100, value=0 if cancelled or errors else 100)
        self.convert_button.configure(state='normal')
        self.cancel_button.configure(state='disabled')
        if cancelled:
            self.status.set(f'Cancelado · {converted} arquivo(s) concluído(s). Originais preservados.')
        elif errors:
            self.status.set(f'Concluído · {converted} convertido(s), {len(errors)} erro(s).')
            messagebox.showwarning(APP_NAME, '\n\n'.join(errors[:5]))
        else:
            self.status.set(f'Pronto! {converted} arquivo(s) convertido(s).')
            if messagebox.askyesno(APP_NAME, 'Conversão concluída!\n\nAbrir a pasta de destino?'):
                os.startfile(destination)


if __name__ == "__main__":
    ConverterApp().mainloop()
