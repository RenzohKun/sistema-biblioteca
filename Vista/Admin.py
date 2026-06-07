# Admin.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# =========================================================================
# CONFIGURACIÓN DE LOGICA Y MATRICES (Heredado de la librería original)
# =========================================================================
ARCHIVO_LIBROS_TXT = "datos/biblioteca_datos.js"
MAX_F, MAX_C = 5, 5
lista_libros = [] 
estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]

def cargar_desde_archivo():
    """Carga los libros y posiciona la matriz de la estantería al iniciar"""
    global lista_libros, estanteria
    lista_libros.clear()
    estanteria = [["Libre" for _ in range(MAX_C)] for _ in range(MAX_F)]
    try:
        if os.path.exists(ARCHIVO_LIBROS_TXT):
            with open(ARCHIVO_LIBROS_TXT, "r") as f:
                for linea in f:
                    datos = linea.strip().split(",")
                    if len(datos) == 4:
                        lib = {"id": datos[0], "titulo": datos[1], "f": int(datos[2]), "c": int(datos[3])}
                        lista_libros.append(lib)
                        estanteria[lib["f"]][lib["c"]] = lib["id"]
    except Exception as e:
        print(f"Aviso al cargar archivo de libros: {e}")

def guardar_en_archivo():
    """Sincroniza la lista de libros con el archivo físico de texto plano"""
    with open(ARCHIVO_LIBROS_TXT, "w") as f:
        for lib in lista_libros:
            f.write(f"{lib['id']},{lib['titulo']},{lib['f']},{lib['c']}\n")

def buscar_recursivo(lista, id_buscado, indice=0):
    """Algoritmo de búsqueda recursiva por ID requerido por la lógica del sistema"""
    if indice >= len(lista):
        return None
    if lista[indice]["id"] == id_buscado:
        return lista[indice]
    return buscar_recursivo(lista, id_buscado, indice + 1)


# =========================================================================
# CLASE DE LA INTERFAZ DEL ADMINISTRADOR
# =========================================================================
class VentanaAdministrador:
    def __init__(self, root, nombre_admin="Administrador"):
        self.root = root
        self.root.title("Sistema de Biblioteca - Panel de Administración")
        self.root.geometry("1050x650")
        self.root.resizable(False, False)
        
        # Cargar los datos de los libros al inicializar el panel
        cargar_desde_archivo()
        
        # --- COLORES DE LA INTERFAZ ---
        self.color_menu = "#2c3e50"       
        self.color_botones = "#34495e"    
        self.color_fondo = "#ecf0f1"      
        self.color_texto = "#ffffff"
        
        # --- CONTENEDORES PRINCIPALES ---
        self.menu_lateral = tk.Frame(self.root, bg=self.color_menu, width=220)
        self.menu_lateral.pack(side="left", fill="y")
        self.menu_lateral.pack_propagate(False) 
        
        self.area_contenido = tk.Frame(self.root, bg=self.color_fondo)
        self.area_contenido.pack(side="right", fill="both", expand=True)
        
        # --- ELEMENTOS DEL MENÚ LATERAL ---
        lbl_logo = tk.Label(self.menu_lateral, text="📚\nBIBLIOTECA", fg=self.color_texto, bg=self.color_menu, font=("Arial", 16, "bold"))
        lbl_logo.pack(pady=20)
        
        lbl_admin = tk.Label(self.menu_lateral, text=f"Bienvenido,\n{nombre_admin}", bg=self.color_menu, font=("Arial", 11, "italic"), fg="#bdc3c7")
        lbl_admin.pack(pady=10)
        
        # Botones de navegación actualizados
        self.crear_boton_menu("Inicio / Dashboard", self.mostrar_inicio)
        self.crear_boton_menu("Gestión de Libros", self.mostrar_gestion_libros)
        self.crear_boton_menu("Ver Estantería (Matriz)", self.mostrar_estanteria_matriz)
        self.crear_boton_menu("Gestión de Usuarios", self.mostrar_gestion_usuarios)
        
        btn_logout = tk.Button(self.menu_lateral, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#c0392b", fg="white", relief="flat", font=("Arial", 10, "bold"), pady=8)
        btn_logout.pack(side="bottom", fill="x", padx=15, pady=20)
        
        self.mostrar_inicio()

    def crear_boton_menu(self, texto, comando):
        btn = tk.Button(self.menu_lateral, text=texto, command=comando, bg=self.color_botones, fg=self.color_texto, relief="flat", font=("Arial", 10, "bold"), pady=10, cursor="hand2")
        btn.pack(fill="x", padx=10, pady=5)

    def limpiar_contenido(self):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

    # =========================================================================
    # VISTA: INICIO / DASHBOARD
    # =========================================================================
    def mostrar_inicio(self):
        self.limpiar_contenido()
        
        lbl_titulo = tk.Label(self.area_contenido, text="Panel de Control General", font=("Arial", 20, "bold"), bg=self.color_fondo, fg="#2c3e50")
        lbl_titulo.pack(pady=(25, 10), padx=30, anchor="w")
        
        lbl_subtitulo = tk.Label(self.area_contenido, text="Estado actual del sistema de biblioteca", font=("Arial", 11), bg=self.color_fondo, fg="#7f8c8d")
        lbl_subtitulo.pack(pady=(0, 25), padx=30, anchor="w")
        
        frame_tarjetas = tk.Frame(self.area_contenido, bg=self.color_fondo)
        frame_tarjetas.pack(padx=30, fill="x", anchor="w")
        
        # Conteo dinámico de usuarios desde usuarios.json
        total_usuarios = 0
        if os.path.exists("datos/usuarios.json"):
            try:
                with open("datos/usuarios.json", "r") as f:
                    datos = json.load(f)
                    total_usuarios = max(0, len(datos) - 1) 
            except: pass

        # Conteo dinámico de libros usando la lista de memoria global
        total_libros = len(lista_libros)

        # Tarjeta 1: Libros
        card_libros = tk.Frame(frame_tarjetas, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dcdde1", padx=20, pady=15)
        card_libros.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        tk.Label(card_libros, text="📚 TOTAL LIBROS", font=("Arial", 10, "bold"), bg="#ffffff", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card_libros, text=str(total_libros), font=("Arial", 24, "bold"), bg="#ffffff", fg="#2c3e50").pack(anchor="w", pady=(5, 0))
        
        # Tarjeta 2: Usuarios
        card_usuarios = tk.Frame(frame_tarjetas, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dcdde1", padx=20, pady=15)
        card_usuarios.grid(row=0, column=1, padx=20, sticky="nsew")
        tk.Label(card_usuarios, text="👥 ESTUDIANTES", font=("Arial", 10, "bold"), bg="#ffffff", fg="#7f8c8d").pack(anchor="w")
        tk.Label(card_usuarios, text=str(total_usuarios), font=("Arial", 24, "bold"), bg="#ffffff", fg="#27ae60").pack(anchor="w", pady=(5, 0))

        # Sección inferior de accesos rápidos
        lbl_accesos = tk.Label(self.area_contenido, text="Acciones Rápidas", font=("Arial", 14, "bold"), bg=self.color_fondo, fg="#2c3e50")
        lbl_accesos.pack(pady=(40, 15), padx=30, anchor="w")
        
        frame_acciones = tk.Frame(self.area_contenido, bg=self.color_fondo)
        frame_acciones.pack(padx=30, fill="x", anchor="w")
        
        tk.Button(frame_acciones, text="➕ Gestionar Catálogo", command=self.mostrar_gestion_libros, bg="#2c3e50", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8, relief="flat", cursor="hand2").pack(side="left", padx=(0, 15))
        tk.Button(frame_acciones, text="🔍 Ver Mapa Estantería", command=self.mostrar_estanteria_matriz, bg="#e67e22", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8, relief="flat", cursor="hand2").pack(side="left")

    # =========================================================================
    # VISTA: GESTIÓN DE LIBROS (Formulario + Tabla Treeview + Búsqueda)
    # =========================================================================
    def mostrar_gestion_libros(self):
        self.limpiar_contenido()
        
        lbl_titulo = tk.Label(self.area_contenido, text="Administración del Catálogo de Libros", font=("Arial", 18, "bold"), bg=self.color_fondo, fg="#2c3e50")
        lbl_titulo.pack(pady=10, padx=20, anchor="w")
        
        # Formulario Integrado para añadir libros a las coordenadas fijas de la estantería
        frame_formulario = tk.LabelFrame(self.area_contenido, text=" Registrar o Buscar Libro ", bg=self.color_fondo, font=("Arial", 10, "bold"), fg="#34495e", padx=10, pady=10)
        frame_formulario.pack(padx=20, pady=5, fill="x")
        
        tk.Label(frame_formulario, text="ID Libro:", bg=self.color_fondo).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_id = tk.Entry(frame_formulario, width=12)
        self.ent_id.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_formulario, text="Título:", bg=self.color_fondo).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_titulo = tk.Entry(frame_formulario, width=25)
        self.ent_titulo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_formulario, text="Fila (0-4):", bg=self.color_fondo).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_f = tk.Entry(frame_formulario, width=8)
        self.ent_f.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(frame_formulario, text="Columna (0-4):", bg=self.color_fondo).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.ent_c = tk.Entry(frame_formulario, width=8)
        self.ent_c.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Botones operativos
        frame_botones = tk.Frame(self.area_contenido, bg=self.color_fondo)
        frame_botones.pack(padx=20, pady=5, fill="x")
        
        btn_registrar = tk.Button(frame_botones, text="➕ Registrar Posición", command=self.registrar_libro_logica, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), padx=12, pady=4, relief="flat", cursor="hand2")
        btn_registrar.pack(side="left", padx=5)
        
        btn_buscar = tk.Button(frame_botones, text="🔍 Búsqueda Recursiva", command=self.ejecutar_busqueda_recursiva, bg="#2980b9", fg="white", font=("Arial", 10, "bold"), padx=12, pady=4, relief="flat", cursor="hand2")
        btn_buscar.pack(side="left", padx=5)
        
        btn_eliminar = tk.Button(frame_botones, text="🗑️ Remover del Catálogo", command=self.eliminar_libro_logica, bg="#c0392b", fg="white", font=("Arial", 10, "bold"), padx=12, pady=4, relief="flat", cursor="hand2")
        btn_eliminar.pack(side="left", padx=5)
        
        # Tabla visual para renderizar la lista global de libros
        frame_tabla = tk.Frame(self.area_contenido, bg=self.color_fondo)
        frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)
        
        columnas = ("id", "titulo", "fila", "columna")
        self.tabla_libros = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        
        self.tabla_libros.heading("id", text="ID Libro")
        self.tabla_libros.heading("titulo", text="Título de la Obra")
        self.tabla_libros.heading("fila", text="Fila Estante")
        self.tabla_libros.heading("columna", text="Columna Estante")
        
        self.tabla_libros.column("id", width=120, anchor="center")
        self.tabla_libros.column("titulo", width=300, anchor="w")
        self.tabla_libros.column("fila", width=100, anchor="center")
        self.tabla_libros.column("columna", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_libros.yview)
        self.tabla_libros.configure(yscrollcommand=scrollbar.set)
        self.tabla_libros.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.actualizar_tabla_libros()

    def actualizar_tabla_libros(self):
        """Sincroniza el Treeview gráfico con el arreglo global lista_libros"""
        for fila in self.tabla_libros.get_children():
            self.tabla_libros.delete(fila)
        for lib in lista_libros:
            self.tabla_libros.insert("", "end", values=(lib["id"], lib["titulo"], lib["f"], lib["c"]))

    def registrar_libro_logica(self):
        """Valida e inserta el libro en la matriz bidimensional y el archivo .js"""
        id_lib = self.ent_id.get().strip()
        titulo = self.ent_titulo.get().strip()
        fila_raw = self.ent_f.get().strip()
        col_raw = self.ent_c.get().strip()
        
        if not id_lib or not titulo:
            messagebox.showerror("Error", "ID y Título son estrictamente obligatorios")
            return
        
        try:
            f, c = int(fila_raw), int(col_raw)
            if f >= MAX_F or c >= MAX_C or f < 0 or c < 0:
                raise IndexError("La ubicación está fuera de los rangos válidos de la estantería (0-4).")
            
            if estanteria[f][c] != "Libre":
                messagebox.showwarning("Atención", f"Operación cancelada. El cuadrante [{f}][{c}] ya cuenta con el libro ID: {estanteria[f][c]}")
                return

            # Agregar a las estructuras de memoria heredadas
            lista_libros.append({"id": id_lib, "titulo": titulo, "f": f, "c": c})
            estanteria[f][c] = id_lib
            
            # Persistencia física en archivo plano
            guardar_en_archivo()
            
            messagebox.showinfo("Éxito", f"Libro '{titulo}' indexado en el cuadrante estantería [{f}][{c}]")
            self.actualizar_tabla_libros()
            
            # Limpieza del formulario
            self.ent_id.delete(0, tk.END); self.ent_titulo.delete(0, tk.END)
            self.ent_f.delete(0, tk.END); self.ent_c.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error de entrada", "Los cuadrantes de Fila y Columna deben procesarse como enteros.")
        except IndexError as e:
            messagebox.showerror("Índice Inválido", str(e))

    def ejecutar_busqueda_recursiva(self):
        """Invoca al algoritmo recursivo usando el ID provisto en el campo"""
        id_buscar = self.ent_id.get().strip()
        if not id_buscar:
            messagebox.showwarning("Búsqueda", "Escribe un ID de Libro en el campo de texto superior para ejecutar el algoritmo recursivo.")
            return
            
        resultado = buscar_recursivo(lista_libros, id_buscar)
        if resultado:
            messagebox.showinfo("Búsqueda Recursiva Exitosa", f"Elemento Encontrado:\nTítulo: {resultado['titulo']}\nUbicación Física: Fila {resultado['f']}, Columna {resultado['c']}")
        else:
            messagebox.showwarning("Búsqueda Recursiva", f"El ID '{id_buscar}' no coincide con ningún registro activo.")

    def eliminar_libro_logica(self):
        """Remueve el libro seleccionado del arreglo dinámico, de la matriz y limpia el espacio"""
        seleccion = self.tabla_libros.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila del catálogo de libros para eliminar.")
            return
            
        valores = self.tabla_libros.item(seleccion, "values")
        id_eliminar = valores[0]
        titulo_eliminar = valores[1]
        f_eliminar = int(valores[2])
        c_eliminar = int(valores[3])
        
        if messagebox.askyesno("Confirmar acción", f"¿Está seguro de que desea remover del inventario permanentemente la obra: '{titulo_eliminar}'?"):
            global lista_libros
            # Filtrar de la lista global
            lista_libros = [lib for lib in lista_libros if lib["id"] != id_eliminar]
            # Liberar espacio en el cuadrante de la estantería
            estanteria[f_eliminar][c_eliminar] = "Libre"
            
            guardar_en_archivo()
            self.actualizar_tabla_libros()
            messagebox.showinfo("Inventario Actualizado", "El libro fue removido y la coordenada en la estantería ha quedado libre.")

    # =========================================================================
    # VISTA: ESTANTERÍA (Mapeo de la matriz bidimensional)
    # =========================================================================
    def mostrar_estanteria_matriz(self):
        self.limpiar_contenido()
        
        lbl_titulo = tk.Label(self.area_contenido, text="Mapa de Distribución Física (Estantería)", font=("Arial", 18, "bold"), bg=self.color_fondo, fg="#2c3e50")
        lbl_titulo.pack(pady=15, padx=20, anchor="w")
        
        lbl_desc = tk.Label(self.area_contenido, text="Gráfica en tiempo real de la matriz de almacenamiento (5x5).", font=("Arial", 11), bg=self.color_fondo, fg="#7f8c8d")
        lbl_desc.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Grid para dibujar las celdas directamente de la variable 'estanteria'
        fr_matriz = tk.Frame(self.area_contenido, bg="#bdc3c7", bd=2, relief="solid")
        fr_matriz.pack(pady=10, padx=20)
        
        for r in range(MAX_F):
            for c in range(MAX_C):
                contenido_celda = estanteria[r][c]
                
                # Definición de color estético para indicar estado del espacio
                if contenido_celda == "Libre":
                    bg_color = "#2ecc71"  # Verde brillante
                    fg_color = "#ffffff"
                    texto_celda = "Libre"
                else:
                    bg_color = "#e74c3c"  # Rojo / Coral para ocupado
                    fg_color = "#ffffff"
                    texto_celda = f"ID: {contenido_celda}"
                
                # Crear caja contenedora individual de la cuadrícula
                lbl_celda = tk.Label(fr_matriz, text=f"[{r}][{c}]\n{texto_celda}", bg=bg_color, fg=fg_color, width=12, height=3, relief="flat", font=("Arial", 10, "bold"), bd=1)
                lbl_celda.grid(row=r, column=c, padx=3, pady=3)

    # =========================================================================
    # VISTA: GESTIÓN DE USUARIOS (Lectura de usuarios.json)
    # =========================================================================
    def mostrar_gestion_usuarios(self):
        self.limpiar_contenido()
        
        lbl_titulo = tk.Label(self.area_contenido, text="Control de Usuarios y Permisos", font=("Arial", 18, "bold"), bg=self.color_fondo, fg="#2c3e50")
        lbl_titulo.pack(pady=20, padx=20, anchor="w")
        
        frame_tabla = tk.Frame(self.area_contenido, bg=self.color_fondo)
        frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)
        
        columnas = ("usuario", "contrasena")
        self.tabla_usuarios = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)
        
        self.tabla_usuarios.heading("usuario", text="Nombre de Usuario")
        self.tabla_usuarios.heading("contrasena", text="Contraseña / Clave")
        self.tabla_usuarios.column("usuario", width=200, anchor="center")
        self.tabla_usuarios.column("contrasena", width=200, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_usuarios.yview)
        self.tabla_usuarios.configure(yscrollcommand=scrollbar.set)
        self.tabla_usuarios.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if os.path.exists("datos/usuarios.json"):
            try:
                with open("datos/usuarios.json", "r") as f:
                    usuarios = json.load(f)
                    for usuario, contrasena in usuarios.items():
                        self.tabla_usuarios.insert("", "end", values=(usuario, contrasena))
            except Exception as e:
                tk.Label(self.area_contenido, text=f"Error al leer JSON: {e}", fg="red", bg=self.color_fondo).pack()
        else:
            tk.Label(self.area_contenido, text="Archivo usuarios.json no encontrado.", fg="red", bg=self.color_fondo).pack()

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres salir?"):
            self.root.destroy()


# Para correr de forma aislada para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaAdministrador(root, "admin")
    root.mainloop()