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
  titulo-seccion:
    fontFamily: "Montserrat Variable, Montserrat, sans-serif"
    fontSize: "clamp(34px, 4vw, 56px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.035em"
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
- Display (h1 de la portada): `clamp(44px, 5.2vw, 98px)`, siempre en 3 líneas (su ancho ubica el cubo).
- Título de sección: `clamp(34px, 4vw, 56px)`, interlineado ~1,05, `text-wrap: balance`.
- Título de tarjeta: 22 px. Cuerpo: 18 px / 1,55, `text-wrap: pretty`. Pequeño: 13 px.

## Layout

Contenedor de 1400 px con 24 px de margen en celular y 32 px en computador. En computador las secciones dejan 164 px a la derecha para el carril del cubo. Un solo punto de corte: 900 px (`md:`). Secciones con 96 / 150 px arriba y 72 / 110 px abajo.

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
Header pegado arriba, lavanda translúcido con desenfoque (el único `backdrop-filter`). En celular solo quedan el logo y «Contáctanos».

### Kai 3D
Un solo `<canvas>` que viaja entre portada, acompañante y contacto. Reglas en `docs/diseno/KAI-3D.md`.

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
