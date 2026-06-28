"""
Módulo de préstamos y reservas.

Se mantiene separado de Admin.py a propósito: Admin.py concentra el
catálogo (libros + estantería) y usuarios del sistema (login). Este
archivo concentra el movimiento de la biblioteca (quién tiene qué libro
y quién lo está esperando), que es un dominio distinto.

Estructura de cada préstamo en prestamos.json:
    {
        "id_libro": "L001",
        "usuario": "Juan Pérez",        # nombre libre del lector, NO es
                                         # una cuenta de usuarios.json
        "fecha_prestamo": "2026-06-10",
        "fecha_limite": "2026-06-17",
        "fecha_devolucion": null,       # se llena al devolver
        "estado": "activo"              # activo | devuelto | vencido
    }

Estructura de cada reserva en reservas.json:
    {
        "id_libro": "L001",
        "usuario": "María G.",
        "fecha_solicitud": "2026-06-15",
        "estado": "pendiente"           # pendiente | aprobada | rechazada
    }
"""

import json
import os
from datetime import datetime, timedelta

CARPETA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS = os.path.join(CARPETA_RAIZ, "datos")
ARCHIVO_PRESTAMOS = os.path.join(CARPETA_DATOS, "prestamos.json")
ARCHIVO_RESERVAS = os.path.join(CARPETA_DATOS, "reservas.json")

DIAS_PRESTAMO_DEFAULT = 7  # plazo estándar al registrar un préstamo nuevo

lista_prestamos = []
lista_reservas = []


# =========================================================================
# CARGA / GUARDADO — mismo patrón que cargar_desde_archivo() en Admin.py
# =========================================================================
def cargar_prestamos():
    global lista_prestamos
    lista_prestamos = []
    os.makedirs(CARPETA_DATOS, exist_ok=True)

    if not os.path.exists(ARCHIVO_PRESTAMOS):
        return

    try:
        with open(ARCHIVO_PRESTAMOS, "r", encoding="utf-8") as f:
            lista_prestamos = json.load(f)
    except Exception as e:
        print(f"Aviso al cargar préstamos: {e}")

    _actualizar_estados_vencidos()


def guardar_prestamos():
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_PRESTAMOS, "w", encoding="utf-8") as f:
            json.dump(lista_prestamos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar préstamos: {e}")


def cargar_reservas():
    global lista_reservas
    lista_reservas = []
    os.makedirs(CARPETA_DATOS, exist_ok=True)

    if not os.path.exists(ARCHIVO_RESERVAS):
        return

    try:
        with open(ARCHIVO_RESERVAS, "r", encoding="utf-8") as f:
            lista_reservas = json.load(f)
    except Exception as e:
        print(f"Aviso al cargar reservas: {e}")


def guardar_reservas():
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_RESERVAS, "w", encoding="utf-8") as f:
            json.dump(lista_reservas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar reservas: {e}")


# =========================================================================
# LÓGICA DE ESTADOS
# =========================================================================
def _hoy_str():
    return datetime.now().strftime("%Y-%m-%d")


def _actualizar_estados_vencidos():
    """Recalcula 'vencido' para préstamos activos cuya fecha_limite ya pasó.
    Se llama automáticamente al cargar, así el estado siempre refleja la
    fecha real del sistema sin depender de que alguien lo marque a mano."""
    hoy = datetime.now().date()
    cambio = False
    for p in lista_prestamos:
        if p["estado"] == "activo":
            limite = datetime.strptime(p["fecha_limite"], "%Y-%m-%d").date()
            if hoy > limite:
                p["estado"] = "vencido"
                cambio = True
    if cambio:
        guardar_prestamos()


def registrar_prestamo(id_libro, usuario, dias=DIAS_PRESTAMO_DEFAULT):
    """Crea un nuevo préstamo activo. No valida aquí si el libro ya está
    prestado: esa validación de negocio vive en la capa de UI, que tiene
    acceso a lista_libros para cruzar datos."""
    hoy = datetime.now()
    limite = hoy + timedelta(days=dias)
    nuevo = {
        "id_libro": id_libro,
        "usuario": usuario,
        "fecha_prestamo": hoy.strftime("%Y-%m-%d"),
        "fecha_limite": limite.strftime("%Y-%m-%d"),
        "fecha_devolucion": None,
        "estado": "activo",
    }
    lista_prestamos.append(nuevo)
    guardar_prestamos()
    return nuevo


def registrar_devolucion(id_libro):
    """Marca como devuelto el préstamo activo/vencido más reciente de ese
    libro. Retorna el registro actualizado, o None si no había préstamo
    abierto para ese id_libro."""
    candidatos = [p for p in lista_prestamos if p["id_libro"] == id_libro and p["estado"] in ("activo", "vencido")]
    if not candidatos:
        return None
    prestamo = candidatos[-1]
    prestamo["fecha_devolucion"] = _hoy_str()
    prestamo["estado"] = "devuelto"
    guardar_prestamos()
    return prestamo


def prestamo_activo_de(id_libro):
    """Devuelve el préstamo activo/vencido de un libro, si existe."""
    for p in lista_prestamos:
        if p["id_libro"] == id_libro and p["estado"] in ("activo", "vencido"):
            return p
    return None


def contar_vencidos():
    return sum(1 for p in lista_prestamos if p["estado"] == "vencido")


def contar_activos():
    return sum(1 for p in lista_prestamos if p["estado"] in ("activo", "vencido"))


def actividad_reciente(limite=5):
    """Últimos movimientos (préstamos y devoluciones) ordenados por fecha
    descendente, para el widget de 'Actividad reciente' del dashboard."""
    eventos = []
    for p in lista_prestamos:
        eventos.append({
            "tipo": "prestamo",
            "fecha": p["fecha_prestamo"],
            "usuario": p["usuario"],
            "id_libro": p["id_libro"],
        })
        if p["fecha_devolucion"]:
            eventos.append({
                "tipo": "devolucion",
                "fecha": p["fecha_devolucion"],
                "usuario": p["usuario"],
                "id_libro": p["id_libro"],
            })
    eventos.sort(key=lambda e: e["fecha"], reverse=True)
    return eventos[:limite]


# =========================================================================
# RESERVAS
# =========================================================================
def registrar_reserva(id_libro, usuario):
    nueva = {
        "id_libro": id_libro,
        "usuario": usuario,
        "fecha_solicitud": _hoy_str(),
        "estado": "pendiente",
    }
    lista_reservas.append(nueva)
    guardar_reservas()
    return nueva


def contar_pendientes():
    return sum(1 for r in lista_reservas if r["estado"] == "pendiente")


def aprobar_reserva(indice, dias=DIAS_PRESTAMO_DEFAULT):
    """Aprueba una reserva y la convierte automáticamente en préstamo."""
    if not (0 <= indice < len(lista_reservas)):
        return None
    reserva = lista_reservas[indice]
    reserva["estado"] = "aprobada"
    guardar_reservas()
    return registrar_prestamo(reserva["id_libro"], reserva["usuario"], dias)


def rechazar_reserva(indice):
    if not (0 <= indice < len(lista_reservas)):
        return None
    lista_reservas[indice]["estado"] = "rechazada"
    guardar_reservas()
    return lista_reservas[indice]


# =========================================================================
# CONSULTAS POR USUARIO — usadas por el panel de estudiante/invitado
# =========================================================================
def prestamos_de_usuario(nombre_usuario):
    """Devuelve la lista de préstamos activos o vencidos de un usuario."""
    return [p for p in lista_prestamos
            if p["usuario"] == nombre_usuario and p["estado"] in ("activo", "vencido")]


def contar_prestamos_activos_usuario(nombre_usuario):
    """Cantidad de libros que el usuario tiene actualmente en su poder."""
    return len(prestamos_de_usuario(nombre_usuario))


def historial_usuario(nombre_usuario):
    """Todos los préstamos del usuario (activos, vencidos y devueltos)."""
    return [p for p in lista_prestamos if p["usuario"] == nombre_usuario]