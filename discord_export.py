"""Exportação local de imagens para perfis do Discord."""
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import tempfile
import threading
import shutil
import sys
import time


@dataclass(frozen=True)
class Preset:
    label: str
    width: int
    height: int
    max_bytes: int


# Margens de exportação, não limites contratuais da plataforma.
PRESETS = {
    "avatar": Preset("Avatar", 512, 512, 7_500_000),
    "banner": Preset("Capa de perfil", 680, 240, 9_500_000),
}
IMAGE_PATTERNS = "*.png *.jpg *.jpeg *.gif *.webp *.avif *.bmp *.tif *.tiff *.heic *.heif *.svg *.ico *.psd"


class Cancelled(Exception):
    pass


def run_command(command, cancelled, on_tick=None):
    if cancelled.is_set():
        raise Cancelled("Conversão cancelada.")
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(command, stdout=log, stderr=log,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            started = time.monotonic()
            for _ in range(2400):  # limite de dez minutos por tentativa
                try:
                    code = process.wait(timeout=0.25)
                    break
                except subprocess.TimeoutExpired:
                    if cancelled.is_set():
                        raise Cancelled("Conversão cancelada.")
                    if on_tick:
                        on_tick(time.monotonic() - started)
            else:
                raise RuntimeError("Tempo limite excedido. Tente um GIF mais curto.")
            log.seek(0)
            output = log.read().decode("utf-8", errors="replace")
            if code != 0:
                raise RuntimeError(output[-1400:] or "Não foi possível ler ou converter a imagem.")
            return output
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


def find_video_engine():
    for candidate in (Path(sys.executable).parent / "ffmpeg.exe",
                      Path(__file__).parent / "vendor" / "ffmpeg.exe"):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("ffmpeg")


def encode_gif(ffmpeg, source, candidate, width, height, fit, colors,
               frames, last_delay, cancelled, progress, percent):
    """Processa quadros em fluxo: não mantém a animação inteira descompactada."""
    mode = "increase" if fit == "crop" else "decrease"
    geometry = f"scale={width}:{height}:force_original_aspect_ratio={mode}:flags=lanczos,format=rgba"
    geometry += (f",crop={width}:{height}" if fit == "crop" else
                 f",pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x00000000")
    palette = candidate.with_suffix('.palette.png')
    percent(-1)
    progress(f"Analisando cores · {width}×{height} · {colors} cores...")
    run_command([ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                 '-ignore_loop', '1', '-min_delay', '0', '-i', str(source),
                 '-vf', geometry + f',palettegen=max_colors={colors}',
                 '-frames:v', '1', str(palette)], cancelled,
                lambda elapsed: progress(f"Analisando cores · {elapsed:.0f}s"))
    graph = f"[0:v]{geometry},setsar=1[v];[v][1:v]paletteuse=dither=none"
    stats = candidate.with_suffix(".progress")
    stats.write_text("", encoding="utf-8")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
               "-ignore_loop", "1", "-min_delay", "0", "-i", str(source),
               "-i", str(palette), "-filter_complex_threads", "2", "-filter_complex", graph,
               "-fps_mode", "passthrough", "-final_delay", str(last_delay),
               "-loop", "0", "-progress", str(stats), "-stats_period", "0.25", str(candidate)]
    prefix = f"{width}×{height} · {colors} cores"
    last = [-1]
    def tick(elapsed):
        try:
            lines = stats.read_text(encoding="utf-8").splitlines()
            values = [int(line.split("=", 1)[1].strip()) for line in lines if line.startswith("frame=")]
            frame = values[-1] if values else 0
        except (OSError, ValueError):
            frame = 0
        if frame != last[0]:
            last[0] = frame
            percent(min(99, 100 * frame / max(1, frames)))
            progress(f"{prefix} · quadro {min(frame, frames)}/{frames} · {elapsed:.0f}s")
    percent(0)
    run_command(command, cancelled, tick)
    percent(100)


def convert_image(magick, source, directory, kind, fit, output_format,
                  cancelled=None, progress=lambda text: None, percent=lambda value: None):
    cancelled = cancelled or threading.Event()
    preset = PRESETS[kind]
    source = Path(source).resolve(strict=True)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if fit not in {"crop", "contain"} or output_format not in {"AUTO", "PNG", "JPG", "GIF"}:
        raise ValueError("Opções de exportação inválidas.")
    base = [str(magick), "-limit", "memory", "256MiB", "-limit", "map", "512MiB"]
    progress("Lendo a imagem e os quadros...")
    info = run_command([str(magick), "identify", "-ping", "-format", "%m %T\n", str(source)], cancelled)
    frames = len(info.strip().splitlines())
    animated = frames > 1
    is_gif = info.startswith("GIF ")
    ffmpeg = find_video_engine() if is_gif else None
    ext = ("gif" if animated else "png") if output_format == "AUTO" else output_format.lower()
    sizes = [(preset.width, preset.height)]
    if kind == "avatar":
        sizes += [(256, 256), (128, 128)]
    colors = [256, 128, 64, 32] if ext in {"gif", "png"} else [92, 82, 70, 55]
    with tempfile.TemporaryDirectory(prefix=".vsy-discord-", dir=directory) as temp:
        candidate = Path(temp) / ("resultado." + ext)
        for width, height in sizes:
            for level in colors:
                progress(f"Otimizando {width}×{height} • {'qualidade' if ext == 'jpg' else 'cores'} {level}...")
                read_path = str(source) if ext == "gif" else str(source) + "[0]"
                command = base + [read_path]
                if ext == "gif":
                    command += ["-coalesce"]
                command += ["-auto-orient", "-resize", f"{width}x{height}" + ("^" if fit == "crop" else ""),
                            "-gravity", "center", "-background", "white" if ext == "jpg" else "none",
                            "-extent", f"{width}x{height}", "+repage", "-strip"]
                if ext == "jpg":
                    command += ["-alpha", "remove", "-alpha", "off", "-quality", str(level)]
                elif ext == "gif":
                    command += ["-colors", str(level), "-layers", "OptimizeTransparency", "-loop", "0"]
                elif level < 256:
                    command += ["-colors", str(level)]
                command += [str(candidate)]
                if ext == "gif" and ffmpeg:
                    last_delay = int(info.strip().splitlines()[-1].split()[1])
                    encode_gif(ffmpeg, source, candidate, width, height, fit, level,
                               frames, last_delay, cancelled, progress, percent)
                else:
                    run_command(command, cancelled,
                                lambda elapsed: progress(f"Otimizando {width}×{height} · {elapsed:.0f}s"))
                size = candidate.stat().st_size
                progress(f"Verificando {size / 1_000_000:.2f} MB (meta < {preset.max_bytes / 1_000_000:g} MB)...")
                if 0 < size < preset.max_bytes:
                    dimensions = run_command([str(magick), "identify", "-ping", "-format", "%W %H\n" if ext == 'gif' else "%w %h\n", str(candidate)], cancelled)
                    if any(line != f"{width} {height}" for line in dimensions.strip().splitlines()):
                        raise RuntimeError("A validação de dimensões falhou. Nenhum arquivo foi publicado.")
                    if ext == 'gif' and len(dimensions.strip().splitlines()) != frames:
                        raise RuntimeError('A validação dos quadros falhou. Nenhum arquivo foi publicado.')
                    if cancelled.is_set():
                        raise Cancelled("Conversão cancelada.")
                    stem = f"{source.stem}-discord-{kind}"
                    number = 1
                    while True:
                        target = directory / (stem + (f" ({number})" if number > 1 else "") + "." + ext)
                        try:
                            # Windows: rename falha se o destino existir, sem sobrescrever.
                            if target.exists():
                                number += 1
                                continue
                            os.rename(candidate, target)
                            break
                        except FileExistsError:
                            number += 1
                    note = " • primeiro quadro (imagem estática)" if animated and ext != "gif" else ""
                    return target, f"{width}×{height} • {size / 1_000_000:.2f} MB • {ext.upper()}{note}"
    raise RuntimeError(f"O arquivo continua acima da margem de tamanho: {size / 1_000_000:.2f} MB, para uma meta abaixo de {preset.max_bytes / 1_000_000:g} MB.\nUse um GIF mais curto ou escolha PNG/JPG para salvar apenas o primeiro quadro. O original foi preservado.")
