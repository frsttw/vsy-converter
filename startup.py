"""Integração opcional com a inicialização do Windows para o usuário atual."""
from pathlib import Path
import os
import sys
import winreg


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "Vsy Converter"


def _command(executable=None):
    target = Path(executable or sys.executable).resolve()
    if getattr(sys, "frozen", False) or executable:
        return f'"{target}"'
    # Ao executar a partir do código, não registre o interpretador sozinho.
    return f'"{target}" "{Path(__file__).resolve().with_name("app.py")}"'


def is_enabled(executable=None):
    target = Path(executable or sys.executable).resolve()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            command, _ = winreg.QueryValueEx(key, VALUE_NAME)
        first = str(command).strip().strip('"').split('" "', 1)[0]
        return Path(first).resolve() == target
    except (FileNotFoundError, OSError, ValueError):
        return False


def set_enabled(enabled, executable=None):
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, _command(executable))
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
