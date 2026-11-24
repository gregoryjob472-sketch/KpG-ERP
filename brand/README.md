# Marca KpG y Asesores SpA

Logotipo tipográfico con dos detalles del oficio contable:

- **Doble subrayado**: la doble raya que cierra un total cuadrado en un estado financiero.
- **Cuenta T**: el trazo descendente de la *p* cruza la doble raya y la divide, como el eje entre el debe y el haber.

## Archivos

| Carpeta | Contenido |
|---|---|
| `svg/` | Logos vectoriales (texto convertido a trazos, no requieren fuentes instaladas). Usar estos siempre que se pueda. |
| `png/` | Los mismos logos en PNG con fondo transparente, a 800 y 2400 px de ancho. Íconos a 1024 px. |
| `favicon/` | `favicon.ico`, `favicon.svg`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` para el ERP y la web. |
| `_fuente/` | Script que genera todo el set (`build.py`). |

### Qué versión usar

| Archivo | Uso |
|---|---|
| `kpg-logo` | Principal. Documentos, portadas, informes. Fondos claros. |
| `kpg-logo-inverso` | Principal sobre azul tinta u otro fondo oscuro. |
| `kpg-logo-horizontal` / `-inverso` | Membretes, encabezados web, firmas. |
| `kpg-wordmark` / `-inverso` | Solo "KpG" con la doble raya, sin descriptor. Para tamaños bajo 180 px de ancho y la barra del ERP. |
| `kpg-logo-mono-negro` / `-azul` / `-blanco` | Una sola tinta: timbres, grabados, fondos de color o foto. |
| `kpg-isotipo` / `-claro` | Cuadrado. Redes sociales, firma de correo, avatar. |
| `kpg-app-icon` | Ícono de aplicación con esquinas redondeadas. |
| `favicon/favicon.svg` | "K" simplificada para tamaños bajo 32 px. |

## Colores

| Nombre | HEX | RGB | Uso |
|---|---|---|---|
| Azul tinta | `#0E2A47` | 14 42 71 | Color principal |
| Latón | `#A8864F` | 168 134 79 | Doble raya sobre fondo claro |
| Latón claro | `#C9AC78` | 201 172 120 | Doble raya sobre azul tinta |
| Niebla | `#EEF1F5` | 238 241 245 | Fondos de pantalla y tablas |
| Papel | `#F6F7F9` | 246 247 249 | Letras sobre azul tinta |

## Tipografías (gratuitas, Google Fonts, licencia OFL)

- **Newsreader** (peso 500): logotipo y títulos.
- **Instrument Sans**: texto, interfaz del ERP y descriptor del logo.

## Reglas

- Área de resguardo: dejar libre alrededor del logo la altura de la *p* sin su trazo descendente.
- Tamaño mínimo: logo principal 30 mm / 140 px; horizontal 45 mm / 180 px; ícono 32 px.
- No agregar degradados, sombras ni relieves. No encerrar el logo en círculos o sellos. No deformarlo ni cambiar sus colores.

## Regenerar el set

Para cambiar el descriptor u otro detalle, editar `_fuente/build.py` y ejecutar:

```bash
pip install fonttools uharfbuzz
# descargar Newsreader[opsz,wght].ttf e InstrumentSans[wdth,wght].ttf
# (github.com/google/fonts, carpeta ofl/) en _fuente/fonts/
cd brand/_fuente && OUT=../svg python3 build.py
```
