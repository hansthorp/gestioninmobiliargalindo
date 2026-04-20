const { google } = require('googleapis');
const { getAuth } = require('../src/auth/googleAuth.cjs');
const fs = require('fs');
const path = require('path');

// Carga variables de entorno (Local: .env | Cloud: Vercel Settings)
require('dotenv').config();

// --- UTILIDADES ---
const slugify = (t) => t.toString().toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').replace(/[^\w\-]+/g, '').replace(/\-\-+/g, '-');
const cleanNum = (v) => !v || v === "NAN" ? 0 : parseFloat(v.toString().replace(/[$,]/g, '')) || 0;
const getDirectLink = (id) => `https://drive.google.com/thumbnail?sz=w1000&id=${id}`;

async function run() {
  try {
    console.log('🚀 Sincronizando con Google Cloud (Galindo System)...');
    
    const auth = await getAuth();
    const drive = google.drive({ version: 'v3', auth });
    const sheets = google.sheets({ version: 'v4', auth });

    // 1. OBTENER DATOS DEL EXCEL
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: process.env.SPREADSHEET_ID,
      range: "'Template Excel'!A1:Z200", 
    });

    const rows = res.data.values;
    if (!rows || rows.length === 0) {
      throw new Error('No se encontraron datos en el Spreadsheet.');
    }

    let lastTitulo = "", lastZona = "", lastCiudad = "";
    const propiedades = [];

    // 2. PROCESAR FILAS (Saltando encabezados)
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const propId = String(row[0] || "").trim().toUpperCase();
      
      if (!propId || propId === "ID" || propId === "NAN") continue;

      // Lógica de Autocompletado (FFill)
      const titulo = (row[1] || lastTitulo).trim(); lastTitulo = titulo;
      const zona = (row[6] || lastZona).trim(); lastZona = zona;
      const ciudad = (row[7] || lastCiudad).trim(); lastCiudad = ciudad;

      let fotos = ["/images/placeholder.jpg"];

      try {
        // Buscar carpeta por nombre (ID de propiedad)
        const fld = await drive.files.list({
          q: `'${process.env.DRIVE_FOLDER_ID}' in parents and name = '${propId}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`,
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
            console.log(`✅ ${propId}: ${fotos.length} fotos listas.`);
          }
        }
      } catch (e) { 
        console.log(`⚠️ ${propId}: Error al cargar fotos.`); 
      }

      // 3. MAPEO DE DATOS
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

    // 4. GUARDAR ARCHIVO JSON
    const outPath = path.join(process.cwd(), 'src/data/propiedades.json');
    
    // Crear carpeta si no existe (Vital para Vercel)
    if (!fs.existsSync(path.dirname(outPath))) {
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
    }

    fs.writeFileSync(outPath, JSON.stringify(propiedades, null, 2));
    
    console.log(`\n✨ Sincronización Finalizada: ${propiedades.length} propiedades.`);

  } catch (err) {
    console.error('❌ ERROR CRÍTICO:', err.message);
    process.exit(1);
  }
}

run();