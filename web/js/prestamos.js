'use strict';
// ============================================================
// prestamos.js — Préstamos, devoluciones, reservas y penalizaciones
// Equivale a: logica/prestamos.py + partes de menu_bibliotecario.py
// ============================================================

const DIAS_PRESTAMO = 7;

/** Devuelve la fecha de hoy en formato YYYY-MM-DD */
const _hoy = () => new Date().toISOString().split('T')[0];

/** Suma días a una fecha string YYYY-MM-DD */
const _sumarDias = (fechaStr, dias) => {
  const d = new Date(fechaStr + 'T12:00:00');
  d.setDate(d.getDate() + dias);
  return d.toISOString().split('T')[0];
};

/** Diferencia en días entre hoy y una fecha string */
const _diasRestantes = (fechaStr) => {
  const fin = new Date(fechaStr + 'T12:00:00');
  const hoy = new Date();
  hoy.setHours(12, 0, 0, 0);
  return Math.ceil((fin - hoy) / (1000 * 60 * 60 * 24));
};

const Prestamos = {
  // =========================================================
  // PRÉSTAMOS
  // =========================================================

  /** Actualiza estados 'activo' → 'vencido' si ya pasó la fecha límite */
  actualizarVencidos() {
    const prestamos = DB.getPrestamos();
    const hoy = _hoy();
    let cambio = false;
    prestamos.forEach(p => {
      if (p.estado === 'activo' && p.fecha_limite < hoy) {
        p.estado = 'vencido';
        cambio = true;
      }
    });
    if (cambio) DB.setPrestamos(prestamos);
  },

  getAll() {
    this.actualizarVencidos();
    return DB.getPrestamos();
  },

  /**
   * Registra un nuevo préstamo activo.
   * Retorna el registro creado.
   */
  /**
   * login: clave única del usuario (session.login). Opcional para préstamos manuales.
   */
  registrar(id_libro, usuario, dias = DIAS_PRESTAMO, login = null) {
    const fecha_prestamo = _hoy();
    const fecha_limite   = _sumarDias(fecha_prestamo, dias);
    const nuevo = {
      id: 'P' + Date.now(),
      id_libro, usuario,
      login: login || usuario,   // login único para filtrar préstamos del usuario
      fecha_prestamo, fecha_limite,
      fecha_devolucion: null,
      estado: 'activo'
    };
    const p = DB.getPrestamos();
    p.push(nuevo);
    DB.setPrestamos(p);
    return nuevo;
  },

  /**
   * Marca como devuelto el préstamo activo/vencido más reciente de ese libro.
   * Retorna el registro o null si no existía.
   */
  devolver(id_libro) {
    const prestamos = DB.getPrestamos();
    const candidatos = prestamos.filter(
      p => p.id_libro === id_libro && (p.estado === 'activo' || p.estado === 'vencido')
    );
    if (!candidatos.length) return null;
    const prestamo = candidatos[candidatos.length - 1];
    prestamo.fecha_devolucion = _hoy();
    prestamo.estado = 'devuelto';
    DB.setPrestamos(prestamos);
    return prestamo;
  },

  /** Retorna el préstamo activo/vencido de un libro, o null */
  prestamoActivo(id_libro) {
    return this.getAll().find(
      p => p.id_libro === id_libro && (p.estado === 'activo' || p.estado === 'vencido')
    ) || null;
  },

  contarVencidos() { return this.getAll().filter(p => p.estado === 'vencido').length; },
  contarActivos()  { return this.getAll().filter(p => p.estado === 'activo' || p.estado === 'vencido').length; },

  /** Últimos movimientos ordenados por fecha desc (para actividad reciente) */
  actividadReciente(limite = 6) {
    const eventos = [];
    this.getAll().forEach(p => {
      eventos.push({ tipo: 'prestamo', fecha: p.fecha_prestamo, usuario: p.usuario, id_libro: p.id_libro });
      if (p.fecha_devolucion) {
        eventos.push({ tipo: 'devolucion', fecha: p.fecha_devolucion, usuario: p.usuario, id_libro: p.id_libro });
      }
    });
    eventos.sort((a, b) => b.fecha.localeCompare(a.fecha));
    return eventos.slice(0, limite);
  },

  /** Préstamos activos/vencidos de un usuario específico (filtra por login o por nombre para compatibilidad) */
  deUsuario(login) {
    return this.getAll().filter(
      p => (p.login === login || p.usuario === login) && (p.estado === 'activo' || p.estado === 'vencido')
    );
  },

  /** Historial completo (todos los estados) de un usuario */
  historialUsuario(login) {
    return this.getAll().filter(p => p.login === login || p.usuario === login);
  },

  // =========================================================
  // RESERVAS
  // =========================================================

  getReservas() { return DB.getReservas(); },

  registrarReserva(id_libro, usuario) {
    const nueva = {
      id: 'R' + Date.now(),
      id_libro, usuario,
      fecha_solicitud: _hoy(),
      estado: 'pendiente'
    };
    const r = DB.getReservas();
    r.push(nueva);
    DB.setReservas(r);
    return nueva;
  },

  contarPendientes() { return DB.getReservas().filter(r => r.estado === 'pendiente').length; },

  /** Aprueba una reserva y genera el préstamo correspondiente */
  aprobarReserva(id, dias = DIAS_PRESTAMO) {
    const reservas = DB.getReservas();
    const r = reservas.find(x => x.id === id);
    if (!r || r.estado !== 'pendiente') return null;
    r.estado = 'aprobada';
    DB.setReservas(reservas);
    return this.registrar(r.id_libro, r.usuario, dias);
  },

  rechazarReserva(id) {
    const reservas = DB.getReservas();
    const r = reservas.find(x => x.id === id);
    if (!r) return null;
    r.estado = 'rechazada';
    DB.setReservas(reservas);
    return r;
  },

  // =========================================================
  // PENALIZACIONES
  // Equivale a: _estado_penalizacion en menu_usuario.py
  // =========================================================

  estadoPenalizacion(login) {
    const usuario = DB.getUsuario(login);
    if (!usuario) return { puede: true, motivo: '✅ Puedes solicitar libros normalmente.' };

    const strikes        = usuario.strikes || 0;
    const deuda          = usuario.deuda || 0;
    const suspHasta      = usuario.suspendido_hasta || null;

    if (strikes >= 4) {
      return { puede: false, motivo: `🚫 Bloqueo permanente: tienes ${strikes} strikes. Contacta al administrador.` };
    }
    if (suspHasta) {
      const dias = _diasRestantes(suspHasta);
      if (dias > 0) {
        return { puede: false, motivo: `⏳ Suspendido hasta ${suspHasta} (${dias} día(s) restantes). Motivo: 3 strikes acumulados.` };
      }
    }
    if (deuda > 0) {
      return { puede: false, motivo: `💰 Tienes una deuda de $${deuda.toFixed(2)}. Paga en ventanilla para reactivar tus préstamos.` };
    }
    return { puede: true, motivo: '✅ Puedes solicitar libros normalmente.' };
  },

  aplicarStrike(login) {
    const usuario = DB.getUsuario(login);
    if (!usuario) return { ok: false, msg: `El usuario '${login}' no existe.` };

    usuario.strikes = (usuario.strikes || 0) + 1;

    // Al acumular 3 strikes → suspensión de 7 días
    if (usuario.strikes === 3) {
      usuario.suspendido_hasta = _sumarDias(_hoy(), 7);
    }
    DB.saveUsuario(login, usuario);
    return { ok: true, strikes: usuario.strikes };
  },

  limpiarPenalizacion(login) {
    const usuario = DB.getUsuario(login);
    if (!usuario) return { ok: false };
    if (usuario.strikes > 0) usuario.strikes = Math.max(0, usuario.strikes - 1);
    usuario.suspendido_hasta = null;
    usuario.deuda = 0;
    DB.saveUsuario(login, usuario);
    return { ok: true };
  }
};
