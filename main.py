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
    "fondo":         "#F0F4F8",       # gris azulado muy suave
    "tarjeta":       "#FFFFFF",
    "borde":         "#D6DCE4",

    "marino":        "#1B2A4A",       # azul marino profundo (cabecera, título)
    "marino_hover":  "#243561",
    "acento":        "#C8923A",       # dorado cálido (detalle institucional)

    "verde":         "#1A6B45",
    "verde_hover":   "#145739",

    "rojo":          "#8B1A1A",
    "rojo_hover":    "#6E1515",

    "texto":         "#1A1D23",
    "texto_muted":   "#6B7280",
    "blanco":        "#FFFFFF",
}


# ======================================================
# 🖥️ PANTALLA PRINCIPAL
# ======================================================
def pantalla_principal(posicion_actual=None):
    root = tk.Tk()
    root.title("Sistema de Biblioteca — ULEAM")
    root.configure(bg=C["fondo"])
    root.resizable(False, False)
    root.minsize(480, 580)

    if posicion_actual:
        root.geometry(f"500x620+{posicion_actual[0]}+{posicion_actual[1]}")
    else:
        root.geometry("500x620")
        root.eval("tk::PlaceWindow . center")

    # ---- FUENTES ----
    f_titulo    = tkfont.Font(family="Segoe UI", size=18, weight="bold")
    f_subtitulo = tkfont.Font(family="Segoe UI", size=9,  slant="italic")
    f_btn       = tkfont.Font(family="Segoe UI", size=10, weight="bold")
    f_btn_sec   = tkfont.Font(family="Segoe UI", size=9)
    f_footer    = tkfont.Font(family="Segoe UI", size=8)

    # ======================================================
    # BANDA SUPERIOR (marino con línea dorada)
    # ======================================================
    banda = tk.Frame(root, bg=C["marino"], height=6)
    banda.pack(fill="x")

    linea_dorada = tk.Frame(root, bg=C["acento"], height=3)
    linea_dorada.pack(fill="x")

    # ======================================================
    # CUERPO CENTRAL
    # ======================================================
    cuerpo = tk.Frame(root, bg=C["fondo"])
    cuerpo.pack(fill="both", expand=True, padx=50, pady=30)

    # ---- TARJETA ----
    tarjeta = tk.Frame(
        cuerpo, bg=C["tarjeta"],
        highlightthickness=1, highlightbackground=C["borde"]
    )
    tarjeta.pack(fill="both", expand=True)

    inner = tk.Frame(tarjeta, bg=C["tarjeta"])
    inner.pack(fill="both", expand=True, padx=32, pady=28)

    # ---- LOGO ----
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_logo = os.path.join(carpeta_actual, "presentacion", "logo.jpg")

    if os.path.exists(ruta_logo):
        try:
            img = Image.open(ruta_logo).resize((100, 100), Image.Resampling.LANCZOS)

            # Marco circular simulado con borde marino
            marco = tk.Frame(
                inner, bg=C["marino"],
                width=108, height=108,
                highlightthickness=0
            )
            marco.pack(pady=(0, 10))
            marco.pack_propagate(False)

            foto = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(marco, image=foto, bg=C["marino"])
            lbl_logo.place(relx=0.5, rely=0.5, anchor="center")
            lbl_logo.image = foto
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            _icono_fallback(inner)
    else:
        _icono_fallback(inner)

    # ---- TÍTULOS ----
    tk.Label(
        inner, text="BIBLIOTECA ULEAM",
        font=f_titulo, fg=C["marino"], bg=C["tarjeta"]
    ).pack(pady=(4, 2))

    # Línea decorativa dorada bajo el título
    linea = tk.Frame(inner, bg=C["acento"], height=2, width=180)
    linea.pack(pady=(0, 6))

    tk.Label(
        inner, text="Sistema de Gestión de Libros y Usuarios",
        font=f_subtitulo, fg=C["texto_muted"], bg=C["tarjeta"]
    ).pack(pady=(0, 20))

    tk.Frame(inner, bg=C["borde"], height=1).pack(fill="x", pady=(0, 20))

    # ======================================================
    # BOTONES
    # ======================================================
    def _btn_principal(parent, texto, color, hover, comando):
        btn = tk.Button(
            parent, text=texto, font=f_btn,
            bg=color, fg=C["blanco"],
            relief="flat", cursor="hand2",
            bd=0, pady=11, command=comando
        )
        btn.pack(fill="x", pady=(0, 10))
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _btn_secundario(parent, texto, comando):
        btn = tk.Button(
            parent, text=texto, font=f_btn_sec,
            bg=C["tarjeta"], fg=C["texto_muted"],
            relief="flat", cursor="hand2",
            bd=0, pady=9,
            highlightthickness=1, highlightbackground=C["borde"],
            command=comando
        )
        btn.pack(fill="x", pady=(0, 6))
        btn.bind("<Enter>", lambda e: btn.config(
            fg=C["texto"], highlightbackground=C["marino"]
        ))
        btn.bind("<Leave>", lambda e: btn.config(
            fg=C["texto_muted"], highlightbackground=C["borde"]
        ))
        return btn

    # Navegación
    def abrir_login():
        x, y = _pos(root)
        root.destroy()
        login.pantalla_login(posicion_actual=(x, y))

    def abrir_registro():
        x, y = _pos(root)
        root.destroy()
        registro.pantalla_registro(posicion_actual=(x, y))

    _btn_principal(inner, "Iniciar sesión",   C["marino"], C["marino_hover"], abrir_login)
    _btn_principal(inner, "Crear una cuenta", C["verde"],  C["verde_hover"],  abrir_registro)

    tk.Frame(inner, bg=C["borde"], height=1).pack(fill="x", pady=(4, 12))

    _btn_secundario(inner, "Salir del sistema", root.destroy)

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
def _icono_fallback(parent):
    """Muestra un ícono emoji si no hay logo."""
    circulo = tk.Frame(parent, bg="#DBEAFE", width=80, height=80)
    circulo.pack(pady=(0, 10))
    circulo.pack_propagate(False)
    tk.Label(
        circulo, text="📚",
        font=("Segoe UI", 30), bg="#DBEAFE"
    ).place(relx=0.5, rely=0.5, anchor="center")


def _pos(ventana):
    try:
        return ventana.winfo_x(), ventana.winfo_y()
    except Exception:
        return 0, 0


if __name__ == "__main__":
    pantalla_principal()