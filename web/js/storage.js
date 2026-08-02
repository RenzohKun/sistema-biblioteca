'use strict';
// ============================================================
// storage.js — Capa de persistencia en localStorage
// Equivale a: cargar_desde_archivo / guardar_en_archivo de admin.py
// ============================================================

const KEYS = {
  USUARIOS:   'biblio_usuarios',
  LIBROS:     'biblio_libros',
  PRESTAMOS:  'biblio_prestamos',
  RESERVAS:   'biblio_reservas',
  LIBRERIA:   'biblio_libreria_digital',
  COMENTARIOS:'biblio_comentarios',
  OK:         'biblio_initialized'
};

// ---- DATOS INICIALES (replicados de los JSON del proyecto) ----
const INIT_DATA = {
  usuarios: {
    "admin": {
      "clave": "1234", "rol": "admin", "cedula": "0000000000",
      "nombre": "Administrador General", "correo": "admin@uleam.edu.ec",
      "telefono": "0000000000", "strikes": 0, "deuda": 0.0, "suspendido_hasta": null
    },
    "cetace1234": {
      "clave": "12345", "rol": "bibliotecario", "cedula": "1315641116",
      "nombre": "Enoc Elias Pacheco Olivo", "correo": "e1315641116@live.uleam.edu.ec",
      "telefono": "0967241166", "strikes": 0, "deuda": 0.0, "suspendido_hasta": null
    },
    "admin2": {
      "clave": "12345", "rol": "admin", "cedula": "132456785",
      "nombre": "Administrador del Sistema", "correo": "test@live.uleam.edu.ec",
      "telefono": "23223232323", "strikes": 0, "deuda": 0.0, "suspendido_hasta": null
    },
    "maria": {
      "clave": "12345", "rol": "usuario", "cedula": "1345678994",
      "nombre": "Maria Belen", "correo": "maria.velez@uleam.edu.ec",
      "telefono": "0987654321", "strikes": 0, "deuda": 0.0, "suspendido_hasta": null
    }
  },
  libros: [
    { "id": "LIB001", "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "categoria": "Literatura", "f": 0, "c": 0 },
    { "id": "LIB002", "titulo": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "categoria": "Literatura", "f": 0, "c": 1 },
    { "id": "LIB003", "titulo": "Física Universitaria Vol. 1", "autor": "Sears y Zemansky", "categoria": "Física", "f": 0, "c": 2 },
    { "id": "LIB004", "titulo": "El laberinto de la soledad", "autor": "Octavio Paz", "categoria": "Literatura", "f": 0, "c": 3 },
    { "id": "LIB005", "titulo": "Calculo de una variable", "autor": "James Stewart", "categoria": "Matemáticas", "f": 0, "c": 4 },
    { "id": "LIB006", "titulo": "Breve historia del tiempo", "autor": "Stephen Hawking", "categoria": "Física", "f": 1, "c": 0 },
    { "id": "LIB007", "titulo": "Sapiens: De animales a dioses", "autor": "Yuval Noah Harari", "categoria": "Historia", "f": 1, "c": 1 },
    { "id": "LIB008", "titulo": "El hombre en busca de sentido", "autor": "Viktor Frankl", "categoria": "Psicología", "f": 1, "c": 2 }
  ],
  prestamos:  [],
  reservas:   [],
  libreria: [
    { "titulo": "Introducción a la Programación con Python", "autor": "John Zelle", "categoria": "Programación", "url": "https://docs.python.org/3/tutorial/", "descripcion": "Tutorial oficial de Python, ideal para principiantes en programación." },
    { "titulo": "Fundamentos de Bases de Datos", "autor": "Abraham Silberschatz", "categoria": "Bases de Datos", "url": "https://db-book.com/", "descripcion": "Conceptos fundamentales de diseño y gestión de bases de datos relacionales." },
    { "titulo": "Estructura de Datos y Algoritmos", "autor": "Thomas H. Cormen", "categoria": "Algoritmos", "url": "https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/", "descripcion": "Referencia clásica sobre algoritmos, complejidad y estructuras de datos." },
    { "titulo": "Redes de Computadoras", "autor": "Andrew S. Tanenbaum", "categoria": "Redes", "url": "https://www.pearson.com/en-us/subject-catalog/p/computer-networks/P200000003185", "descripcion": "Texto fundamental sobre arquitectura y protocolos de redes." },
    { "titulo": "Ingeniería de Software", "autor": "Ian Sommerville", "categoria": "Ingeniería de Software", "url": "https://software-engineering-book.com/", "descripcion": "Principios y prácticas modernas de ingeniería de software." },
    { "titulo": "Matemáticas Discretas y sus Aplicaciones", "autor": "Kenneth H. Rosen", "categoria": "Matemáticas", "url": "https://www.mheducation.com/highered/product/discrete-mathematics-applications-rosen/M9781259676512.html", "descripcion": "Lógica, conjuntos, grafos y combinatoria aplicados a la computación." }
  ],
  comentarios: []
};

// ============================================================
// DB — API de acceso a datos
// ============================================================
const DB = {
  init() {
    if (localStorage.getItem(KEYS.OK)) return;
    localStorage.setItem(KEYS.USUARIOS,    JSON.stringify(INIT_DATA.usuarios));
    localStorage.setItem(KEYS.LIBROS,      JSON.stringify(INIT_DATA.libros));
    localStorage.setItem(KEYS.PRESTAMOS,   JSON.stringify(INIT_DATA.prestamos));
    localStorage.setItem(KEYS.RESERVAS,    JSON.stringify(INIT_DATA.reservas));
    localStorage.setItem(KEYS.LIBRERIA,    JSON.stringify(INIT_DATA.libreria));
    localStorage.setItem(KEYS.COMENTARIOS, JSON.stringify(INIT_DATA.comentarios));
    localStorage.setItem(KEYS.OK, '1');
    console.log('✅ DB inicializada con datos de ejemplo.');
  },

  /** Reinicia todos los datos al estado inicial */
  reset() {
    Object.values(KEYS).forEach(k => localStorage.removeItem(k));
    this.init();
  },

  // ---- USUARIOS ----
  getUsuarios()              { return JSON.parse(localStorage.getItem(KEYS.USUARIOS)) || {}; },
  setUsuarios(u)             { localStorage.setItem(KEYS.USUARIOS, JSON.stringify(u)); },
  getUsuario(login)          { return this.getUsuarios()[login] || null; },
  saveUsuario(login, datos)  { const u = this.getUsuarios(); u[login] = datos; this.setUsuarios(u); },
  deleteUsuario(login)       { const u = this.getUsuarios(); delete u[login]; this.setUsuarios(u); },

  // ---- LIBROS ----
  getLibros()       { return JSON.parse(localStorage.getItem(KEYS.LIBROS)) || []; },
  setLibros(l)      { localStorage.setItem(KEYS.LIBROS, JSON.stringify(l)); },
  addLibro(libro)   { const l = this.getLibros(); l.push(libro); this.setLibros(l); },
  deleteLibro(id)   { this.setLibros(this.getLibros().filter(lib => lib.id !== id)); },
  findLibro(id)     { const uid = (id || '').toUpperCase(); return this.getLibros().find(lib => lib.id.toUpperCase() === uid) || null; },
  updateLibro(id, cambios) {
    const libros = this.getLibros();
    const idx = libros.findIndex(l => l.id === id);
    if (idx >= 0) { libros[idx] = { ...libros[idx], ...cambios }; this.setLibros(libros); }
  },

  // ---- PRÉSTAMOS ----
  getPrestamos()    { return JSON.parse(localStorage.getItem(KEYS.PRESTAMOS)) || []; },
  setPrestamos(p)   { localStorage.setItem(KEYS.PRESTAMOS, JSON.stringify(p)); },

  // ---- RESERVAS ----
  getReservas()     { return JSON.parse(localStorage.getItem(KEYS.RESERVAS)) || []; },
  setReservas(r)    { localStorage.setItem(KEYS.RESERVAS, JSON.stringify(r)); },

  // ---- LIBRERÍA DIGITAL ----
  getLibreria()     { return JSON.parse(localStorage.getItem(KEYS.LIBRERIA)) || []; },
  setLibreria(l)    { localStorage.setItem(KEYS.LIBRERIA, JSON.stringify(l)); },

  // ---- COMENTARIOS / SUGERENCIAS ----
  getComentarios()  { return JSON.parse(localStorage.getItem(KEYS.COMENTARIOS)) || []; },
  addComentario(c)  {
    const arr = this.getComentarios();
    arr.push(c);
    localStorage.setItem(KEYS.COMENTARIOS, JSON.stringify(arr));
  }
};
