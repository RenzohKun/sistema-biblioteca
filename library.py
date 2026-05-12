# Version 1.0 de la Liberia

import tkinter as tk
from tkinter import messagebox
import os

# Cfg
ARCHIVO = "biblioteca_datos.js"
MAX_F, MAX_C =5, 5
lista_libros = [] 
estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]

def cargar_desde_archivo():
    
    try:
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r") as f:
                for linea in f:
                    # Formato: id,titulo,fila,col
                    datos = linea.strip().split(",")
                    if len(datos) == 4:
                        lib = {"id": datos[0], "titulo": datos[1], "f": int(datos[2]), "c": int(datos[3])}
                        lista_libros.append(lib)
                        estanteria[lib["f"]][lib["c"]] = lib["id"]
    except Exception as e:
        messagebox.showwarning("Aviso", f"No se pudo cargar el archivo: {e}")

def guardar_en_archivo():

    with open(ARCHIVO, "w") as f:
        for lib in lista_libros:
            f.write(f"{lib['id']},{lib['titulo']},{lib['f']},{lib['c']}\n")

def buscar_recursivo(lista, id_buscado, indice=0):
    if indice >= len(lista):
        return None # No encontrado
    if lista[indice]["id"] == id_buscado:
        return lista[indice] # Encontrado
    return buscar_recursivo(lista, id_buscado, indice + 1)

def registrar_logica(id_lib, titulo, fila, col):

    if not id_lib or not titulo:
        messagebox.showerror("Error", "ID y Título son obligatorios")
        return
    
    try:
        f, c = int(fila), int(col)

        if f >= MAX_F or c >= MAX_C or f < 0 or c < 0:
            raise IndexError("La ubicación está fuera de la estantería (0-4)")
        
        if estanteria[f][c] != "Libre":
            messagebox.showwarning("Atención", "Esa ubicación ya está ocupada")
            return

        lista_libros.append({"id": id_lib, "titulo": titulo, "f": f, "c": c})
        estanteria[f][c] = id_lib
        guardar_en_archivo() # Guardar cambio
        messagebox.showinfo("Éxito", "Libro registrado y guardado.")
    except ValueError:
        messagebox.showerror("Error", "Fila y Columna deben ser números")
    except IndexError as e:
        messagebox.showerror("Error de Ubicación", str(e))

# ==========================================
# Interfaz
# ==========================================
def abrir_libros(panel):
    for w in panel.winfo_children(): w.destroy()
    tk.Label(panel, text="GESTIÓN DE LIBROS", font=("Arial", 14, "bold")).pack(pady=10)
    
    
    tk.Label(panel, text="ID del Libro:").pack(); ent_id = tk.Entry(panel); ent_id.pack()
    tk.Label(panel, text="Título:").pack(); ent_titulo = tk.Entry(panel); ent_titulo.pack()
    tk.Label(panel, text="Fila (0-4):").pack(); ent_f = tk.Entry(panel); ent_f.pack()
    tk.Label(panel, text="Col (0-4):").pack(); ent_c = tk.Entry(panel); ent_c.pack()
    
    
    tk.Button(panel, text="Registrar", bg="lightblue", 
              command=lambda: registrar_logica(ent_id.get(), ent_titulo.get(), ent_f.get(), ent_c.get())).pack(pady=10)
    
    
    def btn_buscar():
        res = buscar_recursivo(lista_libros, ent_id.get())
        if res: messagebox.showinfo("Búsqueda", f"Encontrado: {res['titulo']} en [{res['f']}][{res['c']}]")
        else: messagebox.showwarning("Búsqueda", "Libro no encontrado")
        
    tk.Button(panel, text="Buscar (Recursivo)", command=btn_buscar).pack()

def abrir_matriz(panel):
    for w in panel.winfo_children(): w.destroy()
    tk.Label(panel, text="ESTANTERÍA", font=("Arial", 14, "bold")).pack(pady=10)
    fr = tk.Frame(panel); fr.pack()
    for r in range(MAX_F):
        for c in range(MAX_C):
            txt = estanteria[r][c]
            color = "lightgreen" if txt == "Libre" else "salmon"
            tk.Label(fr, text=txt, bg=color, width=8, height=2, relief="ridge").grid(row=r, column=c, padx=2, pady=2)

# ==========================================
# Principal
# ==========================================
def main():
    cargar_desde_archivo() # Cargar datos al iniciar
    ventana = tk.Tk()
    ventana.title("Biblioteca Universitaria")
    ventana.geometry("700x500")

    # Panel Navegación
    nav = tk.Frame(ventana, bg="#2c3e50", width=180); nav.pack(side="left", fill="y")
    cont = tk.Frame(ventana, bg="white"); cont.pack(side="right", fill="both", expand=True)

    tk.Button(nav, text="Libros", width=15, command=lambda: abrir_libros(cont)).pack(pady=10)
    tk.Button(nav, text="Estanteria", width=15, command=lambda: abrir_matriz(cont)).pack(pady=10)
    tk.Button(nav, text="Salir", bg="red", fg="white", command=ventana.quit).pack(side="bottom", pady=20)

    abrir_libros(cont)
    ventana.mainloop()

if __name__ == "__main__":
    main()
