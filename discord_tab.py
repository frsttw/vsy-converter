import queue
import threading
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from discord_export import PRESETS, IMAGE_PATTERNS, convert_image, Cancelled
from ui_layout import lock_controls


class DiscordTab(ttk.Frame):
    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.busy = False
        self.source = tk.StringVar()
        self.kind = tk.StringVar(value="avatar")
        self.fit = tk.StringVar(value="crop")
        self.output_format = tk.StringVar(value="AUTO")
        self.folder = tk.StringVar(value=self.saved_folder())
        self.status = tk.StringVar(value="Choose an image or GIF. The original file will not be changed.")
        self.hint = tk.StringVar()
        self.result = None
        from discord_layout import build_discord
        build_discord(self)
        self.active_kind = self.kind.get()
        self.update_hint()
        self.poll_id = self.after(150, self.poll)

    def saved_folder(self):
        return self.app._saved_output_dir("discord_" + self.kind.get())

    def save_folder(self):
        value = self.folder.get().strip()
        if value:
            self.app.preferences.setdefault("destination_folders", {})["discord_" + self.active_kind] = value
            self.app._save_gif_fps()

    def target_changed(self):
        self.save_folder()
        self.active_kind = self.kind.get()
        self.folder.set(self.saved_folder())
        self.update_hint()

    def update_hint(self):
        p = PRESETS[self.kind.get()]
        self.hint.set(f"{p.label}: {p.width}×{p.height} px • target below {p.max_bytes/1_000_000:g} MB (safety margin).")

    def choose_source(self):
        path = filedialog.askopenfilename(title="Image for Discord", filetypes=[("Images and GIFs", IMAGE_PATTERNS)])
        if path:
            self.source.set(path)

    def choose_folder(self):
        path = filedialog.askdirectory(title="Discord destination folder", initialdir=self.folder.get())
        if path:
            self.folder.set(path)
            self.save_folder()

    def start(self):
        if self.busy:
            return
        if not self.app.magick or not Path(self.source.get()).is_file() or not self.folder.get().strip():
            messagebox.showwarning("Discord", "Choose an image and a destination folder; ImageMagick must be installed.")
            return
        self.save_folder()
        args = (self.app.magick, Path(self.source.get()), Path(self.folder.get().strip()),
                self.kind.get(), self.fit.get(), self.output_format.get())
        self.cancelled.clear()
        self.busy = True
        lock_controls(self.scroll.body, True)
        self.result = None
        self.export_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.configure(mode='indeterminate', value=0)
        self.progress.start(12)
        self.status.set("Preparing...")
        threading.Thread(target=self.worker, args=(args,), daemon=True).start()

    def worker(self, args):
        try:
            path, summary = convert_image(*args, cancelled=self.cancelled,
                                          progress=lambda value: self.events.put(("status", value)),
                                          percent=lambda value: self.events.put(("percent", value)))
            self.events.put(("done", (path, summary)))
        except Cancelled:
            self.events.put(("cancelled", "Cancelled. The original was preserved."))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        while not self.events.empty():
            event, value = self.events.get_nowait()
            if event == 'percent':
                self.progress.stop()
                self.progress.configure(mode='indeterminate' if value < 0 else 'determinate', maximum=100, value=max(0, value))
                if value < 0:
                    self.progress.start(12)
                continue
            if event == "status":
                self.status.set(value)
                continue
            self.busy = False
            lock_controls(self.scroll.body, False)
            self.progress.stop()
            self.export_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            if event == "done":
                self.progress.configure(value=100)
                self.result, summary = value
                self.status.set(f"Ready: {self.result.name}\n{summary}")
                self.open_button.configure(state="normal")
            else:
                self.status.set(value)
                if event == "error":
                    messagebox.showerror("Discord export", value)
        self.poll_id = self.after(150, self.poll)

    def destroy(self):
        self.cancelled.set()
        self.after_cancel(self.poll_id)
        super().destroy()

    def open_result(self):
        if self.result:
            os.startfile(self.result.parent)
