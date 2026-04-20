require('dotenv').config();
const { google } = require('googleapis');
const { getAuth } = require('../src/auth/googleAuth.cjs');
const fs = require('fs');
const path = require('path');

// --- CONFIGURACIÓN E ID's ---
const SPREADSHEET_ID = process.env.SPREADSHEET_ID;
const DRIVE_FOLDER_ID = process.env.DRIVE_FOLDER_ID;

console.log("--- 🔍 DEBUG SISTEMA GALINDO ---");
console.log("¿GOOGLE_CREDENTIALS detectada?:", !!process.env.GOOGLE_CREDENTIALS);
console.log("¿SPREADSHEET_ID detectada?:", !!SPREADSHEET_ID);
console.log("¿DRIVE_FOLDER_ID detectada?:", !!DRIVE_FOLDER_ID);
console.log("---------------------------------");

// --- UTILIDADES ---
const slugify = (t) => t.toString().toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').replace(/[^\w\-]+/g, '').replace(/\-\-+/g, '-');
const cleanNum = (v) => !v || v === "NAN" ? 0 : parseFloat(v.toString().replace(/[$,]/g, '')) || 0;

// Link de miniatura optimizado para carga rápida en la web
const getDirectLink = (id) => `https://drive.google.com/thumbnail?sz=w1000&id=${id}`;

async function run() {
  try {
    if (!SPREADSHEET_ID || !DRIVE_FOLDER_ID) {
      throw new Error("Faltan variables de entorno esenciales (ID de Sheet o Carpeta).");
    }

    console.log('🚀 Iniciando Pipeline Cloud: Sheets + Drive...');
    
    const auth = await getAuth();
    const drive = google.drive({ version: 'v3', auth });
    const sheets = google.sheets({ version: 'v4', auth });

    // 1. EXTRAER DATOS DEL EXCEL
    // Asegúrate que la pestaña se llame exactamente 'Template Excel'
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: "'Template Excel'!A1:Z200", 
    });

    const rows = res.data.values;
    if (!rows || rows.length === 0) {
      console.log('⚠️ No se encontraron filas en el Excel.');
      return;
    }

    let lastTitulo = "", lastZona = "", lastCiudad = "";
    const propiedades = [];

    // 2. PROCESAR FILAS (Desde la fila 2 para saltar encabezados)
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const propId = String(row[0] || "").trim().toUpperCase();
      
      // Saltamos filas vacías o basura
      if (!propId || propId === "ID" || propId === "NAN") continue;

      // Lógica de Autocompletado (FFill)
      const titulo = row[1] || lastTitulo; lastTitulo = titulo;
      const zona = row[6] || lastZona; lastZona = zona;
      const ciudad = row[7] || lastCiudad; lastCiudad = ciudad;

      let fotos = ["/images/placeholder.jpg"];

      try {
        // Buscamos la carpeta que se llame como el ID de la propiedad
        const fld = await drive.files.list({
          q: `'${DRIVE_FOLDER_ID}' in parents and name = '${propId}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`,
          fields: 'files(id)'
        });

        if (fld.data.files?.length > 0) {
          const folderId = fld.data.files[0].id;
          const img = await drive.files.list({
            q: `'${folderId}' in parents and mimeType contains 'image/' and trashed = false`,
            fields: 'files(id, name)'
          });
          
          if (img.data.files?.length > 0) {
            fotos = img.data.files
              .sort((a, b) => a.name.localeCompare(b.name, undefined, {numeric: true}))
              .map(f => getDirectLink(f.id));
            console.log(`✅ ${propId}: ${fotos.length} fotos encontradas.`);
          }
        }
      } catch (e) { 
        console.log(`⚠️ ${propId}: Error al buscar fotos o carpeta no encontrada.`); 
      }

      // 3. ARMADO DEL OBJETO FINAL
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
        fecha_publicacion: row[15] || new Date().toISOString().split('T')[0],
        estatus: (row[16] || "disponible").toLowerCase().trim(),
        imagenes: fotos
      });
    }

    // 4. GUARDAR EL RESULTADO
    const outPath = path.join(process.cwd(), 'src/data/propiedades.json');
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(propiedades, null, 2));
    
    console.log(`\n✨ ÉXITO: Se exportaron ${propiedades.length} propiedades correctamente.`);

  } catch (err) {
    console.error('❌ ERROR CRÍTICO EN EL SCRIPT:', err.message);
    process.exit(1);
  }
}

run();