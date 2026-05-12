import tkinter as tk
from tkinter import messagebox
from library import main
import json
import os

ARCHIVO_USUARIOS = "usuarios.json"

def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON"""
    try:
        if os.path.exists(ARCHIVO_USUARIOS):
            with open(ARCHIVO_USUARIOS, "r") as f:
                return json.load(f)
    except:
        pass
    # Si no existe, retorna usuarios por defecto
    return {"admin": "1234", "estudiante": "manta2026"}

def pantalla_login():
    def validar_acceso():
        usuario = ent_user.get().strip()
        clave = ent_pass.get()
        
        usuarios = cargar_usuarios()
        
        if usuario in usuarios and usuarios[usuario] == clave:
            root_login.destroy() # Cerramos el login
            main() # Abrimos la biblioteca principal
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def ir_a_registro():
        root_login.destroy()
        from registro import pantalla_registro
        pantalla_registro()

    root_login = tk.Tk()
    root_login.title("Login - Sistema Biblioteca")
    root_login.geometry("300x300")
    root_login.eval('tk::PlaceWindow . center') # Centrar ventana

    tk.Label(root_login, text="ACCESO AL SISTEMA", font=("Arial", 12, "bold")).pack(pady=15)

    tk.Label(root_login, text="Usuario:").pack()
    ent_user = tk.Entry(root_login)
    ent_user.pack(pady=5)

    tk.Label(root_login, text="Contraseña:").pack()
    ent_pass = tk.Entry(root_login, show="*") # Ocultar caracteres
    ent_pass.pack(pady=5)

    tk.Button(root_login, text="Entrar", bg="#2c3e50", fg="white", width=15, 
              command=validar_acceso).pack(pady=10)
    
    tk.Button(root_login, text="Registrarse", bg="#27ae60", fg="white", width=15,
              command=ir_a_registro).pack(pady=5)

    root_login.mainloop()

# MODIFICACIÓN AL FINAL DE TU ARCHIVO:
if __name__ == "__main__":
    pantalla_login() # Ahora el programa empieza con el Login