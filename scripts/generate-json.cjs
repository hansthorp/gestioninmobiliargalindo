const { google } = require('googleapis');
const { getAuth } = require('../src/auth/googleAuth.cjs');
const fs = require('fs');
const path = require('path');
require('dotenv').config(); // <--- AGREGA ESTA LÍNEA AQUÍ

// --- UTILIDADES OPTIMIZADAS ---
const slugify = (t) => t.toString().toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').replace(/[^\w\-]+/g, '').replace(/\-\-+/g, '-');
const cleanNum = (v) => !v || v === "NAN" ? 0 : parseFloat(v.toString().replace(/[$,]/g, '')) || 0;

// Link directo optimizado (s0 trae la resolución original)
//const getDirectLink = (id) => `https://lh3.googleusercontent.com/d/${id}=s0`;
// Prueba esta versión si la anterior falla después de dar permisos
//const getDirectLink = (id) => `https://drive.google.com/uc?export=view&id=${id}`;
const getDirectLink = (id) => `https://drive.google.com/thumbnail?sz=w1000&id=${id}`;
async function run() {
  try {
    console.log('🚀 Iniciando Pipeline Cloud: Sheets + Drive...');
    const auth = await getAuth();
    const drive = google.drive({ version: 'v3', auth });
    const sheets = google.sheets({ version: 'v4', auth });

    // 1. EXTRAER DATOS
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: process.env.SPREADSHEET_ID,
      range: "'Template Excel'!A1:Z200", 
    });

    const rows = res.data.values;
    if (!rows) return console.log('❌ Error: No hay datos.');

    let lastTitulo = "", lastZona = "", lastCiudad = "";
    const propiedades = [];

    // 2. PROCESAR FILAS (FFILL + DRIVE SYNC)
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const propId = String(row[0] || "").trim().toUpperCase();
      if (!propId || propId === "ID" || propId === "NAN") continue;

      // Lógica de Relleno (FFill)
      const titulo = row[1] || lastTitulo; lastTitulo = titulo;
      const zona = row[6] || lastZona; lastZona = zona;
      const ciudad = row[7] || lastCiudad; lastCiudad = ciudad;

      let fotos = ["/images/placeholder.jpg"];

      try {
        // Búsqueda de carpeta por nombre (ID)
        const fld = await drive.files.list({
          q: `'${process.env.DRIVE_FOLDER_ID}' in parents and name = '${propId}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`,
          fields: 'files(id)'
        });

        if (fld.data.files?.length > 0) {
          const img = await drive.files.list({
            q: `'${fld.data.files[0].id}' in parents and mimeType contains 'image/' and trashed = false`,
            fields: 'files(id, name)'
          });
          
          if (img.data.files?.length > 0) {
            fotos = img.data.files
              .sort((a, b) => a.name.localeCompare(b.name, undefined, {numeric: true}))
              .map(f => getDirectLink(f.id));
            console.log(`✅ ${propId}: ${fotos.length} fotos.`);
          }
        }
      } catch (e) { console.log(`⚠️ ${propId}: Sin fotos.`); }

      // 3. MAPEO AL OBJETO FINAL
      propiedades.push({
        id: propId,
        slug: slugify(`${titulo}-${propId}`),
        titulo,
        operacion: (row[3] || "venta").toLowerCase().trim(),
        tipo: (row[4] || "casa").toLowerCase().trim(),
        precio: cleanNum(row[5]),
        zona,
        ciudad,
        m2Terreno: cleanNum(row[8]),
        m2Construccion: cleanNum(row[9]),
        recamaras: Math.floor(cleanNum(row[10])),
        banos: Math.floor(cleanNum(row[11])),
        estacionamientos: Math.floor(cleanNum(row[12])),
        descripcion: (row[13] || "").trim(),
        whatsapp: (row[14] || "2281852255").toString().split('.')[0],
        fecha_publicacion: row[15] || "2026-04-03",
        estatus: (row[16] || "disponible").toLowerCase().trim(),
        imagenes: fotos
      });
    }

    // 4. GUARDAR JSON
    const out = path.join(process.cwd(), 'src/data/propiedades.json');
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(propiedades, null, 2));
    console.log(`\n✨ Listo: ${propiedades.length} propiedades exportadas.`);

  } catch (err) {
    console.error('❌ Error Crítico:', err);
    process.exit(1);
  }
}
run();