import tkinter as tk
import library
import login
import registro

def pantalla_principal():

    # Ventana principal
    root_principal = tk.Tk()
    root_principal.title("Sistema de Biblioteca - Menú Principal")
    root_principal.geometry("400x300")
    root_principal.positionfrom = 'center'
    root_principal.eval('tk::PlaceWindow . center')     

      

    # Título
    tk.Label(
        root_principal,
        text="BIENVENIDO AL SISTEMA DE BIBLIOTECA",
        font=("Arial", 14, "bold")
    ).pack(pady=20)

    # Botón LOGIN
    tk.Button(
        root_principal,
        text="Login",
        bg="#27ae60",
        fg="white",
        width=20,
        command=login.pantalla_login
    ).pack(pady=10)

    # Botón REGISTRAR
    tk.Button(
        root_principal,
        text="Registrar",
        bg="#e67e22",
        fg="white",
        width=20,
        command=registro.pantalla_registro
    ).pack(pady=10)

     # Botón SALIR
    tk.Button(
    root_principal,
    text="Salir",
    bg="red",
    fg="white",
    width=20,
    command=root_principal.destroy
    ).pack(pady=10)

    # Mantener ventana abierta
    root_principal.mainloop()


if __name__ == "__main__":
    pantalla_principal()