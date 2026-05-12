import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ==========================================
# CONSTANTES DE CONFIGURACIÓN
# ==========================================
ARCHIVO_DATOS = "datos_biblioteca.json"
MAX_FILAS = 5
MAX_COLS = 5

# ==========================================
# MÓDULO DE PERSISTENCIA Y ESTADO
# ==========================================

def inicializar_estado():
    """Retorna la estructura base del estado de la aplicación."""
    return {
        "libros": [],       # Lista principal de registros de libros
        "usuarios": [],     # Lista principal de usuarios
        "prestamos": [],    # Lista de préstamos activos
        "estanteria": [[None for _ in range(MAX_COLS)] for _ in range(MAX_FILAS)] # Matriz 2D
    }

def cargar_datos():
    """
    Lee los datos desde el archivo JSON.
    Excepción 1: FileNotFoundError manejada aquí si es la primera ejecución.
    """
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos
    except FileNotFoundError:
        # Si el archivo no existe, retornamos un estado limpio
        return inicializar_estado()
    except Exception as e:
        messagebox.showwarning("Advertencia", f"Error al leer archivo, iniciando BD limpia: {e}")
        return inicializar_estado()

def guardar_datos(estado):
    """Guarda el estado actual de la aplicación en formato JSON."""
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump(estado, archivo, indent=4)
    except Exception as e:
        messagebox.showerror("Error Crítico", f"No se pudo guardar la información: {e}")

# ==========================================
# MÓDULO DE LÓGICA DE NEGOCIO Y ALGORITMOS
# ==========================================

def busqueda_binaria_recursiva(lista_ordenada, objetivo_id, inicio, fin):
    """
    Requisito Académico: Proceso Recursivo.
    Realiza una búsqueda binaria en una lista de diccionarios ordenada por 'id'.
    Excepción 3: Lanza LookupError (Registro Inexistente) si no lo encuentra.
    """
    if inicio > fin:
        raise LookupError(f"El registro con ID '{objetivo_id}' no existe en el sistema.")
    
    medio = (inicio + fin) // 2
    elemento_medio = lista_ordenada[medio]
    
    if elemento_medio['id'] == objetivo_id:
        return elemento_medio
    elif elemento_medio['id'] > objetivo_id:
        return busqueda_binaria_recursiva(lista_ordenada, objetivo_id, inicio, medio - 1)
    else:
        return busqueda_binaria_recursiva(lista_ordenada, objetivo_id, medio + 1, fin)

def validar_datos_libro(estado, id_libro, titulo, autor, fila_str, col_str):
    """
    Requisito Académico: Validaciones Estrictas y Excepciones Reales.
    Excepción 2: ValueError para datos inválidos.
    """
    # 1. Validar campos vacíos
    if not id_libro or not titulo or not autor or not fila_str or not col_str:
        raise ValueError("Todos los campos son estrictamente obligatorios.")
    
    # 2. Validar tipos de datos correctos (fila y columna deben ser enteros)
    try:
        fila = int(fila_str)
        col = int(col_str)
    except ValueError:
        raise ValueError("La Fila y Columna de la estantería deben ser valores numéricos enteros.")
    
    # 3. Validar límites de la matriz
    if fila < 0 or fila >= MAX_FILAS or col < 0 or col >= MAX_COLS:
        raise ValueError(f"Coordenadas fuera de límite. La estantería es de {MAX_FILAS}x{MAX_COLS} (0 a {MAX_FILAS-1}).")
    
    # 4. Validar duplicados de ID
    for libro in estado['libros']:
        if libro['id'] == id_libro:
            raise ValueError(f"El libro con ID '{id_libro}' ya se encuentra registrado.")
            
    # 5. Validar disponibilidad física en la Matriz
    if estado['estanteria'][fila][col] is not None:
        raise ValueError(f"La posición [{fila}][{col}] en la estantería ya está ocupada.")

    return fila, col

def agregar_libro(estado, id_libro, titulo, autor, fila_str, col_str):
    """Agrega un libro tras pasar validaciones."""
    id_libro = id_libro.strip()
    titulo = titulo.strip()
    autor = autor.strip()
    
    # Llama a las validaciones (Puede lanzar ValueError)
    fila, col = validar_datos_libro(estado, id_libro, titulo, autor, fila_str, col_str)
    
    nuevo_libro = {
        "id": id_libro,
        "titulo": titulo,
        "autor": autor,
        "fila": fila,
        "col": col
    }
    
    estado['libros'].append(nuevo_libro)
    estado['estanteria'][fila][col] = id_libro # Actualiza la matriz
    guardar_datos(estado)

def eliminar_libro(estado, id_libro):
    """Elimina un libro usando búsqueda recursiva para ubicarlo primero."""
    if not id_libro:
        raise ValueError("Debe ingresar un ID para eliminar.")
    
    lista_ordenada = sorted(estado['libros'], key=lambda x: x['id'])
    
    # Puede lanzar LookupError si no existe
    libro_a_eliminar = busqueda_binaria_recursiva(lista_ordenada, id_libro, 0, len(lista_ordenada) - 1)
    
    # Si lo encuentra, lo eliminamos de la lista y limpiamos la matriz
    estado['libros'] = [lib for lib in estado['libros'] if lib['id'] != id_libro]
    estado['estanteria'][libro_a_eliminar['fila']][libro_a_eliminar['col']] = None
    
    # Eliminar préstamos asociados
    estado['prestamos'] = [p for p in estado['prestamos'] if p['id_libro'] != id_libro]
    
    guardar_datos(estado)

# ==========================================
# MÓDULOS DE INTERFAZ GRÁFICA (VISTAS)
# ==========================================

def limpiar_frame(frame):
    """Elimina todos los widgets hijos de un frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def construir_tabla(frame, columnas, encabezados):
    """Construye y retorna un Treeview estandarizado."""
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=8)
    for col, enc in zip(columnas, encabezados):
        tree.heading(col, text=enc)
        tree.column(col, width=120, anchor=tk.CENTER)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return tree

def poblar_tabla(tree, lista_diccionarios, llaves):
    """Llena un Treeview con los datos de una lista de diccionarios."""
    for item in tree.get_children():
        tree.delete(item)
    for registro in lista_diccionarios:
        valores = [registro.get(llave, "") for llave in llaves]
        tree.insert("", tk.END, values=valores)

def vista_libros(frame_contenido, estado):
    """Módulo CRUD de Libros."""
    limpiar_frame(frame_contenido)
    
    lbl_titulo = tk.Label(frame_contenido, text="Gestión de Libros (CRUD)", font=("Arial", 16, "bold"))
    lbl_titulo.pack(pady=10)
    
    # Formulario
    frame_form = tk.Frame(frame_contenido)
    frame_form.pack(pady=10)
    
    tk.Label(frame_form, text="ID Libro:").grid(row=0, column=0, padx=5, pady=5)
    ent_id = tk.Entry(frame_form)
    ent_id.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Título:").grid(row=0, column=2, padx=5, pady=5)
    ent_titulo = tk.Entry(frame_form)
    ent_titulo.grid(row=0, column=3, padx=5, pady=5)
    
    tk.Label(frame_form, text="Autor:").grid(row=1, column=0, padx=5, pady=5)
    ent_autor = tk.Entry(frame_form)
    ent_autor.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(frame_form, text="Fila (0-4):").grid(row=1, column=2, padx=5, pady=5)
    ent_fila = tk.Entry(frame_form, width=5)
    ent_fila.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
    
    tk.Label(frame_form, text="Columna (0-4):").grid(row=1, column=3, padx=5, pady=5, sticky=tk.E)
    ent_col = tk.Entry(frame_form, width=5)
    ent_col.grid(row=1, column=4, padx=5, pady=5)

    # Tabla para mostrar datos
    frame_tabla = tk.Frame(frame_contenido)
    frame_tabla.pack(pady=10, fill=tk.BOTH, expand=True)
    columnas = ("id", "titulo", "autor", "fila", "col")
    encabezados = ("ID", "Título", "Autor", "Fila", "Columna")
    tabla = construir_tabla(frame_tabla, columnas, encabezados)
    poblar_tabla(tabla, estado['libros'], columnas)

    # Funciones de acción de botones
    def accion_agregar():
        try:
            agregar_libro(
                estado, ent_id.get(), ent_titulo.get(), 
                ent_autor.get(), ent_fila.get(), ent_col.get()
            )
            poblar_tabla(tabla, estado['libros'], columnas)
            messagebox.showinfo("Éxito", "Libro registrado exitosamente en la estantería.")
        except ValueError as e: # Manejo de la Excepción 2
            messagebox.showerror("Error de Validación", str(e))

    def accion_eliminar():
        try:
            eliminar_libro(estado, ent_id.get().strip())
            poblar_tabla(tabla, estado['libros'], columnas)
            messagebox.showinfo("Éxito", "Libro eliminado correctamente.")
        except (ValueError, LookupError) as e: # Manejo de la Excepción 2 y 3
            messagebox.showerror("Error de Búsqueda", str(e))

    def accion_buscar():
        # Uso del algoritmo de búsqueda binaria recursiva
        id_buscado = ent_id.get().strip()
        if not id_buscado:
            messagebox.showwarning("Advertencia", "Ingrese un ID para buscar.")
            return
        try:
            lista_ordenada = sorted(estado['libros'], key=lambda x: x['id'])
            libro = busqueda_binaria_recursiva(lista_ordenada, id_buscado, 0, len(lista_ordenada) - 1)
            messagebox.showinfo("Libro Encontrado", f"Título: {libro['titulo']}\nAutor: {libro['autor']}\nUbicación: Fila {libro['fila']}, Col {libro['col']}")
        except LookupError as e: # Manejo de la Excepción 3
            messagebox.showerror("No Encontrado", str(e))

    # Botones
    frame_botones = tk.Frame(frame_contenido)
    frame_botones.pack(pady=5)
    tk.Button(frame_botones, text="Agregar Libro", bg="lightblue", command=accion_agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Buscar Libro (Recursivo)", bg="lightyellow", command=accion_buscar).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Eliminar Libro", bg="lightcoral", command=accion_eliminar).pack(side=tk.LEFT, padx=5)


def vista_estanteria(frame_contenido, estado):
    """Módulo para visualizar la Matriz de la Estantería."""
    limpiar_frame(frame_contenido)
    lbl_titulo = tk.Label(frame_contenido, text="Mapa de Estantería Física (Matriz)", font=("Arial", 16, "bold"))
    lbl_titulo.pack(pady=10)
    
    frame_matriz = tk.Frame(frame_contenido)
    frame_matriz.pack(pady=20)
    
    matriz = estado['estanteria']
    for i in range(MAX_FILAS):
        for j in range(MAX_COLS):
            valor = matriz[i][j]
            texto = f"Libre\n[{i},{j}]" if valor is None else f"Ocupado\nID: {valor}"
            color = "lightgreen" if valor is None else "salmon"
            
            lbl = tk.Label(frame_matriz, text=texto, bg=color, width=10, height=3, relief="ridge", borderwidth=2)
            lbl.grid(row=i, column=j, padx=2, pady=2)


def vista_usuarios(frame_contenido, estado):
    """Módulo CRUD básico de Usuarios."""
    limpiar_frame(frame_contenido)
    lbl_titulo = tk.Label(frame_contenido, text="Gestión de Usuarios", font=("Arial", 16, "bold"))
    lbl_titulo.pack(pady=10)
    
    frame_form = tk.Frame(frame_contenido)
    frame_form.pack(pady=10)
    
    tk.Label(frame_form, text="ID Usuario:").grid(row=0, column=0, padx=5)
    ent_id = tk.Entry(frame_form)
    ent_id.grid(row=0, column=1, padx=5)
    
    tk.Label(frame_form, text="Nombre Completo:").grid(row=0, column=2, padx=5)
    ent_nombre = tk.Entry(frame_form)
    ent_nombre.grid(row=0, column=3, padx=5)
    
    # Tabla
    frame_tabla = tk.Frame(frame_contenido)
    frame_tabla.pack(pady=10, fill=tk.BOTH, expand=True)
    columnas = ("id", "nombre")
    tabla = construir_tabla(frame_tabla, columnas, ("ID Usuario", "Nombre Completo"))
    poblar_tabla(tabla, estado['usuarios'], columnas)
    
    def accion_agregar():
        id_u = ent_id.get().strip()
        nom = ent_nombre.get().strip()
        if not id_u or not nom:
            messagebox.showerror("Error", "Campos obligatorios vacíos.")
            return
        if any(u['id'] == id_u for u in estado['usuarios']):
            messagebox.showerror("Error", "ID de usuario ya existe.")
            return
            
        estado['usuarios'].append({"id": id_u, "nombre": nom})
        guardar_datos(estado)
        poblar_tabla(tabla, estado['usuarios'], columnas)
        messagebox.showinfo("Éxito", "Usuario registrado.")
        
    tk.Button(frame_contenido, text="Registrar Usuario", bg="lightblue", command=accion_agregar).pack()


def vista_prestamos(frame_contenido, estado):
    """Módulo de Préstamos y Devoluciones."""
    limpiar_frame(frame_contenido)
    lbl_titulo = tk.Label(frame_contenido, text="Préstamos y Devoluciones", font=("Arial", 16, "bold"))
    lbl_titulo.pack(pady=10)
    
    frame_form = tk.Frame(frame_contenido)
    frame_form.pack(pady=10)
    
    tk.Label(frame_form, text="ID Libro:").grid(row=0, column=0, padx=5)
    ent_libro = tk.Entry(frame_form)
    ent_libro.grid(row=0, column=1, padx=5)
    
    tk.Label(frame_form, text="ID Usuario:").grid(row=0, column=2, padx=5)
    ent_user = tk.Entry(frame_form)
    ent_user.grid(row=0, column=3, padx=5)
    
    # Tabla de préstamos activos
    frame_tabla = tk.Frame(frame_contenido)
    frame_tabla.pack(pady=10, fill=tk.BOTH, expand=True)
    columnas = ("id_libro", "id_usuario")
    tabla = construir_tabla(frame_tabla, columnas, ("ID Libro", "ID Usuario"))
    poblar_tabla(tabla, estado['prestamos'], columnas)
    
    def accionar_prestar():
        id_lib = ent_libro.get().strip()
        id_usr = ent_user.get().strip()
        
        if not any(l['id'] == id_lib for l in estado['libros']):
            messagebox.showerror("Error", "El libro no existe.")
            return
        if not any(u['id'] == id_usr for u in estado['usuarios']):
            messagebox.showerror("Error", "El usuario no existe.")
            return
        if any(p['id_libro'] == id_lib for p in estado['prestamos']):
            messagebox.showerror("Error", "El libro ya se encuentra prestado.")
            return
            
        estado['prestamos'].append({"id_libro": id_lib, "id_usuario": id_usr})
        guardar_datos(estado)
        poblar_tabla(tabla, estado['prestamos'], columnas)
        messagebox.showinfo("Éxito", "Préstamo registrado.")

    def accionar_devolver():
        id_lib = ent_libro.get().strip()
        prestamo = next((p for p in estado['prestamos'] if p['id_libro'] == id_lib), None)
        
        if prestamo is None:
            messagebox.showerror("Error", "No existe un préstamo activo para ese libro.")
            return
            
        estado['prestamos'].remove(prestamo)
        guardar_datos(estado)
        poblar_tabla(tabla, estado['prestamos'], columnas)
        messagebox.showinfo("Éxito", "Libro devuelto.")

    frame_botones = tk.Frame(frame_contenido)
    frame_botones.pack(pady=5)
    tk.Button(frame_botones, text="Registrar Préstamo", bg="lightblue", command=accionar_prestar).pack(side=tk.LEFT, padx=5)
    tk.Button(frame_botones, text="Registrar Devolución", bg="lightgreen", command=accionar_devolver).pack(side=tk.LEFT, padx=5)

# ==========================================
# ESTRUCTURA PRINCIPAL DE TKINTER
# ==========================================

def construir_interfaz(raiz, estado):
    """Construye la ventana principal y orquesta los paneles mediante paso de parámetros."""
    raiz.title("Sistema de Gestión de Biblioteca - Universitaria")
    raiz.geometry("850x550")
    
    # Panel de Navegación (Izquierda)
    frame_nav = tk.Frame(raiz, bg="#2c3e50", width=200)
    frame_nav.pack(side=tk.LEFT, fill=tk.Y)
    
    # Panel de Contenido Principal (Derecha)
    frame_contenido = tk.Frame(raiz, bg="#ecf0f1")
    frame_contenido.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Título en Navegación
    tk.Label(frame_nav, text="MENÚ PRINCIPAL", bg="#2c3e50", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
    
    # Botones de Navegación. Se pasa el estado como argumento a las vistas.
    btn_kwargs = {"bg": "#34495e", "fg": "white", "font": ("Arial", 10), "width": 20, "pady": 10}
    tk.Button(frame_nav, text="📚 Gestión de Libros", command=lambda: vista_libros(frame_contenido, estado), **btn_kwargs).pack(pady=5)
    tk.Button(frame_nav, text="🗄️ Ver Estantería", command=lambda: vista_estanteria(frame_contenido, estado), **btn_kwargs).pack(pady=5)
    tk.Button(frame_nav, text="👥 Gestión de Usuarios", command=lambda: vista_usuarios(frame_contenido, estado), **btn_kwargs).pack(pady=5)
    tk.Button(frame_nav, text="🔄 Préstamos / Devol.", command=lambda: vista_prestamos(frame_contenido, estado), **btn_kwargs).pack(pady=5)
    
    tk.Button(frame_nav, text="Salir del Sistema", command=raiz.quit, bg="#c0392b", fg="white", font=("Arial", 10), width=20, pady=10).pack(side=tk.BOTTOM, pady=20)
    
    # Cargar vista por defecto
    vista_libros(frame_contenido, estado)

# ==========================================
# PUNTO DE ENTRADA (MANDATORIO)
# ==========================================

def main():
    """
    Función principal que inicia la aplicación.
    No existen variables globales; el estado vive aquí y se pasa a la interfaz.
    """
    # 1. Cargar estado inicial (Lectura de Archivo, maneja FileNotFoundError)
    estado_aplicacion = cargar_datos()
    
    # 2. Inicializar raíz de Tkinter
    raiz = tk.Tk()
    
    # 3. Construir la interfaz pasando el estado como referencia
    construir_interfaz(raiz, estado_aplicacion)
    
    # 4. Bucle principal de eventos
    raiz.mainloop()

if __name__ == "__main__":
    main()