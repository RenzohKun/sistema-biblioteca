import tkinter as tk
from tkinter import font as tkfont
from presentacion import login
from presentacion import registro
import os
from PIL import Image, ImageTk

# ======================================================
# 🎨 PALETA — tono académico/editorial
# ======================================================
C = {
    "fondo":         "#F0F4F8",
    "tarjeta":       "#FFFFFF",
    "borde":         "#D6DCE4",

    "marino":        "#1B2A4A",
    "marino_hover":  "#243561",
    "acento":        "#C8923A",

    "verde":         "#1A6B45",
    "verde_hover":   "#145739",

    "rojo":          "#8B1A1A",
    "rojo_hover":    "#6E1515",

    "texto":         "#1A1D23",
    "texto_muted":   "#6B7280",
    "blanco":        "#FFFFFF",
}


# ======================================================
# 🖥️ PANTALLA PRINCIPAL — Layout horizontal (imagen | botones)
# ======================================================
def pantalla_principal(posicion_actual=None):
    root = tk.Tk()
    root.title("Sistema de Biblioteca — ULEAM")
    root.configure(bg=C["fondo"])
    root.resizable(True, True)

    # Ventana más ancha para el layout lado a lado
    if posicion_actual:
        root.geometry(f"820x520+{posicion_actual[0]}+{posicion_actual[1]}")
    else:
        root.geometry("820x520")
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"820x520+{(sw-820)//2}+{(sh-520)//2}")

    # ---- FUENTES ----
    f_titulo    = tkfont.Font(family="Segoe UI", size=20, weight="bold")
    f_subtitulo = tkfont.Font(family="Segoe UI", size=9,  slant="italic")
    f_inst      = tkfont.Font(family="Segoe UI", size=8)
    f_btn       = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    f_btn_sec   = tkfont.Font(family="Segoe UI", size=9)
    f_footer    = tkfont.Font(family="Segoe UI", size=8)

    # ======================================================
    # BANDA SUPERIOR
    # ======================================================
    tk.Frame(root, bg=C["marino"], height=6).pack(fill="x")
    tk.Frame(root, bg=C["acento"], height=3).pack(fill="x")

    # ======================================================
    # CUERPO PRINCIPAL — dos columnas
    # ======================================================
    cuerpo = tk.Frame(root, bg=C["fondo"])
    cuerpo.pack(fill="both", expand=True)

    # -------------------------------------------------------
    # COLUMNA IZQUIERDA — panel marino con imagen
    # -------------------------------------------------------
    panel_izq = tk.Frame(cuerpo, bg=C["marino"], width=380)
    panel_izq.pack(side="left", fill="both")
    panel_izq.pack_propagate(False)

    # Contenedor interior centrado verticalmente
    inner_izq = tk.Frame(panel_izq, bg=C["marino"])
    inner_izq.place(relx=0.5, rely=0.5, anchor="center")

    # ---- LOGO / IMAGEN ----
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_logo = os.path.join(carpeta_actual, "presentacion", "logo.jpg")

    if os.path.exists(ruta_logo):
        try:
            img = Image.open(ruta_logo).resize((160, 160), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(image=img, master=root)

            # Marco con borde dorado simulado
            marco = tk.Frame(
                inner_izq, bg=C["acento"],
                width=172, height=172,
            )
            marco.pack(pady=(0, 22))
            marco.pack_propagate(False)

            lbl_logo = tk.Label(marco, image=foto, bg=C["marino"])
            lbl_logo.place(relx=0.5, rely=0.5, anchor="center")
            lbl_logo.image = foto   # evitar recolección de basura
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            _icono_fallback_grande(inner_izq)
    else:
        _icono_fallback_grande(inner_izq)

    # Nombre de la institución
    tk.Label(
        inner_izq, text="BIBLIOTECA ULEAM",
        font=tkfont.Font(family="Segoe UI", size=16, weight="bold"),
        fg=C["blanco"], bg=C["marino"]
    ).pack(pady=(0, 4))

    # Línea dorada decorativa
    tk.Frame(inner_izq, bg=C["acento"], height=2, width=160).pack(pady=(0, 8))

    tk.Label(
        inner_izq,
        text="Universidad Laica Eloy Alfaro\nde Manabí",
        font=f_inst, fg="#8FA8C8", bg=C["marino"], justify="center"
    ).pack()

    # Separador vertical dorado entre columnas
    tk.Frame(cuerpo, bg=C["acento"], width=3).pack(side="left", fill="y")

    # -------------------------------------------------------
    # COLUMNA DERECHA — panel blanco con botones
    # -------------------------------------------------------
    panel_der = tk.Frame(cuerpo, bg=C["tarjeta"])
    panel_der.pack(side="left", fill="both", expand=True)

    # Contenedor interior centrado
    inner_der = tk.Frame(panel_der, bg=C["tarjeta"])
    inner_der.place(relx=0.5, rely=0.5, anchor="center")

    # Saludo
    tk.Label(
        inner_der, text="Bienvenido",
        font=f_titulo, fg=C["marino"], bg=C["tarjeta"]
    ).pack(pady=(0, 4))

    tk.Label(
        inner_der, text="Sistema de Gestión de Libros y Usuarios",
        font=f_subtitulo, fg=C["texto_muted"], bg=C["tarjeta"]
    ).pack(pady=(0, 24))

    tk.Frame(inner_der, bg=C["borde"], height=1, width=280).pack(pady=(0, 24))

    # ---- BOTONES DE ACCESO ----
    def abrir_login():
        x, y = _pos(root)
        root.destroy()
        login.pantalla_login(posicion_actual=(x, y))

    def abrir_registro():
        x, y = _pos(root)
        root.destroy()
        registro.pantalla_registro(posicion_actual=(x, y))

    # Botón: Iniciar sesión
    btn_login = tk.Button(
        inner_der, text="🔑  Iniciar sesión",
        font=f_btn,
        bg=C["marino"], fg=C["blanco"],
        relief="flat", cursor="hand2",
        bd=0, pady=13, width=22,
        command=abrir_login
    )
    btn_login.pack(pady=(0, 12))
    btn_login.bind("<Enter>", lambda e: btn_login.config(bg=C["marino_hover"]))
    btn_login.bind("<Leave>", lambda e: btn_login.config(bg=C["marino"]))

    # Botón: Crear cuenta
    btn_reg = tk.Button(
        inner_der, text="📝  Crear una cuenta",
        font=f_btn,
        bg=C["verde"], fg=C["blanco"],
        relief="flat", cursor="hand2",
        bd=0, pady=13, width=22,
        command=abrir_registro
    )
    btn_reg.pack(pady=(0, 20))
    btn_reg.bind("<Enter>", lambda e: btn_reg.config(bg=C["verde_hover"]))
    btn_reg.bind("<Leave>", lambda e: btn_reg.config(bg=C["verde"]))

    tk.Frame(inner_der, bg=C["borde"], height=1, width=280).pack(pady=(0, 16))

    # Botón: Salir
    btn_salir = tk.Button(
        inner_der, text="Salir del sistema",
        font=f_btn_sec,
        bg=C["tarjeta"], fg=C["texto_muted"],
        relief="flat", cursor="hand2",
        bd=0, pady=9, width=22,
        highlightthickness=1, highlightbackground=C["borde"],
        command=root.destroy
    )
    btn_salir.pack()
    btn_salir.bind("<Enter>", lambda e: btn_salir.config(
        fg=C["texto"], highlightbackground=C["marino"]
    ))
    btn_salir.bind("<Leave>", lambda e: btn_salir.config(
        fg=C["texto_muted"], highlightbackground=C["borde"]
    ))

    # ======================================================
    # FOOTER
    # ======================================================
    footer = tk.Frame(root, bg=C["marino"], height=28)
    footer.pack(fill="x", side="bottom")
    tk.Label(
        footer,
        text="© ULEAM — Sistema de Biblioteca",
        font=f_footer, fg="#8FA8C8", bg=C["marino"]
    ).pack(pady=6)

    root.mainloop()


# ======================================================
# HELPERS
# ======================================================
def _icono_fallback_grande(parent):
    """Ícono grande de fallback cuando no hay logo."""
    circulo = tk.Frame(parent, bg="#1F3558", width=140, height=140)
    circulo.pack(pady=(0, 22))
    circulo.pack_propagate(False)
    tk.Label(
        circulo, text="📚",
        font=("Segoe UI", 52), bg="#1F3558"
    ).place(relx=0.5, rely=0.5, anchor="center")


def _pos(ventana):
    try:
        return ventana.winfo_x(), ventana.winfo_y()
    except Exception:
        return 0, 0


if __name__ == "__main__":
    pantalla_principal()