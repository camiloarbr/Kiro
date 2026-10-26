# Kiro Solutions — Manual de marca v1.0

> Fuente oficial de la identidad de Kiro. Versión visual completa: `docs/marca/manual-de-marca.html` (ábrelo en el navegador).
> Archivos de logo, ícono y correo: `docs/marca/assets/` (SVG y PNG) y `docs/marca/assets/kiro-marca-vectores.pdf`.
> Octubre 2026 · Medellín, Colombia.

---

## 1. Esencia

**Qué es Kiro.** Kiro Solutions es una empresa de software de Medellín. Hace **software a la medida** para negocios pequeños y medianos (páginas y plataformas web, agentes de IA y chatbots, automatización de procesos, sistemas internos y paneles, integraciones) y prepara productos **SaaS** propios. Hoy ataca sobre todo la atención al cliente en hoteles y consultorios de salud.

**Propósito.** Convertir ideas y procesos de negocio en software que funciona, se usa y escala.

**El cursor.** El punto de la «i» es un cuadrado morado: el cursor de una terminal, listo para escribir la siguiente línea. Es el único elemento de color del logo y el sello de la marca.

**Taglines (opciones):**
- «Software que pasa a producción.»
- «De la idea al deploy.»
- «Construimos lo que tu negocio necesita.»

### Personalidad
| Atributo | Qué significa |
|---|---|
| **Audaz** | Decisiones claras, formas contundentes, color con intención. |
| **Precisa** | Estética de ingeniería: grillas, código y cero adorno innecesario. |
| **Ágil** | Habla de entregas, iteraciones y resultados medibles. |
| **Cercana** | Explica la tecnología sin jerga a clientes que no son técnicos. |

### Voz
**Así hablamos**
- Frases cortas y verbos de acción.
- Tuteo en web y redes; «usted» solo si el cliente lo usa.
- Datos concretos (tiempos, ahorros, métricas) **solo si son reales**.

**Así no**
- «Soluciones integrales innovadoras de vanguardia.»
- Siglas sin explicar (API, CI/CD) con clientes no técnicos.
- Promesas o cifras inventadas. Kiro aún no publica casos de éxito ni números hasta tener un piloto medido.
- Exceso de emojis o mayúsculas.

> **Nombre:** Amazon tiene un IDE con IA llamado Kiro. Usar «Kiro Solutions» completo en documentos legales y comerciales, y no imitar su identidad visual. Pendiente validar en la SIC (clases 9 y 42).

---

## 2. Logotipo

- «kiro» en **minúsculas**, Montserrat Bold, tracking cerrado.
- El punto de la «i» es un **cuadrado Kiro Violet** del mismo ancho que el palo de la «i».
- «solutions» debajo, Montserrat Light, tracking amplio, centrado.

**Versiones** (en `assets/logo/`):
| Archivo | Uso |
|---|---|
| `kiro-logo-principal.svg` | Sobre fondos claros |
| `kiro-logo-principal-negativo.svg` | Sobre fondos oscuros |
| `kiro-logo-mono-negro.svg` / `kiro-logo-mono-blanco.svg` | Una sola tinta |
| `kiro-logotipo-corto.svg` / `-negativo.svg` | Solo «kiro» (espacios pequeños, header de la web) |
| `kiro-logo-sobre-blanco/negro/morado.svg` | Imagen con fondo |

**Reglas**
- **Unidad x** = lado del cursor. **Área libre** mínima de 1x en los cuatro lados.
- **Tamaño mínimo** del logo completo: 100 px / 25 mm de ancho. Por debajo, logotipo corto o ícono.
- El cursor **siempre morado**, salvo en versiones monocromas y sobre fondo morado (ahí va blanco).

**Usos incorrectos:** deformar o estirar · cambiar el color del cursor · rotar o inclinar · usar sin contraste suficiente (p. ej. morado sobre morado).

---

## 3. Ícono (monograma «ik»)

La «i» completa (cursor y palo) en **blanco** comparte el palo con los brazos de la **K en Kiro Violet**, sobre **Kiro Black**. Se usa en app, favicon y fotos de perfil.

- Archivos: `assets/icono/kiro-icono-app.svg` (principal), `kiro-icono-app-claro.svg` (fondo blanco, i negra, K morada), `kiro-icono-cuadrado.svg`, `kiro-simbolo-negativo.svg`; PNG en 1024, 512, 180 y 32 px.
- Esquinas: radio de 18,75 % del lado. El monograma ocupa ~35 % del ancho, centrado.
- No hacer: poner la «i» en morado, separar la i de la K, usar el ícono sobre fondo morado.
- **Favicon de la web:** `kiro-icono-app-32.png` + `kiro-icono-app.svg`; `apple-touch-icon` = `kiro-icono-app-180.png`.

---

## 4. Color

| Nombre | HEX | Uso |
|---|---|---|
| **Kiro Violet** | `#8B2CF5` | Acento: cursor, botones principales, dato clave. Máx. 10 %. |
| Morado oscuro | `#5B17B8` | Hover, bloques destacados |
| Morado claro | `#B07CFF` | Texto de acento sobre negro |
| **Kiro Black** | `#0C0A10` | Fondo principal oscuro |
| Grafito | `#1F1A27` | Superficies sobre negro |
| Gris | `#918A9E` | Texto secundario |
| Blanco | `#F6F4FA` | Texto sobre negro, fondos claros |

- Regla **60 / 30 / 10** en piezas de marca: negro dominante, neutros de apoyo, morado solo para lo que debe llamar la atención.
- Contraste: blanco sobre Kiro Violet = 5,6:1 (AA). Kiro Violet sobre negro solo para títulos grandes; para texto usar Morado claro.
- En productos SaaS: verde éxito, ámbar advertencia, rojo error; el morado solo para marca y acciones.

### Extensión web (landing «estilo vidrio», aprobada oct 2026)
La landing usa la paleta oficial más tonos lavanda derivados del morado para las secciones claras:

| Token | HEX | Uso |
|---|---|---|
| `--lav` | `#F4EFFF` | Fondo claro principal |
| `--v3` | `#D9C4FF` | Lavanda media (bordes, brillos) |
| lavanda 2 | `#EADDFF` / `#E4D3FF` / `#EFE6FF` | Degradados de sección |
| `--ink2` | `#3B3346` | Texto secundario sobre lavanda |
| `--muted` | `#5E566B` | Texto terciario sobre lavanda |
| morado profundo | `#3A1677` / `#6E22D6` / `#1A1030` | Degradados oscuros |

Las secciones alternan claro (lavanda) y oscuro (Kiro Black → morado). El morado de acento sigue siendo `#8B2CF5`.

---

## 5. Tipografía

| Familia | Uso | Pesos |
|---|---|---|
| **Montserrat** | Títulos (y logo) | Bold 700 títulos, SemiBold 600, Light 300 subtítulos |
| **Geist** | Texto e interfaz | 400 / 500 / 600 |
| **JetBrains Mono** | Datos, código, etiquetas | 400 / 600 |

Las tres son gratuitas (Google Fonts / licencia OFL). En Google Docs, Slides y Gmail: Montserrat + Arial.

En la web: títulos Montserrat 700 con `letter-spacing` negativo (≈ -0.035em), texto Geist 18 px, eyebrows en mayúsculas 13 px con tracking .16em.

---

## 6. Aplicaciones

- **Firma de correo:** logo PNG 360 px (`assets/correo/kiro-firma-logo-claro.png`) + texto real (nombre, cargo, correo, teléfono).
- **Foto de perfil:** `assets/correo/kiro-foto-perfil-512.png`.
- **Tarjeta:** fondo Kiro Black, logo negativo, cuadrado violeta en la esquina.
- **Post de redes:** fondo Kiro Black, logotipo corto, frase en Montserrat 700 con la palabra clave en Morado claro.

Contacto actual: **KiroSolutionsCol@gmail.com** · Medellín, Colombia · WhatsApp: *pendiente*.

---

## 7. Pendientes de marca
1. Validar nombre en la SIC, dominio (.co / .com) y redes.
2. Número de WhatsApp oficial.
3. Plantillas: propuesta, cotización, presentación.
