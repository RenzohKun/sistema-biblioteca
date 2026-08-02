'use strict';
// ============================================================
// auth.js — Autenticación y gestión de sesión
// Equivale a: login.py + registro.py
// ============================================================

const SESSION_KEY = 'biblio_session';

const Auth = {
  /**
   * Intenta iniciar sesión. Retorna { ok, session } o { ok: false, msg }.
   */
  login(username, password) {
    const trim = s => (s || '').trim();
    const user = trim(username);
    const pass = trim(password);

    if (!user || !pass) return { ok: false, msg: '⚠ Completa todos los campos antes de continuar.' };

    const usuarios = DB.getUsuarios();
    const datos = usuarios[user];

    if (!datos) return { ok: false, msg: '✗ Usuario no encontrado. Verifica tu nombre de usuario.' };
    if (datos.clave !== pass) return { ok: false, msg: '✗ Contraseña incorrecta. Inténtalo de nuevo.' };

    const session = {
      login: user,
      nombre: datos.nombre || user,
      rol: datos.rol || 'usuario'
    };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    return { ok: true, session };
  },

  logout() {
    sessionStorage.removeItem(SESSION_KEY);
  },

  getSession() {
    try {
      const s = sessionStorage.getItem(SESSION_KEY);
      return s ? JSON.parse(s) : null;
    } catch {
      return null;
    }
  },

  isLoggedIn() {
    return !!this.getSession();
  },

  /**
   * Registra una nueva cuenta de usuario.
   * Si se provee la clave maestra, el rol puede ser 'bibliotecario'.
   */
  register({ username, clave, nombre, cedula, correo, telefono, claveMaestra }) {
    const trim = s => (s || '').trim();
    const user = trim(username);
    const pw   = trim(clave);
    const nom  = trim(nombre);

    if (!user || !pw || !nom) return { ok: false, msg: '⚠ Usuario, contraseña y nombre son obligatorios.' };
    if (user.length < 3)      return { ok: false, msg: '⚠ El nombre de usuario debe tener al menos 3 caracteres.' };
    if (pw.length < 4)        return { ok: false, msg: '⚠ La contraseña debe tener al menos 4 caracteres.' };
    if (!/^[a-zA-Z0-9_.\-]+$/.test(user)) return { ok: false, msg: '⚠ El usuario solo puede tener letras, números, puntos o guiones.' };

    const usuarios = DB.getUsuarios();
    if (usuarios[user]) return { ok: false, msg: '⚠ Ese nombre de usuario ya está en uso. Elige otro.' };

    // Determinar rol según clave maestra (ofuscada para no dejarla en texto plano)
    let rol = 'usuario';
    // 'ULEAM_ADMIN_2026' en Base64
    const CLAVE_MAESTRA = atob('VUxFQU1fQURNSU5fMjAyNg==');
    if (trim(claveMaestra) === CLAVE_MAESTRA) rol = 'bibliotecario';

    const nuevoUsuario = {
      clave: pw, nombre: nom,
      cedula: trim(cedula) || '',
      correo: trim(correo) || '',
      telefono: trim(telefono) || '',
      rol,
      strikes: 0, deuda: 0.0, suspendido_hasta: null
    };
    DB.saveUsuario(user, nuevoUsuario);
    return { ok: true };
  }
};
