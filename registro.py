import tkinter as tk
from tkinter import messagebox
import json
import os

ARCHIVO_USUARIOS = "usuarios.json"

def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON con manejo de excepciones"""
    try:
        if os.path.exists(ARCHIVO_USUARIOS):
            with open(ARCHIVO_USUARIOS, "r") as f:
                return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    return {}

def guardar_usuarios(usuarios):
    """Guarda la base de datos de usuarios en el archivo JSON"""
    try:
        with open(ARCHIVO_USUARIOS, "w") as f:
            json.dump(usuarios, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar usuarios: {e}")

def pantalla_registro():
    """Crea la interfaz de registro dinámico con el orden de campos optimizado"""
    
    def verificar_cedula(*args):
        """Monitorea lo que escribe el usuario para validar si pertenece a la ULEAM"""
        cedula = ent_cedula.get().strip()
        
        if len(cedula) == 10 and cedula.startswith("13"):
            lbl_status_cedula.config(text="✓ Estudiante ULEAM Detectado", fg="#27ae60")
            frame_invitado.pack_forget()
            root_registro.geometry("380x540")
        elif len(cedula) == 10:
            lbl_status_cedula.config(text="⚠ Externo: Completar datos de Invitado", fg="#e67e22")
            frame_invitado.pack(pady=5, before=frame_botones)
            root_registro.geometry("380x640")
        else:
            lbl_status_cedula.config(text="Ingrese los 10 dígitos de su cédula", fg="#7f8c8d")
            frame_invitado.pack_forget()
            root_registro.geometry("380x540")

    def registrar_usuario():
        cedula = ent_cedula.get().strip()
        usuario = ent_user.get().strip().lower()
        clave = ent_pass.get()
        confirmar_clave = ent_pass_conf.get()
        correo = ent_correo.get().strip()
        telefono = ent_telefono.get().strip()
        
        # Validaciones de campos obligatorios generales
        if not cedula or not usuario or not clave or not correo or not telefono:
            messagebox.showerror("Error", "Todos los campos principales son obligatorios")
            return
            
        if len(cedula) != 10:
            messagebox.showerror("Error", "La cédula debe contener exactamente 10 dígitos")
            return
        
        if len(clave) < 4:
            messagebox.showerror("Error", "La contraseña debe tener al menos 4 caracteres")
            return
        
        if clave != confirmar_clave:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        # Validación simple de formato de correo
        if "@" not in correo or "." not in correo:
            messagebox.showerror("Error", "Por favor, ingrese un correo electrónico válido")
            return
        
        usuarios = cargar_usuarios()
        
        if usuario in usuarios:
            messagebox.showerror("Error", "El nombre de usuario ya se encuentra registrado")
            return

        # Determinar Rol y Datos extras en base a la cédula
        if cedula.startswith("13"):
            rol = "estudiante"
            nombre_completo = "Estudiante ULEAM Autoverificado"
        else:
            rol = "invitado"
            nom = ent_nombre.get().strip()
            ape = ent_apellido.get().strip()
            if not nom or not ape:
                messagebox.showerror("Datos Faltantes", "Como usuario invitado, debe registrar su Nombre y Apellido")
                return
            nombre_completo = f"{nom} {ape}"
        
        # Insertar el nuevo esquema estructurado incluyendo correo y teléfono
        usuarios[usuario] = {
            "clave": clave,
            "rol": rol,
            "cedula": cedula,
            "nombre": nombre_completo,
            "correo": correo,
            "telefono": telefono
        }
        
        guardar_usuarios(usuarios)
        messagebox.showinfo("Éxito", f"Registro completado.\nRol asignado: {rol.upper()}")
        
        volver_al_login()

    def volver_al_login():
        root_registro.destroy()
        from login import pantalla_login
        pantalla_login()
    
    # --- CONFIGURACIÓN DE LA VENTANA ---
    root_registro = tk.Tk()
    root_registro.title("Registro - Sistema Biblioteca")
    root_registro.geometry("380x540")
    root_registro.resizable(False, False)
    root_registro.eval('tk::PlaceWindow . center')
    
    tk.Label(root_registro, text="REGISTRO DE NUEVO USUARIO", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=15)
    
    # 1. Campo Cédula Identificadora
    tk.Label(root_registro, text="Número de Cédula:", font=("Arial", 9, "bold")).pack()
    var_cedula = tk.StringVar()
    var_cedula.trace_add("write", verificar_cedula)
    ent_cedula = tk.Entry(root_registro, textvariable=var_cedula, width=32, justify="center")
    ent_cedula.pack(pady=2)
    
    lbl_status_cedula = tk.Label(root_registro, text="Ingrese los 10 dígitos de su cédula", font=("Arial", 8, "italic"), fg="#7f8c8d")
    lbl_status_cedula.pack(pady=(0, 10))
    
    # 2. Datos de Identificación y Cuenta
    tk.Label(root_registro, text="Nombre de Usuario:").pack()
    ent_user = tk.Entry(root_registro, width=32)
    ent_user.pack(pady=4)

    # 3. Datos de Contacto (AHORA ARRIBA DE LAS CONTRASEÑAS)
    tk.Label(root_registro, text="Correo Electrónico:").pack()
    ent_correo = tk.Entry(root_registro, width=32)
    ent_correo.pack(pady=4)

    # El teléfono cuenta con un pequeño margen abajo para separar del bloque de seguridad
    tk.Label(root_registro, text="Número de Teléfono:").pack()
    ent_telefono = tk.Entry(root_registro, width=32)
    ent_telefono.pack(pady=(4, 10))
    
    # 4. Credenciales de Seguridad (Al final del formulario)
    tk.Label(root_registro, text="Contraseña:").pack()
    ent_pass = tk.Entry(root_registro, show="*", width=32)
    ent_pass.pack(pady=4)
    
    tk.Label(root_registro, text="Confirmar Contraseña:").pack()
    ent_pass_conf = tk.Entry(root_registro, show="*", width=32)
    ent_pass_conf.pack(pady=4)
    
    # --- CONTENEDOR OCULTO PARA INVITADOS ---
    frame_invitado = tk.Frame(root_registro)
    
    tk.Label(frame_invitado, text="Nombre del Visitante:").pack()
    ent_nombre = tk.Entry(frame_invitado, width=32)
    ent_nombre.pack(pady=2)
    
    tk.Label(frame_invitado, text="Apellido del Visitante:").pack()
    ent_apellido = tk.Entry(frame_invitado, width=32)
    ent_apellido.pack(pady=2)
    
    # --- CONTENEDOR DE BOTONES ---
    frame_botones = tk.Frame(root_registro)
    frame_botones.pack(pady=18)
    
    tk.Button(frame_botones, text="Registrarse", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12, command=registrar_usuario, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Volver", bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), width=12, command=volver_al_login, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=5)
    
    root_registro.mainloop()

if __name__ == "__main__":
    pantalla_registro()