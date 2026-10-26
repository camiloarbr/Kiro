// Datos de contacto de Kiro: cambiar aquí y se actualiza en toda la página.

export const correo = 'KiroSolutionsCol@gmail.com';
export const correoUrl = `mailto:${correo}?subject=${encodeURIComponent('Quiero un diagnóstico con Kiro')}`;

// PENDIENTE: número oficial de WhatsApp con indicativo y sin espacios ni «+», p. ej. '573001234567'.
export const WHATSAPP_NUMERO: string = '';

// Mientras no haya número se muestra el placeholder del diseño y no se genera enlace.
export const whatsappTexto = WHATSAPP_NUMERO
  ? `+${WHATSAPP_NUMERO.slice(0, 2)} ${WHATSAPP_NUMERO.slice(2, 5)} ${WHATSAPP_NUMERO.slice(5)}`
  : '[número de Kiro]';
export const whatsappUrl = WHATSAPP_NUMERO ? `https://wa.me/${WHATSAPP_NUMERO}` : undefined;
