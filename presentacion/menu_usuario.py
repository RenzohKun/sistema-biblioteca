import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

# =========================================================================
# RUTAS Y PATH
# =========================================================================
CARPETA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS = os.path.join(CARPETA_RAIZ, "datos")
CARPETA_PORTADAS = os.path.join(CARPETA_DATOS, "portadas")
ARCHIVO_USUARIOS = os.path.join(CARPETA_DATOS, "usuarios.json")
ARCHIVO_COMENTARIOS = os.path.join(CARPETA_DATOS, "comentarios.json")
ARCHIVO_LIBRERIA_DIGITAL = os.path.join(CARPETA_DATOS, "libreria_digital.json")

if CARPETA_RAIZ not in sys.path:
    sys.path.insert(0, CARPETA_RAIZ)

from presentacion.admin import (
    cargar_desde_archivo,
    lista_libros,
    estanteria,
    MAX_F,
    MAX_C,
    buscar_recursivo,
    C,  # paleta de colores marino/dorado
)
from logica import prestamos as PR

# =========================================================================
# PORTADAS — mapeo de categoría a archivo de imagen
# =========================================================================
_PORTADA_POR_CATEGORIA = {
    "Programación":             "portada_programacion.png",
    "Bases de Datos":           "portada_basesdatos.png",
    "Algoritmos":               "portada_algoritmos.png",
    "Redes":                    "portada_redes.png",
    "Ingeniería de Software":   "portada_software.png",
    "Matemáticas":             "portada_matematicas.png",
}

def _cargar_foto_portada(categoria=None, ancho=90, alto=120):
    """Carga y redimensiona la portada según categoría. Devuelve ImageTk.PhotoImage
    o None si PIL no está disponible."""
    if not PIL_DISPONIBLE:
        return None
    nombre = _PORTADA_POR_CATEGORIA.get(categoria, "portada_default.png")
    ruta = os.path.join(CARPETA_PORTADAS, nombre)
    if not os.path.exists(ruta):
        ruta = os.path.join(CARPETA_PORTADAS, "portada_default.png")
    if not os.path.exists(ruta):
        return None
    try:
        img = Image.open(ruta).resize((ancho, alto), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def _cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        return {}
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _guardar_usuarios(usuarios):
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False


def _cargar_comentarios():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    if not os.path.exists(ARCHIVO_COMENTARIOS):
        return []
    try:
        with open(ARCHIVO_COMENTARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _guardar_comentarios(comentarios):
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_COMENTARIOS, "w", encoding="utf-8") as f:
            json.dump(comentarios, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _cargar_libreria_digital():
    if not os.path.exists(ARCHIVO_LIBRERIA_DIGITAL):
        return []
    try:
        with open(ARCHIVO_LIBRERIA_DIGITAL, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _digitos_y_mas(event):
    """Permite dígitos y el signo + (para prefijos internacionales como +593)."""
    if event.char and event.char.isprintable() and not event.char.isdigit() and event.char != '+':
        return "break"


def _obtener_datos_usuario(usuario_login):
    """Lee los datos del usuario actual y garantiza que existan los campos
    de strikes/deuda/suspensión (los agrega si faltan, para compatibilidad
    con cuentas creadas antes de este módulo)."""
    usuarios = _cargar_usuarios()
    datos = usuarios.get(usuario_login, {})
    cambio = False
    for campo, default in [("strikes", 0), ("deuda", 0.0), ("suspendido_hasta", None)]:
        if campo not in datos:
            datos[campo] = default
            cambio = True
    if cambio:
        usuarios[usuario_login] = datos
        _guardar_usuarios(usuarios)
    return datos


def _estado_penalizacion(datos):
    """Determina si el usuario puede pedir libros físicos.
    Retorna (puede_pedir: bool, motivo: str)."""
    strikes = datos.get("strikes", 0)
    deuda = datos.get("deuda", 0.0)
    susp = datos.get("suspendido_hasta", None)

    # Bloqueo permanente: 4+ strikes
    if strikes >= 4:
        return False, f"🚫 Bloqueo permanente: has acumulado {strikes} strikes. Contacta al administrador."

    # Suspensión temporal
    if susp:
        try:
            fecha_fin = datetime.strptime(susp, "%Y-%m-%d").date()
            if datetime.now().date() <= fecha_fin:
                dias_rest = (fecha_fin - datetime.now().date()).days
                return False, f"⏳ Suspendido hasta {susp} ({dias_rest} día(s) restantes). Motivo: 3 strikes acumulados."
        except Exception:
            pass

    # Deuda pendiente
    if deuda > 0:
        return False, f"💰 Tienes una deuda de ${deuda:.2f}. Paga en ventanilla para reactivar tus préstamos."

    return True, "✅ Puedes solicitar libros normalmente."


# =========================================================================
# CLASE PRINCIPAL — PANEL DE USUARIO
# =========================================================================
class VentanaUsuario:
    def __init__(self, root, usuario_login, nombre_completo="Estudiante"):
        self.root = root
        self.usuario_login = usuario_login
        self.nombre_completo = nombre_completo

        self.root.title("Sistema de Biblioteca — Panel de Estudiante")
        self.root.configure(bg=C["fondo"])
        self.root.geometry("1080x680")
        self.root.resizable(True, True)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"1080x680+{(sw-1080)//2}+{(sh-680)//2}")

        cargar_desde_archivo()
        PR.cargar_prestamos()
        PR.cargar_reservas()

        # --- FUENTES ---
        self.f_logo      = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        self.f_bienv     = tkfont.Font(family="Segoe UI", size=10, slant="italic")
        self.f_menu      = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_titulo    = tkfont.Font(family="Segoe UI", size=19, weight="bold")
        self.f_subtitulo = tkfont.Font(family="Segoe UI", size=10)
        self.f_card_lbl  = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.f_card_num  = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        self.f_seccion   = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.f_btn       = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_label     = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.f_busqueda  = tkfont.Font(family="Segoe UI", size=10)
        self.f_actividad = tkfont.Font(family="Segoe UI", size=9)

        # --- CONTENEDORES PRINCIPALES ---
        self.menu_lateral = tk.Frame(self.root, bg=C["marino"], width=230)
        self.menu_lateral.pack(side="left", fill="y")
        self.menu_lateral.pack_propagate(False)

        self.area_contenido = tk.Frame(self.root, bg=C["fondo"])
        self.area_contenido.pack(side="right", fill="both", expand=True)

        tk.Frame(self.root, bg=C["acento"], width=3).place(x=230, y=0, relheight=1)

        # --- CABECERA DEL MENÚ ---
        tk.Label(
            self.menu_lateral, text="📚 BIBLIOTECA",
            fg=C["blanco"], bg=C["marino"], font=self.f_logo
        ).pack(pady=(26, 4))

        tk.Frame(self.menu_lateral, bg=C["acento"], height=2, width=120).pack(pady=(0, 16))

        tk.Label(
            self.menu_lateral, text=f"Bienvenido,\n{nombre_completo}",
            bg=C["marino"], font=self.f_bienv, fg="#9FB3CC", justify="center"
        ).pack(pady=(0, 4))

        datos_usuario = _obtener_datos_usuario(self.usuario_login)

        tk.Label(
            self.menu_lateral, text="(Estudiante)",
            bg=C["marino"], font=("Segoe UI", 8), fg=C["acento"]
        ).pack(pady=(0, 20))

        # --- BOTONES DE NAVEGACIÓN ---
        self.seccion_activa = "dashboard"
        self.botones_menu = {}
        self._crear_boton_menu("dashboard",  "🏠  Inicio / Mi Perfil",     self.mostrar_inicio)
        self._crear_boton_menu("prestamos",  "📚  Préstamo de Libros",     self.mostrar_prestamos)
        self._crear_boton_menu("digital",    "🌐  Librería Digital",       self.mostrar_libreria_digital)
        self._crear_boton_menu("catalogo",   "🔍  Catálogo / Estantería",  self.mostrar_catalogo)
        self._crear_boton_menu("sugerencias","💬  Buzón de Sugerencias",   self.mostrar_sugerencias)
        self._crear_boton_menu("perfil",     "⚙️  Mi Cuenta",              self.mostrar_editar_perfil)

        # Botón cerrar sesión
        btn_logout = tk.Button(
            self.menu_lateral, text="Cerrar sesión", command=self.cerrar_sesion,
            bg=C["rojo"], fg="white", relief="flat", font=self.f_btn,
            bd=0, pady=10, cursor="hand2",
            activebackground=C["rojo_hover"], activeforeground="white"
        )
        btn_logout.pack(side="bottom", fill="x", padx=18, pady=22)
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg=C["rojo_hover"]))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg=C["rojo"]))

        self.mostrar_inicio()

    # =====================================================================
    # NAVEGACIÓN (idéntica al patrón de Admin / Bibliotecario)
    # =====================================================================
    def _crear_boton_menu(self, clave, texto, comando):
        btn = tk.Button(
            self.menu_lateral, text=texto,
            command=lambda: self._navegar(clave, comando),
            bg=C["marino"], fg=C["blanco"], relief="flat", font=self.f_menu,
            anchor="w", padx=18, pady=11, cursor="hand2", bd=0,
            activebackground="#2C3E63", activeforeground="white"
        )
        btn.pack(fill="x", padx=12, pady=3)
        btn.bind("<Enter>", lambda e, b=btn, k=clave: b.config(bg="#2C3E63") if self.seccion_activa != k else None)
        btn.bind("<Leave>", lambda e, b=btn, k=clave: b.config(bg=C["acento"] if self.seccion_activa == k else C["marino"]))
        self.botones_menu[clave] = btn

    def _navegar(self, clave, comando):
        self.seccion_activa = clave
        for k, btn in self.botones_menu.items():
            if k == clave:
                btn.config(bg=C["acento"], fg=C["marino"])
            else:
                btn.config(bg=C["marino"], fg=C["blanco"])
        comando()

    def limpiar_contenido(self):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

    def _encabezado(self, titulo, subtitulo):
        wrap = tk.Frame(self.area_contenido, bg=C["fondo"])
        wrap.pack(fill="x", padx=32, pady=(26, 0))
        tk.Label(wrap, text=titulo, font=self.f_titulo, bg=C["fondo"], fg=C["marino"]).pack(anchor="w")
        tk.Frame(wrap, bg=C["acento"], height=2, width=70).pack(anchor="w", pady=(6, 8))
        tk.Label(wrap, text=subtitulo, font=self.f_subtitulo, bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 18))

    def _estilizar_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Biblio.Treeview",
            background=C["tarjeta"], fieldbackground=C["tarjeta"],
            foreground=C["texto"], rowheight=28, borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Biblio.Treeview.Heading",
            background=C["marino"], foreground="white",
            font=("Segoe UI", 10, "bold"), relief="flat"
        )
        style.map("Biblio.Treeview.Heading", background=[("active", C["marino_hover"])])
        style.map("Biblio.Treeview", background=[("selected", "#F3E4C8")], foreground=[("selected", C["texto"])])

    def _boton_accion(self, parent, texto, color, hover, comando):
        btn = tk.Button(
            parent, text=texto, command=comando, bg=color, fg="white",
            font=self.f_btn, padx=16, pady=10, relief="flat", bd=0, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _tarjeta_dashboard(self, parent, col, icono, etiqueta, valor, color_valor):
        card = tk.Frame(parent, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        card.grid(row=0, column=col, padx=(0 if col == 0 else 10, 10), sticky="nsew")
        inner = tk.Frame(card, bg=C["tarjeta"])
        inner.pack(fill="both", padx=20, pady=16)
        tk.Label(inner, text=f"{icono}  {etiqueta}", font=self.f_card_lbl, bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w")
        tk.Label(inner, text=str(valor), font=self.f_card_num, bg=C["tarjeta"], fg=color_valor).pack(anchor="w", pady=(6, 0))
        return card

    # =====================================================================
    # 🏠 VISTA: INICIO / DASHBOARD — INDICADORES DE PERFIL
    # =====================================================================
    def mostrar_inicio(self):
        self.limpiar_contenido()
        self._encabezado("Mi perfil", "Tu estado actual en la biblioteca")

        datos = _obtener_datos_usuario(self.usuario_login)
        puede_pedir, motivo = _estado_penalizacion(datos)

        # --- TARJETAS ---
        frame_tarjetas = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas.pack(padx=32, fill="x", anchor="w")
        frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1, uniform="card", minsize=140)

        prestamos_activos = PR.contar_prestamos_activos_usuario(self.nombre_completo)
        strikes = datos.get("strikes", 0)

        # Color del strike según gravedad
        if strikes == 0:
            color_strike = C["verde"]
        elif strikes <= 2:
            color_strike = C["acento"]
        else:
            color_strike = C["rojo"]

        self._tarjeta_dashboard(frame_tarjetas, 0, "📕", "LIBROS PRESTADOS", prestamos_activos, C["marino"])
        self._tarjeta_dashboard(frame_tarjetas, 1, "⚠", "STRIKES", f"{strikes} / 3", color_strike)

        # Estado: activo / suspendido / bloqueado
        if strikes >= 4:
            estado_texto, estado_color = "BLOQUEADO", C["rojo"]
        elif not puede_pedir:
            estado_texto, estado_color = "SUSPENDIDO", C["acento"]
        else:
            estado_texto, estado_color = "ACTIVO", C["verde"]
        self._tarjeta_dashboard(frame_tarjetas, 2, "🟢" if puede_pedir else "🔴", "ESTADO", estado_texto, estado_color)
        color_msg = C["verde"] if puede_pedir else C["rojo"]

        # --- MENSAJE DE ESTADO ---
        frame_estado = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                                highlightthickness=1, highlightbackground=C["borde"])
        frame_estado.pack(padx=32, pady=(18, 0), fill="x")
        inner_estado = tk.Frame(frame_estado, bg=C["tarjeta"])
        inner_estado.pack(fill="x", padx=18, pady=14)

        lbl_motivo = tk.Label(inner_estado, text=motivo, font=self.f_subtitulo, bg=C["tarjeta"],
                 fg=color_msg, wraplength=700, justify="left")
        lbl_motivo.pack(anchor="w")
        # Ajustar wraplength dinámicamente cuando la ventana cambia de tamaño
        def _actualizar_wrap(e, lbl=lbl_motivo):
            lbl.config(wraplength=max(200, e.width - 36))
        inner_estado.bind("<Configure>", _actualizar_wrap)

        # --- ACCIONES RÁPIDAS ---
        tk.Label(
            self.area_contenido, text="Acciones rápidas",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(30, 14), padx=32, anchor="w")

        frame_acciones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_acciones.pack(padx=32, fill="x", anchor="w")

        self._boton_accion(frame_acciones, "📚  Solicitar préstamo", C["verde"], C["verde_hover"],
                           self.mostrar_prestamos).pack(side="left", padx=(0, 14))

        self._boton_accion(frame_acciones, "🌐  Librería Digital", C["azul_dato"], C["azul_dato_hover"],
                           self.mostrar_libreria_digital).pack(side="left", padx=(0, 14))
        self._boton_accion(frame_acciones, "🔍  Ver catálogo", C["acento"], "#B07F2E",
                           self.mostrar_catalogo).pack(side="left")

        # --- HISTORIAL RECIENTE ---
        tk.Label(
            self.area_contenido, text="Mi actividad reciente",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(30, 12), padx=32, anchor="w")

        historial = PR.historial_usuario(self.nombre_completo)
        frame_hist = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"])
        frame_hist.pack(padx=32, pady=(0, 24), fill="x")
        inner_hist = tk.Frame(frame_hist, bg=C["tarjeta"])
        inner_hist.pack(fill="x", padx=18, pady=14)

        if not historial:
            tk.Label(inner_hist, text="Todavía no tienes movimientos registrados.",
                     font=self.f_actividad, bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w")
        else:
            titulos_por_id = {lib["id"]: lib["titulo"] for lib in lista_libros}
            for i, p in enumerate(historial[-6:]):
                titulo = titulos_por_id.get(p["id_libro"], p["id_libro"])
                if p["estado"] == "devuelto":
                    icono, texto, color = "📗", f'Devolviste "{titulo}"', C["verde"]
                elif p["estado"] == "vencido":
                    icono, texto, color = "⏰", f'"{titulo}" está vencido', C["rojo"]
                else:
                    icono, texto, color = "📕", f'Tienes prestado "{titulo}"', C["azul_dato"]

                fila = tk.Frame(inner_hist, bg=C["tarjeta"])
                fila.pack(fill="x", pady=(0 if i == 0 else 5, 0))
                tk.Label(fila, text=icono, bg=C["tarjeta"], font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
                tk.Label(fila, text=texto, bg=C["tarjeta"], font=self.f_actividad, fg=C["texto"]).pack(side="left")
                tk.Label(fila, text=p["fecha_prestamo"], bg=C["tarjeta"],
                         font=("Segoe UI", 8), fg=C["texto_muted"]).pack(side="right")

    # =====================================================================
    # 📚 VISTA: PRÉSTAMO DE LIBROS
    # =====================================================================
    def mostrar_prestamos(self):
        self.seccion_activa = "prestamos"
        self._refrescar_botones()
        self.limpiar_contenido()
        self._encabezado("Préstamo de libros", "Solicita un libro físico de la estantería")

        datos = _obtener_datos_usuario(self.usuario_login)
        puede_pedir, motivo = _estado_penalizacion(datos)

        # --- BANNER DE ESTADO ---
        color_banner = C["verde_suave"] if puede_pedir else C["rojo_suave"]
        color_texto_banner = C["verde"] if puede_pedir else C["rojo"]
        borde_banner = C["verde"] if puede_pedir else C["rojo"]

        frame_banner = tk.Frame(self.area_contenido, bg=color_banner,
                                highlightthickness=1, highlightbackground=borde_banner)
        frame_banner.pack(padx=32, fill="x")
        tk.Label(frame_banner, text=motivo, font=self.f_subtitulo, bg=color_banner,
                 fg=color_texto_banner, wraplength=700, justify="left").pack(padx=16, pady=12, anchor="w")

        # --- FORMULARIO DE SOLICITUD ---
        frame_form = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"])
        frame_form.pack(padx=32, pady=(14, 0), fill="x")
        inner = tk.Frame(frame_form, bg=C["tarjeta"])
        inner.pack(fill="x", padx=18, pady=16)

        tk.Label(inner, text="Solicitar un libro", font=self.f_seccion, bg=C["tarjeta"], fg=C["marino"]).pack(anchor="w", pady=(0, 12))

        fila_campo = tk.Frame(inner, bg=C["tarjeta"])
        fila_campo.pack(fill="x")

        tk.Label(fila_campo, text="ID del libro:", font=self.f_label, bg=C["tarjeta"], fg=C["texto_muted"]).pack(side="left", padx=(0, 8))
        self.ent_prestamo_id = tk.Entry(fila_campo, font=("Segoe UI", 10), relief="flat",
                                        highlightthickness=1, highlightbackground=C["borde"], width=20)
        self.ent_prestamo_id.pack(side="left", ipady=5, padx=(0, 14))

        estado_solicitud = "normal" if puede_pedir else "disabled"
        btn_solicitar = tk.Button(
            fila_campo, text="📚  Solicitar préstamo",
            command=self._solicitar_prestamo,
            bg=C["verde"] if puede_pedir else C["texto_muted"],
            fg="white", font=self.f_btn, padx=16, pady=8,
            relief="flat", bd=0, cursor="hand2" if puede_pedir else "arrow",
            state=estado_solicitud
        )
        btn_solicitar.pack(side="left")
        if puede_pedir:
            btn_solicitar.bind("<Enter>", lambda e: btn_solicitar.config(bg=C["verde_hover"]))
            btn_solicitar.bind("<Leave>", lambda e: btn_solicitar.config(bg=C["verde"]))

        self.lbl_error_prestamo = tk.Label(inner, text="", font=("Segoe UI", 9), bg=C["tarjeta"],
                                           fg=C["rojo"], wraplength=600, justify="left")
        self.lbl_error_prestamo.pack(anchor="w", pady=(8, 0))

        # --- TABLA: MIS PRÉSTAMOS ACTUALES ---
        tk.Label(
            self.area_contenido, text="Mis préstamos actuales",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(padx=32, pady=(20, 10), anchor="w")

        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()
        columnas = ("id_libro", "titulo", "f_prestamo", "f_limite", "estado")
        self.tabla_mis_prestamos = ttk.Treeview(frame_tabla, columns=columnas, show="headings",
                                                 height=8, style="Biblio.Treeview")

        self.tabla_mis_prestamos.heading("id_libro", text="ID Libro")
        self.tabla_mis_prestamos.heading("titulo", text="Título")
        self.tabla_mis_prestamos.heading("f_prestamo", text="Prestado")
        self.tabla_mis_prestamos.heading("f_limite", text="Vence")
        self.tabla_mis_prestamos.heading("estado", text="Estado")

        self.tabla_mis_prestamos.column("id_libro", width=90, anchor="center")
        self.tabla_mis_prestamos.column("titulo", width=300, anchor="w")
        self.tabla_mis_prestamos.column("f_prestamo", width=110, anchor="center")
        self.tabla_mis_prestamos.column("f_limite", width=110, anchor="center")
        self.tabla_mis_prestamos.column("estado", width=100, anchor="center")

        self.tabla_mis_prestamos.tag_configure("vencido", foreground=C["rojo"])
        self.tabla_mis_prestamos.tag_configure("activo", foreground=C["verde"])
        self.tabla_mis_prestamos.tag_configure("devuelto", foreground=C["texto_muted"])

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_mis_prestamos.yview)
        self.tabla_mis_prestamos.configure(yscrollcommand=scrollbar.set)
        self.tabla_mis_prestamos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._actualizar_tabla_mis_prestamos()

    def _solicitar_prestamo(self):
        id_lib = self.ent_prestamo_id.get().strip()
        if not id_lib:
            self.lbl_error_prestamo.config(text="⚠ Escribe el ID del libro que deseas solicitar.")
            return

        # Verificar penalización
        datos = _obtener_datos_usuario(self.usuario_login)
        puede, motivo = _estado_penalizacion(datos)
        if not puede:
            self.lbl_error_prestamo.config(text=motivo)
            return

        # Verificar que el libro exista
        libro = next((lib for lib in lista_libros if lib["id"] == id_lib), None)
        if not libro:
            self.lbl_error_prestamo.config(text=f"⚠ No existe ningún libro con ID '{id_lib}' en el catálogo.")
            return

        # Verificar que no esté ya prestado
        if PR.prestamo_activo_de(id_lib):
            self.lbl_error_prestamo.config(text="⚠ Este libro ya está prestado a otro lector y no ha sido devuelto.")
            return

        # Registrar préstamo usando el nombre completo del usuario
        PR.registrar_prestamo(id_lib, self.nombre_completo)
        messagebox.showinfo("Préstamo registrado",
                            f"📚 Has solicitado el libro:\n\n"
                            f"   \"{libro['titulo']}\"\n\n"
                            f"Tienes 7 días para devolverlo.")
        self.ent_prestamo_id.delete(0, tk.END)
        self.lbl_error_prestamo.config(text="")
        self._actualizar_tabla_mis_prestamos()

    def _actualizar_tabla_mis_prestamos(self):
        for fila in self.tabla_mis_prestamos.get_children():
            self.tabla_mis_prestamos.delete(fila)

        titulos_por_id = {lib["id"]: lib["titulo"] for lib in lista_libros}
        historial = PR.historial_usuario(self.nombre_completo)

        for p in historial:
            titulo = titulos_por_id.get(p["id_libro"], p["id_libro"])
            self.tabla_mis_prestamos.insert(
                "", "end",
                values=(p["id_libro"], titulo, p["fecha_prestamo"], p["fecha_limite"], p["estado"].upper()),
                tags=(p["estado"],)
            )

    # =====================================================================
    # 🌐 VISTA: LIBRERÍA DIGITAL (siempre accesible)
    # =====================================================================
    def mostrar_libreria_digital(self):
        self.seccion_activa = "digital"
        self._refrescar_botones()
        self.limpiar_contenido()
        self._encabezado("Librería Digital", "Accede a recursos de lectura en línea — siempre disponible")

        # Banner informativo
        frame_info = tk.Frame(self.area_contenido, bg="#DBEAFE",
                              highlightthickness=1, highlightbackground="#93C5FD")
        frame_info.pack(padx=32, fill="x")
        tk.Label(frame_info, text="🌐  La librería digital está siempre disponible, sin importar tu estado de cuenta.",
                 font=self.f_actividad, bg="#DBEAFE", fg="#1E40AF", wraplength=700, justify="left").pack(padx=16, pady=10, anchor="w")

        # --- CONTENEDOR SCROLLABLE PARA EL GRID DE TARJETAS ---
        frame_scroll_outer = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_scroll_outer.pack(padx=32, pady=(14, 24), fill="both", expand=True)

        canvas_digital = tk.Canvas(frame_scroll_outer, bg=C["fondo"], bd=0, highlightthickness=0)
        sb_digital = ttk.Scrollbar(frame_scroll_outer, orient="vertical", command=canvas_digital.yview)
        canvas_digital.configure(yscrollcommand=sb_digital.set)
        sb_digital.pack(side="right", fill="y")
        canvas_digital.pack(side="left", fill="both", expand=True)

        frame_cards = tk.Frame(canvas_digital, bg=C["fondo"])
        id_cards = canvas_digital.create_window((0, 0), window=frame_cards, anchor="nw")

        canvas_digital.bind("<Configure>", lambda e: canvas_digital.itemconfig(id_cards, width=e.width))
        frame_cards.bind("<Configure>", lambda e: canvas_digital.configure(scrollregion=canvas_digital.bbox("all")))
        canvas_digital.bind_all("<MouseWheel>", lambda e: canvas_digital.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Colores de chip por categoría
        colores_chip = {
            "Programación":           ("#DBEAFE", "#1E40AF"),
            "Bases de Datos":         ("#D1FAE5", "#065F46"),
            "Algoritmos":             ("#FEF3C7", "#92400E"),
            "Redes":                  ("#F3E8FF", "#6B21A8"),
            "Ingeniería de Software": ("#FFE4E6", "#9F1239"),
            "Matemáticas":           ("#E0F2FE", "#0C4A6E"),
        }

        recursos = _cargar_libreria_digital()
        self._fotos_digital = []   # Mantener referencias para evitar GC

        COLS = 3  # tarjetas por fila
        for i, rec in enumerate(recursos):
            fila_grid  = i // COLS
            col_grid   = i %  COLS

            categoria = rec.get("categoria", "")
            chip_bg, chip_fg = colores_chip.get(categoria, (C["acento_suave"], C["marino"]))

            # Tarjeta contenedor
            card = tk.Frame(frame_cards, bg=C["tarjeta"],
                            highlightthickness=1, highlightbackground=C["borde"])
            card.grid(row=fila_grid, column=col_grid, padx=8, pady=8, sticky="nsew")
            frame_cards.grid_columnconfigure(col_grid, weight=1, uniform="digcol")

            # ---- PORTADA ----
            foto = _cargar_foto_portada(categoria, ancho=120, alto=160)
            if foto:
                self._fotos_digital.append(foto)
                lbl_img = tk.Label(card, image=foto, bg=C["marino"],
                                   width=120, height=160)
                lbl_img.pack(fill="x")
            else:
                # Fallback: recuadro con emoji si PIL no disponible
                lbl_img = tk.Label(card, text="📖", font=("Segoe UI", 36),
                                   bg=C["marino"], fg=C["acento"],
                                   width=120, height=80)
                lbl_img.pack(fill="x", ipady=18)

            # ---- CONTENIDO TEXTO ----
            inner_card = tk.Frame(card, bg=C["tarjeta"])
            inner_card.pack(fill="x", padx=12, pady=10)

            # Chip de categoría
            chip = tk.Label(inner_card, text=categoria,
                            font=("Segoe UI", 7, "bold"),
                            bg=chip_bg, fg=chip_fg, padx=6, pady=2)
            chip.pack(anchor="w", pady=(0, 5))

            # Título (con wrap dinámico)
            lbl_titulo = tk.Label(inner_card, text=rec.get("titulo", ""),
                                  font=("Segoe UI", 9, "bold"),
                                  bg=C["tarjeta"], fg=C["marino"],
                                  wraplength=170, justify="left", anchor="w")
            lbl_titulo.pack(anchor="w", pady=(0, 3))

            # Autor
            tk.Label(inner_card, text=rec.get("autor", ""),
                     font=("Segoe UI", 8), bg=C["tarjeta"],
                     fg=C["texto_muted"], wraplength=170, justify="left").pack(anchor="w")

            # Descripción (2 líneas)
            tk.Label(inner_card, text=rec.get("descripcion", ""),
                     font=("Segoe UI", 8), bg=C["tarjeta"],
                     fg=C["texto_muted"], wraplength=170, justify="left").pack(anchor="w", pady=(4, 6))

            # Botón Abrir
            idx = i  # captura por valor
            url = rec.get("url", "")
            btn = tk.Button(
                inner_card, text="🔗  Abrir recurso",
                font=("Segoe UI", 8, "bold"),
                bg=C["azul_dato"], fg="white", relief="flat", bd=0,
                padx=8, pady=5, cursor="hand2",
                command=lambda u=url: (webbrowser.open(u) if u else
                                       messagebox.showinfo("Sin enlace", "Este recurso no tiene un enlace disponible aún."))
            )
            btn.pack(anchor="w")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=C["azul_dato_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=C["azul_dato"]))

        if not recursos:
            tk.Label(frame_cards, text="No hay recursos digitales disponibles.",
                     font=self.f_actividad, bg=C["fondo"], fg=C["texto_muted"]).pack(padx=20, pady=30)

    # =====================================================================
    # 🔍 VISTA: CATÁLOGO / BÚSQUEDA
    # =====================================================================
    def mostrar_catalogo(self):
        self.seccion_activa = "catalogo"
        self._refrescar_botones()
        self.limpiar_contenido()
        self._encabezado("Catálogo de la biblioteca", "Explora y busca libros en la estantería")

        # Barra de búsqueda
        frame_busqueda = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                                   highlightthickness=1, highlightbackground=C["borde"])
        frame_busqueda.pack(padx=32, fill="x")
        inner_busq = tk.Frame(frame_busqueda, bg=C["tarjeta"])
        inner_busq.pack(fill="x", padx=14, pady=10)

        tk.Label(inner_busq, text="🔍", bg=C["tarjeta"], font=("Segoe UI", 12)).pack(side="left", padx=(2, 8))

        self.ent_busqueda_catalogo = tk.Entry(
            inner_busq, relief="flat", bg=C["tarjeta"], font=self.f_busqueda,
            highlightthickness=0, bd=0
        )
        self.ent_busqueda_catalogo.pack(side="left", fill="x", expand=True, ipady=4)

        placeholder = "Buscar por título o ID..."
        self.ent_busqueda_catalogo.insert(0, placeholder)
        self.ent_busqueda_catalogo.config(fg=C["texto_muted"])

        def al_enfocar(e):
            if self.ent_busqueda_catalogo.get() == placeholder:
                self.ent_busqueda_catalogo.delete(0, tk.END)
                self.ent_busqueda_catalogo.config(fg=C["texto"])

        def al_desenfocar(e):
            if not self.ent_busqueda_catalogo.get().strip():
                self.ent_busqueda_catalogo.insert(0, placeholder)
                self.ent_busqueda_catalogo.config(fg=C["texto_muted"])

        self.ent_busqueda_catalogo.bind("<FocusIn>", al_enfocar)
        self.ent_busqueda_catalogo.bind("<FocusOut>", al_desenfocar)
        self.ent_busqueda_catalogo.bind("<KeyRelease>", lambda e: self._filtrar_catalogo())

        btn_buscar = tk.Button(
            inner_busq, text="Buscar", command=self._filtrar_catalogo,
            bg=C["marino"], fg="white", relief="flat", font=self.f_label,
            bd=0, padx=14, pady=4, cursor="hand2"
        )
        btn_buscar.pack(side="right")

        # Estadísticas
        total = len(lista_libros)
        prestados = sum(1 for p in PR.lista_prestamos if p["estado"] in ("activo", "vencido"))
        disponibles = total - prestados

        frame_stats = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_stats.pack(padx=32, pady=(10, 0), anchor="w")
        tk.Label(frame_stats,
                 text=f"📚 Total: {total}   |   ✅ Disponibles: {disponibles}   |   📕 Prestados: {prestados}",
                 font=self.f_actividad, bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")

        # --- LAYOUT HORIZONTAL: tabla izq + panel detalle der ---
        frame_body = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_body.pack(padx=32, pady=(8, 24), fill="both", expand=True)

        # --- PANEL LATERAL DE DETALLE CON PORTADA (Se empaqueta PRIMERO) ---
        self._panel_detalle_cat = tk.Frame(frame_body, bg=C["tarjeta"],
                                            highlightthickness=1, highlightbackground=C["borde"],
                                            width=200)
        self._panel_detalle_cat.pack(side="right", fill="y", padx=(12, 0))
        self._panel_detalle_cat.pack_propagate(False)

        # Contenido inicial del panel (instrucción)
        self._foto_detalle_cat = None  # referencia para GC
        self._lbl_portada_cat = tk.Label(self._panel_detalle_cat, bg=C["marino"],
                                          width=160, height=210)
        self._lbl_portada_cat.pack(fill="x")

        inner_det = tk.Frame(self._panel_detalle_cat, bg=C["tarjeta"])
        inner_det.pack(fill="both", expand=True, padx=10, pady=10)

        self._lbl_det_titulo = tk.Label(inner_det, text="Selecciona un libro",
                                         font=("Segoe UI", 9, "bold"),
                                         bg=C["tarjeta"], fg=C["marino"],
                                         wraplength=170, justify="left")
        self._lbl_det_titulo.pack(anchor="w", pady=(0, 4))
        self._lbl_det_id = tk.Label(inner_det, text="",
                                    font=("Segoe UI", 8), bg=C["tarjeta"],
                                    fg=C["texto_muted"])
        self._lbl_det_id.pack(anchor="w")
        self._lbl_det_ubic = tk.Label(inner_det, text="",
                                      font=("Segoe UI", 8), bg=C["tarjeta"],
                                      fg=C["texto_muted"])
        self._lbl_det_ubic.pack(anchor="w")
        self._lbl_det_estado = tk.Label(inner_det, text="",
                                         font=("Segoe UI", 9, "bold"),
                                         bg=C["tarjeta"], fg=C["verde"])
        self._lbl_det_estado.pack(anchor="w", pady=(6, 0))

        # Cargar portada default al inicio
        foto_init = _cargar_foto_portada(None, ancho=180, alto=210)
        if foto_init:
            self._foto_detalle_cat = foto_init
            self._lbl_portada_cat.config(image=foto_init)
        else:
            self._lbl_portada_cat.config(image="", text="📖", font=("Segoe UI", 42), fg=C["acento"])

        # Tabla del catálogo (Se empaqueta DESPUÉS)
        frame_tabla = tk.Frame(frame_body, bg=C["fondo"])
        frame_tabla.pack(side="left", fill="both", expand=True)

        self._estilizar_treeview()
        columnas = ("id", "titulo", "fila", "columna", "estado")
        self.tabla_catalogo = ttk.Treeview(frame_tabla, columns=columnas, show="headings",
                                            height=12, style="Biblio.Treeview")

        self.tabla_catalogo.heading("id", text="ID")
        self.tabla_catalogo.heading("titulo", text="Título")
        self.tabla_catalogo.heading("fila", text="Fila")
        self.tabla_catalogo.heading("columna", text="Columna")
        self.tabla_catalogo.heading("estado", text="Disponibilidad")

        self.tabla_catalogo.column("id", width=80, anchor="center")
        self.tabla_catalogo.column("titulo", width=240, anchor="w")
        self.tabla_catalogo.column("fila", width=55, anchor="center")
        self.tabla_catalogo.column("columna", width=65, anchor="center")
        self.tabla_catalogo.column("estado", width=100, anchor="center")

        self.tabla_catalogo.tag_configure("disponible", foreground=C["verde"])
        self.tabla_catalogo.tag_configure("prestado", foreground=C["rojo"])

        scrollbar_cat = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_catalogo.yview)
        self.tabla_catalogo.configure(yscrollcommand=scrollbar_cat.set)
        self.tabla_catalogo.pack(side="left", fill="both", expand=True)
        scrollbar_cat.pack(side="right", fill="y")


        # Vincular selección en tabla a actualización de panel
        self.tabla_catalogo.bind("<<TreeviewSelect>>", self._actualizar_panel_detalle_cat)

        self._filtrar_catalogo()

    def _actualizar_panel_detalle_cat(self, event=None):
        """Actualiza el panel lateral con los datos del libro seleccionado."""
        seleccion = self.tabla_catalogo.selection()
        if not seleccion:
            return
        valores = self.tabla_catalogo.item(seleccion[0], "values")
        if not valores:
            return
        id_libro, titulo, fila, columna, estado = valores

        # Actualizar textos
        self._lbl_det_titulo.config(text=titulo)
        self._lbl_det_id.config(text=f"ID: {id_libro}")
        self._lbl_det_ubic.config(text=f"📂 Fila {fila}, Columna {columna}")

        if estado == "Disponible":
            self._lbl_det_estado.config(text="✅ Disponible", fg=C["verde"])
        else:
            self._lbl_det_estado.config(text="📕 Prestado", fg=C["rojo"])

        # Portada — los libros físicos usan la portada por defecto
        foto = _cargar_foto_portada(None, ancho=180, alto=210)
        if foto:
            self._foto_detalle_cat = foto
            self._lbl_portada_cat.config(image=foto, text="")
        else:
            self._lbl_portada_cat.config(image="", text="📖",
                                          font=("Segoe UI", 42), fg=C["acento"])

    def _filtrar_catalogo(self):
        placeholder = "Buscar por título o ID..."
        texto = self.ent_busqueda_catalogo.get().strip()
        if texto == placeholder:
            texto = ""
        texto_lower = texto.lower()

        for fila in self.tabla_catalogo.get_children():
            self.tabla_catalogo.delete(fila)

        for lib in lista_libros:
            if texto_lower and texto_lower not in lib["titulo"].lower() and texto_lower not in lib["id"].lower():
                continue

            prestado = PR.prestamo_activo_de(lib["id"])
            estado = "Prestado" if prestado else "Disponible"
            tag = "prestado" if prestado else "disponible"

            self.tabla_catalogo.insert("", "end",
                                       values=(lib["id"], lib["titulo"], lib["f"], lib["c"], estado),
                                       tags=(tag,))


    # =====================================================================
    # 💬 VISTA: BUZÓN DE SUGERENCIAS
    # =====================================================================
    def mostrar_sugerencias(self):
        self.seccion_activa = "sugerencias"
        self._refrescar_botones()
        self.limpiar_contenido()
        self._encabezado("Buzón de sugerencias", "Envía tus ideas o reporta problemas — el administrador los revisará")

        # Formulario
        frame_form = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"])
        frame_form.pack(padx=32, fill="x")
        inner = tk.Frame(frame_form, bg=C["tarjeta"])
        inner.pack(fill="x", padx=18, pady=16)

        tk.Label(inner, text="Escribe tu comentario o sugerencia",
                 font=self.f_seccion, bg=C["tarjeta"], fg=C["marino"]).pack(anchor="w", pady=(0, 10))

        self.txt_sugerencia = tk.Text(
            inner, height=8, font=("Segoe UI", 10), relief="flat",
            bg="#F8F9FA", fg=C["texto"], insertbackground=C["marino"],
            highlightthickness=1, highlightbackground=C["borde"],
            wrap="word", padx=12, pady=10
        )
        self.txt_sugerencia.pack(fill="x")

        # Placeholder
        placeholder_sug = "¿Qué te gustaría mejorar del sistema? ¿Encontraste algún error? Escríbelo aquí..."
        self.txt_sugerencia.insert("1.0", placeholder_sug)
        self.txt_sugerencia.config(fg=C["texto_muted"])

        def al_enfocar_txt(e):
            if self.txt_sugerencia.get("1.0", "end-1c") == placeholder_sug:
                self.txt_sugerencia.delete("1.0", tk.END)
                self.txt_sugerencia.config(fg=C["texto"])

        def al_desenfocar_txt(e):
            if not self.txt_sugerencia.get("1.0", "end-1c").strip():
                self.txt_sugerencia.insert("1.0", placeholder_sug)
                self.txt_sugerencia.config(fg=C["texto_muted"])

        self.txt_sugerencia.bind("<FocusIn>", al_enfocar_txt)
        self.txt_sugerencia.bind("<FocusOut>", al_desenfocar_txt)

        self.lbl_confirmacion = tk.Label(inner, text="", font=("Segoe UI", 9), bg=C["tarjeta"],
                                          fg=C["verde"])
        self.lbl_confirmacion.pack(anchor="w", pady=(8, 0))

        frame_btn = tk.Frame(inner, bg=C["tarjeta"])
        frame_btn.pack(fill="x", pady=(10, 0))

        self._boton_accion(frame_btn, "📤  Enviar sugerencia", C["marino"], C["marino_hover"],
                           self._enviar_sugerencia).pack(side="left")

        # Historial de mis sugerencias
        tk.Label(
            self.area_contenido, text="Mis sugerencias anteriores",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(padx=32, pady=(24, 10), anchor="w")

        comentarios = _cargar_comentarios()
        mis_comentarios = [c for c in comentarios if c.get("usuario") == self.usuario_login]

        frame_hist = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"])
        frame_hist.pack(padx=32, pady=(0, 24), fill="x")
        inner_hist = tk.Frame(frame_hist, bg=C["tarjeta"])
        inner_hist.pack(fill="x", padx=18, pady=14)

        if not mis_comentarios:
            tk.Label(inner_hist, text="No has enviado sugerencias aún.",
                     font=self.f_actividad, bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w")
        else:
            for i, com in enumerate(mis_comentarios[-5:]):
                fila = tk.Frame(inner_hist, bg=C["tarjeta"])
                fila.pack(fill="x", pady=(0 if i == 0 else 6, 0))
                tk.Label(fila, text="💬", bg=C["tarjeta"], font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
                msg_preview = com["mensaje"][:80] + ("..." if len(com["mensaje"]) > 80 else "")
                tk.Label(fila, text=msg_preview, bg=C["tarjeta"], font=self.f_actividad,
                         fg=C["texto"], wraplength=550, justify="left").pack(side="left")
                tk.Label(fila, text=com.get("fecha", ""), bg=C["tarjeta"],
                         font=("Segoe UI", 8), fg=C["texto_muted"]).pack(side="right")

    def _enviar_sugerencia(self):
        placeholder_sug = "¿Qué te gustaría mejorar del sistema? ¿Encontraste algún error? Escríbelo aquí..."
        mensaje = self.txt_sugerencia.get("1.0", "end-1c").strip()

        if not mensaje or mensaje == placeholder_sug:
            self.lbl_confirmacion.config(text="⚠ Escribe algo antes de enviar.", fg=C["rojo"])
            return

        comentarios = _cargar_comentarios()
        comentarios.append({
            "usuario": self.usuario_login,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mensaje": mensaje,
            "leido": False
        })
        _guardar_comentarios(comentarios)

        self.txt_sugerencia.delete("1.0", tk.END)
        self.lbl_confirmacion.config(text="✅ ¡Sugerencia enviada! Gracias por tu retroalimentación.", fg=C["verde"])

    # =====================================================================
    # ⚙️ VISTA: EDICIÓN DE PERFIL
    # =====================================================================
    def mostrar_editar_perfil(self):
        self.seccion_activa = "perfil"
        self._refrescar_botones()
        self.limpiar_contenido()
        self._encabezado("Mi cuenta", "Actualiza tus datos personales")

        datos = _obtener_datos_usuario(self.usuario_login)

        frame_form = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"])
        frame_form.pack(padx=32, fill="x")
        inner = tk.Frame(frame_form, bg=C["tarjeta"])
        inner.pack(fill="x", padx=24, pady=20)

        tk.Label(inner, text=self.usuario_login, font=("Segoe UI", 16, "bold"),
                 bg=C["tarjeta"], fg=C["marino"]).pack(anchor="w")
        tk.Label(inner, text=f"Rol: {datos.get('rol', 'usuario').upper()}", font=("Segoe UI", 9, "italic"),
                 bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 16))

        tk.Frame(inner, bg=C["borde"], height=1).pack(fill="x", pady=(0, 14))

        # --- CAMPOS BLOQUEADOS (solo lectura) ---
        tk.Label(inner, text="🔒  Campos protegidos (no editables)", font=self.f_label,
                 bg=C["tarjeta"], fg=C["rojo"]).pack(anchor="w", pady=(0, 8))

        fila_protegidos = tk.Frame(inner, bg=C["tarjeta"])
        fila_protegidos.pack(fill="x", pady=(0, 14))
        fila_protegidos.columnconfigure(0, weight=1)
        fila_protegidos.columnconfigure(1, weight=1)

        # Correo (disabled)
        col_correo = tk.Frame(fila_protegidos, bg=C["tarjeta"])
        col_correo.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(col_correo, text="Correo electrónico", font=("Segoe UI", 9, "bold"),
                 bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 3))
        ent_correo = tk.Entry(col_correo, font=("Segoe UI", 10), relief="flat",
                              highlightthickness=1, highlightbackground=C["borde"],
                              disabledbackground="#F3F4F6", disabledforeground=C["texto_muted"])
        ent_correo.insert(0, datos.get("correo", "No registrado"))
        ent_correo.config(state="disabled")
        ent_correo.pack(fill="x", ipady=5)

        # Cédula (disabled)
        col_cedula = tk.Frame(fila_protegidos, bg=C["tarjeta"])
        col_cedula.grid(row=0, column=1, sticky="ew")
        tk.Label(col_cedula, text="Cédula / Pasaporte", font=("Segoe UI", 9, "bold"),
                 bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 3))
        ent_cedula = tk.Entry(col_cedula, font=("Segoe UI", 10), relief="flat",
                              highlightthickness=1, highlightbackground=C["borde"],
                              disabledbackground="#F3F4F6", disabledforeground=C["texto_muted"])
        ent_cedula.insert(0, datos.get("cedula", "No registrado"))
        ent_cedula.config(state="disabled")
        ent_cedula.pack(fill="x", ipady=5)

        tk.Frame(inner, bg=C["borde"], height=1).pack(fill="x", pady=(4, 14))

        # --- CAMPOS EDITABLES ---
        tk.Label(inner, text="✏️  Datos editables", font=self.f_label,
                 bg=C["tarjeta"], fg=C["verde"]).pack(anchor="w", pady=(0, 8))

        # Nombre completo
        tk.Label(inner, text="Nombre completo", font=("Segoe UI", 9, "bold"),
                 bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 3))
        self.ent_perfil_nombre = tk.Entry(inner, font=("Segoe UI", 10), relief="flat",
                                          highlightthickness=1, highlightbackground=C["borde"])
        self.ent_perfil_nombre.insert(0, datos.get("nombre", ""))
        self.ent_perfil_nombre.pack(fill="x", ipady=5, pady=(0, 10))

        # Teléfono
        fila_tel_pass = tk.Frame(inner, bg=C["tarjeta"])
        fila_tel_pass.pack(fill="x", pady=(0, 10))
        fila_tel_pass.columnconfigure(0, weight=1)
        fila_tel_pass.columnconfigure(1, weight=1)

        col_tel = tk.Frame(fila_tel_pass, bg=C["tarjeta"])
        col_tel.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(col_tel, text="Teléfono", font=("Segoe UI", 9, "bold"),
                 bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 3))
        self.ent_perfil_tel = tk.Entry(col_tel, font=("Segoe UI", 10), relief="flat",
                                       highlightthickness=1, highlightbackground=C["borde"])
        self.ent_perfil_tel.insert(0, datos.get("telefono", ""))
        self.ent_perfil_tel.pack(fill="x", ipady=5)
        self.ent_perfil_tel.bind("<KeyPress>", _digitos_y_mas)

        # Nueva contraseña
        col_pass = tk.Frame(fila_tel_pass, bg=C["tarjeta"])
        col_pass.grid(row=0, column=1, sticky="ew")
        tk.Label(col_pass, text="Nueva contraseña (dejar vacío para no cambiar)",
                 font=("Segoe UI", 9, "bold"), bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 3))
        self.ent_perfil_pass = tk.Entry(col_pass, font=("Segoe UI", 10), relief="flat",
                                        highlightthickness=1, highlightbackground=C["borde"], show="●")
        self.ent_perfil_pass.pack(fill="x", ipady=5)

        self.lbl_perfil_estado = tk.Label(inner, text="", font=("Segoe UI", 9),
                                           bg=C["tarjeta"], fg=C["rojo"])
        self.lbl_perfil_estado.pack(anchor="w", pady=(8, 0))

        # Botón guardar
        frame_btn = tk.Frame(inner, bg=C["tarjeta"])
        frame_btn.pack(fill="x", pady=(10, 0))

        btn_guardar = tk.Button(
            frame_btn, text="💾  Guardar cambios", command=self._guardar_perfil,
            bg=C["verde"], fg="white", font=self.f_btn,
            padx=20, pady=10, relief="flat", bd=0, cursor="hand2"
        )
        btn_guardar.pack(side="left")
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg=C["verde_hover"]))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg=C["verde"]))

    def _guardar_perfil(self):
        nuevo_nombre = self.ent_perfil_nombre.get().strip()
        nuevo_tel = self.ent_perfil_tel.get().strip()
        nueva_clave = self.ent_perfil_pass.get().strip()

        if not nuevo_nombre:
            self.lbl_perfil_estado.config(text="⚠ El nombre no puede estar vacío.", fg=C["rojo"])
            return

        usuarios = _cargar_usuarios()
        if self.usuario_login not in usuarios:
            self.lbl_perfil_estado.config(text="⚠ Error: tu usuario no se encontró en la base de datos.", fg=C["rojo"])
            return

        usuarios[self.usuario_login]["nombre"] = nuevo_nombre
        usuarios[self.usuario_login]["telefono"] = nuevo_tel
        if nueva_clave:
            if len(nueva_clave) < 4:
                self.lbl_perfil_estado.config(text="⚠ La contraseña debe tener al menos 4 caracteres.", fg=C["rojo"])
                return
            usuarios[self.usuario_login]["clave"] = nueva_clave

        if _guardar_usuarios(usuarios):
            self.nombre_completo = nuevo_nombre
            self.lbl_perfil_estado.config(text="✅ Datos guardados correctamente.", fg=C["verde"])
            messagebox.showinfo("Perfil actualizado", "Tus datos se guardaron exitosamente.")
        else:
            self.lbl_perfil_estado.config(text="⚠ Error al guardar los cambios.", fg=C["rojo"])

    # =====================================================================
    # UTILIDADES
    # =====================================================================
    def _refrescar_botones(self):
        for k, btn in self.botones_menu.items():
            if k == self.seccion_activa:
                btn.config(bg=C["acento"], fg=C["marino"])
            else:
                btn.config(bg=C["marino"], fg=C["blanco"])

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?"):
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.destroy()
            try:
                from main import pantalla_principal
                pantalla_principal(posicion_actual=(x, y))
            except ImportError as e:
                messagebox.showerror("Error", f"No se pudo regresar al menú principal:\n{e}")


# =========================================================================
# PUNTO DE ENTRADA — llamado desde login.py
# =========================================================================
def pantalla_usuario(usuario, posicion_actual=None, nombre=None):
    """
    Parámetros:
        usuario: clave de login (ej. "elias pacheco")
        posicion_actual: tupla (x, y) para abrir la ventana en la misma posición
        nombre: nombre completo a mostrar; si no se pasa, se lee de usuarios.json
    """
    if not nombre:
        datos = _obtener_datos_usuario(usuario)
        nombre = datos.get("nombre", usuario)

    root = tk.Tk()
    if posicion_actual:
        root.geometry(f"+{posicion_actual[0]}+{posicion_actual[1]}")

    VentanaUsuario(root, usuario_login=usuario, nombre_completo=nombre)
    root.mainloop()


# =========================================================================
# Ejecución aislada para pruebas
# =========================================================================
if __name__ == "__main__":
    pantalla_usuario(usuario="elias pacheco", nombre="Estudiante Demo")
