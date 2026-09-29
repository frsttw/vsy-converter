"""Layout for the media cutting tab."""
from tkinter import ttk

from ui_layout import ScrollContent, card


def build_cut(tab):
    tab.scroll = ScrollContent(tab)
    root = tab.scroll.body
    ttk.Label(root, text="Precise cuts, no terminal.", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(root, text="Video, audio, and GIF in a few fields. Your original files stay untouched.", style="Hint.TLabel").pack(anchor="w", pady=(4, 18))

    source = card(root, "01  Choose media", "Video, audio, and GIF formats recognized by FFmpeg.")
    source.pack(fill="x")
    ttk.Button(source, text="+ Video, audio, or GIF", command=tab.choose_source).pack(side="left", padx=(0, 12))
    ttk.Entry(source, textvariable=tab.source, state="readonly").pack(side="left", fill="x", expand=True)

    columns = ttk.Frame(root)
    columns.pack(fill="x", pady=16)
    columns.columnconfigure(0, weight=1, uniform="cut-options")
    columns.columnconfigure(1, weight=1, uniform="cut-options")
    timing = card(columns, "02  Set the range", "Enter the start and, optionally, the end.")
    timing.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    row = ttk.Frame(timing, style="CardBody.TFrame")
    row.pack(fill="x")
    ttk.Label(row, text="Start", style="Card.TLabel").pack(side="left")
    ttk.Entry(row, textvariable=tab.start_time, width=14).pack(side="left", padx=(8, 18))
    ttk.Label(row, text="End", style="Card.TLabel").pack(side="left")
    ttk.Entry(row, textvariable=tab.end_time, width=14).pack(side="left", padx=8)
    ttk.Label(timing, text="Examples: 12.5  •  00:01:30  •  01:02:03.500\nLeave the end empty to cut to the end.", style="CardHint.TLabel").pack(anchor="w", pady=(14, 0))

    quality = card(columns, "03  Preservation", "The default prioritizes original quality.")
    quality.grid(row=0, column=1, sticky="nsew")
    ttk.Label(quality, text="✓ Video and audio: direct stream copy, no recompression", style="Card.TLabel").pack(anchor="w", pady=4)
    ttk.Label(quality, text="✓ Metadata and all tracks preserved", style="Card.TLabel").pack(anchor="w", pady=4)
    ttk.Label(quality, text="GIF: re-encoded while preserving resolution, duration, and animation.", style="CardHint.TLabel", wraplength=420).pack(anchor="w", pady=(12, 0))

    output = card(root, "04  Name and destination", "The chosen folder remains available for the next cut.")
    output.pack(fill="x")
    ttk.Label(output, text="Name", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
    ttk.Entry(output, textvariable=tab.output_stem).pack(fill="x")
    ttk.Label(output, text="Folder", style="Card.TLabel").pack(anchor="w", pady=(10, 5))
    row = ttk.Frame(output, style="CardBody.TFrame")
    row.pack(fill="x")
    ttk.Entry(row, textvariable=tab.folder).pack(side="left", fill="x", expand=True)
    ttk.Button(row, text="Choose folder", command=tab.choose_folder).pack(side="right", padx=(10, 0))

    ttk.Label(root, text="No recompression preserves quality, but some videos may align the start to the nearest keyframe. GIFs must be re-encoded to remove frames.", style="Hint.TLabel", wraplength=820).pack(anchor="w", pady=16)
    footer = ttk.Frame(tab, padding=(24, 12, 36, 18))
    tab.scroll.pack_forget()
    footer.pack(side="bottom", fill="x")
    tab.scroll.pack(fill="both", expand=True)
    tab.progress = ttk.Progressbar(footer, mode="indeterminate")
    tab.progress.pack(fill="x")
    ttk.Label(footer, textvariable=tab.status, style="Hint.TLabel", wraplength=800).pack(anchor="w", pady=10)
    tab.cut_button = ttk.Button(footer, text="Cut media", style="Accent.TButton", command=tab.start)
    tab.cut_button.pack(side="left")
    tab.cancel_button = ttk.Button(footer, text="Cancel", command=tab.cancel, state="disabled")
    tab.cancel_button.pack(side="left", padx=10)
    tab.open_button = ttk.Button(footer, text="Open result", command=tab.open_result, state="disabled")
    tab.open_button.pack(side="right")
