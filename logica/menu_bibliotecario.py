import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import os
import sys
import json
from datetime import datetime
try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

# ✅ Igual que en login.py: asegura que la raíz del proyecto esté en el path,
# así este archivo funciona tanto importado desde login.py como ejecutado
# directamente (clic en ▶ desde el editor).
CARPETA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CARPETA_RAIZ not in sys.path:
    sys.path.insert(0, CARPETA_RAIZ)

CARPETA_DATOS         = os.path.join(CARPETA_RAIZ, "datos")
CARPETA_PORTADAS      = os.path.join(CARPETA_DATOS, "portadas")
ARCHIVO_LIBRERIA_DIG  = os.path.join(CARPETA_DATOS, "libreria_digital.json")

CATEGORIAS_DISPONIBLES = [
    "Programación", "Bases de Datos", "Algoritmos",
    "Redes", "Ingeniería de Software", "Matemáticas",
    "Otra",
]

_PORTADA_CATEGORIA = {
    "Programación":           "portada_programacion.png",
    "Bases de Datos":         "portada_basesdatos.png",
    "Algoritmos":             "portada_algoritmos.png",
    "Redes":                  "portada_redes.png",
    "Ingeniería de Software": "portada_software.png",
    "Matemáticas":           "portada_matematicas.png",
}

def _cargar_lib_digital():
    if not os.path.exists(ARCHIVO_LIBRERIA_DIG):
        return []
    try:
        with open(ARCHIVO_LIBRERIA_DIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _guardar_lib_digital(recursos):
    try:
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        with open(ARCHIVO_LIBRERIA_DIG, "w", encoding="utf-8") as f:
            json.dump(recursos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la librería digital:\n{e}")
        return False

def _foto_portada_cat(categoria, ancho=120, alto=160):
    """Devuelve ImageTk.PhotoImage según categoría, o None si no disponible."""
    if not _PIL_OK:
        return None
    nombre = _PORTADA_CATEGORIA.get(categoria, "portada_default.png")
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


# Reutilizamos toda la lógica de datos, paleta y estilo ya construida para el
# panel de administrador: cargar/guardar libros, búsqueda recursiva, estilos
# de Treeview, etc. El bibliotecario es una versión recortada del mismo panel.
from presentacion.Admin import (
    VentanaAdministrador,
    cargar_desde_archivo,
    buscar_recursivo,
    C,
)

# Módulo de préstamos y reservas, vive en la carpeta "logica" junto a este archivo.
from logica import Prestamos as PR


class VentanaBibliotecario(VentanaAdministrador):
    """
    Panel de bibliotecario: mismas funciones de gestión de libros que el
    administrador (registrar, buscar, eliminar, ver estantería), SIN
    acceso a Gestión de Usuarios, MÁS el nuevo módulo de movimiento diario
    (préstamos, devoluciones y reservas) que es el trabajo real del rol.
    """

    def __init__(self, root, nombre_bibliotecario="Bibliotecario", usuario_login=None):
        # Nota: no llamamos a super().__init__() directamente porque ese
        # constructor crea el botón de menú "Gestión de Usuarios" y un
        # dashboard distinto. En su lugar, replicamos su flujo con el menú
        # lateral recortado y un dashboard propio (ver mostrar_inicio).
        self.root = root
        self.nombre_bibliotecario = nombre_bibliotecario
        self.usuario_login = usuario_login

        self.root.title("Sistema de Biblioteca — Panel de Bibliotecario")
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

        # --- FUENTES (idénticas al panel admin + algunas nuevas para alertas) ---
        self.f_logo      = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        self.f_bienv     = tkfont.Font(family="Segoe UI", size=10, slant="italic")
        self.f_menu      = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_titulo    = tkfont.Font(family="Segoe UI", size=19, weight="bold")
        self.f_subtitulo = tkfont.Font(family="Segoe UI", size=10)
        self.f_card_lbl  = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.f_card_num  = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        self.f_seccion   = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.f_btn       = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_btn_grande = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_label     = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.f_actividad = tkfont.Font(family="Segoe UI", size=9)
        self.f_busqueda  = tkfont.Font(family="Segoe UI", size=10)

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
            self.menu_lateral, text=f"Bienvenido,\n{nombre_bibliotecario}",
            bg=C["marino"], font=self.f_bienv, fg="#9FB3CC", justify="center"
        ).pack(pady=(0, 4))

        tk.Label(
            self.menu_lateral, text="(Bibliotecario)",
            bg=C["marino"], font=("Segoe UI", 8), fg=C["acento"]
        ).pack(pady=(0, 20))

        # --- BOTONES DE NAVEGACIÓN — SIN "Gestión de Usuarios" ---
        self.botones_menu = {}
        self._crear_boton_menu("dashboard", "🏠  Inicio / Dashboard", self.mostrar_inicio)
        self._crear_boton_menu("libros",    "📖  Gestión de Libros", self.mostrar_gestion_libros)
        self._crear_boton_menu("prestamos", "🔄  Préstamos y Devoluciones", self.mostrar_prestamos)
        self._crear_boton_menu("reservas",  "🔔  Reservas", self.mostrar_reservas)
        self._crear_boton_menu("matriz",    "🗄  Ver Estantería", self.mostrar_estanteria_matriz)
        self._crear_boton_menu("digital",   "🌐  Librería Digital", self.mostrar_gestion_digital)

        btn_logout = tk.Button(
            self.menu_lateral, text="Cerrar sesión", command=self.cerrar_sesion,
            bg=C["rojo"], fg="white", relief="flat", font=self.f_btn,
            bd=0, pady=10, cursor="hand2", activebackground=C["rojo_hover"], activeforeground="white"
        )
        btn_logout.pack(side="bottom", fill="x", padx=18, pady=22)
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg=C["rojo_hover"]))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg=C["rojo"]))

        self.mostrar_inicio()

    seccion_activa = "dashboard"

    # =========================================================================
    # DASHBOARD — ahora con alertas, acciones de préstamo/devolución reforzadas,
    # buscador global y actividad reciente
    # =========================================================================
    def mostrar_inicio(self):
        from presentacion.Admin import lista_libros, estanteria, MAX_F, MAX_C

        self.limpiar_contenido()
        self._encabezado("Panel de control", "Estado actual del catálogo de la biblioteca")

        # --- BUSCADOR GLOBAL ---
        self._buscador_global()

        # --- TARJETAS: catálogo + alertas en la misma fila de un vistazo ---
        frame_tarjetas = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tarjetas.pack(padx=32, pady=(18, 0), fill="x", anchor="w")
        frame_tarjetas.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card", minsize=120)

        total_libros = len(lista_libros)
        espacios_libres = sum(fila.count("Libre") for fila in estanteria)
        total_espacios = MAX_F * MAX_C
        vencidos = PR.contar_vencidos()
        pendientes = PR.contar_pendientes()

        self._tarjeta_dashboard(frame_tarjetas, 0, "📚", "TOTAL LIBROS", total_libros, C["marino"])

        # Espacios libres: se pone en alerta visual si la estantería está llena
        color_espacios = C["rojo"] if espacios_libres == 0 else C["acento"]
        self._tarjeta_dashboard(frame_tarjetas, 1, "🪑", "ESPACIOS LIBRES", f"{espacios_libres}/{total_espacios}", color_espacios)

        # Préstamos vencidos: tarjeta de alerta, clicable -> filtra la tabla de préstamos
        self._tarjeta_alerta(
            frame_tarjetas, 2, "⏰", "PRÉSTAMOS VENCIDOS", vencidos,
            activa=vencidos > 0, comando=lambda: self.mostrar_prestamos(filtro_inicial="vencido")
        )

        # Reservas pendientes: tarjeta de alerta, clicable -> va a la vista de reservas
        self._tarjeta_alerta(
            frame_tarjetas, 3, "🔔", "RESERVAS PENDIENTES", pendientes,
            activa=pendientes > 0, comando=self.mostrar_reservas
        )

        if espacios_libres == 0:
            tk.Label(
                self.area_contenido,
                text="⚠ La estantería está al 100% de su capacidad. No hay espacios libres para nuevos libros.",
                font=self.f_subtitulo, fg=C["rojo"], bg=C["fondo"]
            ).pack(padx=32, pady=(14, 0), anchor="w")

        # --- ACCIONES RÁPIDAS: préstamo/devolución como botones principales ---
        tk.Label(
            self.area_contenido, text="Acciones rápidas",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(30, 14), padx=32, anchor="w")

        frame_acciones_top = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_acciones_top.pack(padx=32, fill="x", anchor="w")

        # Las dos tareas del 90% del tiempo van primero, más grandes y a la izquierda
        self._boton_accion_grande(
            frame_acciones_top, "📕  Registrar préstamo", C["verde"], C["verde_hover"],
            lambda: self.mostrar_prestamos(abrir_modal="prestamo")
        ).pack(side="left", padx=(0, 14))

        self._boton_accion_grande(
            frame_acciones_top, "📗  Registrar devolución", C["azul_dato"], C["azul_dato_hover"],
            lambda: self.mostrar_prestamos(abrir_modal="devolucion")
        ).pack(side="left")

        frame_acciones_bottom = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_acciones_bottom.pack(padx=32, pady=(12, 0), fill="x", anchor="w")

        self._boton_accion(frame_acciones_bottom, "➕  Gestionar catálogo", C["marino"], C["marino_hover"], self.mostrar_gestion_libros).pack(side="left", padx=(0, 14))
        self._boton_accion(frame_acciones_bottom, "🗄  Ver mapa estantería", C["acento"], "#B07F2E", self.mostrar_estanteria_matriz).pack(side="left")

        # --- ACTIVIDAD RECIENTE ---
        tk.Label(
            self.area_contenido, text="Actividad reciente",
            font=self.f_seccion, bg=C["fondo"], fg=C["marino"]
        ).pack(pady=(30, 12), padx=32, anchor="w")

        self._widget_actividad_reciente()

    # ---------------------------------------------------------------
    # COMPONENTES DEL DASHBOARD
    # ---------------------------------------------------------------
    def _buscador_global(self):
        """Barra de búsqueda centrada arriba: localiza un libro por ID o
        título instantáneamente, sin tener que ir primero a Gestión de Libros."""
        wrap = tk.Frame(self.area_contenido, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        wrap.pack(padx=32, fill="x", anchor="w")

        inner = tk.Frame(wrap, bg=C["tarjeta"])
        inner.pack(fill="x", padx=14, pady=10)

        tk.Label(inner, text="🔍", bg=C["tarjeta"], font=("Segoe UI", 12)).pack(side="left", padx=(2, 8))

        self.ent_busqueda_global = tk.Entry(
            inner, relief="flat", bg=C["tarjeta"], font=self.f_busqueda,
            highlightthickness=0, bd=0
        )
        self.ent_busqueda_global.pack(side="left", fill="x", expand=True, ipady=4)
        self.ent_busqueda_global.insert(0, "")
        self.ent_busqueda_global.bind("<Return>", lambda e: self._ejecutar_busqueda_global())

        placeholder = "Buscar libro por ID o título..."
        self.ent_busqueda_global.insert(0, placeholder)
        self.ent_busqueda_global.config(fg=C["texto_muted"])

        def al_enfocar(e):
            if self.ent_busqueda_global.get() == placeholder:
                self.ent_busqueda_global.delete(0, tk.END)
                self.ent_busqueda_global.config(fg=C["texto"])

        def al_desenfocar(e):
            if not self.ent_busqueda_global.get().strip():
                self.ent_busqueda_global.insert(0, placeholder)
                self.ent_busqueda_global.config(fg=C["texto_muted"])

        self.ent_busqueda_global.bind("<FocusIn>", al_enfocar)
        self.ent_busqueda_global.bind("<FocusOut>", al_desenfocar)

        btn_buscar = tk.Button(
            inner, text="Buscar", command=self._ejecutar_busqueda_global,
            bg=C["marino"], fg="white", relief="flat", font=self.f_label,
            bd=0, padx=14, pady=4, cursor="hand2"
        )
        btn_buscar.pack(side="right")

    def _ejecutar_busqueda_global(self):
        from presentacion.Admin import lista_libros

        texto = self.ent_busqueda_global.get().strip()
        if not texto or texto == "Buscar libro por ID o título...":
            return

        # Primero intenta por ID exacto (reutiliza la búsqueda recursiva ya
        # construida en Admin.py), luego por coincidencia parcial de título
        resultado = buscar_recursivo(lista_libros, texto)
        if not resultado:
            texto_lower = texto.lower()
            coincidencias = [lib for lib in lista_libros if texto_lower in lib["titulo"].lower()]
            resultado = coincidencias[0] if coincidencias else None

        if resultado:
            messagebox.showinfo(
                "Resultado de la búsqueda",
                f"Título: {resultado['titulo']}\nID: {resultado['id']}\nUbicación: Fila {resultado['f']}, Columna {resultado['c']}"
            )
        else:
            messagebox.showwarning("Búsqueda", f"No se encontró ningún libro que coincida con '{texto}'.")

    def _tarjeta_dashboard(self, parent, col, icono, etiqueta, valor, color_valor):
        card = tk.Frame(parent, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        card.grid(row=0, column=col, padx=(0 if col == 0 else 10, 10), sticky="nsew")
        inner = tk.Frame(card, bg=C["tarjeta"])
        inner.pack(fill="both", padx=16, pady=14)
        tk.Label(inner, text=f"{icono}  {etiqueta}", font=self.f_card_lbl, bg=C["tarjeta"], fg=C["texto_muted"]).pack(anchor="w")
        tk.Label(inner, text=str(valor), font=self.f_card_num, bg=C["tarjeta"], fg=color_valor).pack(anchor="w", pady=(6, 0))
        return card

    def _tarjeta_alerta(self, parent, col, icono, etiqueta, valor, activa, comando):
        """Tarjeta de alerta: roja y clicable si hay algo pendiente, gris
        neutral si está en cero. El bibliotecario ve de un vistazo qué
        requiere su atención."""
        color_fondo = C["rojo_suave"] if activa else C["tarjeta"]
        color_borde = C["rojo"] if activa else C["borde"]
        color_valor = C["rojo"] if activa else C["texto_muted"]

        card = tk.Frame(parent, bg=color_fondo, highlightthickness=1, highlightbackground=color_borde, cursor="hand2" if activa else "arrow")
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        inner = tk.Frame(card, bg=color_fondo)
        inner.pack(fill="both", padx=16, pady=14)
        tk.Label(inner, text=f"{icono}  {etiqueta}", font=self.f_card_lbl, bg=color_fondo, fg=C["texto_muted"] if not activa else C["rojo"]).pack(anchor="w")
        tk.Label(inner, text=str(valor), font=self.f_card_num, bg=color_fondo, fg=color_valor).pack(anchor="w", pady=(6, 0))

        if activa:
            for widget in (card, inner, *inner.winfo_children()):
                widget.bind("<Button-1>", lambda e: comando())

        return card

    def _boton_accion(self, parent, texto, color, hover, comando):
        btn = tk.Button(
            parent, text=texto, command=comando, bg=color, fg="white",
            font=self.f_btn, padx=16, pady=10, relief="flat", bd=0, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _boton_accion_grande(self, parent, texto, color, hover, comando):
        """Botón más prominente para las dos acciones de mayor frecuencia
        de uso: registrar préstamo y registrar devolución."""
        btn = tk.Button(
            parent, text=texto, command=comando, bg=color, fg="white",
            font=self.f_btn_grande, padx=26, pady=16, relief="flat", bd=0, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _widget_actividad_reciente(self):
        """Lista simple de los últimos movimientos (préstamos/devoluciones),
        para que el bibliotecario sienta que tiene control sobre el
        movimiento diario de la biblioteca."""
        eventos = PR.actividad_reciente(limite=6)

        wrap = tk.Frame(self.area_contenido, bg=C["tarjeta"], highlightthickness=1, highlightbackground=C["borde"])
        wrap.pack(padx=32, pady=(0, 24), fill="x", anchor="w")

        inner = tk.Frame(wrap, bg=C["tarjeta"])
        inner.pack(fill="x", padx=18, pady=14)

        if not eventos:
            tk.Label(
                inner, text="Todavía no hay movimientos registrados.",
                font=self.f_actividad, bg=C["tarjeta"], fg=C["texto_muted"]
            ).pack(anchor="w")
            return

        from presentacion.Admin import lista_libros
        titulos_por_id = {lib["id"]: lib["titulo"] for lib in lista_libros}

        for i, ev in enumerate(eventos):
            titulo_libro = titulos_por_id.get(ev["id_libro"], ev["id_libro"])
            if ev["tipo"] == "prestamo":
                icono, verbo, color = "📕", "solicitó préstamo de", C["azul_dato"]
            else:
                icono, verbo, color = "📗", "devolvió", C["verde"]

            fila = tk.Frame(inner, bg=C["tarjeta"])
            fila.pack(fill="x", pady=(0 if i == 0 else 6, 0))

            tk.Label(fila, text=icono, bg=C["tarjeta"], font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
            tk.Label(
                fila, bg=C["tarjeta"], font=self.f_actividad, fg=C["texto"],
                text=f"{ev['usuario']} {verbo} \"{titulo_libro}\""
            ).pack(side="left")
            tk.Label(
                fila, bg=C["tarjeta"], font=("Segoe UI", 8), fg=C["texto_muted"],
                text=ev["fecha"]
            ).pack(side="right")

    # =========================================================================
    # VISTA: PRÉSTAMOS Y DEVOLUCIONES
    # =========================================================================
    def mostrar_prestamos(self, filtro_inicial=None, abrir_modal=None):
        """
        filtro_inicial: si se pasa "vencido", la tabla arranca mostrando
            solo los préstamos vencidos (llega así desde la tarjeta de alerta).
        abrir_modal: "prestamo" o "devolucion" — abre el modal correspondiente
            automáticamente al entrar (llega así desde Acciones rápidas).
        """
        self.seccion_activa = "prestamos"
        self._refrescar_estado_botones_menu()

        self.limpiar_contenido()
        self._encabezado("Préstamos y devoluciones", "Registra movimientos y consulta el estado de cada préstamo")

        frame_botones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_botones.pack(padx=32, pady=(0, 14), fill="x")

        self._boton_accion(frame_botones, "📕  Registrar préstamo", C["verde"], C["verde_hover"], self._abrir_modal_prestamo).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "📗  Registrar devolución", C["azul_dato"], C["azul_dato_hover"], self._abrir_modal_devolucion).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "⚠  Penalizar (Strike)", C["rojo"], C["rojo_hover"], self._abrir_modal_strike).pack(side="left")

        # --- Filtro de estado ---
        frame_filtro = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_filtro.pack(padx=32, pady=(0, 10), fill="x", anchor="w")

        tk.Label(frame_filtro, text="Filtrar por estado:", font=self.f_label, bg=C["fondo"], fg=C["texto_muted"]).pack(side="left", padx=(0, 8))

        self.var_filtro_estado = tk.StringVar(value=filtro_inicial or "todos")
        opciones = [("todos", "Todos"), ("activo", "Activos"), ("vencido", "Vencidos"), ("devuelto", "Devueltos")]
        for valor, etiqueta in opciones:
            rb = tk.Radiobutton(
                frame_filtro, text=etiqueta, variable=self.var_filtro_estado, value=valor,
                bg=C["fondo"], font=self.f_actividad, command=self._actualizar_tabla_prestamos,
                activebackground=C["fondo"], selectcolor=C["tarjeta"]
            )
            rb.pack(side="left", padx=(0, 10))

        # --- Tabla ---
        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()

        columnas = ("id_libro", "titulo", "usuario", "f_prestamo", "f_limite", "estado")
        self.tabla_prestamos = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10, style="Biblio.Treeview")

        self.tabla_prestamos.heading("id_libro", text="ID Libro")
        self.tabla_prestamos.heading("titulo", text="Título")
        self.tabla_prestamos.heading("usuario", text="Lector")
        self.tabla_prestamos.heading("f_prestamo", text="Prestado")
        self.tabla_prestamos.heading("f_limite", text="Vence")
        self.tabla_prestamos.heading("estado", text="Estado")

        self.tabla_prestamos.column("id_libro", width=80, anchor="center")
        self.tabla_prestamos.column("titulo", width=260, anchor="w")
        self.tabla_prestamos.column("usuario", width=150, anchor="w")
        self.tabla_prestamos.column("f_prestamo", width=100, anchor="center")
        self.tabla_prestamos.column("f_limite", width=100, anchor="center")
        self.tabla_prestamos.column("estado", width=100, anchor="center")

        self.tabla_prestamos.tag_configure("vencido", foreground=C["rojo"])
        self.tabla_prestamos.tag_configure("activo", foreground=C["verde"])
        self.tabla_prestamos.tag_configure("devuelto", foreground=C["texto_muted"])

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_prestamos.yview)
        self.tabla_prestamos.configure(yscrollcommand=scrollbar.set)
        self.tabla_prestamos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._actualizar_tabla_prestamos()

        if abrir_modal == "prestamo":
            self._abrir_modal_prestamo()
        elif abrir_modal == "devolucion":
            self._abrir_modal_devolucion()

    def _actualizar_tabla_prestamos(self):
        from presentacion.Admin import lista_libros
        titulos_por_id = {lib["id"]: lib["titulo"] for lib in lista_libros}

        for fila in self.tabla_prestamos.get_children():
            self.tabla_prestamos.delete(fila)

        filtro = self.var_filtro_estado.get()
        for p in PR.lista_prestamos:
            if filtro != "todos" and p["estado"] != filtro:
                continue
            titulo = titulos_por_id.get(p["id_libro"], p["id_libro"])
            self.tabla_prestamos.insert(
                "", "end",
                values=(p["id_libro"], titulo, p["usuario"], p["fecha_prestamo"], p["fecha_limite"], p["estado"].upper()),
                tags=(p["estado"],)
            )

    def _abrir_modal_prestamo(self):
        """Modal compacto para registrar un préstamo: ID del libro + nombre
        del lector. Valida que el libro exista y no esté ya prestado."""
        from presentacion.Admin import lista_libros, id_existe

        modal = self._crear_modal_base("Registrar préstamo", 360, 280)
        inner = modal.inner

        tk.Label(inner, text="ID del libro", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_id = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_id.pack(fill="x", ipady=5, pady=(2, 12))

        tk.Label(inner, text="Nombre del lector", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_usuario = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_usuario.pack(fill="x", ipady=5, pady=(2, 16))

        lbl_estado = tk.Label(inner, text="", font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"], wraplength=300, justify="left")
        lbl_estado.pack(anchor="w", pady=(0, 8))

        def confirmar():
            id_lib = ent_id.get().strip()
            usuario = ent_usuario.get().strip()

            if not id_lib or not usuario:
                lbl_estado.config(text="⚠ Completa el ID del libro y el nombre del lector.")
                return

            libro = next((lib for lib in lista_libros if lib["id"] == id_lib), None)
            if not libro:
                lbl_estado.config(text=f"⚠ No existe ningún libro con ID '{id_lib}' en el catálogo.")
                return

            if PR.prestamo_activo_de(id_lib):
                lbl_estado.config(text=f"⚠ Este libro ya está prestado actualmente y no ha sido devuelto.")
                return

            PR.registrar_prestamo(id_lib, usuario)
            messagebox.showinfo("Préstamo registrado", f"'{libro['titulo']}' fue prestado a {usuario}.")
            modal.destroy()
            self.mostrar_prestamos()

        self._botones_modal(inner, "Registrar préstamo", C["verde"], C["verde_hover"], confirmar, modal.destroy)

    def _abrir_modal_devolucion(self):
        """Modal compacto para registrar una devolución: solo pide el ID
        del libro y busca automáticamente su préstamo activo."""
        modal = self._crear_modal_base("Registrar devolución", 360, 220)
        inner = modal.inner

        tk.Label(inner, text="ID del libro a devolver", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_id = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_id.pack(fill="x", ipady=5, pady=(2, 16))

        lbl_estado = tk.Label(inner, text="", font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"], wraplength=300, justify="left")
        lbl_estado.pack(anchor="w", pady=(0, 8))

        def confirmar():
            from presentacion.Admin import lista_libros
            id_lib = ent_id.get().strip()

            if not id_lib:
                lbl_estado.config(text="⚠ Escribe el ID del libro.")
                return

            prestamo = PR.registrar_devolucion(id_lib)
            if not prestamo:
                lbl_estado.config(text=f"⚠ No hay ningún préstamo activo registrado para el ID '{id_lib}'.")
                return

            libro = next((lib for lib in lista_libros if lib["id"] == id_lib), None)
            titulo = libro["titulo"] if libro else id_lib
            messagebox.showinfo("Devolución registrada", f"'{titulo}' fue devuelto por {prestamo['usuario']}.")
            modal.destroy()
            self.mostrar_prestamos()

        self._botones_modal(inner, "Registrar devolución", C["azul_dato"], C["azul_dato_hover"], confirmar, modal.destroy)

    def _abrir_modal_strike(self):
        """Modal para penalizar a un usuario manualmente por daños, pérdida o atraso grave."""
        modal = self._crear_modal_base("Penalizar usuario", 360, 220)
        inner = modal.inner

        tk.Label(inner, text="Nombre de usuario (login)", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_usuario = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_usuario.pack(fill="x", ipady=5, pady=(2, 16))

        lbl_estado = tk.Label(inner, text="", font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"], wraplength=300, justify="left")
        lbl_estado.pack(anchor="w", pady=(0, 8))

        def confirmar():
            from presentacion.Admin import cargar_usuarios, guardar_usuarios
            usr = ent_usuario.get().strip()

            if not usr:
                lbl_estado.config(text="⚠ Escribe el nombre de usuario.")
                return

            usuarios = cargar_usuarios()
            if usr not in usuarios:
                lbl_estado.config(text=f"⚠ El usuario '{usr}' no existe.")
                return

            # Agregar strike
            datos = usuarios[usr]
            strikes_actuales = datos.get("strikes", 0)
            datos["strikes"] = strikes_actuales + 1
            usuarios[usr] = datos
            guardar_usuarios(usuarios)
            
            messagebox.showinfo("Penalización aplicada", f"Se ha añadido 1 strike al usuario '{usr}'.\nStrikes totales: {datos['strikes']}")
            modal.destroy()
            self.mostrar_inicio()

        self._botones_modal(inner, "Aplicar Strike", C["rojo"], C["rojo_hover"], confirmar, modal.destroy)

    # =========================================================================
    # VISTA: RESERVAS
    # =========================================================================
    def mostrar_reservas(self):
        self.seccion_activa = "reservas"
        self._refrescar_estado_botones_menu()

        self.limpiar_contenido()
        self._encabezado("Reservas", "Aprueba o rechaza solicitudes de reserva de libros")

        frame_botones = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_botones.pack(padx=32, pady=(0, 14), fill="x")

        self._boton_accion(frame_botones, "➕  Nueva reserva", C["marino"], C["marino_hover"], self._abrir_modal_nueva_reserva).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "✅  Aprobar seleccionada", C["verde"], C["verde_hover"], self._aprobar_reserva_seleccionada).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_botones, "✖  Rechazar seleccionada", C["rojo"], C["rojo_hover"], self._rechazar_reserva_seleccionada).pack(side="left")

        frame_tabla = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_tabla.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        self._estilizar_treeview()

        columnas = ("id_libro", "titulo", "usuario", "fecha", "estado")
        self.tabla_reservas = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10, style="Biblio.Treeview")

        self.tabla_reservas.heading("id_libro", text="ID Libro")
        self.tabla_reservas.heading("titulo", text="Título")
        self.tabla_reservas.heading("usuario", text="Solicitante")
        self.tabla_reservas.heading("fecha", text="Fecha solicitud")
        self.tabla_reservas.heading("estado", text="Estado")

        self.tabla_reservas.column("id_libro", width=80, anchor="center")
        self.tabla_reservas.column("titulo", width=280, anchor="w")
        self.tabla_reservas.column("usuario", width=150, anchor="w")
        self.tabla_reservas.column("fecha", width=120, anchor="center")
        self.tabla_reservas.column("estado", width=110, anchor="center")

        self.tabla_reservas.tag_configure("pendiente", foreground=C["acento"])
        self.tabla_reservas.tag_configure("aprobada", foreground=C["verde"])
        self.tabla_reservas.tag_configure("rechazada", foreground=C["texto_muted"])

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_reservas.yview)
        self.tabla_reservas.configure(yscrollcommand=scrollbar.set)
        self.tabla_reservas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._actualizar_tabla_reservas()

    def _actualizar_tabla_reservas(self):
        from presentacion.Admin import lista_libros
        titulos_por_id = {lib["id"]: lib["titulo"] for lib in lista_libros}

        for fila in self.tabla_reservas.get_children():
            self.tabla_reservas.delete(fila)

        for i, r in enumerate(PR.lista_reservas):
            titulo = titulos_por_id.get(r["id_libro"], r["id_libro"])
            self.tabla_reservas.insert(
                "", "end", iid=str(i),
                values=(r["id_libro"], titulo, r["usuario"], r["fecha_solicitud"], r["estado"].upper()),
                tags=(r["estado"],)
            )

    def _abrir_modal_nueva_reserva(self):
        from presentacion.Admin import lista_libros

        modal = self._crear_modal_base("Nueva reserva", 360, 280)
        inner = modal.inner

        tk.Label(inner, text="ID del libro", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_id = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_id.pack(fill="x", ipady=5, pady=(2, 12))

        tk.Label(inner, text="Nombre del solicitante", font=("Segoe UI", 9, "bold"), bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_usuario = tk.Entry(inner, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=C["borde"])
        ent_usuario.pack(fill="x", ipady=5, pady=(2, 16))

        lbl_estado = tk.Label(inner, text="", font=("Segoe UI", 8), bg=C["fondo"], fg=C["rojo"], wraplength=300, justify="left")
        lbl_estado.pack(anchor="w", pady=(0, 8))

        def confirmar():
            id_lib = ent_id.get().strip()
            usuario = ent_usuario.get().strip()

            if not id_lib or not usuario:
                lbl_estado.config(text="⚠ Completa el ID del libro y el nombre del solicitante.")
                return

            if not any(lib["id"] == id_lib for lib in lista_libros):
                lbl_estado.config(text=f"⚠ No existe ningún libro con ID '{id_lib}' en el catálogo.")
                return

            PR.registrar_reserva(id_lib, usuario)
            modal.destroy()
            self.mostrar_reservas()

        self._botones_modal(inner, "Crear reserva", C["marino"], C["marino_hover"], confirmar, modal.destroy)

    def _aprobar_reserva_seleccionada(self):
        seleccion = self.tabla_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una reserva de la tabla.")
            return

        indice = int(seleccion[0])
        if PR.lista_reservas[indice]["estado"] != "pendiente":
            messagebox.showwarning("Atención", "Esta reserva ya fue procesada.")
            return

        prestamo = PR.aprobar_reserva(indice)
        if prestamo:
            messagebox.showinfo("Reserva aprobada", "La reserva fue aprobada y se generó el préstamo correspondiente.")
        else:
            messagebox.showerror("Error", "No se pudo aprobar la reserva.")
        self._actualizar_tabla_reservas()

    def _rechazar_reserva_seleccionada(self):
        seleccion = self.tabla_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una reserva de la tabla.")
            return

        indice = int(seleccion[0])
        if PR.lista_reservas[indice]["estado"] != "pendiente":
            messagebox.showwarning("Atención", "Esta reserva ya fue procesada.")
            return

        PR.rechazar_reserva(indice)
        self._actualizar_tabla_reservas()

    # =========================================================================
    # UTILIDADES DE MODALES (compartidas por préstamo / devolución / reserva)
    # =========================================================================
    def _crear_modal_base(self, titulo, ancho, alto):
        """Crea un Toplevel modal con la cabecera marino/dorado consistente
        con el resto del sistema, y devuelve el frame interior listo para
        que cada caso de uso agregue sus campos."""
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.configure(bg=C["fondo"])
        modal.resizable(True, True)
        modal.transient(self.root)
        modal.grab_set()

        modal.geometry(f"{ancho}x{alto}")
        modal.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (ancho // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (alto // 2)
        modal.geometry(f"+{x}+{y}")

        tk.Frame(modal, bg=C["marino"], height=6).pack(fill="x")
        tk.Frame(modal, bg=C["acento"], height=3).pack(fill="x")

        inner = tk.Frame(modal, bg=C["fondo"])
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(inner, text=titulo, font=("Segoe UI", 14, "bold"), bg=C["fondo"], fg=C["marino"]).pack(anchor="w", pady=(0, 14))

        modal.inner = inner
        return modal

    def _botones_modal(self, inner, texto_confirmar, color, hover, comando_confirmar, comando_cancelar):
        frame_btns = tk.Frame(inner, bg=C["fondo"])
        frame_btns.pack(fill="x", side="bottom")

        btn_confirmar = tk.Button(
            frame_btns, text=texto_confirmar, command=comando_confirmar,
            bg=color, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0, pady=9, cursor="hand2"
        )
        btn_confirmar.pack(fill="x", pady=(0, 8))
        btn_confirmar.bind("<Enter>", lambda e: btn_confirmar.config(bg=hover))
        btn_confirmar.bind("<Leave>", lambda e: btn_confirmar.config(bg=color))

        btn_cancelar = tk.Button(
            frame_btns, text="Cancelar", command=comando_cancelar,
            bg=C["tarjeta"], fg=C["texto_muted"], font=("Segoe UI", 9),
            relief="flat", bd=0, pady=8, cursor="hand2",
            highlightthickness=1, highlightbackground=C["borde"]
        )
        btn_cancelar.pack(fill="x")

    def _refrescar_estado_botones_menu(self):
        """Sincroniza el resaltado del menú lateral cuando navegamos a una
        vista programáticamente (p. ej. desde una tarjeta de alerta) en
        lugar de hacer clic directo en el botón del menú."""
        for k, btn in self.botones_menu.items():
            if k == self.seccion_activa:
                btn.config(bg=C["acento"], fg=C["marino"])
            else:
                btn.config(bg=C["marino"], fg=C["blanco"])

    # NOTA: mostrar_gestion_libros, mostrar_estanteria_matriz, registrar_libro_logica,
    # ejecutar_busqueda_recursiva, eliminar_libro_logica, actualizar_tabla_libros y
    # _estilizar_treeview se heredan tal cual de VentanaAdministrador — el
    # bibliotecario tiene exactamente las mismas funciones de catálogo que el admin.
    #
    # Los métodos de gestión de usuarios quedan inertes — no hay botón en el menú.

    # =========================================================================
    # 🌐 VISTA: GESTIÓN DE LIBRERÍA DIGITAL
    # =========================================================================
    def mostrar_gestion_digital(self):
        self.seccion_activa = "digital"
        self._refrescar_estado_botones_menu()
        self.limpiar_contenido()
        self._encabezado(
            "Librería Digital",
            "Agrega, edita y elimina recursos digitales del catálogo en línea"
        )

        # --- Botones de acción ---
        frame_btns = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_btns.pack(padx=32, pady=(0, 14), fill="x")

        self._boton_accion(frame_btns, "➕  Nuevo recurso",
                           C["verde"], C["verde_hover"],
                           lambda: self._modal_recurso_digital()).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_btns, "✏️  Editar seleccionado",
                           C["azul_dato"], C["azul_dato_hover"],
                           self._editar_recurso_digital).pack(side="left", padx=(0, 10))
        self._boton_accion(frame_btns, "🗑  Eliminar seleccionado",
                           C["rojo"], C["rojo_hover"],
                           self._eliminar_recurso_digital).pack(side="left")

        tk.Label(frame_btns,
                 text="Doble clic en una fila para editar rápidamente",
                 font=("Segoe UI", 8, "italic"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(side="left", padx=(16, 0))

        # --- LAYOUT: tabla + panel portada ---
        frame_body = tk.Frame(self.area_contenido, bg=C["fondo"])
        frame_body.pack(padx=32, pady=(0, 24), fill="both", expand=True)

        # --- Panel portada (se empaqueta PRIMERO para reservar espacio) ---
        panel_port = tk.Frame(frame_body, bg=C["tarjeta"],
                              highlightthickness=1, highlightbackground=C["borde"],
                              width=210)
        panel_port.pack(side="right", fill="y", padx=(12, 0))
        panel_port.pack_propagate(False)

        self._foto_dig_admin  = None
        self._lbl_port_dig    = tk.Label(panel_port, bg=C["marino"])
        self._lbl_port_dig.pack(fill="x")

        inner_port = tk.Frame(panel_port, bg=C["tarjeta"])
        inner_port.pack(fill="both", expand=True, padx=10, pady=10)

        self._lbl_pd_titulo = tk.Label(inner_port, text="Selecciona un recurso",
                                        font=("Segoe UI", 9, "bold"),
                                        bg=C["tarjeta"], fg=C["marino"],
                                        wraplength=180, justify="left")
        self._lbl_pd_titulo.pack(anchor="w", pady=(0, 4))
        self._lbl_pd_autor = tk.Label(inner_port, text="",
                                       font=("Segoe UI", 8), bg=C["tarjeta"],
                                       fg=C["texto_muted"], wraplength=180, justify="left")
        self._lbl_pd_autor.pack(anchor="w")
        self._lbl_pd_cat = tk.Label(inner_port, text="",
                                     font=("Segoe UI", 8, "bold"),
                                     bg=C["tarjeta"], fg=C["acento"])
        self._lbl_pd_cat.pack(anchor="w", pady=(4, 0))
        self._lbl_pd_desc = tk.Label(inner_port, text="",
                                      font=("Segoe UI", 8), bg=C["tarjeta"],
                                      fg=C["texto_muted"],
                                      wraplength=180, justify="left")
        self._lbl_pd_desc.pack(anchor="w", pady=(4, 0))

        # Portada inicial — se carga y actualiza dinámicamente al cambiar panel
        def _cargar_portada_en_panel(cat=None):
            foto = _foto_portada_cat(cat, ancho=190, alto=220)
            if foto:
                self._foto_dig_admin = foto
                self._lbl_port_dig.config(image=foto, text="")
            else:
                self._lbl_port_dig.config(image="", text="🌐",
                                          font=("Segoe UI", 46), fg=C["acento"],
                                          bg=C["marino"])
        _cargar_portada_en_panel(None)

        # Tabla (se empaqueta DESPUÉS del panel para que ocupe el resto)
        frame_tabla = tk.Frame(frame_body, bg=C["fondo"])
        frame_tabla.pack(side="left", fill="both", expand=True)

        self._estilizar_treeview()
        columnas = ("titulo", "autor", "categoria", "url")
        self.tabla_digital_admin = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings",
            height=14, style="Biblio.Treeview"
        )

        self.tabla_digital_admin.heading("titulo",    text="Título")
        self.tabla_digital_admin.heading("autor",     text="Autor")
        self.tabla_digital_admin.heading("categoria", text="Categoría")
        self.tabla_digital_admin.heading("url",       text="URL")

        self.tabla_digital_admin.column("titulo",    width=240, anchor="w")
        self.tabla_digital_admin.column("autor",     width=150, anchor="w")
        self.tabla_digital_admin.column("categoria", width=130, anchor="center")
        self.tabla_digital_admin.column("url",       width=220, anchor="w")

        sb_dig = ttk.Scrollbar(frame_tabla, orient="vertical",
                               command=self.tabla_digital_admin.yview)
        self.tabla_digital_admin.configure(yscrollcommand=sb_dig.set)
        self.tabla_digital_admin.pack(side="left", fill="both", expand=True)
        sb_dig.pack(side="right", fill="y")

        # Doble clic para editar
        self.tabla_digital_admin.bind(
            "<Double-1>", lambda e: self._editar_recurso_digital()
        )
        # Selección → portada
        self.tabla_digital_admin.bind(
            "<<TreeviewSelect>>", self._actualizar_portada_digital
        )

        self._actualizar_tabla_digital()

    def _actualizar_tabla_digital(self):
        for fila in self.tabla_digital_admin.get_children():
            self.tabla_digital_admin.delete(fila)
        for i, rec in enumerate(_cargar_lib_digital()):
            self.tabla_digital_admin.insert(
                "", "end", iid=str(i),
                values=(rec.get("titulo", ""), rec.get("autor", ""),
                        rec.get("categoria", ""), rec.get("url", ""))
            )

    def _actualizar_portada_digital(self, event=None):
        """Actualiza el panel derecho al seleccionar una fila."""
        sel = self.tabla_digital_admin.selection()
        if not sel:
            return
        idx = int(sel[0])
        recursos = _cargar_lib_digital()
        if 0 <= idx < len(recursos):
            rec = recursos[idx]
            cat = rec.get("categoria", "")
            self._lbl_pd_titulo.config(text=rec.get("titulo", ""))
            self._lbl_pd_autor.config(text=rec.get("autor", ""))
            self._lbl_pd_cat.config(text=cat)
            self._lbl_pd_desc.config(text=rec.get("descripcion", ""))
            foto = _foto_portada_cat(cat, ancho=190, alto=220)
            if foto:
                self._foto_dig_admin = foto
                self._lbl_port_dig.config(image=foto, text="")

    def _editar_recurso_digital(self):
        sel = self.tabla_digital_admin.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un recurso de la tabla para editar.")
            return
        idx = int(sel[0])
        recursos = _cargar_lib_digital()
        if 0 <= idx < len(recursos):
            self._modal_recurso_digital(indice=idx, datos=recursos[idx])


    def _eliminar_recurso_digital(self):
        sel = self.tabla_digital_admin.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un recurso de la tabla para eliminar.")
            return
        idx = int(sel[0])
        recursos = _cargar_lib_digital()
        if not (0 <= idx < len(recursos)):
            return
        titulo = recursos[idx].get("titulo", "")
        if not messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente '{titulo}'?"):
            return
        recursos.pop(idx)
        if _guardar_lib_digital(recursos):
            messagebox.showinfo("Listo", f"'{titulo}' fue eliminado de la librería digital.")
            self._actualizar_tabla_digital()

    def _modal_recurso_digital(self, indice=None, datos=None):
        """Modal para agregar o editar un recurso digital.
        Si 'indice' es None, se crea uno nuevo; si no, se edita el existente.
        """
        es_nuevo = indice is None
        datos = datos or {}

        modal = self._crear_modal_base(
            "Nuevo recurso digital" if es_nuevo else "Editar recurso digital",
            460, 520
        )
        inner = modal.inner

        # Título
        tk.Label(inner, text="Título", font=("Segoe UI", 9, "bold"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_titulo = tk.Entry(inner, font=("Segoe UI", 10), relief="flat",
                              highlightthickness=1, highlightbackground=C["borde"])
        ent_titulo.insert(0, datos.get("titulo", ""))
        ent_titulo.pack(fill="x", ipady=5, pady=(2, 10))

        # Autor
        tk.Label(inner, text="Autor", font=("Segoe UI", 9, "bold"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_autor = tk.Entry(inner, font=("Segoe UI", 10), relief="flat",
                             highlightthickness=1, highlightbackground=C["borde"])
        ent_autor.insert(0, datos.get("autor", ""))
        ent_autor.pack(fill="x", ipady=5, pady=(2, 10))

        # Categoría (Combobox)
        tk.Label(inner, text="Categoría", font=("Segoe UI", 9, "bold"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        combo_cat = ttk.Combobox(inner, values=CATEGORIAS_DISPONIBLES,
                                  state="readonly", font=("Segoe UI", 10))
        combo_cat.set(datos.get("categoria", CATEGORIAS_DISPONIBLES[0]))
        combo_cat.pack(fill="x", pady=(2, 10))

        # URL
        tk.Label(inner, text="URL del recurso", font=("Segoe UI", 9, "bold"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        ent_url = tk.Entry(inner, font=("Segoe UI", 10), relief="flat",
                           highlightthickness=1, highlightbackground=C["borde"])
        ent_url.insert(0, datos.get("url", ""))
        ent_url.pack(fill="x", ipady=5, pady=(2, 10))

        # Descripción
        tk.Label(inner, text="Descripción breve", font=("Segoe UI", 9, "bold"),
                 bg=C["fondo"], fg=C["texto_muted"]).pack(anchor="w")
        txt_desc = tk.Text(inner, height=4, font=("Segoe UI", 10), relief="flat",
                           highlightthickness=1, highlightbackground=C["borde"],
                           wrap="word", padx=8, pady=6)
        txt_desc.insert("1.0", datos.get("descripcion", ""))
        txt_desc.pack(fill="x", pady=(2, 10))

        lbl_err = tk.Label(inner, text="", font=("Segoe UI", 8),
                           bg=C["fondo"], fg=C["rojo"], wraplength=380, justify="left")
        lbl_err.pack(anchor="w", pady=(0, 6))

        def confirmar():
            titulo  = ent_titulo.get().strip()
            autor   = ent_autor.get().strip()
            cat     = combo_cat.get().strip()
            url     = ent_url.get().strip()
            desc    = txt_desc.get("1.0", "end-1c").strip()

            if not titulo or not autor:
                lbl_err.config(text="⚠ El título y el autor son obligatorios.")
                return

            nuevo = {"titulo": titulo, "autor": autor,
                     "categoria": cat, "url": url, "descripcion": desc}

            recursos = _cargar_lib_digital()
            if es_nuevo:
                recursos.append(nuevo)
                msg = f"'{titulo}' fue añadido a la librería digital."
            else:
                recursos[indice] = nuevo
                msg = f"'{titulo}' fue actualizado correctamente."

            if _guardar_lib_digital(recursos):
                messagebox.showinfo("Guardado", msg)
                modal.destroy()
                self._actualizar_tabla_digital()

        self._botones_modal(
            inner,
            "Guardar recurso" if es_nuevo else "Actualizar recurso",
            C["verde"], C["verde_hover"],
            confirmar, modal.destroy
        )



def pantalla_bibliotecario(usuario, posicion_actual=None, nombre=None):
    """
    Punto de entrada llamado desde login.py para el rol 'bibliotecario'.

    Parámetros:
        usuario: el nombre de usuario (clave de login) — se usa como usuario_login
        posicion_actual: tupla (x, y) para abrir la ventana en la misma posición
        nombre: nombre completo a mostrar (si no se pasa, se usa 'usuario')
    """
    root = tk.Tk()
    if posicion_actual:
        root.geometry(f"+{posicion_actual[0]}+{posicion_actual[1]}")

    VentanaBibliotecario(
        root,
        nombre_bibliotecario=nombre or usuario,
        usuario_login=usuario
    )
    root.mainloop()


# =========================================================================
# Ejecución aislada para pruebas
# =========================================================================
if __name__ == "__main__":
    pantalla_bibliotecario(usuario="biblio_demo", nombre="Bibliotecario Demo")