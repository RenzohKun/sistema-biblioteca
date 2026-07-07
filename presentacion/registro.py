import tkinter as tk
from tkinter import messagebox
import json
import os

# --- RUTAS DE ARCHIVOS LOCALES ---
CARPETA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO_USUARIOS = os.path.join(CARPETA_RAIZ, "datos", "usuarios.json")
ARCHIVO_PADRON = os.path.join(CARPETA_RAIZ, "datos", "padron_uleam.json")

CLAVE_MAESTRA_ADMIN = "ULEAM_ADMIN_2026"

# ======================================================
# 🎨 PALETA DE COLORES CENTRALIZADA
# ======================================================
C = {
    "fondo":           "#F7F8FA",
    "tarjeta":         "#FFFFFF",
    "borde":           "#DDE1E7",
    "borde_focus":     "#185FA5",

    "texto":           "#1A1D23",
    "texto_muted":     "#6B7280",
    "texto_label":     "#374151",

    "azul":            "#185FA5",
    "azul_hover":      "#124D8A",

    "tab_activo_bg":   "#185FA5",
    "tab_activo_fg":   "#FFFFFF",
    "tab_inactivo_bg": "#EAECF0",
    "tab_inactivo_fg": "#6B7280",

    "exito":           "#1A7F4B",
    "advertencia":     "#B45309",
    "peligro":         "#C0392B",
    "peligro_suave":   "#FEF2F2",
    "peligro_borde":   "#FECACA",
}

# ======================================================
# 💾 DATOS
# ======================================================
def cargar_usuarios():
    try:
        if os.path.exists(ARCHIVO_USUARIOS):
            with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    return {}

def guardar_usuarios(usuarios):
    try:
        os.makedirs(os.path.dirname(ARCHIVO_USUARIOS), exist_ok=True)
        with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar usuarios: {e}")

def cargar_padron_universitario():
    try:
        if os.path.exists(ARCHIVO_PADRON):
            with open(ARCHIVO_PADRON, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar el padrón: {e}")
    return []

# ======================================================
# 🏗️ COMPONENTES REUTILIZABLES
# ======================================================
def crear_campo(parent, icono, placeholder, ocultar=False):
    """
    Campo responsive: el Entry crece/encoge con el contenedor padre.
    No usa width fijo — se expande con fill='x'.
    """
    contenedor = tk.Frame(
        parent, bg=C["tarjeta"],
        highlightthickness=1,
        highlightbackground=C["borde"],
        highlightcolor=C["borde"]
    )
    contenedor.pack(fill="x", ipady=1)

    lbl_icono = tk.Label(
        contenedor, text=icono, font=("Segoe UI", 12),
        fg=C["texto_muted"], bg=C["tarjeta"], width=2
    )
    lbl_icono.pack(side="left", padx=(8, 2))

    entry = tk.Entry(
        contenedor,
        font=("Segoe UI", 10),
        bg=C["tarjeta"], fg=C["texto"],
        bd=0, highlightthickness=0,
        insertbackground=C["azul"],
        show="●" if ocultar else ""
    )
    # fill="x" + expand=True hace que el Entry use todo el espacio disponible
    entry.pack(side="left", fill="x", expand=True, ipady=7, pady=2, padx=(0, 8))

    # Placeholder simulado
    entry.insert(0, placeholder)
    entry.config(fg=C["texto_muted"])

    def on_focus_in(e):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=C["texto"])
        contenedor.config(
            highlightbackground=C["borde_focus"],
            highlightcolor=C["borde_focus"]
        )
        lbl_icono.config(fg=C["azul"])

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg=C["texto_muted"])
        contenedor.config(
            highlightbackground=C["borde"],
            highlightcolor=C["borde"]
        )
        lbl_icono.config(fg=C["texto_muted"])

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry._placeholder = placeholder
    return contenedor, entry


def crear_label(parent, texto):
    tk.Label(
        parent, text=texto,
        font=("Segoe UI", 9, "bold"),
        fg=C["texto_label"], bg=C["tarjeta"]
    ).pack(anchor="w", pady=(10, 3))


def get_valor(entry):
    val = entry.get().strip()
    return "" if val == getattr(entry, "_placeholder", None) else val


def _solo_digitos(event):
    """Bloquea cualquier carácter que no sea un dígito (0-9)."""
    if event.char and event.char.isprintable() and not event.char.isdigit():
        return "break"


def _digitos_y_mas(event):
    """Permite dígitos y el signo + (para prefijos internacionales como +593)."""
    if event.char and event.char.isprintable() and not event.char.isdigit() and event.char != '+':
        return "break"


# ======================================================
# 🖥️ PANTALLA PRINCIPAL
# ======================================================
def pantalla_registro(posicion_actual=None):
    root = tk.Tk()
    root.title("Registro — Biblioteca ULEAM")
    root.configure(bg=C["fondo"])
    root.minsize(400, 500)
    root.resizable(True, True)

    if posicion_actual:
        root.geometry(f"560x700+{posicion_actual[0]}+{posicion_actual[1]}")
    else:
        root.geometry("560x700")
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"560x700+{(sw-560)//2}+{(sh-700)//2}")

    correos_validos = cargar_padron_universitario()

    # ---- CANVAS SCROLLABLE ----
    canvas = tk.Canvas(root, bg=C["fondo"], bd=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame_scroll = tk.Frame(canvas, bg=C["fondo"])
    id_ventana = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    # Hacer que frame_scroll siempre tenga el ancho del canvas
    def on_canvas_resize(event):
        canvas.itemconfig(id_ventana, width=event.width)

    def on_frame_resize(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_canvas_resize)
    frame_scroll.bind("<Configure>", on_frame_resize)
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ---- COLUMNA CENTRAL RESPONSIVE ----
    # Esta columna usa padx relativo para centrar el contenido con márgenes proporcionales
    col_centro = tk.Frame(frame_scroll, bg=C["fondo"])
    col_centro.pack(fill="both", expand=True, padx=40, pady=30)

    # ---- TARJETA ----
    tarjeta = tk.Frame(
        col_centro, bg=C["tarjeta"],
        highlightthickness=1, highlightbackground=C["borde"]
    )
    tarjeta.pack(fill="both", expand=True)

    padding = tk.Frame(tarjeta, bg=C["tarjeta"])
    padding.pack(fill="both", expand=True, padx=28, pady=24)

    # ---- CABECERA ----
    tk.Frame(padding, bg=C["tarjeta"], height=4).pack()  # espaciado top

    circulo = tk.Frame(padding, bg="#DBEAFE", width=52, height=52)
    circulo.pack()
    circulo.pack_propagate(False)
    tk.Label(circulo, text="📚", font=("Segoe UI", 22), bg="#DBEAFE").place(
        relx=0.5, rely=0.5, anchor="center"
    )

    tk.Label(
        padding, text="Crear cuenta",
        font=("Segoe UI", 17, "bold"),
        fg=C["texto"], bg=C["tarjeta"]
    ).pack(pady=(8, 2))

    tk.Label(
        padding, text="Sistema de Gestión de Biblioteca ULEAM",
        font=("Segoe UI", 9), fg=C["texto_muted"], bg=C["tarjeta"]
    ).pack(pady=(0, 14))

    tk.Frame(padding, bg=C["borde"], height=1).pack(fill="x", pady=(0, 14))

    # ---- TABS ----
    var_tipo = tk.StringVar(value="lector")

    frame_tabs = tk.Frame(padding, bg=C["borde"])
    frame_tabs.pack(fill="x", pady=(0, 14))
    frame_tabs.columnconfigure(0, weight=1)
    frame_tabs.columnconfigure(1, weight=1)

    btn_tab_lector = tk.Button(
        frame_tabs, text="Lector",
        font=("Segoe UI", 9, "bold"),
        relief="flat", cursor="hand2", bd=0, pady=8
    )
    btn_tab_admin = tk.Button(
        frame_tabs, text="Administrador",
        font=("Segoe UI", 9, "bold"),
        relief="flat", cursor="hand2", bd=0, pady=8
    )
    btn_tab_lector.grid(row=0, column=0, sticky="ew", padx=(2, 1), pady=2)
    btn_tab_admin.grid(row=0, column=1, sticky="ew", padx=(1, 2), pady=2)

    # ---- CAMPOS PRINCIPALES ----
    crear_label(padding, "Nombre de usuario")
    _, ent_user = crear_campo(padding, "👤", "mi_usuario")

    crear_label(padding, "Correo electrónico")
    _, ent_correo = crear_campo(padding, "✉", "correo@live.uleam.edu.ec")

    lbl_correo_status = tk.Label(
        padding, text="Ingresa tu correo electrónico",
        font=("Segoe UI", 8, "italic"),
        fg=C["texto_muted"], bg=C["tarjeta"]
    )
    lbl_correo_status.pack(anchor="w", pady=(2, 0))

    # Cédula + Teléfono (2 columnas, cada una fill="x")
    fila_doc = tk.Frame(padding, bg=C["tarjeta"])
    fila_doc.pack(fill="x", pady=(4, 0))
    fila_doc.columnconfigure(0, weight=1)
    fila_doc.columnconfigure(1, weight=1)

    col_ced = tk.Frame(fila_doc, bg=C["tarjeta"])
    col_ced.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    tk.Label(col_ced, text="Cédula / Pasaporte", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(10, 3))
    _, ent_cedula = crear_campo(col_ced, "🪪", "1234567890")
    ent_cedula.bind("<KeyPress>", _solo_digitos)

    col_tel = tk.Frame(fila_doc, bg=C["tarjeta"])
    col_tel.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    tk.Label(col_tel, text="Teléfono", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(10, 3))
    _, ent_telefono = crear_campo(col_tel, "📞", "+593...")
    ent_telefono.bind("<KeyPress>", _digitos_y_mas)

    # Contraseñas (2 columnas)
    fila_pass = tk.Frame(padding, bg=C["tarjeta"])
    fila_pass.pack(fill="x", pady=(4, 0))
    fila_pass.columnconfigure(0, weight=1)
    fila_pass.columnconfigure(1, weight=1)

    col_p1 = tk.Frame(fila_pass, bg=C["tarjeta"])
    col_p1.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    tk.Label(col_p1, text="Contraseña", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(10, 3))
    _, ent_pass = crear_campo(col_p1, "🔒", "Mínimo 4 caracteres", ocultar=True)

    col_p2 = tk.Frame(fila_pass, bg=C["tarjeta"])
    col_p2.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    tk.Label(col_p2, text="Confirmar contraseña", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(10, 3))
    _, ent_pass_conf = crear_campo(col_p2, "🔒", "Repetir contraseña", ocultar=True)

    # ---- PANEL ADMIN ----
    frame_admin_token = tk.Frame(
        padding, bg=C["tarjeta"],
        highlightthickness=1, highlightbackground=C["borde"]
    )
    lbl_token_titulo = tk.Label(
        frame_admin_token, text="🔑  Código de verificación admin",
        font=("Segoe UI", 9, "bold"), fg=C["azul"], bg=C["tarjeta"]
    )
    lbl_token_titulo.pack(anchor="w", padx=12, pady=(10, 3))

    cont_token = tk.Frame(
        frame_admin_token, bg=C["tarjeta"],
        highlightthickness=1, highlightbackground=C["borde"]
    )
    cont_token.pack(fill="x", padx=12, pady=(0, 4))

    ent_token_admin = tk.Entry(
        cont_token, show="●", font=("Segoe UI", 10),
        bg=C["tarjeta"], fg=C["texto"],
        bd=0, highlightthickness=0, insertbackground=C["azul"]
    )
    ent_token_admin.pack(fill="x", ipady=7, padx=8)
    ent_token_admin.bind("<FocusIn>",  lambda e: cont_token.config(highlightbackground=C["borde_focus"]))
    ent_token_admin.bind("<FocusOut>", lambda e: cont_token.config(highlightbackground=C["borde"]))

    lbl_token_nota = tk.Label(
        frame_admin_token,
        text="Requiere clave maestra provista por soporte técnico",
        font=("Segoe UI", 8, "italic"), fg=C["texto_muted"], bg=C["tarjeta"]
    )
    lbl_token_nota.pack(anchor="w", padx=12, pady=(0, 10))

    def _token_estado_normal():
        """Restaura el panel del token a su estado neutral."""
        frame_admin_token.config(bg=C["tarjeta"], highlightbackground=C["borde"])
        lbl_token_titulo.config(fg=C["azul"], bg=C["tarjeta"])
        cont_token.config(bg=C["tarjeta"], highlightbackground=C["borde"])
        ent_token_admin.config(bg=C["tarjeta"], fg=C["texto"], insertbackground=C["azul"])
        lbl_token_nota.config(fg=C["texto_muted"], bg=C["tarjeta"])

    def _token_estado_error():
        """Pone el panel del token en rojo cuando el código es incorrecto."""
        frame_admin_token.config(bg=C["peligro_suave"], highlightbackground=C["peligro_borde"])
        lbl_token_titulo.config(fg=C["peligro"], bg=C["peligro_suave"])
        cont_token.config(bg=C["peligro_suave"], highlightbackground=C["peligro"])
        ent_token_admin.config(bg=C["peligro_suave"], fg=C["peligro"], insertbackground=C["peligro"])
        lbl_token_nota.config(fg=C["peligro"], bg=C["peligro_suave"])

    # Al escribir, restaurar el color normal (quitar alerta de error anterior)
    ent_token_admin.bind("<KeyRelease>", lambda e: _token_estado_normal())

    # ---- PANEL INVITADO ----
    frame_invitado = tk.Frame(padding, bg=C["tarjeta"])

    tk.Frame(frame_invitado, bg="#FEF3C7", height=1).pack(fill="x", pady=(8, 0))
    tk.Label(
        frame_invitado, text="Datos adicionales del visitante",
        font=("Segoe UI", 9, "bold"), fg="#92400E", bg=C["tarjeta"]
    ).pack(anchor="w", pady=(6, 0))

    fila_nombre = tk.Frame(frame_invitado, bg=C["tarjeta"])
    fila_nombre.pack(fill="x")
    fila_nombre.columnconfigure(0, weight=1)
    fila_nombre.columnconfigure(1, weight=1)

    col_n = tk.Frame(fila_nombre, bg=C["tarjeta"])
    col_n.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    tk.Label(col_n, text="Nombre", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(8, 3))
    _, ent_nombre = crear_campo(col_n, "👤", "Nombre")

    col_a = tk.Frame(fila_nombre, bg=C["tarjeta"])
    col_a.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    tk.Label(col_a, text="Apellido", font=("Segoe UI", 9, "bold"),
             fg=C["texto_label"], bg=C["tarjeta"]).pack(anchor="w", pady=(8, 3))
    _, ent_apellido = crear_campo(col_a, "👤", "Apellido")

    # frame_invitado empieza oculto; solo aparece cuando el correo es de visitante/externo

    # ---- SET_TAB (definida aquí para tener acceso a todos los frames) ----
    def set_tab(tipo):
        var_tipo.set(tipo)
        if tipo == "lector":
            btn_tab_lector.config(bg=C["tab_activo_bg"], fg=C["tab_activo_fg"])
            btn_tab_admin.config(bg=C["tab_inactivo_bg"], fg=C["tab_inactivo_fg"])
            frame_admin_token.pack_forget()
            frame_invitado.pack_forget()
        else:
            btn_tab_admin.config(bg=C["tab_activo_bg"], fg=C["tab_activo_fg"])
            btn_tab_lector.config(bg=C["tab_inactivo_bg"], fg=C["tab_inactivo_fg"])
            frame_invitado.pack_forget()
            frame_admin_token.pack(fill="x", pady=(8, 0), after=fila_pass)
        # Actualizar el estado del correo según la pestaña activa
        verificar_correo()

    btn_tab_lector.config(command=lambda: set_tab("lector"))
    btn_tab_admin.config(command=lambda: set_tab("admin"))
    set_tab("lector")

    # ---- SEPARADOR + BOTONES ----
    tk.Frame(padding, bg=C["borde"], height=1).pack(fill="x", pady=(18, 0))

    frame_botones = tk.Frame(padding, bg=C["tarjeta"])
    frame_botones.pack(fill="x", pady=(14, 4))

    btn_registrar = tk.Button(
        frame_botones, text="Crear cuenta",
        font=("Segoe UI", 10, "bold"),
        bg=C["azul"], fg="white",
        relief="flat", cursor="hand2", bd=0, pady=9
    )
    btn_registrar.pack(fill="x", pady=(0, 8))

    btn_volver = tk.Button(
        frame_botones, text="← Volver al inicio de sesión",
        font=("Segoe UI", 9),
        bg=C["tarjeta"], fg=C["texto_muted"],
        relief="flat", cursor="hand2", bd=0, pady=7,
        highlightthickness=1, highlightbackground=C["borde"]
    )
    btn_volver.pack(fill="x")

    btn_registrar.bind("<Enter>", lambda e: btn_registrar.config(bg=C["azul_hover"]))
    btn_registrar.bind("<Leave>", lambda e: btn_registrar.config(bg=C["azul"]))
    btn_volver.bind("<Enter>",    lambda e: btn_volver.config(fg=C["texto"], highlightbackground=C["azul"]))
    btn_volver.bind("<Leave>",    lambda e: btn_volver.config(fg=C["texto_muted"], highlightbackground=C["borde"]))

    # ======================================================
    # 🔍 VERIFICACIÓN DE CORREO
    # ======================================================
    def verificar_correo(*args):
        correo = get_valor(ent_correo).lower()
        es_uleam = correo.endswith("@live.uleam.edu.ec") or correo.endswith("@uleam.edu.ec")

        # --- Modo Administrador: solo correos institucionales ---
        if var_tipo.get() == "admin":
            frame_invitado.pack_forget()
            if not correo or correo == "":
                lbl_correo_status.config(
                    text="⚠ Solo se aceptan correos institucionales ULEAM",
                    fg=C["advertencia"]
                )
            elif es_uleam:
                lbl_correo_status.config(
                    text="✓ Correo institucional válido para administrador",
                    fg=C["exito"]
                )
            elif len(correo) > 5 and "@" in correo:
                lbl_correo_status.config(
                    text="✗ Solo correos @live.uleam.edu.ec o @uleam.edu.ec",
                    fg=C["peligro"]
                )
            else:
                lbl_correo_status.config(
                    text="⚠ Solo se aceptan correos institucionales ULEAM",
                    fg=C["advertencia"]
                )
            return

        # --- Modo Lector ---
        if es_uleam:
            if correo in correos_validos:
                lbl_correo_status.config(
                    text="✓ Correo institucional verificado (ULEAM)", fg=C["exito"]
                )
                frame_invitado.pack_forget()
            else:
                lbl_correo_status.config(
                    text="⚠ Correo ULEAM no registrado en el padrón", fg=C["peligro"]
                )
                frame_invitado.pack(fill="x", after=lbl_correo_status)
        elif len(correo) > 5 and "@" in correo:
            lbl_correo_status.config(
                text="👤 Correo externo: completa los datos de visitante", fg=C["advertencia"]
            )
            frame_invitado.pack(fill="x", after=lbl_correo_status)
        else:
            lbl_correo_status.config(
                text="Ingresa tu correo electrónico", fg=C["texto_muted"]
            )
            frame_invitado.pack_forget()

    ent_correo.bind("<KeyRelease>", verificar_correo)

    # ======================================================
    # ✅ REGISTRO
    # ======================================================
    def registrar_usuario():
        cedula    = get_valor(ent_cedula)
        usuario   = get_valor(ent_user).lower()
        clave     = get_valor(ent_pass)
        confirmar = get_valor(ent_pass_conf)
        correo    = get_valor(ent_correo).lower()
        telefono  = get_valor(ent_telefono)
        tipo      = var_tipo.get()

        if not all([cedula, usuario, clave, correo, telefono]):
            messagebox.showerror("Campos incompletos", "Todos los campos principales son obligatorios.")
            return
        if not (5 <= len(cedula) <= 15):
            messagebox.showerror("Identificación inválida", "La cédula o pasaporte debe tener entre 5 y 15 caracteres.")
            return
        if len(clave) < 4:
            messagebox.showerror("Contraseña débil", "La contraseña debe tener al menos 4 caracteres.")
            return
        if clave != confirmar:
            messagebox.showerror("Contraseñas distintas", "Las contraseñas ingresadas no coinciden.")
            return
        if "@" not in correo or "." not in correo:
            messagebox.showerror("Correo inválido", "Por favor ingresa un correo electrónico válido.")
            return

        usuarios = cargar_usuarios()
        if usuario in usuarios:
            messagebox.showerror("Usuario ocupado", "Ese nombre de usuario ya está registrado.")
            return

        if tipo == "admin":
            es_inst = correo.endswith("@live.uleam.edu.ec") or correo.endswith("@uleam.edu.ec")
            if not es_inst:
                messagebox.showerror(
                    "Correo no institucional",
                    "Para crear una cuenta de administrador se requiere un "
                    "correo institucional ULEAM.\n\n"
                    "Dominios válidos:\n"
                    "  • @live.uleam.edu.ec\n"
                    "  • @uleam.edu.ec"
                )
                return
            if ent_token_admin.get().strip() != CLAVE_MAESTRA_ADMIN:
                _token_estado_error()
                messagebox.showerror("Código incorrecto", "El código de verificación de administrador es incorrecto.")
                return
            rol = "admin"
            nombre_completo = "Administrador del Sistema"
        else:
            es_inst = correo.endswith("@live.uleam.edu.ec") or correo.endswith("@uleam.edu.ec")
            if es_inst and correo in correos_validos:
                rol = "estudiante"
                nombre_completo = "Estudiante ULEAM Autoverificado"
            else:
                rol = "invitado"
                nom = get_valor(ent_nombre)
                ape = get_valor(ent_apellido)
                if not nom or not ape:
                    messagebox.showerror("Datos faltantes", "Como visitante, debes ingresar nombre y apellido.")
                    return
                nombre_completo = f"{nom} {ape}"

        usuarios[usuario] = {
            "clave":    clave,
            "rol":      rol,
            "cedula":   cedula,
            "nombre":   nombre_completo,
            "correo":   correo,
            "telefono": telefono,
        }
        guardar_usuarios(usuarios)
        messagebox.showinfo("¡Cuenta creada!", f"Registro exitoso.\nRol asignado: {rol.upper()}")
        volver_al_login()

    def volver_al_login():
        x = root.winfo_x()
        y = root.winfo_y()
        root.destroy()
        from presentacion.login import pantalla_login
        pantalla_login(posicion_actual=(x, y))

    btn_registrar.config(command=registrar_usuario)
    btn_volver.config(command=volver_al_login)

    # Navegación con tecla Enter
    def _next_after_pass_conf(e):
        if var_tipo.get() == "admin":
            ent_token_admin.focus_set()
        elif frame_invitado.winfo_ismapped():
            ent_nombre.focus_set()
        else:
            registrar_usuario()

    ent_user.bind("<Return>", lambda e: ent_correo.focus_set())
    ent_correo.bind("<Return>", lambda e: ent_cedula.focus_set())
    ent_cedula.bind("<Return>", lambda e: ent_telefono.focus_set())
    ent_telefono.bind("<Return>", lambda e: ent_pass.focus_set())
    ent_pass.bind("<Return>", lambda e: ent_pass_conf.focus_set())
    ent_pass_conf.bind("<Return>", _next_after_pass_conf)
    ent_token_admin.bind("<Return>", lambda e: registrar_usuario())
    ent_nombre.bind("<Return>", lambda e: ent_apellido.focus_set())
    ent_apellido.bind("<Return>", lambda e: registrar_usuario())

    root.mainloop()


if __name__ == "__main__":
    pantalla_registro()