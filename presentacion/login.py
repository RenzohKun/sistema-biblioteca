import tkinter as tk
from tkinter import messagebox
import json
import os
import sys

# --- RUTAS ---
CARPETA_RAIZ     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO_USUARIOS = os.path.join(CARPETA_RAIZ, "datos", "usuarios.json")

# ✅ CORRECCIÓN: agrega la raíz del proyecto al path
if CARPETA_RAIZ not in sys.path:
    sys.path.insert(0, CARPETA_RAIZ)

# ======================================================
# 🎨 PALETA (misma que registro.py)
# ======================================================
C = {
    "fondo":        "#F7F8FA",
    "tarjeta":      "#FFFFFF",
    "borde":        "#DDE1E7",
    "borde_focus":  "#185FA5",

    "texto":        "#1A1D23",
    "texto_muted":  "#6B7280",
    "texto_label":  "#374151",

    "azul":         "#185FA5",
    "azul_hover":   "#124D8A",

    "exito":        "#1A7F4B",
    "peligro":      "#C0392B",
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
        messagebox.showerror("Error", f"No se pudo cargar usuarios: {e}")
    return {}

# ======================================================
# 🏗️ COMPONENTE: campo con ícono
# ======================================================
def crear_campo(parent, icono, placeholder, ocultar=False):
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

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry._placeholder = placeholder
    return contenedor, entry


def get_valor(entry):
    val = entry.get().strip()
    return "" if val == getattr(entry, "_placeholder", None) else val


# ======================================================
# 🖥️ PANTALLA LOGIN
# ======================================================
def pantalla_login(posicion_actual=None):
    root = tk.Tk()
    root.title("Iniciar sesión — Biblioteca ULEAM")
    root.configure(bg=C["fondo"])
    root.resizable(True, True)
    root.minsize(380, 480)

    if posicion_actual:
        root.geometry(f"480x560+{posicion_actual[0]}+{posicion_actual[1]}")
    else:
        root.geometry("480x560")
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"480x560+{(sw-480)//2}+{(sh-560)//2}")

    # ---- CANVAS SCROLLABLE ----
    canvas = tk.Canvas(root, bg=C["fondo"], bd=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame_scroll = tk.Frame(canvas, bg=C["fondo"])
    id_ventana = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    canvas.bind("<Configure>", lambda e: canvas.itemconfig(id_ventana, width=e.width))
    frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ---- COLUMNA CENTRAL ----
    col_centro = tk.Frame(frame_scroll, bg=C["fondo"])
    col_centro.pack(fill="both", expand=True, padx=50, pady=40)

    # ---- TARJETA ----
    tarjeta = tk.Frame(
        col_centro, bg=C["tarjeta"],
        highlightthickness=1, highlightbackground=C["borde"]
    )
    tarjeta.pack(fill="both", expand=True)

    padding = tk.Frame(tarjeta, bg=C["tarjeta"])
    padding.pack(fill="both", expand=True, padx=30, pady=28)

    # ---- CABECERA ----
    circulo = tk.Frame(padding, bg="#DBEAFE", width=52, height=52)
    circulo.pack()
    circulo.pack_propagate(False)
    tk.Label(circulo, text="📚", font=("Segoe UI", 22), bg="#DBEAFE").place(
        relx=0.5, rely=0.5, anchor="center"
    )

    tk.Label(
        padding, text="Iniciar sesión",
        font=("Segoe UI", 17, "bold"),
        fg=C["texto"], bg=C["tarjeta"]
    ).pack(pady=(10, 2))

    tk.Label(
        padding, text="Sistema de Gestión de Biblioteca ULEAM",
        font=("Segoe UI", 9), fg=C["texto_muted"], bg=C["tarjeta"]
    ).pack(pady=(0, 16))

    tk.Frame(padding, bg=C["borde"], height=1).pack(fill="x", pady=(0, 18))

    # ---- CAMPOS ----
    tk.Label(
        padding, text="Usuario",
        font=("Segoe UI", 9, "bold"), fg=C["texto_label"], bg=C["tarjeta"]
    ).pack(anchor="w", pady=(0, 3))
    _, ent_usuario = crear_campo(padding, "👤", "Nombre de usuario")

    tk.Label(
        padding, text="Contraseña",
        font=("Segoe UI", 9, "bold"), fg=C["texto_label"], bg=C["tarjeta"]
    ).pack(anchor="w", pady=(12, 3))
    _, ent_contra = crear_campo(padding, "🔒", "Tu contraseña", ocultar=True)

    # Label de error (oculto por defecto)
    lbl_error = tk.Label(
        padding, text="",
        font=("Segoe UI", 9), fg=C["peligro"], bg=C["tarjeta"]
    )
    lbl_error.pack(anchor="w", pady=(6, 0))

    # ---- SEPARADOR + BOTONES ----
    tk.Frame(padding, bg=C["borde"], height=1).pack(fill="x", pady=(12, 0))

    frame_botones = tk.Frame(padding, bg=C["tarjeta"])
    frame_botones.pack(fill="x", pady=(14, 0))

    btn_ingresar = tk.Button(
        frame_botones, text="Ingresar",
        font=("Segoe UI", 10, "bold"),
        bg=C["azul"], fg="white",
        relief="flat", cursor="hand2", bd=0, pady=9
    )
    btn_ingresar.pack(fill="x", pady=(0, 8))

    btn_registro = tk.Button(
        frame_botones, text="¿No tienes cuenta? Regístrate",
        font=("Segoe UI", 9),
        bg=C["tarjeta"], fg=C["texto_muted"],
        relief="flat", cursor="hand2", bd=0, pady=7,
        highlightthickness=1, highlightbackground=C["borde"]
    )
    btn_registro.pack(fill="x", pady=(0, 6))

    btn_volver = tk.Button(
        frame_botones, text="← Volver al menú principal",
        font=("Segoe UI", 9),
        bg=C["tarjeta"], fg=C["texto_muted"],
        relief="flat", cursor="hand2", bd=0, pady=7,
        highlightthickness=1, highlightbackground=C["borde"]
    )
    btn_volver.pack(fill="x")

    # Hover
    btn_ingresar.bind("<Enter>", lambda e: btn_ingresar.config(bg=C["azul_hover"]))
    btn_ingresar.bind("<Leave>", lambda e: btn_ingresar.config(bg=C["azul"]))

    for btn in (btn_registro, btn_volver):
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg=C["texto"], highlightbackground=C["azul"]))
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg=C["texto_muted"], highlightbackground=C["borde"]))

    # ======================================================
    # 🔐 LÓGICA DE LOGIN
    # ======================================================
    def ejecutar_login(*args):
        usuario = get_valor(ent_usuario)
        clave   = get_valor(ent_contra)

        if not usuario or not clave:
            lbl_error.config(text="⚠ Completa todos los campos antes de continuar.")
            return

        usuarios = cargar_usuarios()

        if usuario not in usuarios:
            lbl_error.config(text="✗ Usuario no encontrado. Verifica tu nombre de usuario.")
            ent_usuario.focus_set()
            return

        if usuarios[usuario]["clave"] != clave:
            lbl_error.config(text="✗ Contraseña incorrecta. Inténtalo de nuevo.")
            ent_contra.delete(0, "end")
            ent_contra.focus_set()
            return

        # Login exitoso
        lbl_error.config(text="")
        datos  = usuarios[usuario]
        rol    = datos.get("rol", "invitado")
        nombre = datos.get("nombre", usuario)

        messagebox.showinfo(
            "Bienvenido",
            f"Sesión iniciada correctamente.\n\n"
            f"Usuario: {usuario}\n"
            f"Rol: {rol.upper()}\n"
            f"Nombre: {nombre}"
        )

        x = root.winfo_x()
        y = root.winfo_y()
        root.destroy()

        # ✅ Navegar según el rol — 4 roles posibles: admin, bibliotecario, usuario, invitado
        if rol == "admin":
            try:
                from presentacion.admin import VentanaAdministrador
                root_admin = tk.Tk()
                root_admin.geometry(f"+{x}+{y}")
                # Se pasa usuario_login explícitamente para que el panel sepa con certeza
                # quién inició sesión (necesario para la protección de auto-degradación de rol)
                VentanaAdministrador(root_admin, nombre_admin=nombre, usuario_login=usuario)
                root_admin.mainloop()
            except ImportError as e:
                messagebox.showerror("Error de importación", f"No se pudo cargar el módulo Admin:\n{e}")

        elif rol == "bibliotecario":
            try:
                # Pantalla dedicada para bibliotecario (gestión de libros, sin acceso
                # a usuarios ni roles).
                from presentacion.menu_bibliotecario import pantalla_bibliotecario
                pantalla_bibliotecario(usuario=usuario, posicion_actual=(x, y), nombre=nombre)
            except ImportError:
                messagebox.showinfo(
                    "En construcción",
                    "El panel de bibliotecario aún no está disponible.\n"
                    "Se mostrará el menú de usuario mientras tanto."
                )
                try:
                    from presentacion.menu_usuario import pantalla_usuario
                    pantalla_usuario(usuario=usuario, posicion_actual=(x, y))
                except ImportError as e:
                    messagebox.showerror("Error de importación", f"No se pudo cargar el menú de usuario:\n{e}")

        else:  # "usuario" o "invitado"
            try:
                from presentacion.menu_usuario import pantalla_usuario
                pantalla_usuario(usuario=usuario, posicion_actual=(x, y))
            except ImportError as e:
                messagebox.showerror("Error de importación", f"No se pudo cargar el menú de usuario:\n{e}")

    def ir_a_registro():
        x = root.winfo_x()
        y = root.winfo_y()
        root.destroy()
        try:
            from presentacion.registro import pantalla_registro
            pantalla_registro(posicion_actual=(x, y))
        except ImportError as e:
            messagebox.showerror("Error de importación", f"No se pudo cargar registro:\n{e}")

    def volver_al_menu():
        x = root.winfo_x()
        y = root.winfo_y()
        root.destroy()
        try:
            from main import pantalla_principal
            pantalla_principal(posicion_actual=(x, y))
        except ImportError as e:
            messagebox.showerror("Error de importación", f"No se pudo cargar el menú principal:\n{e}")

    # Bindings
    btn_ingresar.config(command=ejecutar_login)
    btn_registro.config(command=ir_a_registro)
    btn_volver.config(command=volver_al_menu)

    # Enter navega al siguiente campo y luego dispara el login
    ent_usuario.bind("<Return>", lambda e: ent_contra.focus_set())
    ent_contra.bind("<Return>",  lambda e: ejecutar_login())

    root.mainloop()


if __name__ == "__main__":
    pantalla_login()