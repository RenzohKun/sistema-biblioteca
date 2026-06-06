# login.py
import tkinter as tk
from tkinter import messagebox
from library import main
from Admin import VentanaAdministrador
import json
import os

ARCHIVO_USUARIOS = "usuarios.json"

def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON adaptado al nuevo formato de objetos"""
    try:
        if os.path.exists(ARCHIVO_USUARIOS):
            with open(ARCHIVO_USUARIOS, "r") as f:
                usuarios = json.load(f)
                
                # Sello de seguridad: Nos aseguramos de que el admin siempre exista con el nuevo formato
                if "admin" not in usuarios:
                    usuarios["admin"] = {
                        "clave": "1234",
                        "rol": "admin",
                        "cedula": "0000000000",
                        "nombre": "Administrador General"
                    }
                return usuarios
    except:
        pass
    
    # Formato por defecto estructurado si el archivo no existe o está corrupto
    return {
        "admin": {
            "clave": "1234",
            "rol": "admin",
            "cedula": "0000000000",
            "nombre": "Administrador General"
        },
        "estudiante": {
            "clave": "manta2026",
            "rol": "estudiante",
            "cedula": "1312345678",
            "nombre": "Estudiante de Prueba"
        }
    }

def pantalla_login():
    def validar_acceso():
        # .lower() convierte a minúsculas para evitar errores de tipeo con 'Admin' o 'ADMIN'
        usuario = ent_user.get().strip().lower()
        clave = ent_pass.get()
        
        usuarios = cargar_usuarios()
        
        # Validación leyendo el nuevo esquema estructurado: usuarios[usuario]["clave"]
        if usuario in usuarios and usuarios[usuario]["clave"] == clave:
            root_login.destroy() # Cerramos la ventana de login
            
            # Extraemos el rol guardado en el sub-diccionario del usuario
            rol_usuario = usuarios[usuario]["rol"]
            
            # --- DERIVACIÓN LOGICA POR ROL ---
            if rol_usuario == "admin":
                # Si es administrador, despliega el panel de control avanzado
                root_admin = tk.Tk()
                app = VentanaAdministrador(root_admin, usuario)
                root_admin.mainloop()
            else:
                # Si es estudiante o invitado, va a la biblioteca convencional de library.py
                main() 
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def ir_a_registro():
        root_login.destroy()
        from registro import pantalla_registro
        pantalla_registro()

    # --- DISEÑO DE LA VENTANA ---
    root_login = tk.Tk()
    root_login.title("Login - Sistema Biblioteca")
    root_login.geometry("320x340")
    root_login.resizable(False, False)
    root_login.eval('tk::PlaceWindow . center') # Centrar ventana

    tk.Label(root_login, text="ACCESO AL SISTEMA", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=20)

    tk.Label(root_login, text="Usuario:", font=("Arial", 10, "bold")).pack()
    ent_user = tk.Entry(root_login, width=28, justify="center")
    ent_user.pack(pady=5)

    tk.Label(root_login, text="Contraseña:", font=("Arial", 10, "bold")).pack()
    ent_pass = tk.Entry(root_login, show="*", width=28, justify="center") 
    ent_pass.pack(pady=5)

    tk.Button(root_login, text="Entrar", bg="#2c3e50", fg="white", font=("Arial", 10, "bold"), width=18, pady=5,
              command=validar_acceso, relief="flat", cursor="hand2").pack(pady=15)
    
    tk.Button(root_login, text="Registrarse", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=18, pady=5,
              command=ir_a_registro, relief="flat", cursor="hand2").pack(pady=5)

    root_login.mainloop()

if __name__ == "__main__":
    pantalla_login()