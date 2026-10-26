# Landing de Kiro — especificación del diseño final

**Fuente de verdad del diseño:**
- `docs/diseno/referencia/landing-estatica.html`: abre este archivo en Chrome. Es la landing completa funcionando, con todas las animaciones.
- `docs/diseno/referencia/Estilo-Glass.dc.html`: el código fuente del diseño (CSS completo, con todas las keyframes y medidas).
- `docs/diseno/referencia/Hero3D.dc.html`: la animación del celular 3D (chat → Kiro Bot → panel), con los textos de Hotel y Consultorio en el script del final.
- `docs/diseno/capturas/`: capturas de computador (1440×900) y celular (390×844) de cada sección.

Los archivos `.dc.html` son de una herramienta de diseño. Úsalos como **referencia** de estilos, medidas, textos y animaciones. **No** los copies tal cual al proyecto. Los `{{...}}`, `<sc-if>` y `<dc-import>` son sintaxis de esa herramienta.

---

## Concepto
Estilo «vidrio» con identidad Kiro:
- **Base:** fondos lavanda, paneles de vidrio morado en 3D, secciones que alternan entre claro y oscuro, botones redondeados (píldora) y la palabra de acento en morado.
- **Movimiento:** casi todo se anima con el scroll.
- **Hilo conductor:** un **cubo de vidrio**. Nace de los paneles de la portada y baja acompañando toda la página.

Regla de contenido: el estilo se inspiró en somoszora.com (competidor). **Nunca** se copia texto, estructura, cifras ni casos de Zora. No se inventan clientes, cifras ni testimonios.

## Estructura (en orden)

### 0. Header (sticky)
- Fondo lavanda translúcido con desenfoque.
- Logo corto «kiro» a la izquierda.
- Links «Tu día», «Servicios» y «Cómo trabajamos». Se ocultan en celular.
- Botón píldora «Contáctanos», que lleva a `#contacto`.

### 1. Portada `#inicio` (escena fija mientras se hace scroll)
- **Altura y escena:** la sección mide ~2600 px en computador y ~2300 px en celular. Dentro hay una escena `position: sticky` que se queda fija mientras se hace scroll.
- **Textos:**
  - H1: «Software a la medida que **trabaja por ti.**» (el final va en morado).
  - Sub: «Páginas web, agentes de IA y automatizaciones hechas para cómo opera tu negocio.»
  - Botón: «Conoce más →», que lleva a `#servicios`.
  - Etiquetas en mayúsculas: Software a la medida · Agentes de IA · Automatización · Integraciones.
- **3 paneles de vidrio morado** (360×460 en computador; 286×168 en celular), con estos textos:
  - ENTENDEMOS — «Mapeamos cómo opera tu negocio hoy.»
  - CONSTRUIMOS — «Software a la medida, con módulos propios e IA.»
  - ACOMPAÑAMOS — «Ajustamos contigo mientras tu negocio crece.»
- **Coreografía según el avance del scroll** dentro de la portada:
  - **0–8 %:** paneles apilados a la derecha, girados en 3D (rotateY -28°), con el texto del héroe a la izquierda.
  - **8–24 %:** el texto del héroe se va. Los paneles se separan dando vueltas en profundidad.
  - **40–64 %:** quedan en fila: izquierda, centro y derecha (en celular, en columna vertical). El texto de cada panel se lee claro, sobre un degradado oscuro en la parte de abajo. El panel central avanza un poco hacia la cámara.
  - **76–88 %:** los paneles se encogen y vuelan al carril derecho, donde **se arman como 3 caras de un cubo** (frente, lado y tapa). Una luz blanca («sol») viaja con ellos y se convierte en el núcleo del cubo.
  - **74–86 %:** aparece la frase «Tecnología que se adapta **a tu negocio.**» con el sub «Automatizamos lo repetitivo para que tu equipo se enfoque en lo importante.»
  - **92–100 %:** el cubo «se enciende» (crece un poco y brilla) y pasa a ser el cubo que acompaña la página.
- Detalle exacto: keyframes `z-p0`, `z-p1`, `z-p2` (computador), `z-p0m`, `z-p1m`, `z-p2m` (celular), `z-sun`, `z-persp`, `z-st` y `z-heroout` en `Estilo-Glass.dc.html`.

### 2. Cubo que acompaña (desde el final de la portada hasta el contacto)
- **Posición:**
  - Computador: carril fijo a la derecha, `position: sticky` centrado verticalmente, cubo de 70 px.
  - Celular: abajo a la derecha, cubo de 32 px.
- **Movimiento:** gira con el scroll (~3 vueltas a lo largo de la página). Tiene un núcleo de luz que pulsa.
- **Línea violeta:** detrás del cubo, se dibuja con el scroll.
- **Espacio reservado:** en computador, las secciones dejan ~164 px a la derecha para que el cubo no tape texto.

### 3. «Tu día, con y sin Kiro» `#dia`
- **Encabezado:**
  - Eyebrow: UN DÍA CUALQUIERA.
  - Título: «Tu día, con y sin **Kiro.**»
  - Sub: «Baja y mira cómo las tareas que hoy haces a mano se van resolviendo solas.»
- **Filas:** 6 filas de vidrio claro (hora · tarea de hoy · flecha · tarjeta morada «CON KIRO»).
  - Al bajar, la tarea de hoy se tacha.
  - Después entra la tarjeta «Con Kiro».

| Hora | Hoy | Con Kiro |
|---|---|---|
| 7:30 a. m. | Revisas los mensajes que llegaron de noche, uno por uno. | Kiro Bot ya los respondió y dejó las citas agendadas. |
| 10:00 a. m. | Confirmas las citas de mañana por WhatsApp. | Los recordatorios salieron solos y ya hay respuestas. |
| 1:00 p. m. | Persigues anticipos y revisas transferencias. | Cada pago quedó registrado al entrar. |
| 4:00 p. m. | Copias reservas del chat a un Excel. | Todo cayó directo en tu panel. |
| 6:30 p. m. | Armas a mano el resumen del día. | El reporte del día ya está listo. |
| 11:00 p. m. | Un cliente escribe y nadie responde. | Kiro Bot responde y le reserva. |

- **Cierre:** «Lo que hoy te quita el día, **Kiro lo hace solo.**»

### 4. Servicios `#servicios` (sección oscura con olas)
- **Fondo:** Kiro Black con brillo morado arriba.
- **Olas:** a izquierda y derecha, **olas de vidrio violeta** (SVG con degradados y un borde brillante) que se mecen sin parar. Además se desplazan con el scroll (parallax).
- **Encabezado** centrado:
  - Eyebrow: SERVICIOS.
  - Título grande: «¿Qué podemos **construir** para ti?» (la palabra «construir» con degradado violeta).
  - Sub: «Partimos de módulos propios y los ajustamos a tu operación. Empiezas por lo que más te duele y sumas lo demás.»
- **5 tarjetas:**
  - Cada una tiene arriba una ilustración de líneas violeta brillante, con rayas de luz en movimiento detrás.
  - Abajo lleva número, título, descripción y etiquetas.
  - Entran inclinadas (rotateX) al hacer scroll.
  - Grilla de 6 columnas en computador: las 2 primeras ocupan 3 columnas y las otras 3 ocupan 2.
  - Las tarjetas:
    1. **Páginas y plataformas web.** Sitios y portales que venden y reservan por ti, conectados a tu operación. Etiquetas: Reservas y citas en línea · Pagos con link · Hechos primero para el celular.
    2. **Agentes de IA y chatbots.** En WhatsApp o en tu web: responden, agendan y ejecutan tareas a cualquier hora. Etiquetas: Respuestas con la información de tu negocio · Agendan y cobran en la conversación · Te pasan los casos que necesitan a una persona.
    3. **Automatización de procesos.** Los pasos que hoy haces a mano se hacen solos. Etiquetas: Recordatorios automáticos · Registros sin digitar · Cobros que se marcan solos.
    4. **Sistemas internos y paneles.** Tu operación y tus números en un solo lugar. Etiquetas: Indicadores del día a la vista · Accesos por rol · Reportes sin armar Excel.
    5. **Integraciones.** Conectamos lo que ya usas: facturación, pagos, calendarios y mensajería. Etiquetas: Facturación y pagos · Calendarios · Canales de mensajería.
- **Botón:** «Cuéntanos qué necesitas ↗», con brillo. Lleva a `#contacto`.

### 5. «Así se ve en tu negocio» (demo)
- **Fondo:** degradado que va de Kiro Black a morado y vuelve a oscuro.
- **Encabezado:**
  - Título: «Del mensaje a la reserva, sin que muevas un dedo.»
  - Sub: «Un cliente escribe, Kiro Bot responde y la reserva aparece confirmada en tu panel.»
- **Selector** Hotel / Consultorio (botones píldora). Cambia los textos de la animación.
- **Animación en bucle de 19,2 s** (ver `Hero3D.dc.html`):
  1. Una barra de chat escribe la pregunta del cliente letra por letra.
  2. La barra viaja al celular 3D. Kiro Bot responde, con puntos de «escribiendo…».
  3. El último mensaje se queda visible ~4 s.
  4. La reserva sale volando del celular a un panel (dashboard). En el panel: el KPI pasa de 7 de 8 a 8 de 8, se ilumina una celda nueva en la grilla de ocupación, la fila de Laura M. cambia de «Por confirmar» a «Confirmada» y aparece un aviso de confirmación.
- **Versión celular:** el celular va casi derecho y a tamaño completo. El panel no tiene barra lateral (350 px de ancho).
- **Textos por escenario:**
  - Hotel: «Hola, ¿hay habitación para el sábado?» / «¡Hola! Sí, nos queda la habitación 8, doble. ¿Te la reservo?» / «Sí, por favor» / «Listo. Te envié el link del anticipo.» El panel es de «Casa Ceiba».
  - Consultorio: «Hola, ¿hay cita de limpieza el jueves?» / «¡Hola! Sí, me queda un espacio a las 3:00 p. m. ¿Te lo agendo?» / «Sí, gracias» / «Listo. Te envié el link del anticipo.» El panel es de «Ceiba Odontología».
  - Datos completos de cada escenario: objeto `S` en el script de `Hero3D.dc.html`.

### 6. Cómo trabajamos `#como`
- **Fondo:** degradado oscuro → morado → lavanda.
- **Encabezado:** título «No solo construimos software. Lo hacemos funcionar contigo.»
- **4 filas de vidrio translúcido:**
  - Diagnóstico — Conversamos y mapeamos cómo opera tu negocio hoy.
  - Prototipo — Ves y pruebas una versión funcional antes de decidir.
  - Entrega — Lo ponemos a funcionar en semanas, con tu equipo.
  - Acompañamiento — Ajustamos contigo a medida que tu negocio crece.

### 7. Contacto `#contacto`
- **Textos:**
  - Eyebrow: HABLEMOS.
  - Título: «¿Qué te quita **tiempo** hoy?»
  - Sub: «Cuéntanos el problema y te mostramos cómo lo resolvemos con software.»
- **Botones:**
  - «WhatsApp [número de Kiro]». **Pendiente**: deja el número en una sola constante.
  - «Escríbenos un correo», que abre `mailto:KiroSolutionsCol@gmail.com?subject=Quiero un diagnóstico con Kiro`.

### 8. Footer (Kiro Black)
- **Columna de marca:** logo negativo + «Software a la medida, agentes de IA y automatización.»
- **Columna de enlaces:** Tu día, Servicios, Cómo trabajamos.
- **Columna de contacto:** Medellín, Colombia · correo · WhatsApp.
- **Pie:** «© 2026 Kiro Solutions» · «Volver arriba».

---

## Tokens
- **Colores:** `docs/marca/MANUAL-DE-MARCA.md`, sección 4 (incluye la extensión web lavanda).
- **Fuentes:** Montserrat (títulos), Geist (texto).
- **Contenedor y espaciado:**
  - Contenedor máximo de 1400 px.
  - Padding lateral de 32 px en computador y 24 px en celular.
  - Secciones con 150 px arriba y 110 px abajo en computador; 96/72 px en celular.
- **Títulos:** H1 `clamp(44px, 5.4vw, 104px)`, line-height 1. H2 `clamp(34px, 4vw, 56px)`.
- **Bordes:** radios de 16–26 px en tarjetas y paneles; botones en píldora (999 px).
- **Punto de quiebre:** ~900 px. Por debajo es el diseño de celular.

## Reglas de rendimiento (ya probadas en el diseño)
- **Solo `transform` y `opacity`:** anima únicamente esas dos propiedades. Nada de `filter: blur()` animado ni `backdrop-filter` en elementos que se mueven. Solo el header usa `backdrop-filter`.
- **Olas:** se mueven con `transform`, no se redibuja el trazado del SVG.
- **`will-change`:** solo en paneles, cubo y olas.
- **Accesibilidad:** con `prefers-reduced-motion: reduce` todo queda estático y legible. Los paneles se muestran en grilla y el cubo se oculta.
- **Navegadores:**
  - Scroll-driven animations (`animation-timeline: view()` / `scroll()`, `view-timeline`, `timeline-scope`) funcionan en Chrome, Edge y Safari recientes.
  - Firefox necesita **mejora progresiva**: una alternativa con `IntersectionObserver` para las entradas y la portada mostrada en estado legible.
