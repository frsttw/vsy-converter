"""Cortes locais de vídeo, áudio e GIF usando os fluxos originais quando possível."""
from pathlib import Path
import os
import re
import tempfile
import threading

from discord_export import Cancelled, run_command


MEDIA_PATTERNS = (
    "*.mp4 *.m4v *.mkv *.mov *.avi *.webm *.wmv *.flv *.f4v *.mpeg *.mpg *.mpe *.mpv "
    "*.mts *.m2ts *.ts *.vob *.ogv *.ogg *.3gp *.3g2 *.asf *.rm *.rmvb *.divx *.xvid "
    "*.mxf *.dv *.qt *.y4m *.amv *.mjpeg *.mjpg *.nut *.gif *.mp3 *.m4a *.aac *.flac "
    "*.wav *.ogg *.opus *.wma *.aiff *.aif *.alac *.ape *.ac3 *.dts *.mka *.caf"
)


def parse_timecode(value):
    """Converte segundos ou HH:MM:SS(.mmm) em segundos."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if ":" not in text:
            result = float(text.replace(",", "."))
        else:
            pieces = text.split(":")
            if len(pieces) > 3 or any(not piece for piece in pieces):
                raise ValueError
            result = 0.0
            for piece in pieces:
                result = result * 60 + float(piece.replace(",", "."))
        if result < 0 or result != result or result == float("inf"):
            raise ValueError
        return result
    except (TypeError, ValueError):
        raise ValueError("Use o tempo em segundos ou no formato HH:MM:SS.000.")


def _time_arg(seconds):
    return f"{seconds:.3f}".rstrip("0").rstrip(".") or "0"


def _unique_target(directory, stem, suffix):
    candidate = directory / f"{stem}{suffix}"
    number = 2
    while candidate.exists():
        candidate = directory / f"{stem} ({number}){suffix}"
        number += 1
    return candidate


def _cut_gif(ffmpeg, source, candidate, start, duration, cancelled, progress):
    graph = "[0:v]split[a][b];[a]palettegen=stats_mode=diff:max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a"
    command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
               "-ss", _time_arg(start), "-ignore_loop", "1", "-i", str(source)]
    if duration is not None:
        command += ["-t", _time_arg(duration)]
    command += ["-filter_complex", graph, "-fps_mode", "passthrough", "-gifflags", "-offsetting",
                "-loop", "0", str(candidate)]
    run_command(command, cancelled,
                lambda elapsed: progress(f"Recodificando GIF… {elapsed:.0f}s"))


def cut_media(ffmpeg, source, directory, output_stem, start, end,
              cancelled=None, progress=lambda text: None):
    """Corta uma mídia sem recompressão; GIF é recodificado para manter a animação."""
    cancelled = cancelled or threading.Event()
    source = Path(source).resolve(strict=True)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    start = parse_timecode(start) or 0.0
    end = parse_timecode(end)
    if end is not None and end <= start:
        raise ValueError("O fim precisa ser maior que o início.")
    if not ffmpeg:
        raise RuntimeError("FFmpeg não foi encontrado. Reinstale o Vsy Converter.")
    suffix = source.suffix.lower()
    stem = Path(str(output_stem or "")).stem.strip()
    stem = re.sub(r"[<>:\"/\\|?*]", "-", stem).strip(" .")
    if not stem:
        stem = source.stem + "-corte"
    target = _unique_target(directory, stem, suffix)
    duration = None if end is None else end - start
    progress("Preparando o corte…")
    with tempfile.TemporaryDirectory(prefix=".vsy-cut-", dir=directory) as temp:
        candidate = Path(temp) / ("resultado" + suffix)
        if suffix == ".gif":
            _cut_gif(ffmpeg, source, candidate, start, duration, cancelled, progress)
            summary = "GIF recodificado mantendo resolução e animação"
        else:
            command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                       "-ss", _time_arg(start), "-i", str(source)]
            if duration is not None:
                command += ["-t", _time_arg(duration)]
            command += ["-map", "0", "-c", "copy", "-map_metadata", "0",
                        "-avoid_negative_ts", "make_zero", str(candidate)]
            run_command(command, cancelled,
                        lambda elapsed: progress(f"Cortando sem recompressão… {elapsed:.0f}s"))
            summary = "vídeo/áudio copiado sem recompressão"
        if cancelled.is_set():
            raise Cancelled("Corte cancelado. O original foi preservado.")
        os.rename(candidate, target)
    return target, summary
