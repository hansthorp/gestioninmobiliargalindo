const { google } = require('googleapis');
const path = require('path');

const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.metadata.readonly'
];

async function getAuth() {
  try {
    let authOptions;

    // MAGIA DE VERCEL: Si detecta la variable de entorno, la usa
    if (process.env.GOOGLE_CREDENTIALS) {
      console.log("Utilizando credenciales desde variable de entorno (Vercel)");
      const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
      authOptions = {
        credentials,
        scopes: SCOPES,
      };
    } 
    // MODO LOCAL: Si no hay variable, busca el archivo en tu PC
    else {
      console.log("Utilizando archivo credentials.json local");
      authOptions = {
        keyFile: path.join(process.cwd(), 'credentials.json'),
        scopes: SCOPES,
      };
    }

    const auth = new google.auth.GoogleAuth(authOptions);
    return await auth.getClient();
  } catch (error) {
    console.error('Error en Auth:', error);
    throw error;
  }
}

module.exports = { getAuth };