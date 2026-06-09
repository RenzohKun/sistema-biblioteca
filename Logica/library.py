import tkinter as tk
from tkinter import messagebox, ttk
import os
import json

# Configuración del Archivo (En formato JSON estándar)
ARCHIVO = "datos/biblioteca_datos.json"
MAX_F, MAX_C = 5, 5
lista_libros = [] 
estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]

def cargar_desde_archivo():
    """Carga los libros guardados y reconstruye la estantería"""
    global lista_libros, estanteria
    lista_libros.clear()
    estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]
    
    if not os.path.exists("datos"):
        os.makedirs("datos")
        
    try:
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                lista_libros = json.load(f)
                for lib in lista_libros:
                    if 0 <= lib["f"] < MAX_F and 0 <= lib["c"] < MAX_C:
                        estanteria[lib["f"]][lib["c"]] = lib["id"]
    except Exception as e:
        messagebox.showwarning("Aviso", f"No se pudo cargar el archivo de libros: {e}")

def guardar_en_archivo():
    """Guarda la lista de libros en formato JSON estructurado"""
    try:
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(lista_libros, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar libros: {e}")

def buscar_recursivo(lista, id_buscado, indice=0):
    """Algoritmo de búsqueda recursiva por ID"""
    if indice >= len(lista):
        return None
    if str(lista[indice]["id"]).strip().lower() == str(id_buscado).strip().lower():
        return lista[indice]
    return buscar_recursivo(lista, id_buscado, indice + 1)

# ==========================================
# Vistas de la Interfaz
# ==========================================

def abrir_libros(panel):
    """Pestaña de gestión: Formulario moderno y tabla de contenidos"""
    for w in panel.winfo_children(): 
        w.destroy()
    
    main_frame = tk.Frame(panel, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=15)
    
    tk.Label(main_frame, text="GESTIÓN DEL CATÁLOGO DE LIBROS", font=("Arial", 14, "bold"), fg="#2c3e50", bg="white").pack(anchor="w", pady=(0, 15))
    
    # ---- FORMULARIO DE REGISTRO ----
    form_frame = tk.LabelFrame(main_frame, text=" Registrar Nuevo Libro ", font=("Arial", 10, "bold"), bg="white", fg="#34495e", padx=15, pady=10)
    form_frame.pack(fill="x", pady=(0, 15))
    
    tk.Label(form_frame, text="ID Libro:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=0, sticky="w", pady=5)
    ent_id = tk.Entry(form_frame, width=15, font=("Arial", 10))
    ent_id.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(form_frame, text="Título:", font=("Arial", 9, "bold"), bg="white").grid(row=0, column=2, sticky="w", pady=5)
    ent_titulo = tk.Entry(form_frame, width=30, font=("Arial", 10))
    ent_titulo.grid(row=0, column=3, padx=10, pady=5)
    
    tk.Label(form_frame, text="Fila (0-4):", font=("Arial", 9, "bold"), bg="white").grid(row=1, column=0, sticky="w", pady=5)
    ent_f = tk.Entry(form_frame, width=15, font=("Arial", 10))
    ent_f.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(form_frame, text="Columna (0-4):", font=("Arial", 9, "bold"), bg="white").grid(row=1, column=2, sticky="w", pady=5)
    ent_c = tk.Entry(form_frame, width=15, font=("Arial", 10))
    ent_c.grid(row=1, column=3, padx=10, pady=5)
    
    btn_frame = tk.Frame(form_frame, bg="white")
    btn_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="e")
    
    # ---- TABLA REFRESCABLE (TREEVIEW) ----
    tabla_frame = tk.LabelFrame(main_frame, text=" Libros en el Sistema ", font=("Arial", 10, "bold"), bg="white", fg="#34495e", padx=5, pady=5)
    tabla_frame.pack(fill="both", expand=True)
    
    columnas = ("id", "titulo", "ubicacion")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=6)
    tabla.pack(side="left", fill="both", expand=True)
    
    scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scroll.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scroll.set)
    
    tabla.heading("id", text="ID")
    tabla.heading("titulo", text="Título del Libro")
    tabla.heading("ubicacion", text="Ubicación (Fila, Col)")
    
    tabla.column("id", width=80, anchor="center")
    tabla.column("titulo", width=250, anchor="w")
    tabla.column("ubicacion", width=120, anchor="center")
    
    def actualizar_tabla():
        for item in tabla.get_children():
            tabla.delete(item)
        for lib in lista_libros:
            tabla.insert("", "end", values=(lib["id"], lib["titulo"], f"Fila {lib['f']} - Col {lib['c']}"))

    # ---- LÓGICA DE LOS BOTONES INTERNOS ----
    def ejecutar_registro():
        id_lib = ent_id.get().strip()
        titulo = ent_titulo.get().strip()
        fila = ent_f.get().strip()
        col = ent_c.get().strip()
        
        if not id_lib or not titulo or not fila or not col:
            messagebox.showerror("Error", "Todos los campos son totalmente obligatorios")
            return
            
        if buscar_recursivo(lista_libros, id_lib) is not None:
            messagebox.showerror("ID Duplicado", f"El ID '{id_lib}' ya pertenece a otro libro.")
            return
            
        try:
            f, c = int(fila), int(col)
            if not (0 <= f < MAX_F) or not (0 <= c < MAX_C):
                raise IndexError(f"Índices fuera de rango. Recuerde usar de 0 a {MAX_F-1}")
                
            if estanteria[f][c] != "Libre":
                messagebox.showwarning("Ubicación Ocupada", f"La celda [{f}][{c}] ya contiene al libro ID: {estanteria[f][c]}")
                return
                
            lista_libros.append({"id": id_lib, "titulo": titulo, "f": f, "c": c})
            estanteria[f][c] = id_lib
            guardar_en_archivo()
            
            messagebox.showinfo("Completado", "Libro registrado y guardado en estantería.")
            
            ent_id.delete(0, tk.END)
            ent_titulo.delete(0, tk.END)
            ent_f.delete(0, tk.END)
            ent_c.delete(0, tk.END)
            actualizar_tabla()
            
        except ValueError:
            messagebox.showerror("Error de Formato", "Fila y Columna obligatoriamente deben ser números enteros")
        except IndexError as e:
            messagebox.showerror("Error de Rango", str(e))

    def ejecutar_busqueda():
        id_buscado = ent_id.get().strip()
        if not id_buscado:
            messagebox.showwarning("Atención", "Por favor inserte un ID en el campo 'ID Libro' para buscar")
            return
            
        resultado = buscar_recursivo(lista_libros, id_buscado)
        if resultado:
            messagebox.showinfo("Libro Localizado", f"📌 Título: {resultado['titulo']}\n📍 Ubicación: Fila {resultado['f']}, Columna {resultado['c']}")
        else:
            messagebox.showwarning("Sin Resultados", f"No se encontró ningún libro con el ID: {id_buscado}")

    tk.Button(btn_frame, text="🔍 Buscar por ID", bg="#34495e", fg="white", font=("Arial", 9, "bold"), cursor="hand2", command=ejecutar_busqueda, width=14, relief="flat").pack(side="left", padx=5)
    tk.Button(btn_frame, text="💾 Registrar", bg="#27ae60", fg="white", font=("Arial", 9, "bold"), cursor="hand2", command=ejecutar_registro, width=12, relief="flat").pack(side="left", padx=5)
    
    actualizar_tabla()


def abrir_matriz(panel):
    """Pestaña de estantería: Matriz gráfica en bloques estilizados"""
    for w in panel.winfo_children(): 
        w.destroy()
        
    main_frame = tk.Frame(panel, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=15)
    
    tk.Label(main_frame, text="MAPA DE LA ESTANTERÍA", font=("Arial", 14, "bold"), fg="#2c3e50", bg="white").pack(anchor="w", pady=(0, 5))
    tk.Label(main_frame, text="Distribución física en bloques matriciales de 5x5", font=("Arial", 9, "italic"), fg="#7f8c8d", bg="white").pack(anchor="w", pady=(0, 15))
    
    map_container = tk.Frame(main_frame, bg="#ecf0f1", padx=15, pady=15, relief="solid", bd=1)
    map_container.pack(anchor="center", pady=10)
    
    for c in range(MAX_C):
        tk.Label(map_container, text=f"Col {c}", font=("Arial", 8, "bold"), bg="#ecf0f1", fg="#7f8c8d").grid(row=0, column=c+1, padx=5, pady=5)
        
    for r in range(MAX_F):
        tk.Label(map_container, text=f"Fila {r}", font=("Arial", 8, "bold"), bg="#ecf0f1", fg="#7f8c8d").grid(row=r+1, column=0, padx=5, pady=5, sticky="e")
        
        for c in range(MAX_C):
            contenido = estanteria[r][c]
            
            if contenido == "Libre":
                color_bg = "#2ecc71"
                color_fg = "white"
                texto_celda = "Libre"
            else:
                color_bg = "#e74c3c"
                color_fg = "white"
                texto_celda = f"ID: {contenido}"
                
            cell = tk.Label(map_container, text=texto_celda, bg=color_bg, fg=color_fg, font=("Arial", 9, "bold"), width=10, height=2, relief="flat")
            cell.grid(row=r+1, column=c+1, padx=3, pady=3)

# ==========================================
# Lanzador Autónomo (Para pruebas directas)
# ==========================================
def main():
    cargar_desde_archivo()
    ventana = tk.Tk()
    ventana.title("Módulo de Biblioteca")
    ventana.geometry("750x550")  # Corregido con la 'x' sin errores
    ventana.eval('tk::PlaceWindow . center')
    
    nav = tk.Frame(ventana, bg="#2c3e50", width=180)
    nav.pack(side="left", fill="y")
    cont = tk.Frame(ventana, bg="white")
    cont.pack(side="right", fill="both", expand=True)
    
    tk.Button(nav, text="📚 Catálogo", width=15, bg="#34495e", fg="white", font=("Arial", 10, "bold"), relief="flat", cursor="hand2", command=lambda: abrir_libros(cont)).pack(pady=10)
    tk.Button(nav, text="🧱 Estantería", width=15, bg="#34495e", fg="white", font=("Arial", 10, "bold"), relief="flat", cursor="hand2", command=lambda: abrir_matriz(cont)).pack(pady=10)
    
    abrir_libros(cont)
    ventana.mainloop()

if __name__ == "__main__":
    main()