"""Layout da área de exportação de perfil."""
from tkinter import ttk
from ui_layout import ScrollContent, card
from discord_export import PRESETS


def build_discord(tab):
    tab.scroll = ScrollContent(tab)
    root = tab.scroll.body
    ttk.Label(root, text='Seu perfil, no tamanho certo.', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
    ttk.Label(root, text='Avatar e capa de perfil • preparação local, sem envio ao Discord', style='Hint.TLabel').pack(anchor='w', pady=(4, 18))
    source = card(root, '01  Escolha sua imagem')
    source.pack(fill='x')
    ttk.Button(source, text='+ Imagem ou GIF', command=tab.choose_source).pack(side='left', padx=(0, 12))
    ttk.Entry(source, textvariable=tab.source, state='readonly').pack(side='left', fill='x', expand=True)
    columns = ttk.Frame(root)
    columns.pack(fill='x', pady=16)
    for i in range(2):
        columns.columnconfigure(i, weight=1, uniform='options')
    target = card(columns, '02  Onde você vai usar?')
    target.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
    for key, preset in PRESETS.items():
        ttk.Radiobutton(target, text=f'{preset.label}   ·   {preset.width} × {preset.height}', variable=tab.kind, value=key, command=tab.target_changed).pack(anchor='w', pady=5)
    ttk.Label(target, textvariable=tab.hint, style='CardHint.TLabel', wraplength=340).pack(anchor='w', pady=(14, 0))
    options = card(columns, '03  Enquadramento e formato')
    options.grid(row=0, column=1, sticky='nsew')
    ttk.Radiobutton(options, text='Preencher • recorte central', variable=tab.fit, value='crop').pack(anchor='w', pady=5)
    ttk.Radiobutton(options, text='Mostrar tudo • com margens', variable=tab.fit, value='contain').pack(anchor='w', pady=5)
    ttk.Combobox(options, textvariable=tab.output_format, values=('AUTO', 'PNG', 'JPG', 'GIF'), state='readonly', width=12).pack(anchor='w', pady=(10, 6))
    ttk.Label(options, text='AUTO mantém a animação.\nPNG e JPG salvam só o primeiro quadro.', style='CardHint.TLabel').pack(anchor='w')
    dest = card(root, '04  Pasta de destino', 'Lembrada separadamente para avatar e capa.')
    dest.pack(fill='x')
    entry = ttk.Entry(dest, textvariable=tab.folder)
    entry.pack(side='left', fill='x', expand=True)
    entry.bind('<FocusOut>', lambda e: tab.save_folder())
    ttk.Button(dest, text='Escolher pasta', command=tab.choose_folder).pack(side='right', padx=(10, 0))
    ttk.Label(root, text='Capas personalizadas e avatares animados exigem Nitro. GIFs mantêm os quadros e a duração.\nA compressão pode reduzir cores e a resolução do avatar; GIFs longos podem exceder a meta.', style='Hint.TLabel', wraplength=800).pack(anchor='w', pady=16)
    # Ações fixas: continuam acessíveis mesmo com a área de opções rolada.
    footer = ttk.Frame(tab, padding=(24, 12, 36, 18))
    tab.scroll.pack_forget()
    footer.pack(side='bottom', fill='x')
    tab.scroll.pack(fill='both', expand=True)
    tab.progress = ttk.Progressbar(footer, mode='indeterminate')
    tab.progress.pack(fill='x')
    ttk.Label(footer, textvariable=tab.status, style='Hint.TLabel', wraplength=800).pack(anchor='w', pady=10)
    tab.export_button = ttk.Button(footer, text='Preparar para Discord', style='Accent.TButton', command=tab.start)
    tab.export_button.pack(side='left')
    tab.cancel_button = ttk.Button(footer, text='Cancelar', command=tab.cancelled.set, state='disabled')
    tab.cancel_button.pack(side='left', padx=10)
    tab.open_button = ttk.Button(footer, text='Abrir resultado', command=tab.open_result, state='disabled')
    tab.open_button.pack(side='right')
