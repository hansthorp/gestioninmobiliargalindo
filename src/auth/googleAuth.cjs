const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

async function getAuth() {
  let credentials;

  // 1. Intentar leer desde la Variable de Entorno (Modo Vercel)
  if (process.env.GOOGLE_CREDENTIALS) {
    try {
      console.log('🔑 Usando credenciales desde Variable de Entorno...');
      credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
    } catch (e) {
      console.error('❌ Error al parsear GOOGLE_CREDENTIALS:', e);
    }
  } 
  
  // 2. Si no hay variable, intentar leer el archivo físico (Modo Local)
  if (!credentials) {
    const keyPath = path.join(process.cwd(), 'credentials.json');
    if (fs.existsSync(keyPath)) {
      console.log('📂 Usando archivo credentials.json local...');
      credentials = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
    }
  }

  if (!credentials) {
    throw new Error('No se encontraron credenciales (ni en variable ni en archivo).');
  }

  // Crear el cliente de autenticación
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: [
      'https://www.googleapis.com/auth/spreadsheets.readonly',
      'https://www.googleapis.com/auth/drive.metadata.readonly'
    ],
  });

  return auth;
}

module.exports = { getAuth };