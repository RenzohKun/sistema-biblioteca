'use strict';
// ============================================================
// usuarios.js — Gestión de usuarios (solo admin)
// Equivale a: gestión de usuarios en admin.py
// ============================================================

const ROLES_VALIDOS = ['usuario', 'bibliotecario', 'admin'];

const Usuarios = {
  /** Lista completa de usuarios como array [{login, ...datos}] */
  getAll() {
    return Object.entries(DB.getUsuarios())
      .map(([login, datos]) => ({ login, ...datos }));
  },

  get(login) { return DB.getUsuario(login); },

  /** Cambia el rol de un usuario. No se puede cambiar el propio rol. */
  cambiarRol(login, nuevoRol, loginAdmin) {
    if (login === loginAdmin)    return { ok: false, msg: '⚠ No puedes cambiar tu propio rol.' };
    if (!ROLES_VALIDOS.includes(nuevoRol)) return { ok: false, msg: '⚠ Rol inválido.' };

    const u = DB.getUsuario(login);
    if (!u) return { ok: false, msg: `⚠ El usuario '${login}' no existe.` };

    u.rol = nuevoRol;
    DB.saveUsuario(login, u);
    return { ok: true };
  },

  /** Elimina un usuario. No se puede eliminar la propia cuenta. */
  eliminar(login, loginAdmin) {
    if (login === loginAdmin) return { ok: false, msg: '⚠ No puedes eliminar tu propia cuenta.' };
    if (!DB.getUsuario(login)) return { ok: false, msg: `⚠ El usuario '${login}' no existe.` };
    DB.deleteUsuario(login);
    return { ok: true };
  },

  /** Actualiza datos del perfil propio (nombre, correo, teléfono, contraseña) */
  actualizarPerfil(login, { nombre, correo, telefono, claveNueva, claveActual }) {
    const u = DB.getUsuario(login);
    if (!u) return { ok: false, msg: '⚠ Usuario no encontrado.' };

    if (claveNueva) {
      if (u.clave !== claveActual) return { ok: false, msg: '✗ La contraseña actual es incorrecta.' };
      if (claveNueva.length < 4)  return { ok: false, msg: '✗ La nueva contraseña debe tener al menos 4 caracteres.' };
      u.clave = claveNueva;
    }
    if (nombre)   u.nombre   = nombre;
    if (correo)   u.correo   = correo;
    if (telefono) u.telefono = telefono;

    DB.saveUsuario(login, u);
    return { ok: true };
  },

  /** Limpiar deuda de un usuario (admin) */
  limpiarDeuda(login) {
    const u = DB.getUsuario(login);
    if (!u) return { ok: false };
    u.deuda = 0;
    u.suspendido_hasta = null;
    DB.saveUsuario(login, u);
    return { ok: true };
  },

  /** Quitar un strike a un usuario (admin) */
  quitarStrike(login) {
    const u = DB.getUsuario(login);
    if (!u) return { ok: false };
    if (u.strikes > 0) u.strikes = u.strikes - 1;
    if (u.strikes < 3) u.suspendido_hasta = null;
    DB.saveUsuario(login, u);
    return { ok: true };
  }
};
