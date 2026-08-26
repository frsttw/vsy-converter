import queue
import threading
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from discord_export import PRESETS, IMAGE_PATTERNS, convert_image, Cancelled


class DiscordTab(ttk.Frame):
    def __init__(self, notebook, app):
        super().__init__(notebook, padding=22)
        self.app = app
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.busy = False
        self.source = tk.StringVar()
        self.kind = tk.StringVar(value="avatar")
        self.fit = tk.StringVar(value="crop")
        self.output_format = tk.StringVar(value="AUTO")
        self.folder = tk.StringVar(value=self.saved_folder())
        self.status = tk.StringVar(value="Escolha uma imagem ou GIF. O arquivo original não será alterado.")
        self.hint = tk.StringVar()
        self.result = None
        ttk.Label(self, text="Seu perfil, no tamanho certo", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(self, text="Avatar e capa de perfil pessoal • exportação local, sem envio ao Discord", style="Hint.TLabel").pack(anchor="w", pady=(0, 18))
        ttk.Button(self, text="Escolher imagem ou GIF...", command=self.choose_source).pack(anchor="w")
        ttk.Entry(self, textvariable=self.source, state="readonly").pack(fill="x", pady=10)
        targets = ttk.Frame(self)
        targets.pack(fill="x", pady=8)
        for key, preset in PRESETS.items():
            ttk.Radiobutton(targets, text=preset.label, variable=self.kind, value=key,
                            command=self.target_changed).pack(side="left", padx=(0, 28))
        ttk.Label(self, textvariable=self.hint, wraplength=700).pack(anchor="w", pady=10)
        options = ttk.LabelFrame(self, text=" Enquadramento e formato ", padding=14)
        options.pack(fill="x", pady=10)
        ttk.Radiobutton(options, text="Preencher (recorte central)", variable=self.fit, value="crop").pack(anchor="w")
        ttk.Radiobutton(options, text="Mostrar tudo (com margens, sem esticar)", variable=self.fit, value="contain").pack(anchor="w", pady=6)
        row = ttk.Frame(options)
        row.pack(fill="x", pady=6)
        ttk.Label(row, text="Saída:").pack(side="left")
        ttk.Combobox(row, textvariable=self.output_format, values=("AUTO", "PNG", "JPG", "GIF"), width=8, state="readonly").pack(side="left", padx=10)
        ttk.Label(options, text="AUTO preserva animações em GIF. PNG/JPG salvam somente o primeiro quadro.\nO avatar aparece circular no Discord: mantenha o rosto ou logo no centro.", wraplength=690).pack(anchor="w", pady=4)
        ttk.Label(self, text="Pasta de destino (lembrada separadamente para avatar e capa):").pack(anchor="w", pady=(12, 6))
        row = ttk.Frame(self)
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=self.folder)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<FocusOut>", lambda _: self.save_folder())
        ttk.Button(row, text="Escolher...", command=self.choose_folder).pack(side="right", padx=8)
        ttk.Label(self, text="Capas personalizadas e avatares animados exigem Nitro.\nO tamanho é verificado após a conversão; GIFs muito longos podem não caber.\nGIFs mantêm a duração e os quadros; a otimização pode reduzir cores e a resolução do avatar.", style="Hint.TLabel", wraplength=710).pack(anchor="w", pady=14)
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x")
        ttk.Label(self, textvariable=self.status, wraplength=710).pack(anchor="w", pady=10)
        actions = ttk.Frame(self)
        actions.pack(fill="x")
        self.export_button = ttk.Button(actions, text="Preparar para Discord", style="Accent.TButton", command=self.start)
        self.export_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Cancelar", command=self.cancelled.set, state="disabled")
        self.cancel_button.pack(side="left", padx=10)
        self.open_button = ttk.Button(actions, text="Abrir pasta do resultado", command=self.open_result, state="disabled")
        self.open_button.pack(side="right")
        self.active_kind = self.kind.get()
        self.update_hint()
        self.poll_id = self.after(150, self.poll)

    def saved_folder(self):
        return self.app._saved_output_dir("discord_" + self.kind.get())

    def save_folder(self):
        value = self.folder.get().strip()
        if value:
            self.app.preferences.setdefault("pastas_destino", {})["discord_" + self.active_kind] = value
            self.app._save_gif_fps()

    def target_changed(self):
        self.save_folder()
        self.active_kind = self.kind.get()
        self.folder.set(self.saved_folder())
        self.update_hint()

    def update_hint(self):
        p = PRESETS[self.kind.get()]
        self.hint.set(f"{p.label}: {p.width}×{p.height} px • meta abaixo de {p.max_bytes/1_000_000:g} MB (margem de segurança).")

    def choose_source(self):
        path = filedialog.askopenfilename(title="Imagem para Discord", filetypes=[("Imagens e GIFs", IMAGE_PATTERNS)])
        if path:
            self.source.set(path)

    def choose_folder(self):
        path = filedialog.askdirectory(title="Pasta para Discord", initialdir=self.folder.get())
        if path:
            self.folder.set(path)
            self.save_folder()

    def start(self):
        if self.busy:
            return
        if not self.app.magick or not Path(self.source.get()).is_file() or not self.folder.get().strip():
            messagebox.showwarning("Discord", "Escolha uma imagem e uma pasta de destino; o ImageMagick precisa estar instalado.")
            return
        self.save_folder()
        args = (self.app.magick, Path(self.source.get()), Path(self.folder.get().strip()),
                self.kind.get(), self.fit.get(), self.output_format.get())
        self.cancelled.clear()
        self.busy = True
        self.result = None
        self.export_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.start(12)
        self.status.set("Preparando...")
        threading.Thread(target=self.worker, args=(args,), daemon=True).start()

    def worker(self, args):
        try:
            path, summary = convert_image(*args, cancelled=self.cancelled,
                                          progress=lambda value: self.events.put(("status", value)))
            self.events.put(("done", (path, summary)))
        except Cancelled:
            self.events.put(("cancelled", "Cancelado. O original foi preservado."))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        while not self.events.empty():
            event, value = self.events.get_nowait()
            if event == "status":
                self.status.set(value)
                continue
            self.busy = False
            self.progress.stop()
            self.export_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            if event == "done":
                self.result, summary = value
                self.status.set(f"Pronto: {self.result.name}\n{summary}")
                self.open_button.configure(state="normal")
            else:
                self.status.set(value)
                if event == "error":
                    messagebox.showerror("Exportação para Discord", value)
        self.poll_id = self.after(150, self.poll)

    def destroy(self):
        self.cancelled.set()
        self.after_cancel(self.poll_id)
        super().destroy()

    def open_result(self):
        if self.result:
            os.startfile(self.result.parent)
