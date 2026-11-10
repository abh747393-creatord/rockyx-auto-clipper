# Bundled caption fonts

22 free fonts from Google Fonts, all under the SIL Open Font License (OFL) —
free to use, including in commercial videos. They ship with the tool so the
caption font picker works identically on Windows, Linux and the VPS with no
install: the renderer points libass at this folder (subtitles filter
`fontsdir`, see `render.py`).

Downloaded 2026-11-10 from Google Fonts (fonts.googleapis.com /
fonts.gstatic.com), one bold/heavy weight per family, chosen for short-form
captions. The font name used in the captions is the TTF's nameID 1, exactly
as `fontTools` reports it (see `config.FONTS`).

| Font | File | Weight |
|---|---|---|
| Montserrat ExtraBold | montserrat.ttf | 800 |
| Poppins | poppins.ttf | 700 |
| Bebas Neue | bebas-neue.ttf | 400 |
| Anton | anton.ttf | 400 |
| Oswald SemiBold | oswald.ttf | 600 |
| Archivo Black | archivo-black.ttf | 400 |
| Roboto Black | roboto.ttf | 900 |
| Inter ExtraBold | inter.ttf | 800 |
| Open Sans ExtraBold | open-sans.ttf | 800 |
| Lato Black | lato.ttf | 900 |
| Nunito ExtraBold | nunito.ttf | 800 |
| Quicksand | quicksand.ttf | 700 |
| Fredoka SemiBold | fredoka.ttf | 600 |
| Baloo 2 ExtraBold | baloo-2.ttf | 800 |
| Luckiest Guy | luckiest-guy.ttf | 400 |
| Bangers | bangers.ttf | 400 |
| Titan One | titan-one.ttf | 400 |
| Alfa Slab One | alfa-slab-one.ttf | 400 |
| Bungee | bungee.ttf | 400 |
| Righteous | righteous.ttf | 400 |
| Russo One | russo-one.ttf | 400 |
| Permanent Marker | permanent-marker.ttf | 400 |

Total: 22 files, ~2.4 MB. To add a font: drop the TTF here and add one
line to `config.FONTS` (+ its group in `config.FONT_GROUPS`).
