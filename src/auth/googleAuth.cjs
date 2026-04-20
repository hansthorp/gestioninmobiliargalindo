const { google } = require('googleapis');
const path = require('path');

// Solo usamos googleapis, que es lo que npm audit confirmó que tienes
// Cambia la línea de SCOPES en src/auth/googleAuth.js
const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.metadata.readonly' // Para ver nombres de fotos
];
async function getAuth() {
  try {
    // Apunta al credentials.json que tienes en la raíz del proyecto
    const auth = new google.auth.GoogleAuth({
      keyFile: path.join(process.cwd(), 'credentials.json'),
      scopes: SCOPES,
    });

    const client = await auth.getClient();
    return client;
  } catch (error) {
    console.error('Error en Auth:', error);
    throw error;
  }
}

// ESTA LÍNEA ES VITAL:
module.exports = { getAuth };