// Filas de «Tu día, con y sin Kiro». hora24 va en el atributo datetime de <time>.
export const filasDia = [
  {
    hora: '7:30 a. m.',
    hora24: '07:30',
    hoy: 'Revisas los mensajes que llegaron de noche, uno por uno.',
    conKiro: 'Kiro Bot ya los respondió y dejó las citas agendadas.',
  },
  {
    hora: '10:00 a. m.',
    hora24: '10:00',
    hoy: 'Confirmas las citas de mañana por WhatsApp.',
    conKiro: 'Los recordatorios salieron solos y ya hay respuestas.',
  },
  {
    hora: '1:00 p. m.',
    hora24: '13:00',
    hoy: 'Persigues anticipos y revisas transferencias.',
    conKiro: 'Cada pago quedó registrado al entrar.',
  },
  {
    hora: '4:00 p. m.',
    hora24: '16:00',
    hoy: 'Copias reservas del chat a un Excel.',
    conKiro: 'Todo cayó directo en tu panel.',
  },
  {
    hora: '6:30 p. m.',
    hora24: '18:30',
    hoy: 'Armas a mano el resumen del día.',
    conKiro: 'El reporte del día ya está listo.',
  },
  {
    hora: '11:00 p. m.',
    hora24: '23:00',
    hoy: 'Un cliente escribe y nadie responde.',
    conKiro: 'Kiro Bot responde y le reserva.',
  },
] as const;
