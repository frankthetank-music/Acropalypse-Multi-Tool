# Acropalypse Restoration Multi-Tool

### A Comprehensive Solution for Acropalypse-Affected Images

Easily restore PNG and GIF files that have fallen victim to the Acropalypse CVE from 2023. This all-in-one solution effectively recovers image data accidentially stored in cropped screenshots by Google Pixel phones or Windows Snipping Tool, and can search and detect vulnerable images within local folders.

This Tool works seamlessly with Python 3.10 cross-platform on Windows and Linux-based systems.

Also, yes this code is dirty, as it was created as part of a lecture at University of applied Sciences Upper Austria, and students dont have much spare time - deal with it 😎

**Key Features & Improvements**:
- Restore and detect both GIF and PNG formats
- Support for PNG images with and without an alpha channel (RGB and RGBA)
- Compatible with all resolutions and tools, including Snipping Tool and Pixel Markup
- Enhanced PNG data restoration for improved reference color filling

**Based on**:
- https://gist.github.com/DavidBuchanan314/93de9d07f7fab494bcdf17c2bd6cef02
- https://github.com/heriet/acropalypse-gif

### System Compatibility

- Python 3.10 (other versions may also work)
- Windows / Linux / WSL

### Required Libraries

Pillow==9.5.0<br>
sv_ttk==2.4.3
