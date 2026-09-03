"""Componentes visuais compartilhados pela aplicação desktop."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import webbrowser

BG = "#1b1b1f"
CARD = "#121215"
TEXT = "#f0edf7"
MUTED = "#a9a4b4"
ACCENT = "#b16bff"


def theme(app):
    app.configure(bg=BG)
    app.option_add("*TCombobox*Listbox.background", CARD)
    app.option_add("*TCombobox*Listbox.foreground", TEXT)
    app.option_add("*TCombobox*Listbox.selectBackground", "#643b86")
    style = ttk.Style(app)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10), background=BG, foreground=TEXT)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD, bordercolor="#36333d", relief="solid", borderwidth=1)
    style.configure("CardBody.TFrame", background=CARD, borderwidth=0, relief='flat')
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"), foreground=TEXT)
    style.configure("Hint.TLabel", foreground=MUTED, font=("Segoe UI", 10))
    style.configure("Watermark.TLabel", foreground="#9e79c7", font=("Segoe UI", 9))
    style.configure("Card.TLabel", background=CARD)
    style.configure("CardTitle.TLabel", background=CARD, font=("Segoe UI", 12, "bold"))
    style.configure("CardHint.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("TButton", padding=(15, 8), background="#232227", foreground=TEXT, bordercolor="#45414d", focuscolor=ACCENT)
    style.map("TButton", background=[("active", "#35303e"), ("disabled", "#222126")], foreground=[("disabled", "#75707e")])
    style.configure("Accent.TButton", background="#9553d3", bordercolor="#9553d3", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
    style.map("Accent.TButton", background=[("active", "#ad68ed"), ("disabled", "#463050")])
    style.configure("Nav.TButton", padding=(18, 9))
    style.configure("ActiveNav.TButton", background="#392947", foreground="#d5acff", bordercolor=ACCENT, padding=(18, 9))
    style.configure("TEntry", fieldbackground="#222126", foreground=TEXT, insertcolor=TEXT, bordercolor="#45414d", padding=7)
    style.map("TEntry", fieldbackground=[("readonly", "#222126"), ("disabled", "#202025")])
    style.configure("TCombobox", fieldbackground="#222126", background="#28252e", foreground=TEXT, arrowcolor=ACCENT, bordercolor="#45414d", padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", "#222126")], foreground=[("readonly", TEXT)])
    for name in ("TCheckbutton", "TRadiobutton"):
        style.configure(name, background=CARD, foreground=TEXT, indicatorbackground="#34303b", indicatorforeground=ACCENT, focuscolor=ACCENT)
        style.map(name, background=[("active", CARD)], indicatorbackground=[("selected", ACCENT)])
    style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor="#312938", borderwidth=0, thickness=5)
    style.configure("Horizontal.TScale", background=CARD, troughcolor="#403547")
    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0)
    style.layout("TNotebook.Tab", [])
    style.configure("Vertical.TScrollbar", background="#49414f", troughcolor=BG, borderwidth=0, arrowsize=12)
    for name in ('TButton', 'TEntry', 'TCombobox', 'Horizontal.TScale', 'Vertical.TScrollbar'):
        style.configure(name, lightcolor='#45414d', darkcolor='#45414d')
    style.configure('TNotebook', bordercolor=BG, lightcolor=BG, darkcolor=BG)
    style.configure('Horizontal.TProgressbar', lightcolor=BG, darkcolor=BG, bordercolor=BG)
    style.layout('Horizontal.TProgressbar', [('Horizontal.Progressbar.trough', {'sticky': 'nswe', 'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})]})])


class ScrollContent(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self, bg=BG, bd=0, highlightthickness=0)
        bar = ttk.Scrollbar(self, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = ttk.Frame(self.canvas, padding=(24, 12, 24, 18))
        self.window = self.canvas.create_window(0, 0, window=self.body, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        self.body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def wheel(self, event):
        if self.body.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")


def card(parent, title, subtitle=None):
    box = ttk.Frame(parent, style="Card.TFrame", padding=16)
    ttk.Label(box, text=title, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 10))
    if subtitle:
        ttk.Label(box, text=subtitle, style="CardHint.TLabel", wraplength=500).pack(anchor="w", pady=(0, 12))
    return box


def label(parent, text):
    ttk.Label(parent, text=text, style="Card.TLabel").pack(anchor="w", pady=(8, 5))


def lock_controls(root, busy):
    if busy:
        root.saved_states = []
        def visit(widget):
            for child in widget.winfo_children():
                if isinstance(child, (ttk.Button, ttk.Entry, ttk.Checkbutton, ttk.Radiobutton, ttk.Scale, tk.Listbox)):
                    root.saved_states.append((child, child.cget('state')))
                    child.configure(state='disabled')
                visit(child)
        visit(root)
    else:
        for widget, state in getattr(root, 'saved_states', []):
            widget.configure(state=state)
        root.saved_states = []


def build_ui(app, discord_class, cut_class, formats, fps_values):
    theme(app)
    header = ttk.Frame(app, padding=(32, 20, 32, 14))
    header.pack(fill="x")
    logo = Path(__file__).parent / "assets" / "vs-conversor.png"
    if logo.exists():
        app.brand_icon = tk.PhotoImage(file=str(logo)).subsample(16)
        ttk.Label(header, image=app.brand_icon).pack(side="left", padx=(0, 8))
    ttk.Label(header, text="Vsy Converter", style="Title.TLabel").pack(side="left")
    app.nav_buttons = []
    navigation = ttk.Frame(header)
    navigation.pack(side="right")
    for index, text in enumerate(("Conversor", "Discord", "Cortes")):
        button = ttk.Button(navigation, text=text, style="Nav.TButton", command=lambda i=index: app.notebook.select(i))
        button.pack(side="left", padx=5)
        app.nav_buttons.append(button)
    app.site_credit = ttk.Label(header, text="frstt.dev", style="Watermark.TLabel", cursor="hand2")
    app.site_credit.pack(side="right", padx=(0, 18))
    app.site_credit.bind("<Button-1>", lambda _event: webbrowser.open("https://frstt.dev"))
    app.notebook = ttk.Notebook(app)
    app.notebook.pack(fill="both", expand=True, padx=8)
    host = ttk.Frame(app.notebook)
    app.notebook.add(host, text="Conversor")
    scroll = ScrollContent(host)
    root = scroll.body
    app.converter_content = root
    ttk.Label(root, text="Converta. Ajuste. Pronto.", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(root, text="Imagens e vídeos, em um só lugar. Seus originais continuam intactos.", style="Hint.TLabel").pack(anchor="w", pady=(4, 20))
    columns = ttk.Frame(root)
    columns.pack(fill="both", expand=True)
    columns.columnconfigure(0, weight=3, minsize=370)
    columns.columnconfigure(1, weight=2, minsize=310)
    files = card(columns, "Arquivos", "Selecione uma ou várias imagens. Vídeos podem ser exportados como GIF.")
    files.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
    toolbar = ttk.Frame(files, style="CardBody.TFrame")
    toolbar.pack(fill="x", pady=(0, 10))
    ttk.Button(toolbar, text="+ Adicionar", command=app.add_files).pack(side="left")
    ttk.Button(toolbar, text="Remover", command=app.remove_selected).pack(side="left", padx=6)
    ttk.Button(toolbar, text="Limpar", command=app.clear_files).pack(side="left")
    app.file_list = tk.Listbox(files, height=12, selectmode="extended", font=("Segoe UI", 10), bg=CARD, fg=TEXT, selectbackground="#604078", selectforeground="white", bd=0, highlightthickness=0, activestyle="none")
    app.file_list.pack(fill="both", expand=True)
    app.file_count = ttk.Label(files, text="0 arquivos", style="CardHint.TLabel")
    app.file_count.pack(anchor="w", pady=(12, 0))
    options = card(columns, "Ajustes de saída")
    options.grid(row=0, column=1, sticky="nsew")
    label(options, "Formato")
    app.format_combo = ttk.Combobox(options, textvariable=app.output_format, values=formats, state="readonly")
    app.format_combo.pack(fill="x")
    app.format_combo.bind("<<ComboboxSelected>>", app._format_changed)
    label(options, "Qualidade (imagens)")
    app.quality_label = ttk.Label(options, text="90%", style="CardHint.TLabel")
    app.quality_label.pack(anchor="e")
    ttk.Scale(options, from_=1, to=100, variable=app.quality, command=app._quality_changed).pack(fill="x")
    label(options, "Fluidez do GIF de vídeo")
    app.fps_combo = ttk.Combobox(options, textvariable=app.gif_fps, values=fps_values, state="readonly")
    app.fps_combo.pack(fill="x")
    app.fps_combo.bind("<<ComboboxSelected>>", lambda e: app._save_gif_fps())
    ttk.Checkbutton(options, text="Redimensionar", variable=app.resize_enabled, command=app._toggle_resize).pack(anchor="w", pady=(18, 6))
    dimensions = ttk.Frame(options, style="CardBody.TFrame")
    dimensions.pack(fill="x")
    app.width_entry = ttk.Entry(dimensions, textvariable=app.width, width=8, state="disabled")
    app.width_entry.pack(side="left")
    ttk.Label(dimensions, text=" × ", style="Card.TLabel").pack(side="left")
    app.height_entry = ttk.Entry(dimensions, textvariable=app.height, width=8, state="disabled")
    app.height_entry.pack(side="left")
    ttk.Label(options, text="Largura × altura, em pixels.\nUm campo vazio mantém a proporção.", style="CardHint.TLabel").pack(anchor="w", pady=8)
    ttk.Checkbutton(options, text="Manter metadados das imagens", variable=app.keep_metadata).pack(anchor="w", pady=6)
    dest = card(root, "Destino", "Lembrado automaticamente por tipo de arquivo.")
    dest.pack(fill="x", pady=(16, 0))
    app.destination_entry = ttk.Entry(dest, textvariable=app.output_dir)
    app.destination_entry.pack(side="left", fill="x", expand=True)
    app.destination_entry.bind("<FocusOut>", lambda e: app._save_current_destination())
    ttk.Button(dest, text="Escolher pasta", command=app.choose_output).pack(side="right", padx=(10, 0))
    ttk.Checkbutton(dest, text="Abrir o Vsy Converter junto com o Windows", variable=app.startup_enabled, command=app.toggle_startup).pack(anchor="w", pady=(12, 0))
    bottom = ttk.Frame(host, padding=(24, 12, 36, 18))
    scroll.pack_forget()
    bottom.pack(side='bottom', fill='x')
    scroll.pack(fill='both', expand=True)
    app.progress = ttk.Progressbar(bottom, mode="indeterminate")
    app.progress.pack(fill="x", pady=(0, 12))
    ttk.Label(bottom, textvariable=app.status, wraplength=760, style="Hint.TLabel").pack(anchor="w", pady=(0, 10))
    app.convert_button = ttk.Button(bottom, text="Converter arquivos", style="Accent.TButton", command=app.start_conversion)
    app.convert_button.pack(side="left")
    app.cancel_button = ttk.Button(bottom, text="Cancelar", state="disabled", command=app.cancel_conversion)
    app.cancel_button.pack(side="left", padx=10)
    app.discord_tab = discord_class(app.notebook, app)
    app.notebook.add(app.discord_tab, text="Discord")
    app.cut_tab = cut_class(app.notebook, app)
    app.notebook.add(app.cut_tab, text="Cortes")
    def nav(event=None):
        selected = app.notebook.index(app.notebook.select())
        for i, button in enumerate(app.nav_buttons):
            button.configure(style="ActiveNav.TButton" if i == selected else "Nav.TButton")
    app.notebook.bind("<<NotebookTabChanged>>", nav)
    def wheel(event):
        if event.widget.winfo_class() not in {"Listbox", "TCombobox"}:
            scrolls = (scroll, app.discord_tab.scroll, app.cut_tab.scroll)
            scrolls[app.notebook.index(app.notebook.select())].wheel(event)
    app.bind("<MouseWheel>", wheel)
    nav()
