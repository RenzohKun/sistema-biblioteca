import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import json
import os
from datetime import datetime
import sys
try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

# =========================================================================
# RUTAS — resueltas desde la raíz del proyecto, sin importar desde dónde
# se ejecute el script
# =========================================================================
CARPETA_RAIZ        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS       = os.path.join(CARPETA_RAIZ, "datos")
CARPETA_PORTADAS    = os.path.join(CARPETA_DATOS, "portadas")
ARCHIVO_LIBROS      = os.path.join(CARPETA_DATOS, "biblioteca_datos.json")
ARCHIVO_USUARIOS    = os.path.join(CARPETA_DATOS, "usuarios.json")
ARCHIVO_PADRON      = os.path.join(CARPETA_DATOS, "padron_uleam.json")

# ✅ Asegura que la raíz del proyecto esté en el path. Se necesita para poder
# hacer "from main import pantalla_principal" al cerrar sesión, sin importar
# si este archivo se abrió directamente o desde login.py.
if CARPETA_RAIZ not in sys.path:
    sys.path.insert(0, CARPETA_RAIZ)

# =========================================================================
# PORTADA HELPER — carga la portada genérica de libro físico
# =========================================================================
def _foto_portada_fisica(ancho=160, alto=210):
    """Devuelve ImageTk.PhotoImage con la portada default o None."""
    if not _PIL_OK:
        return None
    ruta = os.path.join(CARPETA_PORTADAS, "portada_default.png")
    if not os.path.exists(ruta):
        return None
    try:
        img = Image.open(ruta).resize((ancho, alto), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

MAX_F, MAX_C = 5, 5
lista_libros = []
estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]


# =========================================================================
# 🎨 PALETA — consistente con login / registro / main (marino + dorado)
# =========================================================================
C = {
    "fondo":         "#F0F4F8",
    "tarjeta":       "#FFFFFF",
    "borde":         "#D6DCE4",

    "marino":        "#1B2A4A",
    "marino_hover":  "#243561",
    "marino_claro":  "#2C3E63",   # botones de menú lateral sin seleccionar

    "acento":        "#C8923A",
    "acento_suave":  "#F3E4C8",

    "verde":         "#1A6B45",
    "verde_hover":   "#145739",
    "verde_suave":   "#E3F1E9",

    "rojo":          "#8B1A1A",
    "rojo_hover":    "#6E1515",
    "rojo_suave":    "#F6E3E3",

    "azul_dato":     "#2A5C8A",
    "azul_dato_hover": "#1F4A70",

    "texto":         "#1A1D23",
    "texto_muted":   "#6B7280",
    "blanco":        "#FFFFFF",
}


# =========================================================================
# LÓGICA DE DATOS — libros (persistencia en JSON, no en .js de texto)
# =========================================================================
def cargar_desde_archivo():
    """Carga los libros y reconstruye la matriz de la estantería al iniciar."""
    global lista_libros, estanteria
    lista_libros.clear()
    estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]

    os.makedirs(CARPETA_DATOS, exist_ok=True)

    if not os.path.exists(ARCHIVO_LIBROS):
        return

    try:
        with open(ARCHIVO_LIBROS, "r", encoding="utf-8") as f:
            datos = json.load(f)
            for lib in datos:
                f_, c_ = int(lib["f"]), int(lib["c"])
                if 0 <= f_ < MAX_F and 0 <= c_ < MAX_C:
                    lista_libros.append(lib)
                    estanteria[f_][c_] = lib["id"]
    except Exception as e:
        print(f"Aviso al cargar archivo de libros: {e}")


def guardar_en_archivo():
    """Sincroniza la lista de libros con el archivo físico JSON."""
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_LIBROS, "w", encoding="utf-8") as f:
            json.dump(lista_libros, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudieron guardar los cambios:\n{e}")


def buscar_recursivo(lista, id_buscado, indice=0):
    """Búsqueda recursiva por ID."""
    if indice >= len(lista):
        return None
    if lista[indice]["id"] == id_buscado:
        return lista[indice]
    return buscar_recursivo(lista, id_buscado, indice + 1)


def id_existe(id_lib, excluir_celda=None):
    """Revisa si un ID ya está en uso, sin importar la celda."""
    for lib in lista_libros:
        if lib["id"] == id_lib:
            if excluir_celda and (lib["f"], lib["c"]) == excluir_celda:
                continue
            return True
    return False


def cargar_usuarios():
    """Carga usuarios.json respetando la estructura real:
    { "usuario": {"clave": ..., "rol": ..., "nombre": ...} }
    """
    if not os.path.exists(ARCHIVO_USUARIOS):
        return {}
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Aviso al cargar usuarios: {e}")
        return {}


def cargar_padron():
    """Carga la lista de correos válidos del padrón."""
    if not os.path.exists(ARCHIVO_PADRON):
        return []
    try:
        with open(ARCHIVO_PADRON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Aviso al cargar padrón: {e}")
        return []


def guardar_padron(padron):
    """Guarda la lista de correos en el padrón."""
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_PADRON, "w", encoding="utf-8") as f:
            json.dump(padron, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el padrón:\n{e}")
        return False



def guardar_usuarios(usuarios):
    """Persiste el diccionario completo de usuarios en usuarios.json."""
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudieron guardar los cambios de usuarios:\n{e}")
        return False


ROLES_DISPONIBLES = ["admin", "bibliotecario", "usuario"]


# =========================================================================
# CLASE DE LA INTERFAZ DEL ADMINISTRADOR
# =========================================================================
class VentanaAdministrador:
    def __init__(self, root, nombre_admin="Administrador", usuario_login=None):
        self.root = root
        self.nombre_admin = nombre_admin
        # usuario_login = la clave/usuario con la que inició sesión (para protegerlo
        # de quitarse su propio rol de admin). Si no se provee, se intenta deducir
        # buscando por nombre en usuarios.json.
        self.usuario_login = usuario_login or self._deducir_usuario_login(nombre_admin)
        self.root.title("Sistema de Biblioteca — Panel de Administración")
        self.root.configure(bg=C["fondo"])
        self.root.geometry("1080x680")
        self.root.resizable(True, True)
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"1080x680+{(sw-1080)//2}+{(sh-680)//2}")

        cargar_desde_archivo()

        # Cargar datos de préstamos para el dashboard
        try:
            from logica.prestamos import cargar_prestamos
            cargar_prestamos()
            self._prestamos_disponibles = True
        except ImportError:
            self._prestamos_disponibles = False

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

        # --- CONTENEDORES PRINCIPALES ---
        self.menu_lateral = tk.Frame(self.root, bg=C["marino"], width=230)
        self.menu_lateral.pack(side="left", fill="y")
        self.menu_lateral.pack_propagate(False)

        self.area_contenido = tk.Frame(self.root, bg=C["fondo"])
        self.area_contenido.pack(side="right", fill="both", expand=True)

        # Línea dorada separadora entre menú y contenido
        tk.Frame(self.root, bg=C["acento"], width=3).place(x=230, y=0, relheight=1)

        # --- CABECERA DEL MENÚ ---
        tk.Label(
            self.menu_lateral, text="📚 BIBLIOTECA",
            fg=C["blanco"], bg=C["marino"], font=self.f_logo
        ).pack(pady=(26, 4))

        tk.Frame(self.menu_lateral, bg=C["acento"], height=2, width=120).pack(pady=(0, 16))

        tk.Label(
            self.menu_lateral, text=f"Bienvenido,\n{nombre_admin}",
            bg=C["marino"], font=self.f_bienv, fg="#9FB3CC", justify="center"
        ).pack(pady=(0, 20))

        # --- BOTONES DE NAVEGACIÓN ---
        self.botones_menu = {}
        self._crear_boton_menu("dashboard", "🏠  Inicio / Dashboard", self.mostrar_inicio)
        self._crear_boton_menu("libros",    "📖  Gestión de Libros", self.mostrar_gestion_libros)
        self._crear_boton_menu("matriz",    "🗄  Ver Estantería", self.mostrar_estanteria_matriz)
        self._crear_boton_menu("usuarios",  "👥  Gestión de Usuarios", self.mostrar_gestion_usuarios)
        self._crear_boton_menu("padron",    "🎓  Padrón ULEAM", self.mostrar_padron)
        self._crear_boton_menu("strikes",   "⚠  Strikes", self.mostrar_strikes)
        self._crear_boton_menu("prestamos", "📋  Préstamos Activos", self.mostrar_prestamos_activos)

        btn_logout = tk.Button(
            self.menu_lateral, text="Cerrar sesión", command=self.cerrar_sesion,
            bg=C["rojo"], fg="white", relief="flat", font=self.f_btn,
            bd=0, pady=10, cursor="hand2", activebackground=C["rojo_hover"], activeforeground="white"
        )
        btn_logout.pack(side="bottom", fill="x", padx=18, pady=22)
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg=C["rojo_hover"]))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg=C["rojo"]))

        self.mostrar_inicio()

    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    def _deducir_usuario_login(self, nombre_admin):
        """Si no se pasó el usuario de login explícitamente, intenta
        encontrarlo buscando coincidencia por nombre en usuarios.json."""
        usuarios = cargar_usuarios()
        for usuario, datos in usuarios.items():
            if isinstance(datos, dict) and datos.get("nombre") == nombre_admin:
                return usuario
        return None

    def _crear_boton_menu(self, clave, texto, comando):
        btn = tk.Button(
            self.menu_lateral, text=texto, command=lambda: self._navegar(clave, comando),
            bg=C["marino"], fg=C["blanco"], relief="flat", font=self.f_menu,
            anchor="w", padx=18, pady=11, cursor="hand2", bd=0,
            activebackground=C["marino_claro"], activeforeground="white"
        )
        btn.pack(fill="x", padx=12, pady=3)
        btn.bind("<Enter>", lambda e, b=btn, k=clave: b.config(bg=C["marino_claro"]) if self.seccion_activa != k else None)
        btn.bind("<Leave>", lambda e, b=btn, k=clave: b.config(bg=C["acento"] if self.seccion_activa == k else C["marino"]))
        self.botones_menu[clave] = btn

    def _navegar(self, clave, comando):
        self.seccion_activa = clave
        for k, btn in self.botones_menu.items():
            btn.config(bg=C["acento"], fg=C["marino"]) if k == clave else btn.config(bg=C["marino"], fg=C["blanco"])
        comando()

    seccion_activa = "dashboard"

    def limpiar_contenido(self):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

    def _encabezado(self, titulo, subtitulo):
        """Encabezado consistente para cada vista."""
        wrap = tk.Frame(self.area_contenido, bg=C["fondo"])
        wrap.pack(fill="x", padx=32, pady=(26, 0))
        tk.Label(wrap, text=titulo, font=self.f_titulo, bg=C["fondo"], fg=C["marino"]).pack(anchor="w")
        tk.Frame(wrap, bg=C["acento"], height=2, width=70).pack(anchor="w", pady=(6, 8))
        tk.Label(wrap, text=subtitulo, font=self.f_subtitulo, bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 18))

    # =========================================================================
    # VISTA: INICIO / DASHBOARD
    # =========================================================================
    def mostrar_inicio(self):
        self.limpiar_contenido()
        self._encabezado("Panel de control general", "Estado actual del sistema de biblioteca")

        frame_tarjetas = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas.pack(padx=32, fill="x", anchor="w")
        frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1, uniform="card", minsize=140)

        usuarios = cargar_usuarios()
        total_estudiantes = sum(1 for u in usuarios.values() if u.get("rol") != "admin")
        total_admins = sum(1 for u in usuarios.values() if u.get("rol") == "admin")
        total_libros = len(lista_libros)
        espacios_libres = sum(fila.count("Libre") for fila in estanteria)

        self._tarjeta_dashboard(frame_tarjetas, 0, "📚", "TOTAL LIBROS", total_libros, C["marino"])
        self._tarjeta_dashboard(frame_tarjetas, 1, "👥", "ESTUDIANTES", total_estudiantes, C["verde"])
        self._tarjeta_dashboard(frame_tarjetas, 2, "🪑", "ESPACIOS LIBRES", f"{espacios_libres}/{MAX_F*MAX_C}", C["acento"])

        # Acciones rápidas
        tk.Label(
            self.area_contenido, text="Acciones rápidas",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(36, 14), padx=32, anchor="w")

        frame_acciones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_acciones.pack(padx=32, fill="x", anchor="w")

        self._boton_accion(frame_acciones, "➕  Gestionar catálogo", C["marino"], C["marino_hover"], self.mostrar_gestion_libros).pack(side="left", padx=(0, 14))
        self._boton_accion(frame_acciones, "🗄  Ver mapa estantería", C["acento"], "#B07F2E", self.mostrar_estanteria_matriz).pack(side="left")

        # --- Resumen de strikes y préstamos ---
        total_con_strikes = sum(
            1 for u in usuarios.values()
            if isinstance(u, dict) and u.get("strikes", 0) > 0
        )
        total_bloqueados = sum(
            1 for u in usuarios.values()
            if isinstance(u, dict) and u.get("strikes", 0) >= 4
        )

        total_prestamos = 0
        total_vencidos = 0
        if self._prestamos_disponibles:
            try:
                from logica.prestamos import lista_prestamos
                for p in lista_prestamos:
                    if p.get("estado") in ("activo", "vencido"):
                        total_prestamos += 1
                        if p.get("estado") == "vencido":
                            total_vencidos += 1
            except Exception:
                pass

        tk.Label(
            self.area_contenido, text="Estado de usuarios y préstamos",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(28, 14), padx=32, anchor="w")

        frame_tarjetas2 = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas2.pack(padx=32, fill="x", anchor="w")
        frame_tarjetas2.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card2", minsize=120)

        self._tarjeta_dashboard(frame_tarjetas2, 0, "⚠", "CON STRIKES", total_con_strikes,
                                C["acento"] if total_con_strikes > 0 else C["verde"])
        self._tarjeta_dashboard(frame_tarjetas2, 1, "🚫", "BLOQUEADOS", total_bloqueados,
                                C["rojo"] if total_bloqueados > 0 else C["verde"])
        self._tarjeta_dashboard(frame_tarjetas2, 2, "📖", "PRÉSTAMOS ACTIVOS", total_prestamos, C["azul_dato"])
        self._tarjeta_dashboard(frame_tarjetas2, 3, "🔴", "VENCIDOS", total_vencidos,
                                C["rojo"] if total_vencidos > 0 else C["verde"])

        if total_admins == 0:
            tk.Label(
                self.area_contenido,
                text="⚠ No hay ningún usuario con rol 'admin' registrado.",
                font=self.f_subtitulo, fg=C["rojo"], bg=C["fondo"]
            ).pack(padx=32, pady=(24, 0), anchor="w")

    def _tarjeta_dashboard(self, parent, col, icono, etiqueta, valor, color_valor):
        card = tk.Frame(parent, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        card.grid(row=0, column=col, padx=(0 if col == 0 else 10, 10), sticky="nsew")
        inner = tk.Frame(card, bg=C["tarjeta"])
        inner.pack(fill="both", padx=20, pady=16)
        tk.Label(inner, text=f"{icono}  {etiqueta}", font=self.f_card_lbl, bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w")
        tk.Label(inner, text=str(valor), font=self.f_card_num, bg=C["tarjeta"], fg=color_valor).pack(anchor="w", pady=(6, 0))
        return card

    def _boton_accion(self, parent, texto, color, hover, comando):
        btn = tk.Button(
            parent, text=texto, command=comando, bg=color, fg="white",
            font=self.f_btn, padx=16, pady=10, relief="flat", bd=0, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    # =========================================================================
    # VISTA: STRIKES
    # =========================================================================
    def mostrar_strikes(self):
        self.limpiar_contenido()
        self._encabezado("Control de strikes", "Usuarios con penalizaciones activas en el sistema")

        usuarios = cargar_usuarios()

        # --- Tarjetas resumen ---
        frame_tarjetas = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas.pack(padx=32, fill="x", anchor="w")
        frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1, uniform="card", minsize=140)

        con_strikes = []
        bloqueados = 0
        suspendidos = 0
        for usr, datos in usuarios.items():
            if not isinstance(datos, dict):
                continue
            strikes = datos.get("strikes", 0)
            if strikes and strikes > 0:
                susp = datos.get("suspendido_hasta", None)
                con_strikes.append((usr, datos.get("nombre", "—"),
                                    datos.get("rol", "usuario"), strikes,
                                    datos.get("correo", "—"), susp))
                if strikes >= 4:
                    bloqueados += 1
                elif susp:
                    try:
                        if datetime.now().date() < datetime.strptime(susp, "%Y-%m-%d").date():
                            suspendidos += 1
                    except (ValueError, TypeError):
                        pass

        self._tarjeta_dashboard(frame_tarjetas, 0, "⚠", "CON STRIKES", len(con_strikes), C["acento"])
        self._tarjeta_dashboard(frame_tarjetas, 1, "⏳", "SUSPENDIDOS", suspendidos, C["rojo"])
        self._tarjeta_dashboard(frame_tarjetas, 2, "🚫", "BLOQUEADOS", bloqueados, C["rojo"])

        # --- Tabla de strikes ---
        tk.Label(
            self.area_contenido, text="Detalle de usuarios con strikes",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(28, 14), padx=32, anchor="w")

        if not con_strikes:
            card_vacio = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                                  highlightthickness=1, highlightbackground=C["borde"])
            card_vacio.pack(padx=32, fill="x", pady=(0, 24))
            tk.Label(card_vacio, text="✓ Ningún usuario tiene strikes activos.",
                     font=("Segoe UI", 10, "italic"),
                     bg=C["tarjeta"], fg=C["verde"]).pack(padx=20, pady=24)
            return

        con_strikes.sort(key=lambda x: x[3], reverse=True)

        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()
        cols = ("usuario", "nombre", "rol", "strikes", "correo", "estado")
        self.tabla_strikes = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                          height=15, style="Biblio.Treeview")
        self.tabla_strikes.heading("usuario", text="Usuario")
        self.tabla_strikes.heading("nombre", text="Nombre completo")
        self.tabla_strikes.heading("rol", text="Rol")
        self.tabla_strikes.heading("strikes", text="Strikes")
        self.tabla_strikes.heading("correo", text="Correo")
        self.tabla_strikes.heading("estado", text="Estado")

        self.tabla_strikes.column("usuario", width=130, anchor="center")
        self.tabla_strikes.column("nombre", width=180, anchor="w")
        self.tabla_strikes.column("rol", width=90, anchor="center")
        self.tabla_strikes.column("strikes", width=70, anchor="center")
        self.tabla_strikes.column("correo", width=200, anchor="w")
        self.tabla_strikes.column("estado", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_strikes.yview)
        self.tabla_strikes.configure(yscrollcommand=scrollbar.set)
        self.tabla_strikes.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for usr, nombre, rol, strikes, correo, susp in con_strikes:
            if strikes >= 4:
                estado = "🚫 BLOQUEADO"
            elif susp:
                try:
                    fecha_susp = datetime.strptime(susp, "%Y-%m-%d").date()
                    if datetime.now().date() < fecha_susp:
                        estado = f"⏳ Hasta {susp}"
                    else:
                        estado = "⚠ Con strikes"
                except (ValueError, TypeError):
                    estado = "⚠ Con strikes"
            else:
                estado = "⚠ Con strikes"

            self.tabla_strikes.insert("", "end",
                values=(usr, nombre, rol.upper(), f"{strikes}/3", correo, estado))

    # =========================================================================
    # VISTA: PRÉSTAMOS ACTIVOS
    # =========================================================================
    def mostrar_prestamos_activos(self):
        self.limpiar_contenido()
        self._encabezado("Préstamos activos", "Libros actualmente prestados a usuarios del sistema")

        # Recargar préstamos
        if self._prestamos_disponibles:
            try:
                from logica.prestamos import cargar_prestamos
                cargar_prestamos()
            except Exception:
                pass

        # --- Recopilar préstamos activos ---
        prestamos_activos = []
        total_vencidos = 0
        if self._prestamos_disponibles:
            try:
                from logica.prestamos import lista_prestamos
                for p in lista_prestamos:
                    if p.get("estado") in ("activo", "vencido"):
                        usr = p.get("usuario", "—")
                        id_libro = p.get("id_libro", "—")
                        fecha_prest = p.get("fecha_prestamo", "—")
                        fecha_lim = p.get("fecha_limite", "—")
                        estado = p.get("estado", "activo")

                        # Buscar título del libro
                        titulo_libro = id_libro
                        for lib in lista_libros:
                            if lib["id"] == id_libro:
                                titulo_libro = lib["titulo"]
                                break

                        prestamos_activos.append((usr, id_libro, titulo_libro,
                                                  fecha_prest, fecha_lim, estado))
                        if estado == "vencido":
                            total_vencidos += 1
            except Exception:
                pass

        # --- Tarjetas resumen ---
        frame_tarjetas = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas.pack(padx=32, fill="x", anchor="w")
        frame_tarjetas.grid_columnconfigure((0, 1, 2), weight=1, uniform="card", minsize=140)

        self._tarjeta_dashboard(frame_tarjetas, 0, "📖", "PRÉSTAMOS ACTIVOS", len(prestamos_activos), C["azul_dato"])
        self._tarjeta_dashboard(frame_tarjetas, 1, "🟢", "AL DÍA", len(prestamos_activos) - total_vencidos, C["verde"])
        self._tarjeta_dashboard(frame_tarjetas, 2, "🔴", "VENCIDOS", total_vencidos, C["rojo"])

        # --- Tabla de préstamos ---
        tk.Label(
            self.area_contenido, text="Detalle de préstamos",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(28, 14), padx=32, anchor="w")

        if not prestamos_activos:
            card_vacio = tk.Frame(self.area_contenido, bg=C["tarjeta"],
                                  highlightthickness=1, highlightbackground=C["borde"])
            card_vacio.pack(padx=32, fill="x", pady=(0, 24))
            tk.Label(card_vacio, text="✓ No hay préstamos activos en este momento.",
                     font=("Segoe UI", 10, "italic"),
                     bg=C["tarjeta"], fg=C["verde"]).pack(padx=20, pady=24)
            return

        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()
        cols = ("usuario", "id_libro", "titulo", "fecha_prestamo", "fecha_limite", "estado")
        self.tabla_prestamos = ttk.Treeview(frame_tabla, columns=cols, show="headings",
                                             height=15, style="Biblio.Treeview")
        self.tabla_prestamos.heading("usuario", text="Usuario")
        self.tabla_prestamos.heading("id_libro", text="ID Libro")
        self.tabla_prestamos.heading("titulo", text="Título")
        self.tabla_prestamos.heading("fecha_prestamo", text="Fecha préstamo")
        self.tabla_prestamos.heading("fecha_limite", text="Fecha límite")
        self.tabla_prestamos.heading("estado", text="Estado")

        self.tabla_prestamos.column("usuario", width=120, anchor="center")
        self.tabla_prestamos.column("id_libro", width=80, anchor="center")
        self.tabla_prestamos.column("titulo", width=200, anchor="w")
        self.tabla_prestamos.column("fecha_prestamo", width=110, anchor="center")
        self.tabla_prestamos.column("fecha_limite", width=110, anchor="center")
        self.tabla_prestamos.column("estado", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_prestamos.yview)
        self.tabla_prestamos.configure(yscrollcommand=scrollbar.set)
        self.tabla_prestamos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for usr, id_libro, titulo, fecha_prest, fecha_lim, estado in prestamos_activos:
            if estado == "vencido":
                estado_txt = "🔴 VENCIDO"
            else:
                estado_txt = "🟢 Activo"
            self.tabla_prestamos.insert("", "end",
                values=(usr, id_libro, titulo, fecha_prest, fecha_lim, estado_txt))


    # =========================================================================
    # VISTA: PADRÓN ULEAM
    # =========================================================================
    def mostrar_padron(self):
        self.limpiar_contenido()
        self._encabezado("Gestión del Padrón Universitario", "Añade o elimina correos válidos para el registro de estudiantes")

        padron = cargar_padron()

        # --- Controles de adición ---
        frame_controles = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_controles.pack(padx=32, pady=(0, 14), fill="x")

        tk.Label(frame_controles, text="Nuevo correo:", font=self.f_subtitulo, bg=C["fondo"], fg=C["marino"]).pack(side="left", padx=(0, 10))
        self.ent_nuevo_correo = tk.Entry(frame_controles, font=("Segoe UI", 11), width=35,
                                         bg=C["tarjeta"], fg=C["marino"],
                                         highlightthickness=1, highlightbackground=C["borde"], highlightcolor=C["acento"])
        self.ent_nuevo_correo.pack(side="left", padx=(0, 10), ipady=4)

        self._boton_accion(frame_controles, "➕ Añadir al padrón", C["verde"], "#218c53", self._agregar_al_padron).pack(side="left")
        self._boton_accion(frame_controles, "🗑 Eliminar seleccionado", C["rojo"], C["rojo_hover"], self._eliminar_del_padron).pack(side="left", padx=(10, 0))

        # --- Tabla ---
        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()
        self.tabla_padron = ttk.Treeview(frame_tabla, columns=("correo",), show="headings", height=15, style="Biblio.Treeview")
        self.tabla_padron.heading("correo", text="Correo Institucional")
        self.tabla_padron.column("correo", width=500, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_padron.yview)
        self.tabla_padron.configure(yscrollcommand=scrollbar.set)
        self.tabla_padron.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.actualizar_tabla_padron()

    def actualizar_tabla_padron(self):
        for fila in self.tabla_padron.get_children():
            self.tabla_padron.delete(fila)
        padron = cargar_padron()
        padron.sort()
        for correo in padron:
            self.tabla_padron.insert("", "end", values=(correo,))

    def _agregar_al_padron(self):
        correo = self.ent_nuevo_correo.get().strip().lower()
        if not correo:
            messagebox.showwarning("Atención", "Escribe un correo institucional válido.")
            return
        if not (correo.endswith("@live.uleam.edu.ec") or correo.endswith("@uleam.edu.ec")):
            messagebox.showwarning("Dominio inválido", "Solo se admiten dominios @live.uleam.edu.ec o @uleam.edu.ec")
            return

        padron = cargar_padron()
        if correo in padron:
            messagebox.showinfo("Duplicado", "Ese correo ya está registrado en el padrón.")
            return

        padron.append(correo)
        if guardar_padron(padron):
            self.ent_nuevo_correo.delete(0, tk.END)
            self.actualizar_tabla_padron()
            messagebox.showinfo("Éxito", f"Correo '{correo}' añadido al padrón universitario.")

    def _eliminar_del_padron(self):
        seleccion = self.tabla_padron.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un correo de la lista para eliminar.")
            return

        correo = self.tabla_padron.item(seleccion[0], "values")[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{correo}' del padrón?\n\nLos usuarios con este correo ya registrados seguirán funcionando, pero nadie podrá crear cuentas nuevas con él."):
            padron = cargar_padron()
            if correo in padron:
                padron.remove(correo)
                guardar_padron(padron)
                self.actualizar_tabla_padron()
                messagebox.showinfo("Eliminado", "Correo eliminado del padrón.")
    # =========================================================================
    def mostrar_gestion_libros(self):
        self.limpiar_contenido()
        self._encabezado("Administración del catálogo", "Registra, busca y elimina libros del inventario")

        # --- Formulario ---
        frame_formulario = tk.Frame(self.area_contenido, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        frame_formulario.pack(padx=32, pady=(0, 14), fill="x")

        inner_form = tk.Frame(frame_formulario, bg=C["tarjeta"])
        inner_form.pack(fill="x", padx=18, pady=16)
        inner_form.columnconfigure(0, weight=1)
        inner_form.columnconfigure(1, weight=3)
        inner_form.columnconfigure(2, weight=1)
        inner_form.columnconfigure(3, weight=1)

        tk.Label(inner_form, text="Registrar o buscar libro", font=self.f_label, bg=C["tarjeta"], fg=C["marino"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 10)
        )

        tk.Label(inner_form, text="ID Libro", font=self.f_label, bg=C["tarjeta"], fg=C["texto_muted"]).grid(row=1, column=0, padx=(0, 6), sticky="w")
        self.ent_id = tk.Entry(inner_form, relief="flat", highlightthickness=1, highlightbackground=C["borde"], font=("Segoe UI", 10))
        self.ent_id.grid(row=2, column=0, padx=(0, 14), pady=(2, 8), sticky="ew", ipady=4)

        tk.Label(inner_form, text="Título", font=self.f_label, bg=C["tarjeta"], fg=C["texto_muted"]).grid(row=1, column=1, padx=(0, 6), sticky="w")
        self.ent_titulo = tk.Entry(inner_form, relief="flat", highlightthickness=1, highlightbackground=C["borde"], font=("Segoe UI", 10))
        self.ent_titulo.grid(row=2, column=1, padx=(0, 14), pady=(2, 8), sticky="ew", ipady=4)

        tk.Label(inner_form, text="Fila (0-4)", font=self.f_label, bg=C["tarjeta"], fg=C["texto_muted"]).grid(row=1, column=2, padx=(0, 6), sticky="w")
        self.ent_f = tk.Entry(inner_form, width=8, relief="flat", highlightthickness=1, highlightbackground=C["borde"], font=("Segoe UI", 10))
        self.ent_f.grid(row=2, column=2, padx=(0, 14), pady=(2, 8), sticky="ew", ipady=4)

        tk.Label(inner_form, text="Columna (0-4)", font=self.f_label, bg=C["tarjeta"], fg=C["texto_muted"]).grid(row=1, column=3, padx=(0, 6), sticky="w")
        self.ent_c = tk.Entry(inner_form, width=8, relief="flat", highlightthickness=1, highlightbackground=C["borde"], font=("Segoe UI", 10))
        self.ent_c.grid(row=2, column=3, pady=(2, 8), sticky="ew", ipady=4)

        # --- Botones operativos ---
        frame_botones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_botones.pack(padx=32, pady=(0, 14), fill="x")

        self._boton_accion(frame_botones, "➕  Registrar posición", C["verde"], C["verde_hover"], self.registrar_libro_logica).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "🔍  Búsqueda recursiva", C["azul_dato"], C["azul_dato_hover"], self.ejecutar_busqueda_recursiva).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "🗑  Remover del catálogo", C["rojo"], C["rojo_hover"], self.eliminar_libro_logica).pack(side="left")

        # --- LAYOUT HORIZONTAL: tabla + panel detalle derecho ---
        frame_cuerpo = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_cuerpo.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        # --- PANEL DETALLE DERECHO CON PORTADA (va primero para reservar espacio) ---
        panel_det = tk.Frame(frame_cuerpo, bg=C["tarjeta"],
                             highlightthickness=1, highlightbackground=C["borde"],
                             width=210)
        panel_det.pack(side="right", fill="y", padx=(12, 0))
        panel_det.pack_propagate(False)

        self._foto_admin_libros = None
        self._lbl_portada_admin = tk.Label(panel_det, bg=C["marino"])
        self._lbl_portada_admin.pack(fill="x")

        inner_det_admin = tk.Frame(panel_det, bg=C["tarjeta"])
        inner_det_admin.pack(fill="both", expand=True, padx=10, pady=10)

        self._lbl_adm_titulo = tk.Label(inner_det_admin, text="Selecciona un libro",
                                         font=("Segoe UI", 9, "bold"),
                                         bg=C["tarjeta"], fg=C["marino"],
                                         wraplength=180, justify="left")
        self._lbl_adm_titulo.pack(anchor="w", pady=(0, 4))
        self._lbl_adm_id = tk.Label(inner_det_admin, text="", font=("Segoe UI", 8),
                                    bg=C["tarjeta"], fg=C["texto_muted"])
        self._lbl_adm_id.pack(anchor="w")
        self._lbl_adm_ubic = tk.Label(inner_det_admin, text="", font=("Segoe UI", 8),
                                      bg=C["tarjeta"], fg=C["texto_muted"])
        self._lbl_adm_ubic.pack(anchor="w")

        # Portada inicial (default)
        foto0 = _foto_portada_fisica(ancho=190, alto=220)
        if foto0:
            self._foto_admin_libros = foto0
            self._lbl_portada_admin.config(image=foto0)
        else:
            self._lbl_portada_admin.config(text="📖", font=("Segoe UI", 46), fg=C["acento"])

        # Tabla (va después del panel para ocupar el espacio restante)
        frame_tabla = tk.Frame(frame_cuerpo, bg=C["fondo"])
        frame_tabla.pack(side="left", fill="both", expand=True)

        self._estilizar_treeview()

        columnas = ("id", "titulo", "fila", "columna")
        self.tabla_libros = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8, style="Biblio.Treeview")

        self.tabla_libros.heading("id", text="ID Libro")
        self.tabla_libros.heading("titulo", text="Título de la obra")
        self.tabla_libros.heading("fila", text="Fila")
        self.tabla_libros.heading("columna", text="Columna")

        self.tabla_libros.column("id", width=110, anchor="center")
        self.tabla_libros.column("titulo", width=280, anchor="w")
        self.tabla_libros.column("fila", width=80, anchor="center")
        self.tabla_libros.column("columna", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_libros.yview)
        self.tabla_libros.configure(yscrollcommand=scrollbar.set)
        self.tabla_libros.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _al_seleccionar_libro(event):
            sel = self.tabla_libros.selection()
            if not sel:
                return
            vals = self.tabla_libros.item(sel[0], "values")
            if not vals:
                return
            id_l, tit, f_, c_ = vals
            self._lbl_adm_titulo.config(text=tit)
            self._lbl_adm_id.config(text=f"ID: {id_l}")
            self._lbl_adm_ubic.config(text=f"📂 Fila {f_}, Columna {c_}")
            foto = _foto_portada_fisica(ancho=190, alto=220)
            if foto:
                self._foto_admin_libros = foto
                self._lbl_portada_admin.config(image=foto, text="")

        self.tabla_libros.bind("<<TreeviewSelect>>", _al_seleccionar_libro)

        self.actualizar_tabla_libros()


    def _estilizar_treeview(self):
        """Aplica estilo ttk consistente con la paleta marino/dorado."""
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
        style.map("Biblio.Treeview", background=[("selected", C["acento_suave"])], foreground=[("selected", C["texto"])])

    def actualizar_tabla_libros(self):
        for fila in self.tabla_libros.get_children():
            self.tabla_libros.delete(fila)
        for lib in lista_libros:
            self.tabla_libros.insert("", "end", values=(lib["id"], lib["titulo"], lib["f"], lib["c"]))

    def registrar_libro_logica(self):
        id_lib = self.ent_id.get().strip()
        titulo = self.ent_titulo.get().strip()
        fila_raw = self.ent_f.get().strip()
        col_raw = self.ent_c.get().strip()

        if not id_lib or not titulo:
            messagebox.showerror("Error", "ID y título son obligatorios.")
            return

        try:
            f, c = int(fila_raw), int(col_raw)
            if not (0 <= f < MAX_F) or not (0 <= c < MAX_C):
                raise IndexError(f"La ubicación debe estar entre 0 y {MAX_F - 1} (fila) y 0 y {MAX_C - 1} (columna).")

            if estanteria[f][c] != "Libre":
                messagebox.showwarning("Atención", f"El cuadrante [{f}][{c}] ya tiene el libro ID: {estanteria[f][c]}.")
                return

            if id_existe(id_lib):
                messagebox.showwarning("ID duplicado", f"Ya existe un libro registrado con el ID '{id_lib}'.")
                return

            lista_libros.append({"id": id_lib, "titulo": titulo, "f": f, "c": c})
            estanteria[f][c] = id_lib
            guardar_en_archivo()

            messagebox.showinfo("Éxito", f"Libro '{titulo}' indexado en el cuadrante [{f}][{c}].")
            self.actualizar_tabla_libros()

            self.ent_id.delete(0, tk.END)
            self.ent_titulo.delete(0, tk.END)
            self.ent_f.delete(0, tk.END)
            self.ent_c.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error de entrada", "Fila y columna deben ser números enteros.")
        except IndexError as e:
            messagebox.showerror("Índice inválido", str(e))

    def ejecutar_busqueda_recursiva(self):
        id_buscar = self.ent_id.get().strip()
        if not id_buscar:
            messagebox.showwarning("Búsqueda", "Escribe un ID de libro en el campo superior para buscar.")
            return

        resultado = buscar_recursivo(lista_libros, id_buscar)
        if resultado:
            messagebox.showinfo(
                "Resultado de la búsqueda",
                f"Título: {resultado['titulo']}\nUbicación: Fila {resultado['f']}, Columna {resultado['c']}"
            )
        else:
            messagebox.showwarning("Búsqueda", f"El ID '{id_buscar}' no coincide con ningún registro.")

    def eliminar_libro_logica(self):
        seleccion = self.tabla_libros.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una fila del catálogo para eliminar.")
            return

        valores = self.tabla_libros.item(seleccion, "values")
        id_eliminar = valores[0]
        titulo_eliminar = valores[1]
        f_eliminar = int(valores[2])
        c_eliminar = int(valores[3])

        if messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente '{titulo_eliminar}'?"):
            global lista_libros
            lista_libros = [lib for lib in lista_libros if lib["id"] != id_eliminar]
            estanteria[f_eliminar][c_eliminar] = "Libre"
            guardar_en_archivo()
            self.actualizar_tabla_libros()
            messagebox.showinfo("Listo", "El libro fue eliminado y el espacio quedó libre.")

    # =========================================================================
    # VISTA: ESTANTERÍA (Matriz)
    # =========================================================================
    def mostrar_estanteria_matriz(self):
        self.limpiar_contenido()
        self._encabezado("Mapa de distribución física", f"Estado en tiempo real de la estantería ({MAX_F}×{MAX_C})")

        # Leyenda
        frame_leyenda = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_leyenda.pack(padx=32, pady=(0, 16), anchor="w")
        self._leyenda(frame_leyenda, C["verde"], "Libre")
        self._leyenda(frame_leyenda, C["rojo"], "Ocupado")

        fr_matriz = tk.Frame(self.area_contenido, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        fr_matriz.pack(padx=32, pady=(0, 24), anchor="center")

        grid_inner = tk.Frame(fr_matriz, bg=C["tarjeta"])
        grid_inner.pack(padx=18, pady=18)

        for r in range(MAX_F):
            for c in range(MAX_C):
                contenido_celda = estanteria[r][c]

                if contenido_celda == "Libre":
                    bg_color = C["verde_suave"]
                    fg_color = C["verde"]
                    texto_celda = "Libre"
                else:
                    bg_color = C["rojo_suave"]
                    fg_color = C["rojo"]
                    texto_celda = f"ID: {contenido_celda}"

                celda = tk.Frame(grid_inner, bg=bg_color, highlightthickness=1, highlightbackground=C["borde"], width=130, height=70)
                celda.grid(row=r, column=c, padx=4, pady=4)
                celda.pack_propagate(False)

                tk.Label(celda, text=f"[{r}][{c}]", font=("Segoe UI", 8), bg=bg_color, fg=C["texto_muted"]).pack(pady=(8, 2))
                tk.Label(celda, text=texto_celda, font=("Segoe UI", 9, "bold"), bg=bg_color, fg=fg_color,
                         wraplength=120, justify="center").pack(padx=4)

    def _leyenda(self, parent, color, texto):
        wrap = tk.Frame(parent, bg=C["fondo"])
        wrap.pack(side="left", padx=(0, 18))
        tk.Frame(wrap, bg=color, width=14, height=14).pack(side="left", padx=(0, 6))
        tk.Label(wrap, text=texto, font=("Segoe UI", 9), bg=C["fondo"], fg=C["texto_muted"]).pack(side="left")

    # =========================================================================
    # VISTA: GESTIÓN DE USUARIOS
    # =========================================================================
    def mostrar_gestion_usuarios(self):
        self.limpiar_contenido()
        self._encabezado("Control de usuarios", "Gestiona roles, datos y acceso de los usuarios del sistema")

        # --- Botones de acción ---
        frame_botones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_botones.pack(padx=32, pady=(0, 14), fill="x")

        self._boton_accion(frame_botones, "✏️  Editar usuario", C["azul_dato"], C["azul_dato_hover"], self.editar_usuario_seleccionado).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "🗑  Eliminar usuario", C["rojo"], C["rojo_hover"], self.eliminar_usuario_seleccionado).pack(side="left")

        tk.Label(
            frame_botones, text="Doble clic en una fila para editar rápidamente",
            font=("Segoe UI", 8, "italic"), bg=C["fondo"], fg=C["texto_muted"]
        ).pack(side="left", padx=(16, 0))

        # --- Tabla ---
        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()

        columnas = ("usuario", "nombre", "correo", "rol")
        self.tabla_usuarios = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15, style="Biblio.Treeview")

        self.tabla_usuarios.heading("usuario", text="Nombre de usuario")
        self.tabla_usuarios.heading("nombre", text="Nombre completo")
        self.tabla_usuarios.heading("correo", text="Correo")
        self.tabla_usuarios.heading("rol", text="Rol")
        self.tabla_usuarios.column("usuario", width=160, anchor="center")
        self.tabla_usuarios.column("nombre", width=200, anchor="w")
        self.tabla_usuarios.column("correo", width=220, anchor="w")
        self.tabla_usuarios.column("rol", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_usuarios.yview)
        self.tabla_usuarios.configure(yscrollcommand=scrollbar.set)
        self.tabla_usuarios.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabla_usuarios.bind("<Double-1>", lambda e: self.editar_usuario_seleccionado())

        self.actualizar_tabla_usuarios()

    def actualizar_tabla_usuarios(self):
        for fila in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(fila)

        usuarios = cargar_usuarios()
        if not usuarios:
            return

        for usuario, datos in usuarios.items():
            nombre = datos.get("nombre", "—") if isinstance(datos, dict) else "—"
            correo = datos.get("correo", "—") if isinstance(datos, dict) else "—"
            rol = datos.get("rol", "usuario") if isinstance(datos, dict) else "usuario"
            self.tabla_usuarios.insert("", "end", values=(usuario, nombre, correo, rol.upper()))

    def editar_usuario_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un usuario de la tabla para editar.")
            return

        valores = self.tabla_usuarios.item(seleccion, "values")
        usuario_clave = valores[0]
        self._abrir_modal_editar_usuario(usuario_clave)

    def eliminar_usuario_seleccionado(self):
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un usuario de la tabla para eliminar.")
            return

        valores = self.tabla_usuarios.item(seleccion, "values")
        usuario_clave = valores[0]

        if self.usuario_login and usuario_clave == self.usuario_login:
            messagebox.showerror("Acción no permitida", "No puedes eliminar tu propia cuenta mientras tienes la sesión activa.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente al usuario '{usuario_clave}'?"):
            return

        usuarios = cargar_usuarios()
        if usuario_clave in usuarios:
            del usuarios[usuario_clave]
            if guardar_usuarios(usuarios):
                messagebox.showinfo("Listo", f"El usuario '{usuario_clave}' fue eliminado.")
                self.actualizar_tabla_usuarios()

    def _abrir_modal_editar_usuario(self, usuario_clave):
        """Ventana modal para editar nombre, rol y contraseña de un usuario."""
        usuarios = cargar_usuarios()
        datos = usuarios.get(usuario_clave)
        if not isinstance(datos, dict):
            messagebox.showerror("Error", "No se encontraron datos válidos para este usuario.")
            return

        es_uno_mismo = bool(self.usuario_login) and usuario_clave == self.usuario_login

        modal = tk.Toplevel(self.root)
        modal.title(f"Editar usuario — {usuario_clave}")
        modal.configure(bg=C["fondo"])
        modal.resizable(True, True)
        modal.transient(self.root)
        modal.grab_set()

        ancho, alto = 380, 420
        modal.geometry(f"{ancho}x{alto}")
        modal.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (ancho // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (alto // 2)
        modal.geometry(f"+{x}+{y}")

        # Cabecera
        tk.Frame(modal, bg=C["marino"], height=6).pack(fill="x")
        tk.Frame(modal, bg=C["acento"], height=3).pack(fill="x")

        inner = tk.Frame(modal, bg=C["fondo"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(inner, text=usuario_clave, font=("Segoe UI", 14, "bold"), bg=C["fondo"], fg=C["marino"]).pack(anchor="w")
        tk.Label(inner, text="Editar datos del usuario", font=("Segoe UI", 9, "italic"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w", pady=(0, 16))

        # Nombre completo
        tk.Label(inner, text="Nombre completo", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_nombre = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_nombre.insert(0, datos.get("nombre", ""))
        ent_nombre.pack(fill="x", ipady=5, pady=(2, 14))

        # Rol
        tk.Label(inner, text="Rol", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        combo_rol = ttk.Combobox(inner, values=ROLES_DISPONIBLES, state="readonly", font=("Segoe UI", 10))
        combo_rol.set(datos.get("rol", "usuario"))
        combo_rol.pack(fill="x", pady=(2, 4))

        if es_uno_mismo:
            combo_rol.configure(state="disabled")
            tk.Label(
                inner, text="⚠ No puedes cambiar tu propio rol de administrador.",
                font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"], wraplength=320, justify="left"
            ).pack(anchor="w", pady=(0, 10))
        else:
            tk.Frame(inner, bg=C["fondo"], height=10).pack()

        # Nueva contraseña (opcional)
        tk.Label(inner, text="Nueva contraseña (déjalo vacío para no cambiarla)", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_clave = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"], show="●")
        ent_clave.pack(fill="x", ipady=5, pady=(2, 18))

        lbl_estado = tk.Label(inner, text="", font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"])
        lbl_estado.pack(anchor="w", pady=(0, 8))

        def guardar_cambios():
            nuevo_nombre = ent_nombre.get().strip()
            nuevo_rol = combo_rol.get().strip()
            nueva_clave = ent_clave.get().strip()

            if not nuevo_nombre:
                lbl_estado.config(text="⚠ El nombre completo no puede estar vacío.")
                return

            if nuevo_rol not in ROLES_DISPONIBLES:
                lbl_estado.config(text="⚠ Selecciona un rol válido.")
                return

            usuarios_actuales = cargar_usuarios()
            if usuario_clave not in usuarios_actuales:
                lbl_estado.config(text="⚠ Este usuario ya no existe.")
                return

            # Protección: no permitir que el propio admin se quite el rol admin
            if es_uno_mismo and nuevo_rol != "admin":
                lbl_estado.config(text="⚠ No puedes cambiarte tu propio rol de admin.")
                return

            usuarios_actuales[usuario_clave]["nombre"] = nuevo_nombre
            usuarios_actuales[usuario_clave]["rol"] = nuevo_rol
            if nueva_clave:
                usuarios_actuales[usuario_clave]["clave"] = nueva_clave

            if guardar_usuarios(usuarios_actuales):
                messagebox.showinfo("Guardado", f"Los datos de '{usuario_clave}' se actualizaron correctamente.")
                modal.destroy()
                self.actualizar_tabla_usuarios()
                if usuario_clave == self.usuario_login:
                    self.nombre_admin = nuevo_nombre

        frame_modal_btns = tk.Frame(inner, bg=C["fondo"])
        frame_modal_btns.pack(fill="x", side="bottom")

        btn_guardar = tk.Button(
            frame_modal_btns, text="Guardar cambios", command=guardar_cambios,
            bg=C["verde"], fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0, pady=9, cursor="hand2"
        )
        btn_guardar.pack(fill="x", pady=(0, 8))
        btn_guardar.bind("<Enter>", lambda e: btn_guardar.config(bg=C["verde_hover"]))
        btn_guardar.bind("<Leave>", lambda e: btn_guardar.config(bg=C["verde"]))

        btn_cancelar = tk.Button(
            frame_modal_btns, text="Cancelar", command=modal.destroy,
            bg=C["tarjeta"], fg=C["texto_muted"], font=("Segoe UI", 9),
            relief="flat", bd=0, pady=8, cursor="hand2",
            highlightthickness=1, highlightbackground=C["borde"]
        )
        btn_cancelar.pack(fill="x")

    # ---------------------------------------------------------------
    # ✅ CORREGIDO: antes intentaba usar una variable global "root" que no
    # existe cuando este panel se abre desde login.py (solo existía si se
    # ejecutaba Admin.py directo), lo cual provocaba un NameError.
    # Ahora destruye esta ventana y abre limpiamente pantalla_principal()
    # de main.py, igual que hace "Volver al menú principal" en login.py.
    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres salir?"):
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.destroy()
            try:
                from main import pantalla_principal
                pantalla_principal(posicion_actual=(x, y))
            except ImportError as e:
                messagebox.showerror("Error de importación", f"No se pudo regresar al menú principal:\n{e}")


# =========================================================================
# Ejecución aislada para pruebas
# =========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaAdministrador(root, "admin")
    root.mainloop()