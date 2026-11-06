# Landing de Kairo — especificación del diseño final

> **Audit de Impeccable (nov 2026):** se quitaron el resplandor de la portada, el texto con degradado, el botón con brillo, las rayas animadas y los halos y sombras de color, porque el manual no los permite. También las etiquetas en mayúsculas sobre los títulos (eyebrows) y los números 01–05 de las tarjetas: el título habla solo. Detalles y valores en `DESIGN.md`.

**Fuente de verdad del diseño:**
- `docs/diseno/referencia/landing-estatica.html`: abre este archivo en Chrome. Es la landing completa funcionando, con todas las animaciones.
- `docs/diseno/referencia/Estilo-Glass.dc.html`: el código fuente del diseño (CSS completo, con todas las keyframes y medidas).
- `docs/diseno/referencia/Hero3D.dc.html`: la animación del celular 3D (chat → Kai → panel), con los textos de Hotel y Consultorio en el script del final.
- `docs/diseno/capturas/`: capturas de computador (1440×900) y celular (390×844) de cada sección.

Los archivos `.dc.html` son de una herramienta de diseño. Úsalos como **referencia** de estilos, medidas, textos y animaciones. **No** los copies tal cual al proyecto. Los `{{...}}`, `<sc-if>` y `<dc-import>` son sintaxis de esa herramienta.

---

## Concepto
Estilo «vidrio» con identidad Kairo:
- **Base:** fondos lavanda, bloques y piezas de vidrio morado en 3D, secciones que alternan entre claro y oscuro, botones redondeados (píldora) y la palabra de acento en morado.
- **Movimiento:** casi todo se anima con el scroll.
- **Hilo conductor:** un **cubo**. En la portada lo forman 27 bloques-cursor que se transforman con el scroll; al final se convierte en el cubo de vidrio que baja acompañando toda la página.

Regla de contenido: el estilo se inspiró en somoszora.com (competidor). **Nunca** se copia texto, estructura, cifras ni casos de Zora. No se inventan clientes, cifras ni testimonios.

## Estructura (en orden)

### 0. Header (sticky)
- Fondo lavanda translúcido con desenfoque. Sobre las secciones oscuras (Servicios, demo, Cómo trabajamos) pasa a Kairo Black translúcido con el logo negativo y los enlaces claros, con un fundido corto (nov 2026).
- Alto: 64 px en celular y tablet, 76 px en computador.
- Logo corto «kairo» a la izquierda.
- Links «Tu día», «Servicios» y «Cómo trabajamos». Se ocultan en celular.
- Botón píldora «Contáctanos», que lleva a `#contacto`.

### 1. Portada `#inicio` — «bloques-cursor» (escena fija mientras se hace scroll)
Referencia: `docs/diseno/referencia/portada-bloques-cursor.html` (verla en Chrome) y `portada-bloques-cursor.dc.html` (CSS, keyframes y posiciones). La sección «Tu día» de relleno y la etiqueta «Opción A» de esa referencia no son parte del diseño.

- **Altura y escena:** la sección mide 2900 px en computador y 1900 px en celular y tablet (antes 2600; nov 2026). Dentro hay una escena `position: sticky` que se queda fija mientras se hace scroll.
- **Textos:**
  - H1: «Software a la medida que **trabaja por ti.**» (el final va en morado). Sin el cursor parpadeante de la referencia (decisión de Gallo, oct 2026).
  - Sub: «Páginas web, agentes de IA y automatizaciones hechas para cómo opera tu negocio.»
  - Botón: «Conoce más →» (56 px de alto), que lleva a `#servicios`.
- **Kai + cubo (nov 2026):** una sola composición. Kai está parado junto al cubo inicial, a su derecha y en el mismo piso, un poco más alto que él y con la cabeza tapando apenas la esquina del cubo; los dos tienen sombra en el piso. Computador: columna derecha, junto al texto. Tablet (640–899 px): dos columnas, texto a la izquierda y la composición a la derecha. Celular: bajo el texto. Cuando el cubo explota, Kai sale lanzado. Sigue el cursor con la mirada. Detalles en `docs/diseno/KAI-3D.md`.
- **27 bloques-cursor:** mini cubos de **62 px** con 6 caras: frente/atrás, tapa clara y costados oscuros. Sus posiciones se generan en `src/data/bloques.ts`.
- **Cámara 3D:** perspectiva de 1500 px. Un grupo lleva todo al carril al final y una cámara gira el conjunto (`rotateX`/`rotateY`) y se aleja en el «ik».
- **Coreografía según el avance del scroll** dentro de la portada:
  - **0–5 %:** cubo 3×3×3 de bloques violeta a la derecha del título (cámara `rotateX(-24°) rotateY(-35°)`).
  - **8–22 %:** el texto del héroe se va a la izquierda.
  - **~16 %:** los bloques explotan en una nube y flotan girando. Algunos se vuelven grafito.
  - **28–38 %:** se ordenan en el monograma **«ik»**: la i en grafito (punto + palo de 9 bloques) y la K en violeta (dos brazos diagonales de 2 bloques de grosor). La cámara se aleja (`scale(.8)`).
  - **48–64 %:** se separan en **3 mini cubos 2×2×2**, cada uno en su tono de morado (claro, medio, oscuro), con sus textos (aparecen entre 46 y 52 % y se van entre 66 y 72 %):
    - ENTENDEMOS — «Mapeamos cómo opera tu negocio hoy.»
    - CONSTRUIMOS — «Software a la medida, con módulos propios e IA.»
    - ACOMPAÑAMOS — «Ajustamos contigo mientras tu negocio crece.»
    En computador van en fila con el texto debajo; en celular, en columna con el texto a la derecha.
  - **76–84 %:** se vuelven a armar en el cubo 3×3×3 al centro.
  - **72–82 %:** aparece la frase «Tecnología que se adapta **a tu negocio.**» con el sub «Automatizamos lo repetitivo para que tu equipo se enfoque en lo importante.»
  - **84–94 %:** el cubo se encoge (de 186 a 88 px) y vuela al carril derecho; la lente se acerca al carril (perspectiva 700 px).
  - **93–97 %:** el cubo de bloques se apaga mientras aparece el cubo que acompaña la página, en el mismo lugar, tamaño y pose.
- **Celular y tablet:** la cámara va a escala 0,6, el cubo inicial sale bajo el título junto a Kai (en tablet, a la derecha del texto) y la nube es más compacta. El cubo **no viaja al carril**: termina armado bajo la frase y la portada se va con él; vuelve a aparecer armado junto a Kai en el contacto.
- **Versión estática** (Firefox, sin scroll-driven animations o con «reducir movimiento»): título, el cubo 3×3×3 quieto, los tres pasos en lista y la frase.

### 2. Cubo que acompaña (desde el final de la portada hasta el contacto)
- **Posición:**
  - Computador: carril fijo a la derecha, `position: sticky` centrado verticalmente, cubo de 88 px.
  - Celular y tablet: no hay carril (nov 2026). Antes iba pegado al borde derecho y pisaba títulos, tarjetas y el demo. El contenido tiene márgenes parejos de 24 px.
- **Movimiento:** gira con el scroll (~3 vueltas a lo largo de la página). Tiene un núcleo de luz que pulsa.
- **Línea violeta:** detrás del cubo, se dibuja con el scroll.
- **Espacio reservado:** en computador, las secciones dejan ~164 px a la derecha para que el cubo no tape texto.

### 3. «Tu día, con y sin Kairo» `#dia`
- **Encabezado:**
  - Título: «Tu día, con y sin **Kairo.**»
  - Sub: «Baja y mira cómo las tareas que hoy haces a mano se van resolviendo solas.»
- **Filas:** 6 filas de vidrio claro (hora · tarea de hoy · flecha · tarjeta Kairo Violet plana con «CON KAIRO» en blanco).
  - Al bajar, la tarea de hoy se tacha.
  - Después entra la tarjeta «Con Kairo».

| Hora | Hoy | Con Kairo |
|---|---|---|
| 7:30 a. m. | Revisas los mensajes que llegaron de noche, uno por uno. | Kai ya los respondió y dejó las citas agendadas. |
| 10:00 a. m. | Confirmas las citas de mañana por WhatsApp. | Los recordatorios salieron solos y ya hay respuestas. |
| 1:00 p. m. | Persigues anticipos y revisas transferencias. | Cada pago quedó registrado al entrar. |
| 4:00 p. m. | Copias reservas del chat a un Excel. | Todo cayó directo en tu panel. |
| 6:30 p. m. | Armas a mano el resumen del día. | El reporte del día ya está listo. |
| 11:00 p. m. | Un cliente escribe y nadie responde. | Kai responde y le reserva. |

- **Cierre:** «Lo que hoy te quita el día, **Kairo lo hace solo.**»

### 4. Servicios `#servicios` (sección oscura con olas)
- **Fondo:** Kairo Black plano.
- **Olas:** a izquierda y derecha, **olas de vidrio violeta** (SVG con degradados y un borde brillante) que se mecen sin parar. Además se desplazan con el scroll (parallax).
- **Encabezado** centrado:
  - Título grande: «¿Qué podemos **construir** para ti?» (la palabra «construir» en morado claro; sin texto con degradado).
  - Sub: «Partimos de módulos propios y los ajustamos a tu operación. Empiezas por lo que más te duele y sumas lo demás.»
- **5 tarjetas:**
  - Cada una tiene arriba una ilustración de líneas lavanda sobre un panel `profundo-3`. Tarjeta en grafito.
  - Abajo lleva número, título, descripción y etiquetas.
  - Entran inclinadas (rotateX) al hacer scroll.
  - Grilla de 6 columnas en computador: las 2 primeras ocupan 3 columnas y las otras 3 ocupan 2.
  - Las tarjetas:
    1. **Páginas y plataformas web.** Sitios y portales que venden y reservan por ti, conectados a tu operación. Etiquetas: Reservas y citas en línea · Pagos con link · Hechos primero para el celular.
    2. **Agentes de IA y chatbots.** En WhatsApp o en tu web: responden, agendan y ejecutan tareas a cualquier hora. Etiquetas: Respuestas con la información de tu negocio · Agendan y cobran en la conversación · Te pasan los casos que necesitan a una persona.
    3. **Automatización de procesos.** Los pasos que hoy haces a mano se hacen solos. Etiquetas: Recordatorios automáticos · Registros sin digitar · Cobros que se marcan solos.
    4. **Sistemas internos y paneles.** Tu operación y tus números en un solo lugar. Etiquetas: Indicadores del día a la vista · Accesos por rol · Reportes sin armar Excel.
    5. **Integraciones.** Conectamos lo que ya usas: facturación, pagos, calendarios y mensajería. Etiquetas: Facturación y pagos · Calendarios · Canales de mensajería.
- **Celular:** tarjeta compacta (ilustración de 96 px, menos relleno). **Tablet:** dos columnas; la última tarjeta va a lo ancho con la ilustración al lado.
- **Botón:** «Cuéntanos qué necesitas →» (botón principal, sin brillo). Lleva a `#contacto`.

### 5. «Así se ve en tu negocio» (demo)
- **Fondo:** degradado que va de Kairo Black a morado y vuelve a oscuro.
- **Encabezado:**
  - Título: «Del mensaje a la reserva, sin que muevas un dedo.»
  - Sub: «Un cliente escribe, Kai responde y la reserva aparece confirmada en tu panel.»
- **Selector** Hotel / Consultorio (botones píldora). Cambia los textos de la animación.
- **Animación en bucle de 19,2 s** (ver `Hero3D.dc.html`):
  1. Una barra de chat escribe la pregunta del cliente letra por letra.
  2. La barra viaja al celular 3D. Kai responde, con puntos de «escribiendo…».
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
- **Tablet:** las 4 filas en una cuadrícula de 2 × 2.

### 7. Contacto `#contacto`
- **Kai:** al llegar da un saltito. En celular y tablet tiene al lado el cubo armado (el de la portada en miniatura), que gira hasta su pose al entrar en pantalla.
- **Textos:**
  - Título: «¿Qué te quita **tiempo** hoy?»
  - Sub: «Cuéntanos el problema y te mostramos cómo lo resolvemos con software.»
- **Botones:**
  - «WhatsApp [número de Kairo]». **Pendiente**: deja el número en una sola constante.
  - «Escríbenos un correo», que abre `mailto:KiroSolutionsCol@gmail.com?subject=Quiero un diagnóstico con Kairo`.

### 8. Footer (Kairo Black)
- **Columna de marca:** logo negativo + «Software a la medida, agentes de IA y automatización.»
- **Columna de enlaces:** Tu día, Servicios, Cómo trabajamos.
- **Columna de contacto:** Medellín, Colombia · correo · WhatsApp.
- **Pie:** «© 2026 Kairo Solutions» · «Volver arriba».

---

## Tokens
- **Colores:** `docs/marca/MANUAL-DE-MARCA.md`, sección 4 (incluye la extensión web lavanda).
- **Fuentes:** Montserrat (títulos), Geist (texto).
- **Contenedor y espaciado:**
  - Contenedor máximo de 1400 px.
  - Padding lateral de 32 px en computador y 24 px en celular.
  - Secciones con 150 px arriba y 110 px abajo en computador; 96/72 px en celular.
- **Títulos:** H1 `clamp(44px, 5.4vw, 104px)`, line-height 1. H2 `clamp(34px, 4vw, 56px)`. En celular y tablet todos los H2 usan `clamp(30px, 8.6vw, 38px)` (nov 2026).
- **Bordes:** radios de 16–26 px en tarjetas y paneles; botones en píldora (999 px).
- **Puntos de quiebre:** 900 px (computador) y 640 px (tablet: portada en dos columnas, servicios en dos columnas, «Cómo trabajamos» en 2 × 2 y el demo a tamaño completo). Por debajo de 640 px es el diseño de celular.

## Reglas de rendimiento (ya probadas en el diseño)
- **Solo `transform` y `opacity`:** anima únicamente esas dos propiedades. Nada de `filter: blur()` animado ni `backdrop-filter` en elementos que se mueven. Solo el header usa `backdrop-filter`.
- **Olas:** se mueven con `transform`, no se redibuja el trazado del SVG.
- **`will-change`:** solo en paneles, cubo y olas.
- **Accesibilidad:** con `prefers-reduced-motion: reduce` todo queda estático y legible. En la portada, el cubo de bloques queda quieto, los tres pasos se muestran en lista y el cubo que acompaña se oculta.
- **Navegadores:**
  - Scroll-driven animations (`animation-timeline: view()` / `scroll()`, `view-timeline`, `timeline-scope`) funcionan en Chrome, Edge y Safari recientes.
  - Firefox necesita **mejora progresiva**: una alternativa con `IntersectionObserver` para las entradas y la portada mostrada en estado legible.
