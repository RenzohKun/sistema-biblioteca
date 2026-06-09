import tkinter as tk
from presentacion import login
from presentacion import registro
import os
# Importamos Pillow para soportar formatos .jpg de manera limpia
from PIL import Image, ImageTk 

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
    # CORRECCIÓN 1: La ruta ahora apunta correctamente adentro de "presentacion"
    ruta_logo = os.path.join(carpeta_actual, "presentacion", "logo.jpg") 
    
    imagen_logo = None 
    
    # 1. Zona del Logo (Carga y reajuste con Pillow)
    if os.path.exists(ruta_logo):
        try:
            # CORRECCIÓN 2: Abrimos el .jpg usando Pillow
            img_original = Image.open(ruta_logo)
            
            # Redimensionamos la imagen de forma limpia a un tamaño ideal para el menú (ejm: 130x130)
            img_redimensionada = img_original.resize((130, 130), Image.Resampling.LANCZOS)
            
            # Convertimos al formato compatible con Tkinter
            imagen_logo = ImageTk.PhotoImage(img_redimensionada)
            
            lbl_logo = tk.Label(root_principal, image=imagen_logo, bg=COLOR_FONDO)
            lbl_logo.pack(pady=(30, 5)) # Margen superior moderado
            
            # CORRECCIÓN 3: Anclamos la referencia en el mismo Label para evitar el Garbage Collector
            lbl_logo.image = imagen_logo 
            
        except Exception as e:
            print(f"Nota: No se pudo procesar o achicar el logo con Pillow: {e}")
    else:
        print(f"Advertencia: No se encontró el archivo del logo en: {ruta_logo}")

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
        root_principal.quit()
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

    # Botón SALIR
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

    # Guardamos también la referencia global en la raíz por seguridad
    root_principal.imagen_logo = imagen_logo
    root_principal.mainloop()

if __name__ == "__main__":
    pantalla_principal()