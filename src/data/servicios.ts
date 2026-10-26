// Tarjetas de la sección Servicios. «grande» ocupa 3 de las 6 columnas en computador.
// «arte» es el contenido del SVG de la ilustración (viewBox 0 0 300 180); .fill va en violeta.
export const servicios = [
  {
    titulo: 'Páginas y plataformas web',
    descripcion: 'Sitios y portales que venden y reservan por ti, conectados a tu operación.',
    etiquetas: ['Reservas y citas en línea', 'Pagos con link', 'Hechos primero para el celular'],
    grande: true,
    arte: '<rect x="60" y="34" width="180" height="112" rx="10"/><path d="M60 56h180"/><circle cx="74" cy="45" r="3"/><circle cx="85" cy="45" r="3"/><rect x="76" y="70" width="70" height="8" rx="4"/><rect x="76" y="86" width="110" height="6" rx="3" opacity=".5"/><rect x="76" y="112" width="56" height="20" rx="10" class="fill"/>',
  },
  {
    titulo: 'Agentes de IA y chatbots',
    descripcion: 'En WhatsApp o en tu web: responden, agendan y ejecutan tareas a cualquier hora.',
    etiquetas: [
      'Respuestas con la información de tu negocio',
      'Agendan y cobran en la conversación',
      'Te pasan los casos que necesitan a una persona',
    ],
    grande: true,
    arte: '<rect x="70" y="40" width="120" height="34" rx="14"/><rect x="120" y="86" width="120" height="34" rx="14" class="fill"/><path d="M84 130h36" opacity=".5"/><circle cx="84" cy="57" r="3"/><circle cx="96" cy="57" r="3"/><circle cx="108" cy="57" r="3"/>',
  },
  {
    titulo: 'Automatización de procesos',
    descripcion: 'Los pasos que hoy haces a mano se hacen solos.',
    etiquetas: ['Recordatorios automáticos', 'Registros sin digitar', 'Cobros que se marcan solos'],
    grande: false,
    arte: '<circle cx="64" cy="90" r="16"/><rect x="124" y="74" width="52" height="32" rx="8" class="fill"/><circle cx="236" cy="90" r="16"/><path d="M80 90h44M176 90h44"/><path d="M150 40v34M150 106v34" opacity=".5"/>',
  },
  {
    titulo: 'Sistemas internos y paneles',
    descripcion: 'Tu operación y tus números en un solo lugar.',
    etiquetas: ['Indicadores del día a la vista', 'Accesos por rol', 'Reportes sin armar Excel'],
    grande: false,
    arte: '<rect x="60" y="34" width="180" height="112" rx="10"/><path d="M84 128V100M112 128V84M140 128V92M168 128V66M196 128V76" stroke-width="10" stroke-linecap="round"/><path d="M84 56h60" opacity=".5"/>',
  },
  {
    titulo: 'Integraciones',
    descripcion: 'Conectamos lo que ya usas: facturación, pagos, calendarios y mensajería.',
    etiquetas: ['Facturación y pagos', 'Calendarios', 'Canales de mensajería'],
    grande: false,
    arte: '<circle cx="150" cy="90" r="20" class="fill"/><circle cx="70" cy="50" r="12"/><circle cx="230" cy="50" r="12"/><circle cx="70" cy="130" r="12"/><circle cx="230" cy="130" r="12"/><path d="M82 56l50 24M218 56l-50 24M82 124l50-24M218 124l-50-24"/>',
  },
] as const;
