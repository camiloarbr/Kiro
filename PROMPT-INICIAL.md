Hola. Vamos a desarrollar la landing page de **Kiro Solutions** en este repositorio (https://github.com/camiloarbr/Kiro), paso a paso y explicándome todo lo que hagas.

**Contexto**
- **Quiénes somos:** Kiro Solutions es mi empresa de software en Medellín. Hacemos software a la medida para pymes: páginas web, agentes de IA y chatbots, automatización, sistemas internos e integraciones. Hoy nos enfocamos en atención al cliente para hoteles y consultorios.
- **Para qué es la landing:** darnos credibilidad y conseguir conversaciones con clientes.
- **Diseño:** ya está terminado y aprobado.

**Lee primero, en este orden:**
1. `CLAUDE.md`: contexto, stack, estructura y reglas de trabajo.
2. `docs/marca/MANUAL-DE-MARCA.md`: manual de marca completo de Kiro. Los logos e íconos oficiales están en `docs/marca/assets/`.
3. `docs/diseno/ESPECIFICACION-LANDING.md`: el diseño final, sección por sección, con todos los textos.
4. `docs/diseno/referencia/landing-estatica.html`: el diseño final funcionando. Ábrelo en el navegador y míralo en computador y en celular. Los `.dc.html` de esa carpeta tienen el CSS y las keyframes exactas.
5. `docs/diseno/capturas/`: capturas de cada sección.

**Stack**
- Astro 5 + TypeScript.
- Tailwind CSS v4.
- Animaciones con CSS nativo (scroll-driven animations y 3D) y JS vanilla mínimo.
- Fuentes autoalojadas: Montserrat y Geist.
- pnpm; deploy en Cloudflare Workers (sitio estático) con dominio propio más adelante.

**Cómo quiero que trabajes**
- **Un paso a la vez.** Al terminar cada paso, para, dime cómo verlo y espera mi OK antes de seguir.
- **Explícame en español** en cada paso:
  - qué archivos creaste o cambiaste;
  - por qué se organiza así;
  - cómo funciona el código importante, sobre todo las animaciones con scroll y el 3D.
  Estoy estudiando Ingeniería de Sistemas y quiero entenderlo.
- **Fidelidad al diseño:** igual a la referencia en computador y en celular.
- **Rendimiento y accesibilidad:** anima solo `transform` y `opacity` y respeta `prefers-reduced-motion`. Pon una alternativa para navegadores sin scroll-driven animations (Firefox).
- **Git:** yo soy el autor del proyecto. Al final de cada paso propón el mensaje del commit y, si lo apruebo, haz el commit con mi configuración de git, sin `Co-Authored-By` ni menciones a Claude. **Nunca hagas push**: el push lo hago yo.

**Plan sugerido** (ajústalo si ves algo mejor y dime por qué):
1. Crear el proyecto Astro + Tailwind. Configurar los tokens de marca, las fuentes, el favicon y el layout base.
2. Header y Footer.
3. Portada con los 3 paneles de vidrio, que al final se arman como un cubo.
4. Cubo que acompaña el scroll.
5. «Tu día, con y sin Kiro».
6. Servicios con olas y tarjetas.
7. Demo de Kiro Bot (celular 3D → panel) con el selector Hotel/Consultorio.
8. Cómo trabajamos y Contacto.
9. Pulido final: comparación con las capturas, `prefers-reduced-motion`, la alternativa para Firefox, Lighthouse, SEO (título, descripción, Open Graph) y `wrangler.jsonc` para desplegar en Cloudflare Workers.

Empieza con el **paso 0**. Revisa el repo, lee los documentos y dame un resumen corto de lo que entendiste y del plan. No escribas código todavía.
