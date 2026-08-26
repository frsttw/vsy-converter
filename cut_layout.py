"""Layout da aba de cortes."""
from tkinter import ttk

from ui_layout import ScrollContent, card


def build_cut(tab):
    tab.scroll = ScrollContent(tab)
    root = tab.scroll.body
    ttk.Label(root, text="Cortes precisos, sem terminal.", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(root, text="Vídeo, áudio e GIF em poucos campos. Seus arquivos originais continuam intactos.", style="Hint.TLabel").pack(anchor="w", pady=(4, 18))

    source = card(root, "01  Escolha a mídia", "Formatos de vídeo, áudio e GIF reconhecidos pelo FFmpeg.")
    source.pack(fill="x")
    ttk.Button(source, text="+ Vídeo, áudio ou GIF", command=tab.choose_source).pack(side="left", padx=(0, 12))
    ttk.Entry(source, textvariable=tab.source, state="readonly").pack(side="left", fill="x", expand=True)

    columns = ttk.Frame(root)
    columns.pack(fill="x", pady=16)
    columns.columnconfigure(0, weight=1, uniform="cut-options")
    columns.columnconfigure(1, weight=1, uniform="cut-options")
    timing = card(columns, "02  Defina o trecho", "Informe o início e, opcionalmente, o fim.")
    timing.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    row = ttk.Frame(timing, style="CardBody.TFrame")
    row.pack(fill="x")
    ttk.Label(row, text="Início", style="Card.TLabel").pack(side="left")
    ttk.Entry(row, textvariable=tab.start_time, width=14).pack(side="left", padx=(8, 18))
    ttk.Label(row, text="Fim", style="Card.TLabel").pack(side="left")
    ttk.Entry(row, textvariable=tab.end_time, width=14).pack(side="left", padx=8)
    ttk.Label(timing, text="Exemplos: 12.5  •  00:01:30  •  01:02:03.500\nDeixe o fim vazio para cortar até o final.", style="CardHint.TLabel").pack(anchor="w", pady=(14, 0))

    quality = card(columns, "03  Preservação", "O padrão prioriza a qualidade original.")
    quality.grid(row=0, column=1, sticky="nsew")
    ttk.Label(quality, text="✓ Vídeo e áudio: cópia direta, sem recompressão", style="Card.TLabel").pack(anchor="w", pady=4)
    ttk.Label(quality, text="✓ Metadados e todas as faixas preservados", style="Card.TLabel").pack(anchor="w", pady=4)
    ttk.Label(quality, text="GIF: recodificado mantendo resolução, duração e animação.", style="CardHint.TLabel", wraplength=420).pack(anchor="w", pady=(12, 0))

    output = card(root, "04  Nome e destino", "A pasta escolhida fica disponível para o próximo corte.")
    output.pack(fill="x")
    ttk.Label(output, text="Nome", style="Card.TLabel").pack(anchor="w", pady=(0, 5))
    ttk.Entry(output, textvariable=tab.output_stem).pack(fill="x")
    ttk.Label(output, text="Pasta", style="Card.TLabel").pack(anchor="w", pady=(10, 5))
    row = ttk.Frame(output, style="CardBody.TFrame")
    row.pack(fill="x")
    ttk.Entry(row, textvariable=tab.folder).pack(side="left", fill="x", expand=True)
    ttk.Button(row, text="Escolher pasta", command=tab.choose_folder).pack(side="right", padx=(10, 0))

    ttk.Label(root, text="O modo sem recompressão mantém a qualidade, mas o início pode ser ajustado ao keyframe mais próximo em alguns vídeos. Para GIF, a recodificação é necessária para remover quadros.", style="Hint.TLabel", wraplength=820).pack(anchor="w", pady=16)
    footer = ttk.Frame(tab, padding=(24, 12, 36, 18))
    tab.scroll.pack_forget()
    footer.pack(side="bottom", fill="x")
    tab.scroll.pack(fill="both", expand=True)
    tab.progress = ttk.Progressbar(footer, mode="indeterminate")
    tab.progress.pack(fill="x")
    ttk.Label(footer, textvariable=tab.status, style="Hint.TLabel", wraplength=800).pack(anchor="w", pady=10)
    tab.cut_button = ttk.Button(footer, text="Cortar mídia", style="Accent.TButton", command=tab.start)
    tab.cut_button.pack(side="left")
    tab.cancel_button = ttk.Button(footer, text="Cancelar", command=tab.cancel, state="disabled")
    tab.cancel_button.pack(side="left", padx=10)
    tab.open_button = ttk.Button(footer, text="Abrir resultado", command=tab.open_result, state="disabled")
    tab.open_button.pack(side="right")
