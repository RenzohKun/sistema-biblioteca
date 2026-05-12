import tkinter as tk
from tkinter import messagebox
import json
import os

ARCHIVO_USUARIOS = "usuarios.json"

def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON"""
    try:
        if os.path.exists(ARCHIVO_USUARIOS):
            with open(ARCHIVO_USUARIOS, "r") as f:
                return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    return {}

def guardar_usuarios(usuarios):
    """Guarda los usuarios en el archivo JSON"""
    try:
        with open(ARCHIVO_USUARIOS, "w") as f:
            json.dump(usuarios, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar usuarios: {e}")

def pantalla_registro():
    """Crea la interfaz de registro de nuevos usuarios"""
    
    def registrar_usuario():
        usuario = ent_user.get().strip()
        clave = ent_pass.get()
        confirmar_clave = ent_pass_conf.get()
        
        # Validaciones
        if not usuario or not clave:
            messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
            return
        
        if len(clave) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
        
        if clave != confirmar_clave:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        usuarios = cargar_usuarios()
        
        if usuario in usuarios:
            messagebox.showerror("Error", "El usuario ya existe")
            return
        
        # Registrar nuevo usuario
        usuarios[usuario] = clave
        guardar_usuarios(usuarios)
        messagebox.showinfo("Éxito", f"Usuario '{usuario}' registrado correctamente")
        
        # Limpiar campos
        ent_user.delete(0, tk.END)
        ent_pass.delete(0, tk.END)
        ent_pass_conf.delete(0, tk.END)
    
    def volver_al_login():
        root_registro.destroy()
        from login import pantalla_login
        pantalla_login()
    
    root_registro = tk.Tk()
    root_registro.title("Registro - Sistema Biblioteca")
    root_registro.geometry("350x350")
    root_registro.eval('tk::PlaceWindow . center')
    
    tk.Label(root_registro, text="REGISTRO DE NUEVO USUARIO", 
             font=("Arial", 12, "bold")).pack(pady=15)
    
    tk.Label(root_registro, text="Usuario:").pack()
    ent_user = tk.Entry(root_registro, width=30)
    ent_user.pack(pady=5)
    
    tk.Label(root_registro, text="Contraseña:").pack()
    ent_pass = tk.Entry(root_registro, show="*", width=30)
    ent_pass.pack(pady=5)
    
    tk.Label(root_registro, text="Confirmar Contraseña:").pack()
    ent_pass_conf = tk.Entry(root_registro, show="*", width=30)
    ent_pass_conf.pack(pady=5)
    
    frame_botones = tk.Frame(root_registro)
    frame_botones.pack(pady=20)
    
    tk.Button(frame_botones, text="Registrarse", bg="#27ae60", fg="white", 
              width=12, command=registrar_usuario).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botones, text="Volver", bg="#95a5a6", fg="white", 
              width=12, command=volver_al_login).pack(side=tk.LEFT, padx=5)
    
    root_registro.mainloop()

if __name__ == "__main__":
    pantalla_registro()
