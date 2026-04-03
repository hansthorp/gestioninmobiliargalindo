// src/data/propiedades.ts
export const propiedades = [
    {
      id: "prop-001",
      slug: "casa-lujo-coapexpan",
      titulo: "Casa de Lujo en Coapexpan",
      descripcion: "Residencia con acabados premium y vista al bosque.",
      operacion: "venta",
      tipo: "casa",
      precio: 3500000,
      moneda: "MXN",
      zona: "Coapexpan",
      ciudad: "Xalapa",
      recamaras: 3,
      banos: 2,
      estacionamientos: 2,
      m2Construccion: 250,
      imagenes: ["https://images.unsplash.com/photo-1568605114967-8130f3a36994"],
      contacto: {
        whatsapp: "5212281234567",
        mensajeBase: "Hola, me interesa la casa en Coapexpan"
      },
      seo: { title: "Casa Coapexpan", description: "Venta de casa" }
    },
    {
      id: "prop-002",
      slug: "departamento-centro",
      titulo: "Penthouse Moderno Centro",
      descripcion: "Ubicación inmejorable en el corazón de la ciudad.",
      operacion: "renta",
      tipo: "departamento",
      precio: 15000,
      moneda: "MXN",
      zona: "Centro",
      ciudad: "Xalapa",
      recamaras: 2,
      banos: 2,
      estacionamientos: 1,
      m2Construccion: 110,
      imagenes: ["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688"],
      contacto: {
        whatsapp: "5212281234567",
        mensajeBase: "Hola, me interesa el depa en el Centro"
      },
      seo: { title: "Depa Centro", description: "Renta de depa" }
    }
  ];