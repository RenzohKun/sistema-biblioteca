'use strict';
// ============================================================
// libros.js — Gestión del catálogo físico y estantería 5×5
// Equivale a: admin.py (lógica de libros + búsqueda recursiva)
// ============================================================

const MAX_F = 5;   // Filas de la estantería
const MAX_C = 5;   // Columnas de la estantería

const Libros = {
  getAll() { return DB.getLibros(); },

  find(id) { return DB.findLibro(id); },

  /** Actualiza título, autor y categoría. La posición (f, c) no se puede cambiar aquí. */
  update(id, { titulo, autor, categoria }) {
    if (!titulo) return { ok: false, msg: '⚠ El título es obligatorio.' };
    const libro = DB.findLibro(id);
    if (!libro) return { ok: false, msg: `⚠ No existe el libro '${id}'.` };
    DB.updateLibro(id, { titulo, autor: autor || '', categoria: categoria || libro.categoria });
    return { ok: true };
  },

  /** Búsqueda recursiva por ID (equivale a buscar_recursivo de admin.py) */
  buscarRecursivo(lista, id, i = 0) {
    if (i >= lista.length) return null;
    if (lista[i].id === id) return lista[i];
    return this.buscarRecursivo(lista, id, i + 1);
  },

  /** Búsqueda por título o ID parcial (para barra de búsqueda) */
  buscar(texto) {
    if (!texto) return this.getAll();
    const t = texto.toLowerCase();
    return this.getAll().filter(lib =>
      lib.titulo.toLowerCase().includes(t) ||
      lib.id.toLowerCase().includes(t) ||
      (lib.autor || '').toLowerCase().includes(t)
    );
  },

  /** Reconstruye la matriz 5×5 desde la lista de libros */
  getEstanteria() {
    const grid = Array.from({ length: MAX_F }, () => Array(MAX_C).fill('Libre'));
    DB.getLibros().forEach(lib => {
      const f = parseInt(lib.f), c = parseInt(lib.c);
      if (f >= 0 && f < MAX_F && c >= 0 && c < MAX_C) {
        grid[f][c] = lib.id;
      }
    });
    return grid;
  },

  contarEspaciosLibres() {
    return this.getEstanteria().flat().filter(v => v === 'Libre').length;
  },

  getPrimerEspacioLibre() {
    const est = this.getEstanteria();
    for (let f = 0; f < MAX_F; f++)
      for (let c = 0; c < MAX_C; c++)
        if (est[f][c] === 'Libre') return { f, c };
    return null;
  },

  /**
   * Agrega un libro al catálogo y lo ubica en la estantería.
   * Retorna { ok, libro } o { ok: false, msg }.
   */
  add({ titulo, autor, categoria, f, c }) {
    if (!titulo) return { ok: false, msg: '⚠ El título es obligatorio.' };

    const fNum = parseInt(f), cNum = parseInt(c);
    if (isNaN(fNum) || isNaN(cNum) || fNum < 0 || fNum >= MAX_F || cNum < 0 || cNum >= MAX_C) {
      return { ok: false, msg: `⚠ Posición inválida. Fila: 0–${MAX_F-1}, Columna: 0–${MAX_C-1}.` };
    }

    const estanteria = this.getEstanteria();
    if (estanteria[fNum][cNum] !== 'Libre') {
      return { ok: false, msg: `⚠ La posición Fila ${fNum}, Col ${cNum} ya está ocupada.` };
    }

    const id = 'LIB' + String(Date.now()).slice(-6);
    const libro = { id, titulo, autor: autor || '', categoria: categoria || '', f: fNum, c: cNum };
    DB.addLibro(libro);
    return { ok: true, libro };
  },

  /**
   * Elimina un libro del catálogo.
   * Retorna { ok } o { ok: false, msg }.
   */
  delete(id) {
    const libro = DB.findLibro(id);
    if (!libro) return { ok: false, msg: `⚠ No existe ningún libro con ID '${id}'.` };
    DB.deleteLibro(id);
    return { ok: true };
  }
};

const CATEGORIAS = [
  'Programación', 'Bases de Datos', 'Algoritmos',
  'Redes', 'Ingeniería de Software', 'Matemáticas',
  'Sistemas', 'Otra'
];
