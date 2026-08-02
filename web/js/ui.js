'use strict';
// ============================================================
// ui.js — SPA Router + Renderizado de todas las vistas
// Equivale a: admin.py (UI), menu_usuario.py, menu_bibliotecario.py
// ============================================================

// ---- CONSTANTES DE NAVEGACIÓN ----
const SIDEBAR_ITEMS = {
  admin: [
    { id: 'dashboard',       icon: '🏠', label: 'Inicio / Dashboard' },
    { id: 'libros',          icon: '📖', label: 'Gestión de Libros' },
    { id: 'prestamos',       icon: '🔄', label: 'Préstamos y Devoluciones' },
    { id: 'reservas',        icon: '🔔', label: 'Reservas' },
    { id: 'estanteria',      icon: '🗄', label: 'Ver Estantería' },
    { id: 'libreria-digital',icon: '🌐', label: 'Librería Digital' },
    { id: 'usuarios',        icon: '👥', label: 'Gestión de Usuarios' },
    { id: 'sugerencias-admin', icon: '💬', label: 'Buzón de Sugerencias' },
  ],
  bibliotecario: [
    { id: 'dashboard',       icon: '🏠', label: 'Inicio / Dashboard' },
    { id: 'libros',          icon: '📖', label: 'Gestión de Libros' },
    { id: 'prestamos',       icon: '🔄', label: 'Préstamos y Devoluciones' },
    { id: 'reservas',        icon: '🔔', label: 'Reservas' },
    { id: 'estanteria',      icon: '🗄', label: 'Ver Estantería' },
    { id: 'libreria-digital',icon: '🌐', label: 'Librería Digital' },
    { id: 'sugerencias-admin', icon: '💬', label: 'Buzón de Sugerencias' },
  ],
  usuario: [
    { id: 'mi-perfil',       icon: '🏠', label: 'Inicio / Mi Perfil' },
    { id: 'mis-prestamos',   icon: '📚', label: 'Préstamo de Libros' },
    { id: 'libreria-digital',icon: '🌐', label: 'Librería Digital' },
    { id: 'catalogo',        icon: '🔍', label: 'Catálogo / Estantería' },
    { id: 'sugerencias',     icon: '💬', label: 'Buzón de Sugerencias' },
    { id: 'mi-cuenta',       icon: '⚙️', label: 'Mi Cuenta' },
  ]
};

const CHIP_COLORES = {
  'Programación':           { bg: '#DBEAFE', text: '#1E40AF' },
  'Bases de Datos':         { bg: '#D1FAE5', text: '#065F46' },
  'Algoritmos':             { bg: '#FEF3C7', text: '#92400E' },
  'Redes':                  { bg: '#F3E8FF', text: '#6B21A8' },
  'Ingeniería de Software': { bg: '#FFE4E6', text: '#9F1239' },
  'Matemáticas':            { bg: '#E0F2FE', text: '#0C4A6E' },
  'Sistemas':               { bg: '#FEE2E2', text: '#7F1D1D' },
  'Otra':                   { bg: '#F3F4F6', text: '#374151' },
};

// Portadas en Base64 (cargadas desde images.js — compatible con file:// protocol)
const PORTADA_CATEGORIA = {
  'Programación':           'portada_programacion',
  'Bases de Datos':         'portada_basesdatos',
  'Algoritmos':             'portada_algoritmos',
  'Redes':                  'portada_redes',
  'Ingeniería de Software': 'portada_software',
  'Matemáticas':            'portada_matematicas',
};

/** Devuelve el data URI de una portada según categoría */
function _getPortada(categoria) {
  const key = PORTADA_CATEGORIA[categoria] || 'portada_default';
  return (typeof IMAGES_B64 !== 'undefined' && IMAGES_B64[key]) || '';
}

// ============================================================
// UI — objeto principal de la interfaz
// ============================================================
const UI = {
  currentSection: null,

  // ==========================================================
  // NAVEGACIÓN DE PANTALLAS (Welcome / Login / Register / App)
  // ==========================================================
  showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
  },

  // ==========================================================
  // SIDEBAR — construye la navegación lateral según el rol
  // ==========================================================
  buildSidebar(session) {
    const items = SIDEBAR_ITEMS[session.rol] || SIDEBAR_ITEMS.usuario;
    const rolLabel = { admin: 'Administrador', bibliotecario: 'Bibliotecario', usuario: 'Estudiante' }[session.rol] || 'Estudiante';

    document.getElementById('sidebar-username').textContent = session.nombre;
    document.getElementById('sidebar-role').textContent = `(${rolLabel})`;

    const nav = document.getElementById('sidebar-nav');
    nav.innerHTML = items.map(item => `
      <button class="nav-item" data-section="${item.id}" onclick="UI.navigate('${item.id}')">
        <span class="nav-icon">${item.icon}</span>
        <span>${item.label}</span>
      </button>
    `).join('');
  },

  /** Activa visualmente el botón del menú lateral */
  _activarNavItem(sectionId) {
    document.querySelectorAll('.nav-item').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.section === sectionId);
    });
  },

  /** Navega a una sección dentro del app shell */
  navigate(section) {
    const session = Auth.getSession();
    if (!session) { this.showScreen('screen-welcome'); return; }

    this.currentSection = section;
    this._activarNavItem(section);

    const content = document.getElementById('content');
    content.innerHTML = '<div class="loading">⏳ Cargando...</div>';

    // Renderizar la vista correcta
    const renderMap = {
      // Staff (admin + bibliotecario)
      'dashboard':        () => this.renderDashboard(session),
      'libros':           () => this.renderGestionLibros(session),
      'prestamos':        () => this.renderPrestamos(session),
      'reservas':         () => this.renderReservas(session),
      'estanteria':       () => this.renderEstanteria(session),
      'libreria-digital': () => session.rol === 'usuario'
                                  ? this.renderLibreriaDigitalUsuario(session)
                                  : this.renderLibreriaDigitalAdmin(session),
      'usuarios':         () => this.renderGestionUsuarios(session),
      'sugerencias-admin':() => this.renderSugerenciasAdmin(session),
      // Usuario
      'mi-perfil':        () => this.renderMiPerfil(session),
      'mis-prestamos':    () => this.renderMisPrestamos(session),
      'catalogo':         () => this.renderCatalogo(session),
      'sugerencias':      () => this.renderSugerencias(session),
      'mi-cuenta':        () => this.renderMiCuenta(session),
    };

    const fn = renderMap[section];
    if (fn) {
      setTimeout(() => { content.innerHTML = ''; fn(); }, 50);
    } else {
      content.innerHTML = '<div class="empty-state"><span>🚧</span><p>Sección no disponible.</p></div>';
    }
  },

  // ==========================================================
  // HELPERS DE RENDERIZADO
  // ==========================================================
  _encabezado(titulo, subtitulo) {
    return `
      <div class="section-header">
        <h2 class="section-title">${titulo}</h2>
        <div class="section-divider"></div>
        <p class="section-subtitle">${subtitulo}</p>
      </div>`;
  },

  _tarjeta(icono, etiqueta, valor, colorValor = 'var(--marino)', clickable = false, onClick = '') {
    return `
      <div class="dashboard-card ${clickable ? 'clickable' : ''}" ${onClick ? `onclick="${onClick}"` : ''}>
        <span class="card-label">${icono}  ${etiqueta}</span>
        <span class="card-value" style="color:${colorValor}">${valor}</span>
      </div>`;
  },

  _badge(estado) {
    const map = {
      activo:    { bg: '#D1FAE5', text: '#065F46', label: 'ACTIVO' },
      vencido:   { bg: '#FEE2E2', text: '#7F1D1D', label: 'VENCIDO' },
      devuelto:  { bg: '#F3F4F6', text: '#6B7280', label: 'DEVUELTO' },
      pendiente: { bg: '#FEF3C7', text: '#92400E', label: 'PENDIENTE' },
      aprobada:  { bg: '#D1FAE5', text: '#065F46', label: 'APROBADA' },
      rechazada: { bg: '#FEE2E2', text: '#7F1D1D', label: 'RECHAZADA' },
    };
    const b = map[estado] || { bg: '#E5E7EB', text: '#374151', label: estado.toUpperCase() };
    return `<span class="badge" style="background:${b.bg};color:${b.text}">${b.label}</span>`;
  },

  _chip(categoria) {
    const col = CHIP_COLORES[categoria] || { bg: '#F3F4F6', text: '#374151' };
    return `<span class="chip" style="background:${col.bg};color:${col.text}">${categoria}</span>`;
  },

  _tituloPorId(idLibro) {
    const libro = DB.findLibro(idLibro);
    return libro ? libro.titulo : idLibro;
  },

  /** Genera un input con autocompletado nativo (datalist) de IDs de libros */
  _inputLibroConAutocomplete(id, placeholder = 'Ej: LIB001') {
    const opts = Libros.getAll()
      .map(l => `<option value="${l.id}">${l.titulo}${l.autor ? ' — ' + l.autor : ''}</option>`)
      .join('');
    return `<input type="text" id="${id}" class="form-input" placeholder="${placeholder}"
               list="dl-${id}" autocomplete="off"><datalist id="dl-${id}">${opts}</datalist>`;
  },

  // ==========================================================
  // TOAST NOTIFICATIONS
  // ==========================================================
  toast(msg, tipo = 'success') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = `toast toast-${tipo} show`;
    clearTimeout(UI._toastTimer);
    UI._toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
  },

  // ==========================================================
  // MODAL GENÉRICO
  // ==========================================================
  openModal(titulo, bodyHtml, onConfirm, labelConfirmar = 'Confirmar', colorConfirmar = 'var(--verde)') {
    document.getElementById('modal-title').textContent = titulo;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-overlay').classList.remove('hidden');

    const btnOk = document.getElementById('modal-confirm');
    const btnCancelar = document.getElementById('modal-cancel');

    btnOk.style.background = colorConfirmar;
    btnOk.textContent = labelConfirmar;

    // Limpiar listeners previos clonando el nodo
    const newOk  = btnOk.cloneNode(true);
    const newCan = btnCancelar.cloneNode(true);
    btnOk.parentNode.replaceChild(newOk, btnOk);
    btnCancelar.parentNode.replaceChild(newCan, btnCancelar);

    newOk.style.background = colorConfirmar;
    newOk.textContent = labelConfirmar;
    newOk.addEventListener('click', onConfirm);
    newCan.addEventListener('click', () => this.closeModal());
  },

  closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
    document.getElementById('modal-body').innerHTML = '';
  },

  // ==========================================================
  // VISTA: DASHBOARD (Admin + Bibliotecario)
  // ==========================================================
  renderDashboard(session) {
    const content = document.getElementById('content');
    const libros = Libros.getAll();
    const espaciosLibres = Libros.contarEspaciosLibres();
    const totalEspacios  = MAX_F * MAX_C;
    const vencidos   = Prestamos.contarVencidos();
    const pendientes = Prestamos.contarPendientes();

    const colorEspacios = espaciosLibres === 0 ? 'var(--rojo)' : 'var(--acento)';
    const colorVenc = vencidos > 0 ? 'var(--rojo)' : 'var(--texto-muted)';
    const colorPend = pendientes > 0 ? 'var(--acento)' : 'var(--texto-muted)';

    const eventos = Prestamos.actividadReciente(6);

    const actividadHtml = eventos.length === 0
      ? '<p class="text-muted">Todavía no hay movimientos registrados.</p>'
      : eventos.map(ev => {
          const titulo = this._tituloPorId(ev.id_libro);
          const [icono, verbo, color] = ev.tipo === 'prestamo'
            ? ['📕', 'solicitó préstamo de', 'var(--azul)']
            : ['📗', 'devolvió', 'var(--verde)'];
          return `
            <div class="activity-row">
              <span>${icono}</span>
              <span class="activity-text" style="color:${color}">${ev.usuario} ${verbo} "<em>${titulo}</em>"</span>
              <span class="activity-date">${ev.fecha}</span>
            </div>`;
        }).join('');

    content.innerHTML = `
      ${this._encabezado('Panel de control', 'Estado actual del catálogo de la biblioteca')}

      <!-- Buscador global -->
      <div class="card mb-4">
        <div class="search-bar">
          <span>🔍</span>
          <input type="text" id="buscador-global" placeholder="Buscar libro por ID o título..." class="search-input">
          <button class="btn btn-primary" onclick="UI._ejecutarBusquedaGlobal()">Buscar</button>
        </div>
      </div>

      <!-- Tarjetas de resumen -->
      <div class="cards-grid mb-4">
        ${this._tarjeta('📚', 'TOTAL LIBROS', libros.length, 'var(--marino)')}
        ${this._tarjeta('🪑', 'ESPACIOS LIBRES', `${espaciosLibres}/${totalEspacios}`, colorEspacios)}
        ${this._tarjeta('⏰', 'PRÉSTAMOS VENCIDOS', vencidos, colorVenc, vencidos > 0, "UI.navigate('prestamos')")}
        ${this._tarjeta('🔔', 'RESERVAS PENDIENTES', pendientes, colorPend, pendientes > 0, "UI.navigate('reservas')")}
      </div>

      <!-- Acciones rápidas -->
      <h3 class="section-label mb-3">Acciones rápidas</h3>
      <div class="actions-row mb-5">
        <button class="btn btn-success btn-lg" onclick="UI._modalRegistrarPrestamo()">📕 Registrar préstamo</button>
        <button class="btn btn-primary btn-lg" onclick="UI._modalRegistrarDevolucion()">📗 Registrar devolución</button>
        <button class="btn btn-secondary" onclick="UI.navigate('libros')">➕ Gestionar catálogo</button>
        <button class="btn btn-accent"    onclick="UI.navigate('estanteria')">🗄 Ver estantería</button>
      </div>

      <!-- Actividad reciente -->
      <h3 class="section-label mb-3">Actividad reciente</h3>
      <div class="card">
        <div class="activity-list">${actividadHtml}</div>
      </div>
    `;

    // Búsqueda con Enter
    const inp = document.getElementById('buscador-global');
    if (inp) inp.addEventListener('keydown', e => { if (e.key === 'Enter') UI._ejecutarBusquedaGlobal(); });
  },

  _ejecutarBusquedaGlobal() {
    const texto = (document.getElementById('buscador-global')?.value || '').trim();
    if (!texto) return;
    const resultados = Libros.buscar(texto);
    if (!resultados.length) {
      UI.toast(`No se encontró ningún libro con "${texto}"`, 'error');
      return;
    }
    const bodyHtml = resultados.map(r => {
      const prest = Prestamos.prestamoActivo(r.id);
      const estadoTxt = prest
        ? `🔴 Prestado a <strong>${prest.usuario}</strong> — vence ${prest.fecha_limite}`
        : '🟢 Disponible';
      return `
        <div class="detail-grid mb-3" style="border:1px solid var(--borde);border-radius:8px;padding:12px">
          <div class="detail-row"><strong>ID:</strong><span><code>${r.id}</code></span></div>
          <div class="detail-row"><strong>Título:</strong><span>${r.titulo}</span></div>
          <div class="detail-row"><strong>Autor:</strong><span>${r.autor || '—'}</span></div>
          <div class="detail-row"><strong>Categoría:</strong><span>${this._chip(r.categoria)}</span></div>
          <div class="detail-row"><strong>Ubicación:</strong><span>Fila ${r.f}, Col ${r.c}</span></div>
          <div class="detail-row"><strong>Estado:</strong><span>${estadoTxt}</span></div>
        </div>`;
    }).join('');
    this.openModal(
      `🔍 ${resultados.length} resultado(s) para "${texto}"`,
      bodyHtml,
      () => this.closeModal(), 'Cerrar', 'var(--marino)'
    );
  },

  // ==========================================================
  // VISTA: GESTIÓN DE LIBROS (Admin + Bibliotecario)
  // ==========================================================
  renderGestionLibros(session, filtro = '') {
    const content = document.getElementById('content');
    const listaFiltrada = filtro ? Libros.buscar(filtro) : Libros.getAll();
    const espacioSugerido = Libros.getPrimerEspacioLibre();

    const filas = listaFiltrada.map(lib => {
      const prest = Prestamos.prestamoActivo(lib.id);
      return `
        <tr>
          <td><code>${lib.id}</code></td>
          <td>${lib.titulo}</td>
          <td>${lib.autor || '—'}</td>
          <td>${this._chip(lib.categoria)}</td>
          <td class="text-center">F${lib.f} · C${lib.c}</td>
          <td class="text-center">${prest ? this._badge(prest.estado) : '<span class="badge" style="background:#D1FAE5;color:#065F46">DISPONIBLE</span>'}</td>
          <td class="text-center">
            <button class="btn-icon btn-warning mr-1" title="Editar" onclick="UI._modalEditarLibro('${lib.id}')">✏️</button>
            <button class="btn-icon btn-danger" title="Eliminar" onclick="UI._confirmarEliminarLibro('${lib.id}', '${lib.titulo.replace(/'/g,"\\'")}')" >🗑</button>
          </td>
        </tr>`;
    }).join('') || '<tr><td colspan="7" class="text-center text-muted py-4">No hay libros que coincidan con la búsqueda.</td></tr>';

    content.innerHTML = `
      ${this._encabezado('Gestión de Libros', 'Registra, busca y elimina libros del catálogo')}

      <!-- Formulario de registro -->
      <div class="card mb-4">
        <h3 class="card-title">Registrar nuevo libro</h3>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Título *</label>
            <input type="text" id="lib-titulo" class="form-input" placeholder="Título del libro">
          </div>
          <div class="form-group">
            <label class="form-label">Autor</label>
            <input type="text" id="lib-autor" class="form-input" placeholder="Nombre del autor">
          </div>
          <div class="form-group">
            <label class="form-label">Categoría</label>
            <select id="lib-categoria" class="form-input">
              ${CATEGORIAS.map(c => `<option>${c}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Fila (0–${MAX_F-1}) *</label>
            <input type="number" id="lib-f" class="form-input" min="0" max="${MAX_F-1}" value="${espacioSugerido ? espacioSugerido.f : 0}">
          </div>
          <div class="form-group">
            <label class="form-label">Columna (0–${MAX_C-1}) *</label>
            <input type="number" id="lib-c" class="form-input" min="0" max="${MAX_C-1}" value="${espacioSugerido ? espacioSugerido.c : 0}">
          </div>
        </div>
        <p id="lib-error" class="error-text"></p>
        <button class="btn btn-success mt-2" onclick="UI._registrarLibro()">✅ Registrar libro</button>
        ${espacioSugerido
          ? `<span class="hint ml-3">💡 Primer espacio libre sugerido: F${espacioSugerido.f}, C${espacioSugerido.c}</span>`
          : '<span class="hint ml-3 text-danger">⚠ Estantería llena (25/25)</span>'}
      </div>

      <!-- Buscador + tabla -->
      <div class="card">
        <div class="table-header">
          <h3 class="card-title">Catálogo (${Libros.getAll().length} libros)</h3>
          <div class="search-bar compact">
            <span>🔍</span>
            <input type="text" id="lib-buscar" placeholder="Buscar por título, ID o autor..." class="search-input" value="${filtro}"
              oninput="UI.renderGestionLibros(App.session, this.value)">
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th><th>Título</th><th>Autor</th><th>Categoría</th>
                <th class="text-center">Ubicación</th><th class="text-center">Estado</th><th class="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;
  },

  _registrarLibro() {
    const titulo    = document.getElementById('lib-titulo').value.trim();
    const autor     = document.getElementById('lib-autor').value.trim();
    const categoria = document.getElementById('lib-categoria').value;
    const f         = document.getElementById('lib-f').value;
    const c         = document.getElementById('lib-c').value;

    const res = Libros.add({ titulo, autor, categoria, f, c });
    if (!res.ok) {
      document.getElementById('lib-error').textContent = res.msg;
      return;
    }
    this.toast(`✅ "${titulo}" registrado como ${res.libro.id}`);
    this.navigate('libros');
  },

  _confirmarEliminarLibro(id, titulo) {
    this.openModal(
      'Eliminar libro',
      `<p>¿Estás seguro de que deseas eliminar el libro <strong>"${titulo}"</strong>?</p>
       <p class="text-muted mt-2">Esta acción no se puede deshacer.</p>`,
      () => {
        const res = Libros.delete(id);
        this.closeModal();
        if (res.ok) { this.toast(`🗑 Libro "${titulo}" eliminado.`); this.navigate('libros'); }
        else this.toast(res.msg, 'error');
      },
      'Eliminar', 'var(--rojo)'
    );
  },

  _modalEditarLibro(id) {
    const lib = Libros.find(id);
    if (!lib) return;
    this.openModal(
      `✏️ Editar libro`,
      `<div class="form-group mb-3">
        <label class="form-label">Título *</label>
        <input type="text" id="e-titulo" class="form-input" value="${lib.titulo.replace(/"/g,'&quot;')}">
      </div>
      <div class="form-group mb-3">
        <label class="form-label">Autor</label>
        <input type="text" id="e-autor" class="form-input" value="${(lib.autor||'').replace(/"/g,'&quot;')}">
      </div>
      <div class="form-group mb-3">
        <label class="form-label">Categoría</label>
        <select id="e-categoria" class="form-input">
          ${CATEGORIAS.map(c => `<option ${c === lib.categoria ? 'selected' : ''}>${c}</option>`).join('')}
        </select>
      </div>
      <p class="text-muted" style="font-size:0.85rem">ID: <code>${lib.id}</code> · Fila ${lib.f}, Col ${lib.c} <em>(ubicación no editable)</em></p>
      <p id="m-error" class="error-text"></p>`,
      () => {
        const titulo    = (document.getElementById('e-titulo').value  || '').trim();
        const autor     = (document.getElementById('e-autor').value   || '').trim();
        const categoria = document.getElementById('e-categoria').value;
        const res = Libros.update(id, { titulo, autor, categoria });
        if (!res.ok) { document.getElementById('m-error').textContent = res.msg; return; }
        this.closeModal();
        this.toast(`✅ Libro "${titulo}" actualizado.`);
        this.navigate('libros');
      },
      'Guardar cambios', 'var(--verde)'
    );
  },

  // ==========================================================
  // VISTA: PRÉSTAMOS Y DEVOLUCIONES (Admin + Bibliotecario)
  // ==========================================================
  renderPrestamos(session, filtroEstado = 'todos') {
    const content = document.getElementById('content');
    const todos = Prestamos.getAll();
    const filtrados = filtroEstado === 'todos' ? todos : todos.filter(p => p.estado === filtroEstado);

    const filas = filtrados.map(p => {
      const titulo = this._tituloPorId(p.id_libro);
      const btnDevolver = (p.estado === 'activo' || p.estado === 'vencido')
        ? `<button class="btn-icon btn-success" title="Registrar devolución" onclick="UI._devolverDesdeTabla('${p.id_libro}')">📗</button>`
        : '—';
      return `
        <tr class="row-${p.estado}">
          <td><code>${p.id_libro}</code></td>
          <td>${titulo}</td>
          <td>${p.usuario}</td>
          <td>${p.fecha_prestamo}</td>
          <td>${p.fecha_limite}</td>
          <td>${p.fecha_devolucion || '—'}</td>
          <td class="text-center">${this._badge(p.estado)}</td>
          <td class="text-center">${btnDevolver}</td>
        </tr>`;
    }).join('') || '<tr><td colspan="8" class="text-center text-muted py-4">No hay préstamos con este filtro.</td></tr>';

    const filtros = ['todos', 'activo', 'vencido', 'devuelto'];
    const filterBtns = filtros.map(f => `
      <button class="btn-filter ${filtroEstado === f ? 'active' : ''}"
        onclick="UI.renderPrestamos(App.session, '${f}')">
        ${f.charAt(0).toUpperCase() + f.slice(1)}
      </button>`).join('');

    content.innerHTML = `
      ${this._encabezado('Préstamos y Devoluciones', 'Registra movimientos y consulta el estado de cada préstamo')}

      <div class="actions-row mb-4">
        <button class="btn btn-success" onclick="UI._modalRegistrarPrestamo()">📕 Registrar préstamo</button>
        <button class="btn btn-primary" onclick="UI._modalRegistrarDevolucion()">📗 Registrar devolución</button>
        <button class="btn btn-danger"  onclick="UI._modalStrike()">⚠ Penalizar (Strike)</button>
      </div>

      <div class="filter-bar mb-3">
        <span class="text-muted mr-2">Filtrar:</span> ${filterBtns}
      </div>

      <div class="card">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID Libro</th><th>Título</th><th>Lector</th>
                <th>Prestado</th><th>Vence</th><th>Devuelto</th><th class="text-center">Estado</th><th class="text-center">Acción</th>
              </tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;
  },

  _modalRegistrarPrestamo() {
    this.openModal(
      '📕 Registrar préstamo',
      `<div class="form-group mb-3">
        <label class="form-label">ID del libro</label>
        ${this._inputLibroConAutocomplete('m-id-libro')}
      </div>
      <div class="form-group mb-3">
        <label class="form-label">Nombre del lector</label>
        <input type="text" id="m-lector" class="form-input" placeholder="Nombre completo">
      </div>
      <p id="m-error" class="error-text"></p>`,
      () => {
        const idLib  = document.getElementById('m-id-libro').value.trim().toUpperCase();
        const lector = document.getElementById('m-lector').value.trim();
        if (!idLib || !lector) { document.getElementById('m-error').textContent = '⚠ Completa todos los campos.'; return; }
        const libro = Libros.find(idLib);
        if (!libro) { document.getElementById('m-error').textContent = `⚠ No existe el libro '${idLib}'.`; return; }
        if (Prestamos.prestamoActivo(idLib)) { document.getElementById('m-error').textContent = '⚠ Este libro ya está prestado.'; return; }
        Prestamos.registrar(idLib, lector);
        this.closeModal();
        this.toast(`✅ "${libro.titulo}" prestado a ${lector}.`);
        this.navigate('prestamos');
      },
      'Registrar', 'var(--verde)'
    );
  },

  _modalRegistrarDevolucion() {
    this.openModal(
      '📗 Registrar devolución',
      `<div class="form-group mb-3">
        <label class="form-label">ID del libro a devolver</label>
        ${this._inputLibroConAutocomplete('m-id-dev')}
      </div>
      <p id="m-error" class="error-text"></p>`,
      () => {
        const idLib = document.getElementById('m-id-dev').value.trim().toUpperCase();
        if (!idLib) { document.getElementById('m-error').textContent = '⚠ Escribe el ID del libro.'; return; }
        const prestamo = Prestamos.devolver(idLib);
        if (!prestamo) { document.getElementById('m-error').textContent = `⚠ No hay préstamo activo para '${idLib}'.`; return; }
        const titulo = this._tituloPorId(idLib);
        this.closeModal();
        this.toast(`✅ "${titulo}" devuelto por ${prestamo.usuario}.`);
        this.navigate('prestamos');
      },
      'Registrar', 'var(--azul)'
    );
  },

  _modalStrike() {
    this.openModal(
      '⚠ Penalizar usuario (Strike)',
      `<div class="form-group mb-3">
        <label class="form-label">Nombre de usuario (login)</label>
        <input type="text" id="m-strike-usr" class="form-input" placeholder="Nombre de usuario">
      </div>
      <p class="text-muted mb-3">Se sumará 1 strike al usuario. Al llegar a 3 strikes, queda suspendido 7 días.</p>
      <p id="m-error" class="error-text"></p>`,
      () => {
        const usr = document.getElementById('m-strike-usr').value.trim();
        if (!usr) { document.getElementById('m-error').textContent = '⚠ Escribe el nombre de usuario.'; return; }
        const res = Prestamos.aplicarStrike(usr);
        if (!res.ok) { document.getElementById('m-error').textContent = res.msg; return; }
        this.closeModal();
        this.toast(`⚠ Strike aplicado a ${usr}. Total: ${res.strikes}`, 'warning');
        this.navigate('prestamos');
      },
      'Aplicar Strike', 'var(--rojo)'
    );
  },

  _devolverDesdeTabla(idLib) {
    const prestamo = Prestamos.devolver(idLib);
    if (!prestamo) { this.toast('⚠ No se pudo registrar la devolución.', 'error'); return; }
    const titulo = this._tituloPorId(idLib);
    this.toast(`✅ "${titulo}" devuelto por ${prestamo.usuario}.`);
    this.navigate('prestamos');
  },

  // ==========================================================
  // VISTA: RESERVAS (Admin + Bibliotecario)
  // ==========================================================
  renderReservas(session) {
    const content = document.getElementById('content');
    const reservas = Prestamos.getReservas();

    const filas = reservas.map((r, idx) => {
      const titulo = this._tituloPorId(r.id_libro);
      const acciones = r.estado === 'pendiente' ? `
        <button class="btn-icon btn-success mr-1" title="Aprobar" onclick="UI._aprobarReserva('${r.id}')">✅</button>
        <button class="btn-icon btn-danger"  title="Rechazar" onclick="UI._rechazarReserva('${r.id}')">✖</button>
      ` : '—';
      return `
        <tr>
          <td><code>${r.id_libro}</code></td>
          <td>${titulo}</td>
          <td>${r.usuario}</td>
          <td>${r.fecha_solicitud}</td>
          <td class="text-center">${this._badge(r.estado)}</td>
          <td class="text-center">${acciones}</td>
        </tr>`;
    }).join('') || '<tr><td colspan="6" class="text-center text-muted py-4">No hay reservas registradas.</td></tr>';

    content.innerHTML = `
      ${this._encabezado('Reservas', 'Aprueba o rechaza solicitudes de reserva de libros')}

      <div class="actions-row mb-4">
        <button class="btn btn-secondary" onclick="UI._modalNuevaReserva()">➕ Nueva reserva</button>
      </div>

      <div class="card">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID Libro</th><th>Título</th><th>Solicitante</th>
                <th>Fecha</th><th class="text-center">Estado</th><th class="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;
  },

  _modalNuevaReserva() {
    this.openModal(
      '🔔 Nueva reserva',
      `<div class="form-group mb-3">
        <label class="form-label">ID del libro</label>
        ${this._inputLibroConAutocomplete('m-res-libro')}
      </div>
      <div class="form-group mb-3">
        <label class="form-label">Nombre del solicitante</label>
        <input type="text" id="m-res-usuario" class="form-input" placeholder="Nombre completo">
      </div>
      <p id="m-error" class="error-text"></p>`,
      () => {
        const idLib = document.getElementById('m-res-libro').value.trim().toUpperCase();
        const usr   = document.getElementById('m-res-usuario').value.trim();
        if (!idLib || !usr) { document.getElementById('m-error').textContent = '⚠ Completa todos los campos.'; return; }
        if (!Libros.find(idLib)) { document.getElementById('m-error').textContent = `⚠ No existe el libro '${idLib}'.`; return; }
        if (Prestamos.getReservas().some(r => r.id_libro === idLib && r.usuario === usr && r.estado === 'pendiente')) {
          document.getElementById('m-error').textContent = `⚠ Ya existe una reserva pendiente de '${usr}' para '${idLib}'.`;
          return;
        }
        Prestamos.registrarReserva(idLib, usr);
        this.closeModal();
        this.toast('🔔 Reserva creada correctamente.');
        this.navigate('reservas');
      },
      'Crear reserva', 'var(--marino)'
    );
  },

  _aprobarReserva(id) {
    const res = Prestamos.aprobarReserva(id);
    if (res) { this.toast('✅ Reserva aprobada y préstamo generado.'); this.navigate('reservas'); }
    else     this.toast('⚠ No se pudo aprobar la reserva.', 'error');
  },

  _rechazarReserva(id) {
    Prestamos.rechazarReserva(id);
    this.toast('✖ Reserva rechazada.');
    this.navigate('reservas');
  },

  // ==========================================================
  // VISTA: ESTANTERÍA 5×5 (Admin + Bibliotecario + Usuario)
  // ==========================================================
  renderEstanteria(session) {
    const content = document.getElementById('content');
    const estanteria = Libros.getEstanteria();
    const librosMap = {};
    Libros.getAll().forEach(l => { librosMap[l.id] = l; });

    const celdas = estanteria.map((fila, f) =>
      fila.map((celda, c) => {
        if (celda === 'Libre') {
          return `<div class="shelf-cell libre" title="Libre — Fila ${f}, Col ${c}">
            <span class="shelf-pos">F${f}·C${c}</span>
            <span class="shelf-status">LIBRE</span>
          </div>`;
        }
        const lib = librosMap[celda];
        const prest = Prestamos.prestamoActivo(celda);
        const ocupadoClass = prest ? 'prestado' : 'ocupado';
        const titulo = lib ? lib.titulo : celda;
        return `<div class="shelf-cell ${ocupadoClass}" title="${titulo}${lib && lib.autor ? '\nAutor: ' + lib.autor : ''}\n${prest ? '🔴 Prestado a: ' + prest.usuario + '\nVence: ' + prest.fecha_limite : '🟢 Disponible'}"
          onclick="UI._mostrarDetalleLibro('${celda}')">
          <span class="shelf-id">${celda}</span>
          <span class="shelf-titulo">${titulo.length > 20 ? titulo.slice(0,18)+'…' : titulo}</span>
          <span class="shelf-status">${prest ? '🔴' : '🟢'}</span>
        </div>`;
      }).join('')
    ).join('');

    const libres = Libros.contarEspaciosLibres();
    content.innerHTML = `
      ${this._encabezado('Estantería', `Mapa visual de los ${MAX_F * MAX_C} espacios de la estantería`)}

      <div class="shelf-legend mb-4">
        <span class="legend-item"><span class="dot verde"></span> Disponible</span>
        <span class="legend-item"><span class="dot rojo"></span> Prestado</span>
        <span class="legend-item"><span class="dot gris"></span> Libre (vacío)</span>
        <span class="text-muted ml-4">Espacios libres: <strong>${libres}</strong> / ${MAX_F * MAX_C}</span>
      </div>

      <div class="shelf-grid">
        <div class="shelf-labels-col">
          ${Array.from({length: MAX_F}, (_, f) => `<div class="shelf-row-label">Fila ${f}</div>`).join('')}
        </div>
        <div class="shelf-cells">${celdas}</div>
      </div>
    `;
  },

  _mostrarDetalleLibro(id) {
    const lib = Libros.find(id);
    if (!lib) return;
    const prest = Prestamos.prestamoActivo(id);
    this.openModal(
      `📖 ${lib.titulo}`,
      `<div class="detail-grid">
        <div class="detail-row"><strong>ID:</strong><span><code>${lib.id}</code></span></div>
        <div class="detail-row"><strong>Autor:</strong><span>${lib.autor || '—'}</span></div>
        <div class="detail-row"><strong>Categoría:</strong><span>${this._chip(lib.categoria)}</span></div>
        <div class="detail-row"><strong>Ubicación:</strong><span>Fila ${lib.f}, Columna ${lib.c}</span></div>
        <div class="detail-row"><strong>Estado:</strong><span>${prest
          ? `🔴 Prestado a <strong>${prest.usuario}</strong> — vence ${prest.fecha_limite}`
          : '🟢 Disponible'}</span></div>
      </div>`,
      () => this.closeModal(), 'Cerrar', 'var(--marino)'
    );
  },

  // ==========================================================
  // VISTA: LIBRERÍA DIGITAL — Administrador/Bibliotecario
  // ==========================================================
  renderLibreriaDigitalAdmin(session) {
    const content = document.getElementById('content');
    const recursos = DB.getLibreria();

    const tarjetas = recursos.map((r, idx) => {
      const chip    = this._chip(r.categoria);
      const portada = _getPortada(r.categoria);
      return `
        <div class="book-card">
          <div class="book-cover">
            <img src="${portada}" alt="Portada ${r.titulo}"
              class="book-cover-img"
              onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <div class="book-cover-fallback" style="display:none">📖</div>
          </div>
          <div class="book-info">
            ${chip}
            <h4 class="book-title">${r.titulo}</h4>
            <p class="book-author">${r.autor}</p>
            <p class="book-desc">${r.descripcion}</p>
            <div class="book-actions">
              <a href="${r.url}" target="_blank" class="btn btn-primary btn-sm">🔗 Abrir recurso</a>
              <button class="btn btn-danger btn-sm" onclick="UI._eliminarRecursoDigital(${idx})">🗑</button>
            </div>
          </div>
        </div>`;
    }).join('') || '<p class="text-muted py-4">No hay recursos digitales. Agrega el primero.</p>';

    content.innerHTML = `
      ${this._encabezado('Librería Digital', 'Gestiona los recursos de lectura en línea')}

      <div class="card mb-4">
        <h3 class="card-title">Agregar nuevo recurso</h3>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Título *</label>
            <input type="text" id="dig-titulo" class="form-input" placeholder="Título del recurso">
          </div>
          <div class="form-group">
            <label class="form-label">Autor</label>
            <input type="text" id="dig-autor" class="form-input" placeholder="Autor o editorial">
          </div>
          <div class="form-group">
            <label class="form-label">Categoría</label>
            <select id="dig-categoria" class="form-input">
              ${CATEGORIAS.map(c => `<option>${c}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">URL</label>
            <input type="url" id="dig-url" class="form-input" placeholder="https://...">
          </div>
          <div class="form-group" style="grid-column: 1 / -1">
            <label class="form-label">Descripción</label>
            <input type="text" id="dig-desc" class="form-input" placeholder="Descripción breve">
          </div>
        </div>
        <p id="dig-error" class="error-text"></p>
        <button class="btn btn-success mt-2" onclick="UI._agregarRecursoDigital()">✅ Agregar recurso</button>
      </div>

      <div class="books-grid">${tarjetas}</div>
    `;
  },

  _agregarRecursoDigital() {
    const titulo    = document.getElementById('dig-titulo').value.trim();
    const autor     = document.getElementById('dig-autor').value.trim();
    const categoria = document.getElementById('dig-categoria').value;
    const url       = document.getElementById('dig-url').value.trim();
    const desc      = document.getElementById('dig-desc').value.trim();
    if (!titulo) { document.getElementById('dig-error').textContent = '⚠ El título es obligatorio.'; return; }
    const recursos = DB.getLibreria();
    recursos.push({ titulo, autor, categoria, url, descripcion: desc });
    DB.setLibreria(recursos);
    this.toast(`✅ "${titulo}" agregado a la librería digital.`);
    this.navigate('libreria-digital');
  },

  _eliminarRecursoDigital(idx) {
    const recursos = DB.getLibreria();
    const r = recursos[idx];
    if (!r) return;
    this.openModal('Eliminar recurso',
      `<p>¿Eliminar "<strong>${r.titulo}</strong>" de la librería digital?</p>`,
      () => {
        recursos.splice(idx, 1);
        DB.setLibreria(recursos);
        this.closeModal();
        this.toast('🗑 Recurso eliminado.');
        this.navigate('libreria-digital');
      }, 'Eliminar', 'var(--rojo)'
    );
  },

  // ==========================================================
  // VISTA: LIBRERÍA DIGITAL — Usuario (solo lectura)
  // ==========================================================
  renderLibreriaDigitalUsuario(session) {
    const content = document.getElementById('content');
    const recursos = DB.getLibreria();

    const tarjetas = recursos.map(r => {
      const chip    = this._chip(r.categoria);
      const portada = _getPortada(r.categoria);
      return `
        <div class="book-card">
          <div class="book-cover">
            <img src="${portada}" alt="Portada ${r.titulo}"
              class="book-cover-img"
              onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <div class="book-cover-fallback" style="display:none">📖</div>
          </div>
          <div class="book-info">
            ${chip}
            <h4 class="book-title">${r.titulo}</h4>
            <p class="book-author">${r.autor}</p>
            <p class="book-desc">${r.descripcion}</p>
            <a href="${r.url || '#'}" target="_blank" class="btn btn-primary btn-sm mt-2">🔗 Abrir recurso</a>
          </div>
        </div>`;
    }).join('') || '<p class="text-muted py-4">No hay recursos digitales disponibles aún.</p>';

    content.innerHTML = `
      ${this._encabezado('Librería Digital', 'Accede a recursos de lectura en línea — siempre disponible')}
      <div class="banner-info mb-4">
        🌐 La librería digital está siempre disponible, sin importar tu estado de cuenta.
      </div>
      <div class="books-grid">${tarjetas}</div>
    `;
  },

  // ==========================================================
  // VISTA: GESTIÓN DE USUARIOS (solo Admin)
  // ==========================================================
  renderGestionUsuarios(session) {
    const content = document.getElementById('content');
    const usuarios = Usuarios.getAll();

    const filas = usuarios.map(u => {
      const rolBadge = {
        admin: `<span class="badge" style="background:#DBEAFE;color:#1E40AF">ADMIN</span>`,
        bibliotecario: `<span class="badge" style="background:#D1FAE5;color:#065F46">BIBLIOTECARIO</span>`,
        usuario: `<span class="badge" style="background:#F3F4F6;color:#374151">ESTUDIANTE</span>`,
      }[u.rol] || `<span class="badge">${u.rol}</span>`;

      const strikes = u.strikes || 0;
      const colorStrikes = strikes >= 4 ? 'var(--rojo)' : strikes >= 2 ? 'var(--acento)' : 'var(--verde)';

      return `
        <tr>
          <td><code>${u.login}</code></td>
          <td>${u.nombre || '—'}</td>
          <td>${u.correo || '—'}</td>
          <td class="text-center">${rolBadge}</td>
          <td class="text-center" style="color:${colorStrikes}"><strong>${strikes}</strong></td>
          <td class="text-center">$${(u.deuda || 0).toFixed(2)}</td>
          <td class="text-center">
            <select class="select-sm" onchange="UI._cambiarRol('${u.login}', this.value, '${session.login}'); this.value='${u.rol}'">
              <option value="${u.rol}" selected>${u.rol}</option>
              ${['usuario','bibliotecario','admin'].filter(r => r !== u.rol)
                .map(r => `<option value="${r}">${r}</option>`).join('')}
            </select>
          </td>
          <td class="text-center">
            <button class="btn-icon btn-accent mr-1" title="Ver préstamos activos" onclick="UI._verPrestamosUsuario('${u.login}', '${(u.nombre||u.login).replace(/'/g,String.fromCharCode(39))}')">📋</button>
            <button class="btn-icon btn-primary mr-1" title="Limpiar deuda" onclick="UI._limpiarDeuda('${u.login}')">💰</button>
            <button class="btn-icon btn-warning mr-1" title="Quitar strike" onclick="UI._quitarStrike('${u.login}')">🏳</button>
            <button class="btn-icon btn-danger" title="Eliminar usuario" onclick="UI._eliminarUsuario('${u.login}', '${session.login}')">🗑</button>
          </td>
        </tr>`;
    }).join('');

    content.innerHTML = `
      ${this._encabezado('Gestión de Usuarios', `${usuarios.length} usuarios registrados en el sistema`)}
      <div class="card">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Usuario</th><th>Nombre</th><th>Correo</th>
                <th class="text-center">Rol</th><th class="text-center">Strikes</th>
                <th class="text-center">Deuda</th><th class="text-center">Cambiar Rol</th>
                <th class="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;
  },

  _cambiarRol(login, nuevoRol, loginAdmin) {
    const res = Usuarios.cambiarRol(login, nuevoRol, loginAdmin);
    if (res.ok) { this.toast(`✅ Rol de '${login}' cambiado a ${nuevoRol}.`); this.navigate('usuarios'); }
    else this.toast(res.msg, 'error');
  },

  _quitarStrike(login) {
    const res = Usuarios.quitarStrike(login);
    if (res.ok) { this.toast(`🏳 Strike quitado a '${login}'.`); this.navigate('usuarios'); }
  },

  _limpiarDeuda(login) {
    const res = Usuarios.limpiarDeuda(login);
    if (res.ok) { this.toast(`💰 Deuda de '${login}' eliminada.`); this.navigate('usuarios'); }
    else this.toast('⚠ No se pudo limpiar la deuda.', 'error');
  },

  _eliminarUsuario(login, loginAdmin) {
    this.openModal('Eliminar usuario',
      `<p>¿Eliminar definitivamente al usuario <strong>${login}</strong>?</p>
       <p class="text-muted mt-2">Esta acción no se puede deshacer.</p>`,
      () => {
        const res = Usuarios.eliminar(login, loginAdmin);
        this.closeModal();
        if (res.ok) { this.toast(`🗑 Usuario '${login}' eliminado.`); this.navigate('usuarios'); }
        else this.toast(res.msg, 'error');
      }, 'Eliminar', 'var(--rojo)'
    );
  },

  _verPrestamosUsuario(login, nombre) {
    const prestamos = Prestamos.deUsuario(login);
    const html = prestamos.length === 0
      ? '<p class="text-muted py-2">No tiene préstamos activos en este momento.</p>'
      : prestamos.map(p => {
          const titulo = this._tituloPorId(p.id_libro);
          return `<div class="detail-row" style="margin-bottom:8px;gap:8px">
            <strong><code>${p.id_libro}</code></strong>
            <span>${titulo} — ${this._badge(p.estado)} — vence <em>${p.fecha_limite}</em></span>
          </div>`;
        }).join('');
    this.openModal(
      `📋 Préstamos activos: ${nombre}`,
      `<div class="detail-grid">${html}</div>`,
      () => this.closeModal(), 'Cerrar', 'var(--marino)'
    );
  },

  // ==========================================================
  // VISTA: SUGERENCIAS — Admin / Bibliotecario
  // ==========================================================
  renderSugerenciasAdmin(session) {
    const content = document.getElementById('content');
    const todos = DB.getComentarios();
    const totalUsuarios = [...new Set(todos.map(c => c.login))].length;

    const items = todos.length === 0
      ? '<p class="text-muted py-4 text-center">No hay sugerencias recibidas aún.</p>'
      : todos.slice().reverse().map(c => `
          <div class="comment-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
              <strong style="color:var(--marino)">👤 ${c.login}</strong>
              <span class="comment-date">${c.fecha}</span>
            </div>
            <p class="comment-text">"${c.texto}"</p>
          </div>`).join('');

    content.innerHTML = `
      ${this._encabezado('Buzón de Sugerencias', `${todos.length} sugerencia(s) de ${totalUsuarios} usuario(s)`)}
      <div class="card">
        <div class="activity-list">${items}</div>
      </div>
    `;
  },

  // ==========================================================
  // VISTA: MI PERFIL / DASHBOARD USUARIO
  // ==========================================================
  renderMiPerfil(session) {
    const content = document.getElementById('content');
    const datos = DB.getUsuario(session.login) || {};
    const { puede, motivo } = Prestamos.estadoPenalizacion(session.login);

    const strikes = datos.strikes || 0;
    const prestamosActivos = Prestamos.deUsuario(session.login).length;
    const colorStrikes = strikes === 0 ? 'var(--verde)' : strikes <= 2 ? 'var(--acento)' : 'var(--rojo)';
    const estadoTxt = strikes >= 4 ? 'BLOQUEADO' : !puede ? 'SUSPENDIDO' : 'ACTIVO';
    const estadoColor = strikes >= 4 ? 'var(--rojo)' : !puede ? 'var(--acento)' : 'var(--verde)';

    const historial = Prestamos.historialUsuario(session.login);
    const actHtml = historial.length === 0
      ? '<p class="text-muted">Todavía no tienes movimientos registrados.</p>'
      : historial.slice(-6).reverse().map(p => {
          const titulo = this._tituloPorId(p.id_libro);
          const [icono, txt, color] = p.estado === 'devuelto'
            ? ['📗', `Devolviste "${titulo}"`, 'var(--verde)']
            : p.estado === 'vencido'
              ? ['⏰', `"${titulo}" está vencido`, 'var(--rojo)']
              : ['📕', `Tienes prestado "${titulo}"`, 'var(--azul)'];
          return `<div class="activity-row">
            <span>${icono}</span>
            <span class="activity-text" style="color:${color}">${txt}</span>
            <span class="activity-date">${p.fecha_prestamo}</span>
          </div>`;
        }).join('');

    const bannerColor = puede ? '#E3F1E9' : '#F6E3E3';
    const bannerBorder = puede ? 'var(--verde)' : 'var(--rojo)';
    const bannerText = puede ? 'var(--verde)' : 'var(--rojo)';

    content.innerHTML = `
      ${this._encabezado('Mi Perfil', 'Tu estado actual en la biblioteca')}

      <div class="cards-grid mb-4">
        ${this._tarjeta('📕', 'LIBROS PRESTADOS', prestamosActivos, 'var(--marino)')}
        ${this._tarjeta('⚠', 'STRIKES', strikes, colorStrikes)}
        ${this._tarjeta('🔵', 'ESTADO', estadoTxt, estadoColor)}
      </div>

      <div class="banner mb-4" style="background:${bannerColor};border-color:${bannerBorder};color:${bannerText}">
        ${motivo}
      </div>

      <h3 class="section-label mb-3">Acciones rápidas</h3>
      <div class="actions-row mb-5">
        <button class="btn btn-success" onclick="UI.navigate('mis-prestamos')">📚 Solicitar préstamo</button>
        <button class="btn btn-primary" onclick="UI.navigate('libreria-digital')">🌐 Librería Digital</button>
        <button class="btn btn-accent"  onclick="UI.navigate('catalogo')">🔍 Ver catálogo</button>
      </div>

      <h3 class="section-label mb-3">Mi actividad reciente</h3>
      <div class="card">
        <div class="activity-list">${actHtml}</div>
      </div>
    `;
  },

  // ==========================================================
  // VISTA: MIS PRÉSTAMOS (Usuario)
  // ==========================================================
  renderMisPrestamos(session) {
    const content = document.getElementById('content');
    const { puede, motivo } = Prestamos.estadoPenalizacion(session.login);
    const historial = Prestamos.historialUsuario(session.login);

    const bannerStyle = puede
      ? 'background:#E3F1E9;border-color:var(--verde);color:var(--verde)'
      : 'background:#F6E3E3;border-color:var(--rojo);color:var(--rojo)';

    const filas = historial.map(p => {
      const titulo = this._tituloPorId(p.id_libro);
      return `
        <tr class="row-${p.estado}">
          <td><code>${p.id_libro}</code></td>
          <td>${titulo}</td>
          <td>${p.fecha_prestamo}</td>
          <td>${p.fecha_limite}</td>
          <td>${p.fecha_devolucion || '—'}</td>
          <td class="text-center">${this._badge(p.estado)}</td>
        </tr>`;
    }).join('') || '<tr><td colspan="6" class="text-center text-muted py-4">Aún no tienes préstamos registrados.</td></tr>';

    content.innerHTML = `
      ${this._encabezado('Préstamo de Libros', 'Solicita un libro físico de la estantería')}

      <div class="banner mb-4" style="${bannerStyle}">${motivo}</div>

      <div class="card mb-4">
        <h3 class="card-title">Solicitar un libro</h3>
        <div class="search-bar">
          ${this._inputLibroConAutocomplete('prest-id', 'ID del libro (ej: LIB001)')}
          <button class="btn btn-success ${!puede ? 'disabled' : ''}"
            ${!puede ? 'disabled' : ''} onclick="UI._solicitarPrestamo('${session.login}', '${session.nombre}')">
            📚 Solicitar préstamo
          </button>
        </div>
        <p id="prest-error" class="error-text mt-2"></p>
      </div>

      <h3 class="section-label mb-3">Mis préstamos</h3>
      <div class="card">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr><th>ID Libro</th><th>Título</th><th>Prestado</th><th>Vence</th><th>Devuelto</th><th class="text-center">Estado</th></tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;

    const input = document.getElementById('prest-id');
    if (input) input.addEventListener('keydown', e => {
      if (e.key === 'Enter') UI._solicitarPrestamo(session.login, session.nombre);
    });
  },

  _solicitarPrestamo(login, nombre) {
    const idLib = (document.getElementById('prest-id')?.value || '').trim().toUpperCase();
    const errEl = document.getElementById('prest-error');
    if (!idLib) { errEl.textContent = '⚠ Escribe el ID del libro que deseas solicitar.'; return; }

    const { puede, motivo } = Prestamos.estadoPenalizacion(login);
    if (!puede) { errEl.textContent = motivo; return; }

    const libro = Libros.find(idLib);
    if (!libro) { errEl.textContent = `⚠ No existe ningún libro con ID '${idLib}'.`; return; }
    if (Prestamos.prestamoActivo(idLib)) { errEl.textContent = '⚠ Este libro ya está prestado a otro lector.'; return; }

    Prestamos.registrar(idLib, nombre, DIAS_PRESTAMO, login);
    this.toast(`✅ Has solicitado "${libro.titulo}". Tienes 7 días para devolverlo.`);
    this.navigate('mis-prestamos');
  },

  // ==========================================================
  // VISTA: CATÁLOGO (Usuario)
  // ==========================================================
  renderCatalogo(session, filtro = '') {
    const content = document.getElementById('content');
    const libros = filtro ? Libros.buscar(filtro) : Libros.getAll();
    const total = Libros.getAll().length;
    const activos = Prestamos.contarActivos();

    const esUsuario = session.rol === 'usuario';
    const { puede: puedePrestar } = esUsuario ? Prestamos.estadoPenalizacion(session.login) : { puede: false };

    const filas = libros.map(lib => {
      const prest = Prestamos.prestamoActivo(lib.id);
      let btnSolicitar = '';
      if (esUsuario) {
        btnSolicitar = (!prest && puedePrestar)
          ? `<button class="btn btn-success btn-sm" style="padding:4px 10px;font-size:.8rem"
               onclick="event.stopPropagation();UI._solicitarDesdeCatalogo('${lib.id}','${session.login}','${session.nombre}')">📚 Solicitar</button>`
          : '—';
      }
      return `
        <tr style="cursor:pointer" onclick="UI._mostrarDetalleLibro('${lib.id}')">
          <td><code>${lib.id}</code></td>
          <td>${lib.titulo}</td>
          <td>${lib.autor || '—'}</td>
          <td>${this._chip(lib.categoria)}</td>
          <td class="text-center">F${lib.f}·C${lib.c}</td>
          <td class="text-center">${prest ? this._badge(prest.estado) : '<span class="badge" style="background:#D1FAE5;color:#065F46">DISPONIBLE</span>'}</td>
          ${esUsuario ? `<td class="text-center">${btnSolicitar}</td>` : ''}
        </tr>`;
    }).join('') || `<tr><td colspan="${esUsuario ? 7 : 6}" class="text-center text-muted py-4">Sin resultados.</td></tr>`;

    content.innerHTML = `
      ${this._encabezado('Catálogo de la Biblioteca', 'Explora y busca libros en la estantería')}

      <div class="card mb-3">
        <div class="search-bar">
          <span>🔍</span>
          <input type="text" id="cat-buscar" class="search-input" placeholder="Buscar por título, ID o autor..." value="${filtro}"
            oninput="UI.renderCatalogo(App.session, this.value)">
          <button class="btn btn-secondary" onclick="UI.renderCatalogo(App.session,'')">Limpiar</button>
        </div>
      </div>

      <div class="stats-bar mb-3">
        📚 Total: <strong>${total}</strong> &nbsp;·&nbsp;
        ✅ Disponibles: <strong>${total - activos}</strong> &nbsp;·&nbsp;
        📕 Prestados: <strong>${activos}</strong>
        <span class="text-muted ml-3">(haz clic en una fila para ver el detalle)</span>
      </div>

      <div class="card">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Título</th><th>Autor</th><th>Categoría</th><th class="text-center">Ubicación</th><th class="text-center">Estado</th>${esUsuario ? '<th class="text-center">Solicitar</th>' : ''}</tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>
      </div>
    `;
  },

  _solicitarDesdeCatalogo(idLib, login, nombre) {
    const { puede, motivo } = Prestamos.estadoPenalizacion(login);
    if (!puede) { this.toast(motivo, 'error'); return; }
    const libro = Libros.find(idLib);
    if (!libro) return;
    if (Prestamos.prestamoActivo(idLib)) { this.toast('⚠ Este libro ya está prestado a otro lector.', 'error'); return; }
    Prestamos.registrar(idLib, nombre, DIAS_PRESTAMO, login);
    this.toast(`✅ "${libro.titulo}" solicitado. Tienes 7 días para devolverlo.`);
    this.navigate('catalogo');
  },

  // ==========================================================
  // VISTA: BUZÓN DE SUGERENCIAS (Usuario)
  // ==========================================================
  renderSugerencias(session) {
    const content = document.getElementById('content');
    const comentarios = DB.getComentarios().filter(c => c.login === session.login);

    const histHtml = comentarios.length === 0
      ? '<p class="text-muted">Aún no has enviado ninguna sugerencia.</p>'
      : comentarios.slice().reverse().map(c => `
          <div class="comment-card">
            <p class="comment-text">"${c.texto}"</p>
            <span class="comment-date">${c.fecha}</span>
          </div>`).join('');

    content.innerHTML = `
      ${this._encabezado('Buzón de Sugerencias', 'Envía tus comentarios sobre la biblioteca')}

      <div class="card mb-4" style="max-width:600px">
        <h3 class="card-title">Nueva sugerencia</h3>
        <div class="form-group mb-3">
          <label class="form-label">Tu mensaje</label>
          <textarea id="sug-texto" class="form-input" rows="4" placeholder="Escribe tu sugerencia, comentario o solicitud de libro…"></textarea>
        </div>
        <p id="sug-error" class="error-text"></p>
        <p id="sug-ok" class="success-text"></p>
        <button class="btn btn-success" onclick="UI._enviarSugerencia('${session.login}')">💬 Enviar sugerencia</button>
      </div>

      <h3 class="section-label mb-3">Mis sugerencias enviadas</h3>
      <div>${histHtml}</div>
    `;
  },

  _enviarSugerencia(login) {
    const texto = (document.getElementById('sug-texto')?.value || '').trim();
    if (!texto) { document.getElementById('sug-error').textContent = '⚠ Escribe tu sugerencia antes de enviar.'; return; }
    DB.addComentario({ login, texto, fecha: new Date().toLocaleDateString('es-EC') });
    document.getElementById('sug-error').textContent = '';
    document.getElementById('sug-ok').textContent = '✅ ¡Sugerencia enviada! Gracias por tu aporte.';
    document.getElementById('sug-texto').value = '';
    this.toast('💬 Sugerencia enviada correctamente.');
  },

  // ==========================================================
  // VISTA: MI CUENTA (Usuario)
  // ==========================================================
  renderMiCuenta(session) {
    const content = document.getElementById('content');
    const datos = DB.getUsuario(session.login) || {};

    content.innerHTML = `
      ${this._encabezado('Mi Cuenta', 'Actualiza tus datos personales')}

      <div class="card" style="max-width:560px">
        <h3 class="card-title">Información personal</h3>
        <div class="form-grid form-grid-2">
          <div class="form-group">
            <label class="form-label">Nombre completo</label>
            <input type="text" id="p-nombre" class="form-input" value="${datos.nombre || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Cédula</label>
            <input type="text" id="p-cedula" class="form-input" value="${datos.cedula || ''}" readonly>
          </div>
          <div class="form-group">
            <label class="form-label">Correo electrónico</label>
            <input type="email" id="p-correo" class="form-input" value="${datos.correo || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Teléfono</label>
            <input type="tel" id="p-telefono" class="form-input" value="${datos.telefono || ''}">
          </div>
        </div>

        <hr class="divider-line my-4">
        <h3 class="card-title">Cambiar contraseña</h3>
        <div class="form-grid form-grid-2">
          <div class="form-group">
            <label class="form-label">Contraseña actual</label>
            <input type="password" id="p-actual" class="form-input" placeholder="••••">
          </div>
          <div class="form-group">
            <label class="form-label">Nueva contraseña</label>
            <input type="password" id="p-nueva" class="form-input" placeholder="••••">
          </div>
        </div>

        <p id="cuenta-error" class="error-text"></p>
        <p id="cuenta-ok" class="success-text"></p>
        <button class="btn btn-success mt-3" onclick="UI._guardarPerfil('${session.login}')">💾 Guardar cambios</button>
      </div>
    `;
  },

  _guardarPerfil(login) {
    const nombre    = document.getElementById('p-nombre').value.trim();
    const correo    = document.getElementById('p-correo').value.trim();
    const telefono  = document.getElementById('p-telefono').value.trim();
    const claveActual = document.getElementById('p-actual').value;
    const claveNueva  = document.getElementById('p-nueva').value;

    const errEl = document.getElementById('cuenta-error');
    const okEl  = document.getElementById('cuenta-ok');
    errEl.textContent = '';
    okEl.textContent  = '';

    const res = Usuarios.actualizarPerfil(login, { nombre, correo, telefono, claveNueva, claveActual });
    if (!res.ok) { errEl.textContent = res.msg; return; }

    // Actualizar nombre en la sesión
    if (nombre) {
      const sess = Auth.getSession();
      if (sess) { sess.nombre = nombre; sessionStorage.setItem('biblio_session', JSON.stringify(sess)); }
      document.getElementById('sidebar-username').textContent = nombre;
    }
    okEl.textContent = '✅ Datos actualizados correctamente.';
    this.toast('💾 Perfil actualizado.');
  }
};
