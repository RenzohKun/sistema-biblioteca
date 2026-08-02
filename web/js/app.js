'use strict';
// ============================================================
// app.js — Inicialización principal y binding de eventos globales
// Equivale a: main.py (punto de entrada del sistema)
// ============================================================

/** Estado global de la aplicación */
const App = {
  session: null,
};

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // 1. Inicializar base de datos (siembra datos si es la primera vez)
  DB.init();

  // 1b. Inyectar imágenes Base64
  if (typeof IMAGES_B64 !== 'undefined') {
    const logoEl = document.getElementById('logo-img');
    if (logoEl && IMAGES_B64.logo) logoEl.src = IMAGES_B64.logo;
  }

  // 2. Comprobar sesión activa (recarga de página)
  const session = Auth.getSession();
  if (session) {
    App.session = session;
    iniciarAppShell(session);
  } else {
    UI.showScreen('screen-welcome');
  }

  // 3. Binding de eventos globales
  bindEventos();
});

// ============================================================
// BINDING DE EVENTOS DE PANTALLAS
// ============================================================
function bindEventos() {
  // ---- WELCOME ----
  document.getElementById('btn-go-login')?.addEventListener('click', () => {
    limpiarLogin();
    UI.showScreen('screen-login');
    document.getElementById('login-username')?.focus();
  });

  document.getElementById('btn-go-register')?.addEventListener('click', () => {
    limpiarRegister();
    UI.showScreen('screen-register');
  });

  // ---- LOGIN ----
  document.getElementById('btn-login')?.addEventListener('click', ejecutarLogin);
  document.getElementById('login-username')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('login-password')?.focus();
  });
  document.getElementById('login-password')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') ejecutarLogin();
  });

  document.getElementById('btn-to-register')?.addEventListener('click', () => {
    limpiarRegister();
    UI.showScreen('screen-register');
  });
  document.getElementById('btn-login-back')?.addEventListener('click', () => UI.showScreen('screen-welcome'));

  // ---- REGISTER ----
  document.getElementById('btn-register')?.addEventListener('click', ejecutarRegistro);
  document.getElementById('btn-to-login')?.addEventListener('click', () => {
    limpiarLogin();
    UI.showScreen('screen-login');
  });
  document.getElementById('btn-register-back')?.addEventListener('click', () => UI.showScreen('screen-welcome'));

  // ---- LOGOUT ----
  document.getElementById('btn-logout')?.addEventListener('click', cerrarSesion);

  // ---- MODAL ---- (cerrar con click fuera)
  document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-overlay')) UI.closeModal();
  });

  // ---- ESC para cerrar modal ----
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') UI.closeModal();
  });
}

// ============================================================
// FLUJO DE LOGIN
// ============================================================
function ejecutarLogin() {
  const username = document.getElementById('login-username')?.value ?? '';
  const password = document.getElementById('login-password')?.value ?? '';
  const errorEl  = document.getElementById('login-error');

  const result = Auth.login(username, password);

  if (!result.ok) {
    errorEl.textContent = result.msg;
    if (result.msg.includes('Usuario')) document.getElementById('login-username')?.select();
    else document.getElementById('login-password')?.focus();
    return;
  }

  errorEl.textContent = '';
  App.session = result.session;
  iniciarAppShell(result.session);
}

function limpiarLogin() {
  const u = document.getElementById('login-username');
  const p = document.getElementById('login-password');
  const e = document.getElementById('login-error');
  if (u) u.value = '';
  if (p) p.value = '';
  if (e) e.textContent = '';
}

// ============================================================
// FLUJO DE REGISTRO
// ============================================================
function ejecutarRegistro() {
  const get = id => document.getElementById(id)?.value ?? '';
  const errorEl   = document.getElementById('register-error');
  const successEl = document.getElementById('register-success');
  errorEl.textContent   = '';
  successEl.textContent = '';

  const result = Auth.register({
    username:     get('reg-username'),
    clave:        get('reg-clave'),
    nombre:       get('reg-nombre'),
    cedula:       get('reg-cedula'),
    correo:       get('reg-correo'),
    telefono:     get('reg-telefono'),
    claveMaestra: get('reg-maestra'),
  });

  if (!result.ok) { errorEl.textContent = result.msg; return; }

  successEl.textContent = '✅ ¡Cuenta creada! Ahora puedes iniciar sesión.';
  setTimeout(() => { limpiarLogin(); UI.showScreen('screen-login'); }, 2000);
}

function limpiarRegister() {
  ['reg-username','reg-clave','reg-nombre','reg-cedula','reg-correo','reg-telefono','reg-maestra'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const e = document.getElementById('register-error');
  const s = document.getElementById('register-success');
  if (e) e.textContent = '';
  if (s) s.textContent = '';
}

// ============================================================
// INICIO DEL APP SHELL (post-login)
// ============================================================
function iniciarAppShell(session) {
  UI.buildSidebar(session);
  UI.showScreen('app-shell');

  // Sección de inicio según el rol
  const seccionInicio = session.rol === 'usuario' ? 'mi-perfil' : 'dashboard';
  UI.navigate(seccionInicio);
}

// ============================================================
// CIERRE DE SESIÓN
// ============================================================
function cerrarSesion() {
  UI.openModal(
    'Cerrar sesión',
    '<p>¿Estás seguro de que deseas salir del sistema?</p>',
    () => {
      Auth.logout();
      App.session = null;
      limpiarLogin();
      UI.closeModal();
      UI.showScreen('screen-welcome');
    },
    'Sí, cerrar sesión',
    'var(--danger)'
  );
}
