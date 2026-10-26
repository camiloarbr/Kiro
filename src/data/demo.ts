// Textos del demo de Kiro Bot por escenario (objeto S de docs/diseno/referencia/Hero3D.dc.html).
// «Casa Ceiba», «Ceiba Odontología» y «Laura M.» son nombres de muestra, no clientes reales.

export interface Escenario {
  id: 'hotel' | 'consultorio';
  boton: string;
  etiquetaAccesible: string;
  cliente1: string;
  bot1: string;
  cliente2: string;
  bot2: string;
  marca: string;
  inicialMarca: string;
  menu: [string, string, string, string];
  titulo: string;
  semana: string;
  accion: string;
  kpi1: string;
  kpi3: string;
  kpi3Valor: string;
  columnas: string[];
  filas: [string, string, string];
  columnaA: string;
  detalle: [string, string, string];
  vuelo: string;
  aviso: string;
}

export const escenarios: Escenario[] = [
  {
    id: 'hotel',
    boton: 'Hotel',
    etiquetaAccesible:
      'Un cliente escribe por chat, Kiro Bot le reserva la habitación 8 y la reserva aparece confirmada en el panel del hotel',
    cliente1: 'Hola, ¿hay habitación para el sábado?',
    bot1: '¡Hola! Sí, nos queda la habitación 8, doble. ¿Te la reservo?',
    cliente2: 'Sí, por favor',
    bot2: 'Listo. Te envié el link del anticipo.',
    marca: 'Casa Ceiba',
    inicialMarca: 'C',
    menu: ['Reservas', 'Calendario', 'Huéspedes', 'Pagos'],
    titulo: 'Reservas',
    semana: 'Viernes 23 a domingo 25 de octubre',
    accion: 'Nueva reserva',
    kpi1: 'Ocupación sábado',
    kpi3: 'Llegadas hoy',
    kpi3Valor: '2',
    columnas: ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8'],
    filas: ['Vie', 'Sáb', 'Dom'],
    columnaA: 'Huésped',
    detalle: ['Hab. 8 · sábado', 'Hab. 3 · vie y sáb', 'Hab. 5 · domingo'],
    vuelo: 'Reserva de Laura M.',
    aviso: 'Reserva confirmada · anticipo pagado',
  },
  {
    id: 'consultorio',
    boton: 'Consultorio',
    etiquetaAccesible:
      'Un paciente escribe por chat, Kiro Bot le agenda una cita y la cita aparece confirmada en la agenda del consultorio',
    cliente1: 'Hola, ¿hay cita de limpieza el jueves?',
    bot1: '¡Hola! Sí, me queda un espacio a las 3:00 p. m. ¿Te lo agendo?',
    cliente2: 'Sí, gracias',
    bot2: 'Listo. Te envié el link del anticipo.',
    marca: 'Ceiba Odontología',
    inicialMarca: 'C',
    menu: ['Agenda', 'Pacientes', 'Pagos', 'Recordatorios'],
    titulo: 'Agenda',
    semana: 'Miércoles 21 a viernes 23 de octubre',
    accion: 'Nueva cita',
    kpi1: 'Citas jueves',
    kpi3: 'Pacientes hoy',
    kpi3Valor: '5',
    columnas: ['8', '9', '10', '11', '12', '1', '2', '3'],
    filas: ['Mié', 'Jue', 'Vie'],
    columnaA: 'Paciente',
    detalle: ['Limpieza · jue 3 p. m.', 'Control · jue 9 a. m.', 'Valoración · vie'],
    vuelo: 'Cita de Laura M.',
    aviso: 'Cita confirmada · anticipo pagado',
  },
];

// Ocupación de la grilla (3 filas × 8 columnas): 0 libre, 1 ocupada, 2 la que reserva Kiro Bot.
export const ocupacion = [
  [1, 1, 0, 1, 1, 1, 0, 1],
  [1, 1, 1, 1, 1, 1, 1, 2],
  [1, 0, 0, 1, 0, 1, 0, 0],
] as const;
