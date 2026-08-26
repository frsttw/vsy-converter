from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from discord_tab import DiscordTab


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
    beside_app = Path(sys.executable).resolve().parent / "ffmpeg.exe"
    if beside_app.exists():
        return str(beside_app)
    return shutil.which("ffmpeg")


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        icon_path = Path(__file__).resolve().parent / "assets" / "vs-conversor.ico"
        if icon_path.is_file():
            self.iconbitmap(str(icon_path))
        self.geometry("1000x850")
        self.minsize(900, 800)
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
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._close)
        if not self.magick:
            self.after(200, lambda: messagebox.showerror(APP_NAME, "ImageMagick não foi encontrado. Reinstale-o e abra o aplicativo novamente."))

    def _build_ui(self) -> None:
        self.configure(bg=BG)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#dfb7ff", background=BG)
        style.configure("Hint.TLabel", font=("Segoe UI", 10), foreground=MUTED, background=BG)
        style.configure("CardHint.TLabel", font=("Segoe UI", 9), foreground=MUTED, background=PANEL)
        style.configure("TLabelframe", background=PANEL, bordercolor="#3b2450", lightcolor="#3b2450", darkcolor="#3b2450", relief="solid")
        style.configure("TLabelframe.Label", background=PANEL, foreground="#d8a7ff", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", background=PANEL_ALT, foreground=TEXT, bordercolor="#453357", padding=(12, 7), font=("Segoe UI", 9))
        style.map("TButton", background=[("active", "#292138")], bordercolor=[("active", PURPLE)])
        style.configure("Accent.TButton", background=PURPLE, foreground="#ffffff", bordercolor=MAGENTA, font=("Segoe UI", 11, "bold"), padding=(22, 11))
        style.map("Accent.TButton", background=[("active", MAGENTA), ("disabled", "#3d3348")])
        style.configure("TEntry", fieldbackground="#0d0d13", foreground=TEXT, insertcolor=TEXT, bordercolor="#49315e", padding=6)
        style.configure("TCombobox", fieldbackground="#0d0d13", background=PANEL_ALT, foreground=TEXT, arrowcolor="#d8a7ff", bordercolor="#49315e", padding=5)
        style.map("TCombobox", fieldbackground=[("readonly", "#0d0d13")], foreground=[("readonly", TEXT)])
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT, indicatorbackground="#0d0d13", indicatorforeground=PURPLE)
        style.map("TCheckbutton", background=[("active", PANEL)], indicatorbackground=[("selected", PURPLE)])
        style.configure("Horizontal.TProgressbar", troughcolor="#1d1725", background=PURPLE, bordercolor="#1d1725", lightcolor=MAGENTA, darkcolor=PURPLE)
        style.configure("Horizontal.TScale", background=PANEL, troughcolor="#24182f")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_ALT, foreground=TEXT, padding=(20, 10))
        style.map("TNotebook.Tab", background=[("selected", "#553078")])
        style.configure("TRadiobutton", background=PANEL, foreground=TEXT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)
        root = ttk.Frame(self.notebook, padding=26)
        self.notebook.add(root, text="Conversor")
        header = ttk.Frame(root)
        header.pack(fill="x", pady=(0, 18))
        title_area = ttk.Frame(header)
        title_area.pack(side="left")
        ttk.Label(title_area, text="Vsy Converter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_area, text="powered by ImageMagick  •  simples, rápido e sem terminal", style="Hint.TLabel").pack(anchor="w", pady=(3, 0))
        ttk.Label(header, text="● PRONTO", foreground=GREEN, background=BG, font=("Consolas", 10, "bold")).pack(side="right", anchor="n", pady=10)

        files_box = ttk.LabelFrame(root, text=" 01  ARQUIVOS ", padding=12)
        files_box.pack(fill="both", expand=True)
        buttons = ttk.Frame(files_box)
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(buttons, text="Adicionar arquivos...", command=self.add_files).pack(side="left")
        ttk.Button(buttons, text="Remover selecionados", command=self.remove_selected).pack(side="left", padx=8)
        ttk.Button(buttons, text="Limpar lista", command=self.clear_files).pack(side="left")
        self.file_count = ttk.Label(buttons, text="0 arquivos")
        self.file_count.pack(side="right")

        list_frame = ttk.Frame(files_box)
        list_frame.pack(fill="both", expand=True)
        self.file_list = tk.Listbox(list_frame, selectmode="extended", font=("Segoe UI", 10), borderwidth=1, relief="solid", bg="#0c0c12", fg=TEXT, selectbackground="#7434a9", selectforeground="#ffffff", highlightbackground="#3b2450", highlightcolor=PURPLE, activestyle="none")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        self.file_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        options = ttk.LabelFrame(root, text=" 02  CONFIGURAÇÕES ", padding=12)
        options.pack(fill="x", pady=12)
        ttk.Label(options, text="Formato de saída:").grid(row=0, column=0, sticky="w")
        self.format_combo = ttk.Combobox(options, textvariable=self.output_format, values=OUTPUT_FORMATS, state="readonly", width=9)
        self.format_combo.grid(row=0, column=1, sticky="w", padx=(8, 22))
        self.format_combo.bind("<<ComboboxSelected>>", self._format_changed)
        ttk.Label(options, text="Qualidade:").grid(row=0, column=2, sticky="w")
        ttk.Scale(options, from_=1, to=100, variable=self.quality, orient="horizontal", length=160, command=self._quality_changed).grid(row=0, column=3, padx=8)
        self.quality_label = ttk.Label(options, text="90%", width=5)
        self.quality_label.grid(row=0, column=4, sticky="w")
        ttk.Checkbutton(options, text="Manter metadados (data, câmera etc.)", variable=self.keep_metadata).grid(row=0, column=5, padx=(18, 0), sticky="w")

        ttk.Label(options, text="FPS do GIF:").grid(row=2, column=0, pady=(12, 0), sticky="w")
        self.fps_combo = ttk.Combobox(options, textvariable=self.gif_fps, values=GIF_FPS_OPTIONS, state="readonly", width=7)
        self.fps_combo.grid(row=2, column=1, pady=(12, 0), padx=(8, 22), sticky="w")
        self.fps_combo.bind("<<ComboboxSelected>>", lambda _event: self._save_gif_fps())
        ttk.Label(options, text="Use 60 para máxima fluidez; o arquivo ficará maior.", style="CardHint.TLabel").grid(row=2, column=2, columnspan=4, pady=(12, 0), sticky="w")

        ttk.Checkbutton(options, text="Redimensionar", variable=self.resize_enabled, command=self._toggle_resize).grid(row=1, column=0, pady=(12, 0), sticky="w")
        ttk.Label(options, text="Largura:").grid(row=1, column=1, pady=(12, 0), sticky="e")
        self.width_entry = ttk.Entry(options, textvariable=self.width, width=8, state="disabled")
        self.width_entry.grid(row=1, column=2, pady=(12, 0), padx=(8, 18), sticky="w")
        ttk.Label(options, text="Altura:").grid(row=1, column=3, pady=(12, 0), sticky="e")
        self.height_entry = ttk.Entry(options, textvariable=self.height, width=8, state="disabled")
        self.height_entry.grid(row=1, column=4, pady=(12, 0), padx=8, sticky="w")
        ttk.Label(options, text="Deixe um campo vazio para manter a proporção.", style="Hint.TLabel").grid(row=1, column=5, pady=(12, 0), sticky="w")

        destination = ttk.LabelFrame(root, text=" 03  DESTINO ", padding=12)
        destination.pack(fill="x")
        self.destination_entry = ttk.Entry(destination, textvariable=self.output_dir)
        self.destination_entry.pack(side="left", fill="x", expand=True)
        self.destination_entry.bind("<FocusOut>", lambda _event: self._save_current_destination())
        ttk.Button(destination, text="Escolher pasta...", command=self.choose_output).pack(side="left", padx=(8, 0))

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(14, 0))
        self.progress = ttk.Progressbar(bottom, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 7))
        ttk.Label(bottom, textvariable=self.status, foreground=MUTED).pack(side="left")
        self.convert_button = ttk.Button(bottom, text="Converter agora", style="Accent.TButton", command=self.start_conversion)
        self.convert_button.pack(side="right")
        self.discord_tab = DiscordTab(self.notebook, self)
        self.notebook.add(self.discord_tab, text="Discord • Avatar e capa")

    def _close(self):
        if self.discord_tab.busy:
            if messagebox.askyesno(APP_NAME, "Cancelar a exportação para Discord e fechar?"):
                self.discord_tab.cancelled.set()
                self._wait_close()
        else:
            self.destroy()

    def _wait_close(self):
        if self.discord_tab.busy:
            self.after(150, self._wait_close)
        else:
            self.destroy()

    def _quality_changed(self, _value: str) -> None:
        self.quality_label.configure(text=f"{round(self.quality.get())}%")

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
        destination = Path(self.output_dir.get().strip())
        if not str(destination):
            messagebox.showwarning(APP_NAME, "Escolha uma pasta de destino.")
            return
        self._save_current_destination()
        self.convert_button.configure(state="disabled")
        self.progress.configure(maximum=len(self.files), value=0)
        self.status.set("Iniciando...")
        self._save_gif_fps()
        settings = (self.output_format.get().lower(), str(round(self.quality.get())), self.keep_metadata.get(), int(self.gif_fps.get()))
        threading.Thread(target=self._convert_all, args=(destination, geometry, settings), daemon=True).start()

    @staticmethod
    def _unique_output(directory: Path, stem: str, extension: str) -> Path:
        candidate = directory / f"{stem}.{extension}"
        number = 2
        while candidate.exists():
            candidate = directory / f"{stem} ({number}).{extension}"
            number += 1
        return candidate

    def _convert_all(self, destination: Path, geometry: str | None, settings: tuple[str, str, bool, int]) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        errors: list[str] = []
        extension, quality, keep_metadata, gif_fps = settings
        for index, source in enumerate(self.files, start=1):
            output = self._unique_output(destination, source.stem, extension)
            self.after(0, self.status.set, f"Convertendo {index} de {len(self.files)}: {source.name}")
            is_video = source.suffix.lower() in VIDEO_EXTENSIONS
            if is_video:
                scale = "scale='min(960,iw)':-2:flags=lanczos"
                command = [self.ffmpeg, "-y", "-i", str(source), "-vf", f"fps={gif_fps},{scale},split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=sierra2_4a", "-loop", "0", str(output)]
            else:
                command = [self.magick, str(source)]
            if geometry:
                if is_video:
                    width, height = geometry.split("x", 1)
                    if width and height:
                        video_scale = f"scale={width}:{height}:flags=lanczos"
                    elif width:
                        video_scale = f"scale={width}:-2:flags=lanczos"
                    else:
                        video_scale = f"scale=-2:{height}:flags=lanczos"
                    command[command.index("-vf") + 1] = f"fps={gif_fps},{video_scale},split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=sierra2_4a"
                else:
                    command.extend(["-resize", geometry])
            if not is_video:
                command.extend(["-quality", quality])
                if not keep_metadata:
                    command.append("-strip")
                if extension in {"jpg", "jpeg"}:
                    command.extend(["-background", "white", "-alpha", "remove", "-alpha", "off"])
                command.append(str(output))
            try:
                result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode != 0:
                    errors.append(f"{source.name}: {result.stderr.strip() or 'erro desconhecido'}")
            except Exception as exc:
                errors.append(f"{source.name}: {exc}")
            self.after(0, self.progress.configure, {"value": index})
        self.after(0, self._finished, destination, errors)

    def _finished(self, destination: Path, errors: list[str]) -> None:
        self.convert_button.configure(state="normal")
        converted = len(self.files) - len(errors)
        if errors:
            self.status.set(f"Concluído: {converted} convertido(s), {len(errors)} erro(s).")
            details = "\n\n".join(errors[:5])
            messagebox.showwarning(APP_NAME, f"{converted} arquivo(s) convertido(s).\n\nAlguns arquivos falharam:\n{details}")
        else:
            self.status.set(f"Pronto! {converted} arquivo(s) convertido(s).")
            if messagebox.askyesno(APP_NAME, f"Conversão concluída!\n\nAbrir a pasta de destino?"):
                os.startfile(destination)


if __name__ == "__main__":
    ConverterApp().mainloop()
