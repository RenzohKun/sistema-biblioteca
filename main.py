import tkinter as tk
from Vista import login
from Vista import registro
import os

def pantalla_principal():
    # Creación de la ventana principal
    root_principal = tk.Tk()
    root_principal.title("Sistema de Biblioteca - Menú Principal")
    root_principal.geometry("550x600")
    root_principal.resizable(False, False)
    
    # Fondo blanco limpio e institucional
    COLOR_FONDO = "#ffffff"
    root_principal.configure(bg=COLOR_FONDO)
    
    # Centrar la ventana perfectamente en la pantalla
    root_principal.eval('tk::PlaceWindow . center')     

    # --- CONTENEDOR PARA LOGO E INFORMACIÓN ---
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_logo = os.path.join(carpeta_actual, "logo.jpg") 
    
    imagen_logo = None 
    
    # 1. Zona del Logo (Reducido dinámicamente)
    if os.path.exists(ruta_logo):
        try:
            # Cargamos la imagen original
            imagen_original = tk.PhotoImage(file=ruta_logo)
            
            # .subsample(2, 2) reduce la imagen a la mitad pixel por pixel de forma limpia
            imagen_logo = imagen_original.subsample(2, 2)
            
            lbl_logo = tk.Label(root_principal, image=imagen_logo, bg=COLOR_FONDO)
            lbl_logo.pack(pady=(30, 5)) # Margen superior moderado
        except Exception as e:
            print(f"Nota: No se pudo procesar o achicar el logo: {e}")

    # 2. Textos Institucionales
    tk.Label(
        root_principal,
        text="SISTEMA DE BIBLIOTECA",
        font=("Arial", 18, "bold"),
        fg="#2c3e50",
        bg=COLOR_FONDO
    ).pack(pady=(5, 2))

    tk.Label(
        root_principal,
        text="Gestión de Libros y Control de Usuarios",
        font=("Arial", 11, "italic"),
        fg="#7f8c8d",
        bg=COLOR_FONDO
    ).pack(pady=(0, 20))

    # --- LÓGICA DE NAVEGACIÓN ---
    def abrir_login():
        root_principal.destroy()
        login.pantalla_login()

    def abrir_registro():
        root_principal.destroy()
        registro.pantalla_registro()

    # --- BOTONES INTERACTIVOS ---
    btn_login = tk.Button(
        root_principal,
        text="Iniciar Sesión",
        bg="#34495e",
        fg="white",
        font=("Arial", 12, "bold"),
        width=28,
        pady=10,
        relief="flat",
        cursor="hand2",
        command=abrir_login
    )
    btn_login.pack(pady=6)

    btn_registrar = tk.Button(
        root_principal,
        text="Crear una Cuenta",
        bg="#2ecc71",
        fg="white",
        font=("Arial", 12, "bold"),
        width=28,
        pady=10,
        relief="flat",
        cursor="hand2",
        command=abrir_registro
    )
    btn_registrar.pack(pady=6)

    # Línea divisoria de diseño sutil
    separador = tk.Frame(root_principal, height=1, bg="#eaeded", width=360)
    separador.pack(pady=20)

    # Botón SALIR (Ya visible en pantalla)
    btn_salir = tk.Button(
        root_principal,
        text="Salir del Sistema",
        bg="#e74c3c",
        fg="white",
        font=("Arial", 11, "bold"),
        width=28,
        pady=8,
        relief="flat",
        cursor="hand2",
        command=root_principal.destroy
    )
    btn_salir.pack(pady=(0, 20))

    # Mantener la referencia en la RAM para que Tkinter no borre la imagen modificada
    root_principal.imagen_logo = imagen_logo
    root_principal.mainloop()

if __name__ == "__main__":
    pantalla_principal()