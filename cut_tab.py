import os
import queue
import threading
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from cut_layout import build_cut
from discord_export import Cancelled
from media_cutter import MEDIA_PATTERNS, cut_media, parse_timecode
from ui_layout import lock_controls


class CutTab(ttk.Frame):
    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.busy = False
        import tkinter as tk
        self.source = tk.StringVar()
        self.output_stem = tk.StringVar(value="")
        self.start_time = tk.StringVar(value="0")
        self.end_time = tk.StringVar(value="")
        self.folder = tk.StringVar(value=app._saved_output_dir("cortes"))
        self.status = tk.StringVar(value="Choose a video, audio, or GIF to begin.")
        self.result = None
        build_cut(self)
        self.poll_id = self.after(150, self.poll)

    def choose_source(self):
        path = filedialog.askopenfilename(title="Video, audio, or GIF", filetypes=[("Supported media", MEDIA_PATTERNS), ("All files", "*.*")])
        if path:
            self.source.set(path)
            self.output_stem.set(Path(path).stem + "-corte")

    def choose_folder(self):
        path = filedialog.askdirectory(title="Cut destination folder", initialdir=self.folder.get())
        if path:
            self.folder.set(path)
            self.save_folder()

    def save_folder(self):
        value = self.folder.get().strip()
        if value:
            self.app.preferences.setdefault("destination_folders", {})["cortes"] = value
            self.app._save_gif_fps()

    def start(self):
        if self.busy:
            return
        if not self.app.ffmpeg or not Path(self.source.get()).is_file() or not self.folder.get().strip():
            messagebox.showwarning("Cuts", "Choose media and a destination folder; FFmpeg must be installed.")
            return
        try:
            start = parse_timecode(self.start_time.get()) or 0.0
            end = parse_timecode(self.end_time.get())
            if end is not None and end <= start:
                raise ValueError("The end must be later than the start.")
        except ValueError as exc:
            messagebox.showwarning("Cuts", str(exc))
            return
        self.save_folder()
        args = (self.app.ffmpeg, Path(self.source.get()), Path(self.folder.get().strip()), self.output_stem.get(), start, end)
        self.cancelled.clear()
        self.busy = True
        self.result = None
        lock_controls(self.scroll.body, True)
        self.cut_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.configure(mode="indeterminate", value=0)
        self.progress.start(12)
        self.status.set("Preparing the cut…")
        threading.Thread(target=self.worker, args=(args,), daemon=True).start()

    def cancel(self):
        self.cancelled.set()
        self.status.set("Cancelling… The original will be preserved.")

    def worker(self, args):
        try:
            result = cut_media(*args, cancelled=self.cancelled, progress=lambda text: self.events.put(("status", text)))
            self.events.put(("done", result))
        except Cancelled:
            self.events.put(("cancelled", "Cancelled. The original was preserved."))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        while not self.events.empty():
            event, value = self.events.get_nowait()
            if event == "status":
                self.status.set(value)
                continue
            self.busy = False
            lock_controls(self.scroll.body, False)
            self.progress.stop()
            self.cut_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            if event == "done":
                self.result, summary = value
                self.progress.configure(mode="determinate", maximum=100, value=100)
                self.status.set(f"Ready: {self.result.name}\n{summary}")
                self.open_button.configure(state="normal")
            else:
                self.status.set(value)
                if event == "error":
                    messagebox.showerror("Cuts", value)
        self.poll_id = self.after(150, self.poll)

    def destroy(self):
        self.cancelled.set()
        if hasattr(self, "poll_id"):
            self.after_cancel(self.poll_id)
        super().destroy()

    def open_result(self):
        if self.result:
            os.startfile(self.result.parent)
