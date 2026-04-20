const { google } = require('googleapis');
const path = require('path');

const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.metadata.readonly'
];

async function getAuth() {
  try {
    let authOptions;

    // 1. Verificamos si estamos en Vercel (Variable de entorno)
    if (process.env.GOOGLE_CREDENTIALS) {
      console.log("✅ Utilizando credenciales desde Vercel (Variable de Entorno)");
      const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
      authOptions = {
        credentials,
        scopes: SCOPES,
      };
    } 
    // 2. Si no, buscamos el archivo local (Tu PC)
    else {
      console.log("💻 Utilizando archivo credentials.json local");
      authOptions = {
        keyFile: path.join(process.cwd(), 'credentials.json'),
        scopes: SCOPES,
      };
    }

    const auth = new google.auth.GoogleAuth(authOptions);
    return await auth.getClient();
    
  } catch (error) {
    console.error('❌ Error en Auth:', error);
    throw error;
  }
}

module.exports = { getAuth };