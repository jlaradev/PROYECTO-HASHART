// Configuración de URLs de la API según el ambiente
const API_BASE_URL = 'https://proyecto-hashart.onrender.com';

export const API_ENDPOINTS = {
  REGISTRAR_PDF: `${API_BASE_URL}/registrar_pdf/`,
  VERIFICAR_PDF: `${API_BASE_URL}/verificar_pdf/`,
  HEALTH_CHECK: `${API_BASE_URL}/`,
};

export default API_BASE_URL;
