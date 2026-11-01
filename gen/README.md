# Generador del perfil

Todo lo que se ve en el perfil se genera con `python gen/build.py`. No edites `assets/` ni los README de la raíz a mano: se sobrescriben.

| Quiero cambiar… | Dónde |
|---|---|
| Textos, ficha, logros, terminal, misiones, enlaces, inventario | `data/profile.json` |
| Colores, fuente, marcos | `gen/pixel.py` |
| La chica, el lobito, el lobo, la luna | `gen/sprites.py` (dibujos en ASCII: cada letra es un color) |
| Cómo se dibuja cada sección | `gen/sections.py` |
| Estructura del README | `gen/readme.py` |
| Un logo del inventario | Pon el SVG en `gen/icons/` y ejecuta `python tools/pixelate_icons.py` |

`data/live.json` lo escribe la Action **Datos vivos** cada día (contribuciones, rachas y lenguajes). Mientras esté vacío, la sección de puntuación no aparece.

Antes de subir cambios:

```bash
python gen/build.py
python tools/validate.py
pytest -q
python tools/preview.py   # opcional: capturas en previews/
```

Si añades texto con letras nuevas (por ejemplo, otro idioma), ejecuta `python tools/subset_font.py` para incluirlas en la fuente pixel.

Fuente: VT323 (SIL Open Font License, ver `fonts/OFL.txt`). Logos de [devicon](https://devicon.dev) y [Simple Icons](https://simpleicons.org), convertidos a pixel art.
