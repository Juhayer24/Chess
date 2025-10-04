<img src="https://github.com/user-attachments/assets/1a59c7b2-11e7-492d-bf9e-f923c58d00b8">
<img src="https://github.com/user-attachments/assets/02fdbe9d-0818-4143-829e-60d46a3223c5">
<img src="https://github.com/user-attachments/assets/d95d7598-75d9-414e-b42e-c6ddd9b14480">

# Notes

- Piece image transparency: The code now prefers loading PNGs with per-pixel alpha. If your piece images have solid backgrounds, the loader will attempt to treat the top-left pixel as transparent. For best results, use PNG images with an alpha channel so the board color shows through the piece sprites.
- Bug fix (2025-10-04): `utils.create_piece_surfaces` was updated to call `convert_alpha()` and `smoothscale()` when possible to preserve transparency and avoid black background boxes behind piece images.

