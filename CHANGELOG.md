# Changelog

## 2.9.0 — English interface

- Translated the complete application interface, status messages, help text, and installer to English.
- Reworked the project page, screenshots, banner, and documentation for an English-speaking audience.
- Renamed documentation and license files to clear English names.
- Kept existing destination-folder and GIF-FPS preferences compatible with previous releases.
- Added an explicit English-only contribution policy for future releases.

## 2.8.2 — Start menu shortcut

- The installer creates a Start menu shortcut only.
- Vsy Converter does not register itself to start automatically with Windows.
- Existing desktop and legacy shortcuts are removed during installation.

## 2.8.1 — Shortcut cleanup

- Corrected the application shortcut so it appears only in the Start menu.
- Removed desktop shortcut creation.

## 2.8.0 — Media cuts

- Added a dedicated Cuts tab for video, audio, and GIF.
- Cut by start and end time in seconds or `HH:MM:SS.000`.
- Video and audio use direct stream copy to avoid recompression.
- GIFs are re-encoded while preserving resolution, duration, and animation.
- Remembered cut destination folder and safe cancellation.

## 2.7.0 — Discord export

- Added local Discord avatar and profile-banner preparation.
- Added size and dimension validation, conservative targets, and separate remembered folders.
- Added GIF animation preservation and static first-frame export.

## 2.6.0 — Refined interface

- Added the graphite and violet visual system, top navigation, responsive cards, and the `frstt.dev` project credit.
- Added cancellable conversion, progress reporting, duplicate-name protection, and remembered output preferences.
- Added 10–60 FPS video-to-GIF conversion with frame-aware timing.

## 2.3.0 — First public release

- Image conversion with ImageMagick.
- Video-to-GIF conversion with FFmpeg.
- Batch processing, resize controls, metadata options, and a complete Windows installer.

## Known behavior

Long GIFs may exceed Discord's target even after color reduction. Vsy Converter never drops frames or shortens duration automatically; it reports the result and preserves the original.
