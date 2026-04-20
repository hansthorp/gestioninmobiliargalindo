require('dotenv').config(); // <--- ESTA LÍNEA ES EL "BOTÓN DE ENCENDIDO" PARA LAS VARIABLES
const { google } = require('googleapis');
const path = require('path');

const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.metadata.readonly'
];

async function getAuth() {
  try {
    let authOptions;

    // Prioridad a Vercel
    if (process.env.GOOGLE_CREDENTIALS && process.env.GOOGLE_CREDENTIALS.length > 0) {
      console.log("✅ Utilizando credenciales desde Vercel (Variable de Entorno)");
      const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
      authOptions = {
        credentials,
        scopes: SCOPES,
      };
    } 
    // Plan B: Local
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
    console.error('❌ Error en Auth:', error.message);
    throw error;
  }
}

module.exports = { getAuth };