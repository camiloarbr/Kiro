---
name: Kairo Solutions · landing
description: Software a la medida para pymes. Tech moderna y audaz: negro dominante, un solo morado con intención y el cursor de terminal como sello.
colors:
  kairo-violet: "#8b2cf5"
  violeta-hover: "#9b45f7"
  morado-oscuro: "#5b17b8"
  morado-claro: "#b07cff"
  rosa-electrico: "#ff2bd6"
  rosa-oscuro: "#a1007f"
  kairo-black: "#0c0a10"
  grafito: "#1f1a27"
  gris: "#918a9e"
  blanco: "#f6f4fa"
  white: "#ffffff"
  lav: "#f4efff"
  lav-media: "#d9c4ff"
  lav-2: "#eaddff"
  lav-3: "#e4d3ff"
  lav-4: "#efe6ff"
  tinta-2: "#3b3346"
  tenue: "#5e566b"
  profundo-1: "#3a1677"
  profundo-2: "#6e22d6"
  profundo-3: "#1a1030"
  texto-oscuro: "#c9c3d3"
  texto-oscuro-2: "#a39cb0"
typography:
  display:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(44px, 5.2vw, 98px)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.035em"
  display-movil:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(36px, 10vw, 52px)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.035em"
  display-tablet:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(40px, 6.6vw, 58px)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.035em"
  titulo-seccion:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(34px, 4vw, 56px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.035em"
  titulo-seccion-movil:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(30px, 8.6vw, 38px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.035em"
  titulo-tarjeta-movil:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  cuerpo-tarjeta:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0em"
  titulo-tarjeta:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  cuerpo:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0em"
  pequeno:
    fontFamily: "Geist Variable, Geist, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.16em"
rounded:
  sm: "6px"
  md: "14px"
  lg: "22px"
  pill: "999px"
spacing:
  gutter-movil: "24px"
  gutter: "32px"
  carril-cubo: "164px"
  header-movil: "64px"
  header: "76px"
  seccion-movil: "96px"
  seccion: "150px"
components:
  button-primary:
    backgroundColor: "{colors.kairo-violet}"
    textColor: "{colors.white}"
    rounded: "{rounded.pill}"
    padding: "0 28px"
  button-primary-hover:
    backgroundColor: "{colors.violeta-hover}"
  card-oscura:
    backgroundColor: "{colors.grafito}"
    textColor: "{colors.white}"
    rounded: "{rounded.lg}"
  tarjeta-con-kairo:
    backgroundColor: "{colors.kairo-violet}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
---

# Design System: Kairo Solutions · landing

La fuente de la marca es `docs/marca/MANUAL-DE-MARCA.md` (copia del manual de Claude Design). Este archivo describe cómo ese manual se aplica en la landing y qué valores usa el código (`src/styles/global.css`). Si los dos chocan, gana el manual.

## Overview

Landing para pymes de Medellín (hoteles y consultorios). Su trabajo es dar confianza y abrir conversaciones: modo **persuadir**. El recorrido cuenta una historia con el cubo de 27 piezas (desarmado = un negocio sin Kairo; armado = Kairo llegó) y con Kai, la mascota en 3D, que acompaña la lectura. Alterna secciones lavanda («el problema, en claro») con secciones en Kairo Black.

## Colors

### Primary
- **Kairo Violet** `#8b2cf5`: logo, cursor, cubo armado y botón principal. Nunca más del 10 % de la pantalla.
- **Morado oscuro** `#5b17b8`: texto de acento sobre fondos claros (etiquetas de los mini cubos).
- **Morado claro** `#b07cff`: texto de acento sobre Kairo Black.

### Secondary
- **Rosa eléctrico** `#ff2bd6`: una sola cosa en toda la página (hoy, el contador del demo). Sobre claro, `#a1007f`.

### Neutral
- Kairo Black `#0c0a10` y grafito `#1f1a27` (tarjetas sobre negro).
- Lavandas de la extensión web: `lav`, `lav-2`, `lav-3`, `lav-4`, `lav-media`.
- Texto: `tinta-2` y `tenue` sobre lavanda; `texto-oscuro` y `texto-oscuro-2` sobre negro.

### Named Rules
- **Acento según el fondo:** sobre claro, morado oscuro; sobre negro, morado claro. El violeta como texto solo en títulos de 24 px o más sobre negro.
- **Sin efectos de color:** ni texto con degradado, ni brillos o halos de color, ni sombras moradas.

## Typography

Montserrat 700 para títulos, Geist para texto e interfaz. Manual: JetBrains Mono para datos y etiquetas (todavía no se usa en la landing).

### Hierarchy
- Display (h1 de la portada): `clamp(44px, 5.2vw, 98px)` en computador, siempre en 3 líneas (su ancho ubica el cubo). Tablet: `clamp(40px, 6.6vw, 58px)`, también en 3 líneas para caber en su columna. Celular: `clamp(36px, 10vw, 52px)`.
- Título de sección: `clamp(34px, 4vw, 56px)` en computador. **En celular y tablet, todos los h2 usan la misma escala: `clamp(30px, 8.6vw, 38px)`** (antes iban de 30 a 40 px según la sección y «No solo construimos software…» ocupaba 5 líneas a 360 px). Interlineado ~1,05 y `text-wrap: balance`.
- Título de tarjeta: 22 px (20 px en celular). Cuerpo: 18 px / 1,55, `text-wrap: pretty`; en las tarjetas de servicios, 16 px / 1,5. Pequeño: 13 px.
- Etiquetas que pueden partir en dos líneas (las de servicios): `text-wrap: balance`, para que no quede una palabra sola abajo.

## Layout

Contenedor de 1400 px con 24 px de margen en celular y 32 px en computador. En computador las secciones dejan 164 px a la derecha para el carril del cubo; en celular y tablet el cubo no viaja y los márgenes son parejos. Secciones con 96 / 150 px arriba y 72 / 110 px abajo.

Puntos de corte:
- **< 640 px, celular:** una columna. Portada de 1.900 px de scroll con Kai + cubo bajo el texto.
- **640–899 px, tablet (`40rem`):** portada en dos columnas (texto | Kai + cubo), servicios en dos columnas con la última tarjeta a lo ancho, «Cómo trabajamos» en 2 × 2 y el demo con las piezas a tamaño completo. No es el celular estirado.
- **≥ 900 px, computador (`md:`).** El diseño de computador no cambió con el ajuste de celular y tablet (nov 2026). Entre 900 y 1099 px la nube y los mini cubos van al 78 % para que sus textos no se salgan.

### Kai + cubo en la portada
Una sola composición: Kai parado junto al cubo, a su derecha y en el mismo piso, con la cabeza del tamaño del cubo y tapando apenas su esquina. Los dos tienen sombra neutra en el piso y la misma luz (de arriba a la izquierda). El conjunto, no solo el cubo, va centrado en su espacio y crece con la pantalla (`--s0`). Medidas y cálculo en `Hero.astro` y `docs/diseno/KAI-3D.md`.

## Elevation & Depth

Plano. La profundidad viene del 3D real (cubo y Kai), no de sombras. Las únicas sombras son neutras y con desplazamiento (Kai en la tarjeta de agentes).

## Shapes

Botones en píldora (999 px). Tarjetas de 22 px (servicios) y 14 px (tarjetas «Con Kairo»). El cursor de la marca es un cuadrado de esquinas rectas.

## Components

### Buttons
Píldora Kairo Violet con texto blanco, mínimo 52 px de alto (56 en la portada). Hover: `#9b45f7` y sube 2 px. Foco: contorno violeta de 2 px.

### Cards / Containers
Servicios: grafito con borde de 1 px lavanda al 16 % y un panel de ilustración en `profundo-3`. Tu día: tarjeta Kairo Violet con texto blanco.

### Navigation
Header pegado arriba, lavanda translúcido con desenfoque (el único `backdrop-filter`), de 64 px en celular y tablet y 76 px en computador. Sobre las secciones oscuras (Servicios, demo, Cómo trabajamos) pasa a Kairo Black al 90 % con el logo negativo y los enlaces en `texto-oscuro`: una capa que se enciende con `opacity` en 0,35 s, sin trabajo en cada scroll (lo avisa un IntersectionObserver). En celular solo quedan el logo y «Contáctanos». Enlaces del footer de 44 px de alto en celular y tablet.

### Kai 3D
Un solo `<canvas>` que viaja entre portada, acompañante y contacto. Reglas en `docs/diseno/KAI-3D.md`. En el contacto (celular y tablet) lo acompaña el cubo armado en miniatura, el mismo de la portada, que cierra el recorrido.

## Do's and Don'ts

### Do:
- Usar solo colores de la paleta, con su token.
- Contraste AA: 4,5:1 en texto normal y 3:1 en títulos grandes.
- Respetar «reducir movimiento» y animar solo `transform` y `opacity`.

### Don't:
- Texto con degradado, brillos o halos de color, rayas animadas de adorno.
- Rosa en el logo, el cubo, los botones o junto a un bloque morado.
- Colores escritos a mano fuera de la paleta.
- Etiquetas en mayúsculas encima de los títulos (eyebrows) o números de sección de adorno (01, 02…).

## Pendiente (decisión de marca)

El manual dice «no uses degradados». Todavía tienen degradado, porque son parte del diseño aprobado: las olas de Servicios, los fondos de las secciones (portada, Tu día, demo, cómo trabajamos, contacto), las franjas de transición claro → oscuro y el brillo del cubo de vidrio. La ilustración del teléfono y el panel del demo usa sus propios colores de interfaz. Falta decidir si se aplanan o si el manual agrega una excepción para la web.

Mientras tanto, en celular y tablet se suavizaron (nov 2026): la franja «Tu día» → Servicios es más corta (112 px) y no pasa por el lavanda medio, que en pantalla angosta se veía como una banda de brillo, y el centro del fondo del demo está más apagado para no competir con el panel. El cubo de vidrio con brillo ya no aparece en celular ni en tablet.
