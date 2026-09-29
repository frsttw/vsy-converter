<div align="center">
  <img src="docs/banner.png" alt="Vsy Converter" width="100%">
  <p><strong>A graphical interface for image and media conversion on Windows.</strong></p>
</div>

## Overview

Vsy Converter provides a visual workflow for the existing **ImageMagick** and **FFmpeg** tools. It coordinates input selection, output formats, quality, resizing, GIF creation, Discord profile assets, and media cuts without requiring terminal commands. The application is an interface and workflow layer over these established conversion engines.

## Features

- Batch image conversion to JPG, PNG, WebP, AVIF, GIF, BMP, TIFF, ICO, and PDF.
- Video-to-GIF conversion through FFmpeg.
- Quality, resize, metadata, and frame-rate controls.
- Discord avatar and profile-banner preparation.
- Video, audio, and GIF cutting.
- Original-file protection and automatic duplicate naming.
- Cancelable operations with progress feedback.
- Complete Windows installer with ImageMagick and FFmpeg.

## Technology stack

- Python and Tkinter/ttk for the desktop interface.
- ImageMagick for image conversion and processing.
- FFmpeg for video, audio, GIF, and cutting operations.
- PyInstaller and Inno Setup for packaging.

## Usage

1. Download `Instalador-Vsy-Converter.exe` from [Releases](https://github.com/frsttw/vsy-converter/releases).
2. Add one or more images or media files.
3. Select the output format and quality.
4. Choose a destination folder and start the operation.

## Build and tests

Run the installer build script on Windows:

```powershell
.\build-installer.ps1
python -m unittest discover -p "test_*.py" -v
```

## License

MIT License. See [LICENCAS-DE-TERCEIROS.txt](LICENCAS-DE-TERCEIROS.txt) for third-party notices.

<p align="center">Built by <a href="https://frstt.dev">frstt.dev</a> · <a href="https://github.com/frsttw">@frsttw</a></p>
