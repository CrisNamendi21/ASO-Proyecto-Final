"""GUI de procesos, archivos y bitácora (diseño, sección 12)."""

import json
import tkinter as tk
from tkinter import ttk

from ..aplicacion import AplicacionUsuario
from ..contratos import Resultado


class Ventana:
    def __init__(self, raiz: tk.Tk, aplicacion: AplicacionUsuario) -> None:
        self.raiz = raiz
        self.aplicacion = aplicacion
        self._configurar_estilos()
        raiz.title("Simulador de System Calls")
        raiz.geometry("1050x780")
        raiz.minsize(850, 700)
        raiz.configure(background="#F3F5F7")
        raiz.columnconfigure(1, weight=1)
        raiz.rowconfigure(1, weight=1)

        encabezado = ttk.Frame(raiz, style="Header.TFrame", padding=(18, 16))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(encabezado, text="Simulador de interfaz de llamadas al sistema",
                  style="Encabezado.TLabel").pack(anchor="w")

        lateral = ttk.Frame(raiz, style="Sidebar.TFrame", padding=(12, 16))
        lateral.grid(row=1, column=0, sticky="nsew")
        lateral.columnconfigure(0, weight=1)
        lateral.rowconfigure(2, weight=1)

        self.botones_navegacion: dict[str, ttk.Button] = {}
        boton_inicio = ttk.Button(
            lateral, text="Inicio", style="ActiveNavigation.TButton",
            command=lambda: self.mostrar("Inicio"))
        boton_inicio.grid(row=0, column=0, sticky="ew")
        self.botones_navegacion["Inicio"] = boton_inicio

        grupo_navegacion = ttk.Frame(lateral, style="Sidebar.TFrame")
        grupo_navegacion.grid(row=1, column=0, sticky="ew", pady=(28, 0))
        grupo_navegacion.columnconfigure(0, weight=1)
        for fila, nombre in enumerate(("Procesos", "Archivos", "Bitácora")):
            boton = ttk.Button(
                grupo_navegacion, text=nombre, style="Navigation.TButton",
                command=lambda n=nombre: self.mostrar(n))
            boton.grid(row=fila, column=0, sticky="ew", pady=(0, 10))
            self.botones_navegacion[nombre] = boton

        ttk.Button(
            lateral, text="Salir", style="Exit.TButton", command=raiz.destroy).grid(
                row=3, column=0, sticky="ew", pady=(24, 0))

        self.contenido = ttk.Frame(raiz, style="App.TFrame", padding=12)
        self.contenido.grid(row=1, column=1, sticky="nsew")
        self.contenido.columnconfigure(0, weight=1)
        self.contenido.rowconfigure(0, weight=1)
        self.vistas: dict[str, ttk.Frame] = {}

        self._crear_inicio()
        self._crear_procesos()
        self._crear_archivos()
        self._crear_bitacora()

        panel_inferior = ttk.Frame(
            raiz, style="App.TFrame", padding=(12, 5, 12, 12))
        panel_inferior.grid(row=2, column=0, columnspan=2, sticky="nsew")
        panel_inferior.columnconfigure(0, weight=2)
        panel_inferior.columnconfigure(1, weight=3)

        panel_resultado = ttk.LabelFrame(
            panel_inferior, text="Resultado de la última llamada",
            style="Output.TLabelframe", padding=8)
        panel_resultado.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.resultado = self._texto_lectura(panel_resultado, 5)
        self._poner_texto(self.resultado, "Todavía no se ha enviado ninguna solicitud.")

        panel_recorrido = ttk.LabelFrame(
            panel_inferior,
            text="Recorrido conceptual — no cambia privilegios del procesador",
            style="Output.TLabelframe", padding=8)
        panel_recorrido.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.recorrido = self._texto_lectura(panel_recorrido, 5)
        self._poner_texto(self.recorrido, "El recorrido aparecerá después de una llamada.")
        self.mostrar("Inicio")

    def _configurar_estilos(self) -> None:
        """Aplica una escala legible y uniforme sin alterar la lógica de la GUI."""
        estilo = ttk.Style(self.raiz)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")

        fondo = "#F3F5F7"
        blanco = "#FFFFFF"
        principal = "#244A6A"
        secundario = "#3F6685"
        borde = "#D8DEE5"
        texto = "#20252B"
        texto_secundario = "#59636E"
        salir = "#A94B4B"

        estilo.configure("App.TFrame", background=fondo)
        estilo.configure("Sidebar.TFrame", background="#E8EDF2")
        estilo.configure("Header.TFrame", background=blanco)
        estilo.configure("Card.TFrame", background=blanco)

        estilo.configure("TLabel", background=fondo, foreground=texto,
                         font=("Segoe UI", 11))
        estilo.configure("Encabezado.TLabel", background=blanco, foreground=texto,
                         font=("Segoe UI", 18, "bold"))
        estilo.configure("Titulo.TLabel", background=fondo, foreground=principal,
                         font=("Segoe UI", 16, "bold"))
        estilo.configure("Subtitulo.TLabel", background=fondo, foreground=principal,
                         font=("Segoe UI", 11, "bold"))
        estilo.configure("Destacado.TLabel", background=fondo, foreground=texto_secundario,
                         font=("Segoe UI", 11))
        estilo.configure("CardBody.TLabel", background=blanco, foreground=texto_secundario,
                         font=("Segoe UI", 11))
        estilo.configure("CardHint.TLabel", background=blanco, foreground=texto_secundario,
                         font=("Segoe UI", 10))

        estilo.configure("TButton", background=blanco, foreground=texto,
                         bordercolor=borde, lightcolor=borde, darkcolor=borde,
                         font=("Segoe UI", 11), padding=(12, 7), relief="flat")
        estilo.map("TButton", background=[("active", "#E7EDF2")],
                   bordercolor=[("focus", secundario)])
        estilo.configure("Navigation.TButton", background=blanco, foreground=texto,
                         bordercolor=borde, lightcolor=borde, darkcolor=borde,
                         font=("Segoe UI", 11), padding=(12, 8), relief="flat")
        estilo.map("Navigation.TButton",
                   background=[("active", "#DDE7EF")],
                   foreground=[("active", principal)])
        estilo.configure("ActiveNavigation.TButton", background=principal,
                         foreground=blanco, bordercolor=principal,
                         lightcolor=principal, darkcolor=principal,
                         font=("Segoe UI", 11, "bold"), padding=(12, 8), relief="flat")
        estilo.map("ActiveNavigation.TButton",
                   background=[("active", secundario)],
                   foreground=[("active", blanco)])
        estilo.configure("Exit.TButton", background=blanco, foreground=salir,
                         bordercolor=borde, lightcolor=borde, darkcolor=borde,
                         font=("Segoe UI", 11), padding=(12, 8), relief="flat")
        estilo.map("Exit.TButton", background=[("active", "#F4E8E8")],
                   foreground=[("active", "#843B3B")])
        estilo.configure("Primary.TButton", background=principal, foreground=blanco,
                         bordercolor=principal, lightcolor=principal, darkcolor=principal,
                         font=("Segoe UI", 11, "bold"), padding=(14, 8), relief="flat")
        estilo.map("Primary.TButton", background=[("active", secundario)],
                   foreground=[("active", blanco)])
        estilo.configure("Secondary.TButton", background="#E8F0F6", foreground=principal,
                         bordercolor="#B8C8D5", lightcolor="#B8C8D5", darkcolor="#B8C8D5",
                         font=("Segoe UI", 11), padding=(12, 7), relief="flat")
        estilo.map("Secondary.TButton", background=[("active", "#D5E3ED")])
        estilo.configure("Danger.TButton", background=blanco, foreground=salir,
                         bordercolor="#D8BDBD", lightcolor="#D8BDBD", darkcolor="#D8BDBD",
                         font=("Segoe UI", 11), padding=(12, 7), relief="flat")
        estilo.map("Danger.TButton", background=[("active", "#F4E8E8")],
                   foreground=[("active", "#843B3B")])

        estilo.configure("TEntry", fieldbackground=blanco, foreground=texto,
                         bordercolor=borde, insertcolor=texto,
                         font=("Segoe UI", 11), padding=5)
        estilo.configure("TCombobox", fieldbackground=blanco, background=blanco,
                         foreground=texto, bordercolor=borde, arrowcolor=principal,
                         font=("Segoe UI", 11), padding=4)

        estilo.configure("TLabelframe", background=fondo, bordercolor=borde,
                         lightcolor=borde, darkcolor=borde, relief="solid")
        estilo.configure("TLabelframe.Label", background=fondo, foreground=texto,
                         font=("Segoe UI", 11, "bold"))
        estilo.configure("Card.TLabelframe", background=blanco, bordercolor=borde,
                         lightcolor=borde, darkcolor=borde, relief="solid")
        estilo.configure("Card.TLabelframe.Label", background=blanco,
                         foreground=principal, font=("Segoe UI", 11, "bold"))
        estilo.configure("Output.TLabelframe", background=blanco, bordercolor=borde,
                         lightcolor=borde, darkcolor=borde, relief="solid")
        estilo.configure("Output.TLabelframe.Label", background=blanco,
                         foreground=principal, font=("Segoe UI", 11, "bold"))

        estilo.configure("Treeview", background=blanco, fieldbackground=blanco,
                         foreground=texto, bordercolor=borde,
                         font=("Segoe UI", 10), rowheight=27)
        estilo.configure("Treeview.Heading", background="#E8EDF2", foreground=principal,
                         bordercolor=borde, font=("Segoe UI", 10, "bold"))
        estilo.map("Treeview", background=[("selected", secundario)],
                   foreground=[("selected", blanco)])

    def _vista(self, nombre: str) -> ttk.Frame:
        vista = ttk.Frame(self.contenido, style="App.TFrame")
        self.vistas[nombre] = vista
        return vista

    def _crear_inicio(self) -> None:
        vista = self._vista("Inicio")
        vista.columnconfigure(0, weight=1, uniform="inicio")
        vista.columnconfigure(1, weight=1, uniform="inicio")
        vista.rowconfigure(3, weight=1)

        ttk.Label(vista, text="Procesos y archivos simulados", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(
            vista, style="Destacado.TLabel", justify="left", wraplength=620,
            text="Esta versión incorpora las cuatro operaciones de procesos y las siete "
                 "operaciones de archivos mediante una arquitectura por capas.").grid(
                     row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        flujo = ttk.LabelFrame(
            vista, text="Recorrido de una solicitud", style="Card.TLabelframe", padding=8)
        flujo.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(
            flujo, style="CardBody.TLabel", justify="left", wraplength=600,
            text="GUI → Aplicación en modo usuario → System Call Interface → Kernel simulado "
                 "→ Dispatcher → Gestor correspondiente → Resultado o error → Usuario").pack(
                     anchor="w", fill="x")

        procesos = ttk.LabelFrame(
            vista, text="Procesos simulados", style="Card.TLabelframe", padding=8)
        procesos.grid(row=3, column=0, sticky="nsew", padx=(0, 6), pady=(0, 8))
        ttk.Label(
            procesos, style="CardBody.TLabel", justify="left", wraplength=280,
            text="No son procesos de Windows. Finalizar conserva el registro y las consultas "
                 "no cambian estados. No se implementa planificación real.").pack(
                     anchor="nw", fill="both", expand=True)

        archivos = ttk.LabelFrame(
            vista, text="Archivos confinados", style="Card.TLabelframe", padding=8)
        archivos.grid(row=3, column=1, sticky="nsew", padx=(6, 0), pady=(0, 8))
        ttk.Label(
            archivos, style="CardBody.TLabel", justify="left", wraplength=280,
            text="Permanecen bajo datos/archivos y sobreviven al cierre. Los descriptores son "
                 "simulados y las aperturas duran solo durante la sesión.").pack(
                     anchor="nw", fill="both", expand=True)

        bitacora = ttk.LabelFrame(
            vista, text="Bitácora de la sesión", style="Card.TLabelframe", padding=8)
        bitacora.grid(row=4, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            bitacora, style="CardBody.TLabel", justify="left", wraplength=600,
            text="Cada solicitud genera un evento final con su llamada, resultado, código y "
                 "mensaje. La consulta de la bitácora es de solo lectura.").pack(
                     anchor="w", fill="x")

    def _crear_procesos(self) -> None:
        vista = self._vista("Procesos")
        vista.columnconfigure(0, weight=1)
        vista.rowconfigure(2, weight=1)
        ttk.Label(vista, text="Gestión de procesos", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6))

        nuevo = ttk.LabelFrame(
            vista, text="Nuevo proceso", style="Card.TLabelframe", padding=8)
        nuevo.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        nuevo.columnconfigure(1, weight=1)

        ttk.Label(
            nuevo, text="Nombre (1 a 50 caracteres)", style="CardBody.TLabel").grid(
                row=0, column=0, sticky="w", pady=4)
        self.nombre = tk.StringVar()
        self.entrada_nombre = ttk.Entry(nuevo, textvariable=self.nombre, width=32)
        self.entrada_nombre.grid(row=0, column=1, sticky="w", padx=(20, 8), pady=4)
        ttk.Label(
            nuevo, text="Prioridad (1 baja · 5 alta)", style="CardBody.TLabel").grid(
                row=1, column=0, sticky="w", pady=4)
        self.prioridad = tk.StringVar(value="3")
        ttk.Combobox(
            nuevo, textvariable=self.prioridad, values=(1, 2, 3, 4, 5),
            state="readonly", width=10).grid(
                row=1, column=1, sticky="w", padx=(20, 8), pady=4)
        ttk.Button(
            nuevo, text="Crear proceso", style="Primary.TButton",
            command=self.crear_proceso).grid(
                row=0, column=2, rowspan=2, sticky="e", padx=(12, 0))

        registrados = ttk.LabelFrame(
            vista, text="Procesos registrados", style="Card.TLabelframe", padding=8)
        registrados.grid(row=2, column=0, sticky="nsew")
        registrados.columnconfigure(1, weight=1)
        registrados.rowconfigure(4, weight=1)

        ttk.Label(
            registrados, text="PID (escriba o seleccione una fila)",
            style="CardBody.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.pid = tk.StringVar()
        ttk.Entry(registrados, textvariable=self.pid, width=15).grid(
            row=1, column=1, sticky="w", padx=(20, 0), pady=4)

        acciones = ttk.Frame(registrados, style="Card.TFrame")
        acciones.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(4, 6))
        ttk.Button(
            acciones, text="Consultar proceso", style="Secondary.TButton",
            command=self.consultar_proceso).pack(side="left", padx=(0, 8))
        ttk.Button(
            acciones, text="Finalizar proceso", style="Danger.TButton",
            command=self.finalizar_proceso).pack(side="left")
        ttk.Button(
            acciones, text="Listar procesos", style="Secondary.TButton",
            command=self.listar_procesos).pack(side="right")

        self.estado_tabla = tk.StringVar(value="Pulse Listar procesos para consultar el estado actual.")
        ttk.Label(
            registrados, textvariable=self.estado_tabla, style="CardHint.TLabel").grid(
                row=3, column=0, columnspan=3, sticky="w", pady=(0, 6))

        tabla = ttk.Frame(registrados, style="Card.TFrame")
        tabla.grid(row=4, column=0, columnspan=3, sticky="nsew")
        self.procesos = ttk.Treeview(tabla, columns=("pid", "nombre", "estado", "prioridad"),
                                    show="headings", height=2)
        for columna, titulo, ancho in (("pid", "PID", 65), ("nombre", "Nombre", 260),
                                      ("estado", "Estado", 110), ("prioridad", "Prioridad", 80)):
            self.procesos.heading(columna, text=titulo)
            self.procesos.column(columna, width=ancho, minwidth=50)
        barra = ttk.Scrollbar(tabla, orient="vertical", command=self.procesos.yview)
        self.procesos.configure(yscrollcommand=barra.set)
        self.procesos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.procesos.bind("<<TreeviewSelect>>", self.seleccionar_proceso)

    def _crear_archivos(self) -> None:
        vista = self._vista("Archivos")
        vista.columnconfigure(0, weight=1)
        vista.rowconfigure(2, weight=1)
        vista.rowconfigure(3, weight=4)
        ttk.Label(vista, text="Gestión de archivos confinados",
                  style="Titulo.TLabel").grid(
                      row=0, column=0, sticky="w", pady=(0, 4))

        superior = ttk.Frame(vista, style="App.TFrame")
        superior.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        superior.columnconfigure(0, weight=1, uniform="archivos_superior")
        superior.columnconfigure(1, weight=1, uniform="archivos_superior")

        archivo = ttk.LabelFrame(
            superior, text="Archivo", style="Card.TLabelframe", padding=(8, 4))
        archivo.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        archivo.columnconfigure(1, weight=1)

        ttk.Label(archivo, text="Nombre simple", style="CardBody.TLabel").grid(
            row=0, column=0, sticky="w", pady=3)
        self.nombre_archivo = tk.StringVar()
        ttk.Entry(archivo, textvariable=self.nombre_archivo, width=26).grid(
            row=0, column=1, sticky="ew", padx=(12, 0), pady=2)

        ttk.Label(archivo, text="Modo", style="CardBody.TLabel").grid(
            row=1, column=0, sticky="w", pady=3)
        self.modo_archivo = tk.StringVar(value="rw")
        ttk.Combobox(
            archivo, textvariable=self.modo_archivo, values=("r", "w", "rw"),
            state="readonly", width=9).grid(
                row=1, column=1, sticky="w", padx=(12, 0), pady=2)

        acciones_archivo = ttk.Frame(archivo, style="Card.TFrame")
        acciones_archivo.grid(
            row=2, column=1, sticky="w", padx=(12, 0), pady=(4, 0))
        ttk.Button(
            acciones_archivo, text="Crear", style="Primary.TButton",
            command=self.crear_archivo, width=7, padding=(9, 5)).pack(
                side="left", padx=(0, 8))
        ttk.Button(
            acciones_archivo, text="Abrir", style="Secondary.TButton",
            command=self.abrir_archivo, width=7, padding=(9, 5)).pack(side="left")

        operaciones = ttk.LabelFrame(
            superior, text="Operaciones mediante descriptor",
            style="Card.TLabelframe", padding=(8, 4))
        operaciones.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
        operaciones.columnconfigure(1, weight=1)

        ttk.Label(operaciones, text="Descriptor", style="CardBody.TLabel").grid(
            row=0, column=0, sticky="w", pady=3)
        self.descriptor_archivo = tk.StringVar()
        ttk.Entry(operaciones, textvariable=self.descriptor_archivo, width=13).grid(
            row=0, column=1, sticky="w", padx=(12, 8), pady=2)
        ttk.Button(
            operaciones, text="Eliminar", style="Danger.TButton",
            command=self.eliminar_archivo, width=7, padding=(9, 5)).grid(
                row=0, column=2, sticky="e", pady=2)

        acciones = ttk.Frame(operaciones, style="Card.TFrame")
        acciones.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))
        ttk.Button(
            acciones, text="Leer", style="Secondary.TButton",
            command=self.leer_archivo, width=6, padding=(8, 5)).pack(
                side="left", padx=(0, 8))
        ttk.Button(
            acciones, text="Escribir", style="Secondary.TButton",
            command=self.escribir_archivo, width=7, padding=(8, 5)).pack(
                side="left", padx=(0, 8))
        ttk.Button(
            acciones, text="Cerrar", style="Secondary.TButton",
            command=self.cerrar_archivo, width=6, padding=(8, 5)).pack(side="left")

        contenido = ttk.LabelFrame(
            vista, text="Contenido (la escritura reemplaza todo)",
            style="Card.TLabelframe", padding=8)
        contenido.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
        contenido.columnconfigure(0, weight=1)
        contenido.rowconfigure(0, weight=1)

        marco_texto = ttk.Frame(contenido, style="Card.TFrame")
        marco_texto.grid(row=0, column=0, sticky="nsew")
        marco_texto.columnconfigure(0, weight=1)
        marco_texto.rowconfigure(0, weight=1)
        self.contenido_archivo = tk.Text(
            marco_texto, width=50, height=2, wrap="word", font=("Consolas", 11),
            background="#F8FAFC", foreground="#20252B", relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground="#D8DEE5", padx=8, pady=6)
        barra_texto = ttk.Scrollbar(marco_texto, orient="vertical", command=self.contenido_archivo.yview)
        self.contenido_archivo.configure(yscrollcommand=barra_texto.set)
        self.contenido_archivo.grid(row=0, column=0, sticky="nsew")
        barra_texto.grid(row=0, column=1, sticky="ns")

        registrados = ttk.LabelFrame(
            vista, text="Archivos registrados", style="Card.TLabelframe", padding=8)
        registrados.grid(row=3, column=0, sticky="nsew")
        registrados.columnconfigure(0, weight=1)
        registrados.rowconfigure(1, weight=1)

        barra_acciones = ttk.Frame(registrados, style="Card.TFrame")
        barra_acciones.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Button(
            barra_acciones, text="Listar archivos", style="Secondary.TButton",
            command=self.listar_archivos).pack(side="right")
        self.estado_tabla_archivos = tk.StringVar(
            value="Pulse Listar archivos para consultar el estado actual.")
        ttk.Label(
            barra_acciones, textvariable=self.estado_tabla_archivos,
            style="CardHint.TLabel").pack(side="left")

        tabla = ttk.Frame(registrados, style="Card.TFrame")
        tabla.grid(row=1, column=0, sticky="nsew")
        self.archivos = ttk.Treeview(
            tabla, columns=("nombre", "estado", "descriptor", "modo"), show="headings", height=2)
        for columna, titulo, ancho in (("nombre", "Nombre", 250), ("estado", "Estado", 90),
                                      ("descriptor", "Descriptor", 90), ("modo", "Modo", 65)):
            self.archivos.heading(columna, text=titulo)
            self.archivos.column(columna, width=ancho, minwidth=50)
        barra = ttk.Scrollbar(tabla, orient="vertical", command=self.archivos.yview)
        self.archivos.configure(yscrollcommand=barra.set)
        self.archivos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.archivos.bind("<<TreeviewSelect>>", self.seleccionar_archivo)

    def _crear_bitacora(self) -> None:
        vista = self._vista("Bitácora")
        vista.columnconfigure(0, weight=1)
        vista.rowconfigure(1, weight=3)
        vista.rowconfigure(3, weight=2)
        ttk.Label(vista, text="Bitácora de la sesión (solo lectura)",
                  style="Titulo.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        tabla = ttk.Frame(vista, style="Card.TFrame", padding=8)
        tabla.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        columnas = ("evento", "hora", "llamada", "estado", "codigo")
        titulos = ("Evento", "Hora", "Llamada", "Estado", "Código")
        self.eventos = ttk.Treeview(tabla, columns=columnas, show="headings", height=4)
        for columna, titulo, ancho in zip(columnas, titulos, (55, 210, 170, 80, 100)):
            self.eventos.heading(columna, text=titulo)
            ancla = "center" if columna in {"evento", "estado", "codigo"} else "w"
            self.eventos.column(columna, width=ancho, minwidth=45, anchor=ancla)
        barra = ttk.Scrollbar(tabla, orient="vertical", command=self.eventos.yview)
        self.eventos.configure(yscrollcommand=barra.set)
        self.eventos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.eventos.bind("<<TreeviewSelect>>", self.mostrar_evento)

        ttk.Label(
            vista, text="Detalle del evento seleccionado", style="Subtitulo.TLabel").grid(
                row=2, column=0, sticky="w", pady=(0, 6))
        detalle = ttk.Frame(vista, style="Card.TFrame", padding=8)
        detalle.grid(row=3, column=0, sticky="nsew")
        self.detalle = self._texto_lectura(detalle, 5)
        self.detalle.configure(width=50)

    @staticmethod
    def _texto_lectura(padre: ttk.Frame, alto: int) -> tk.Text:
        marco = ttk.Frame(padre, style="Card.TFrame")
        marco.pack(fill="both", expand=True)
        texto = tk.Text(
            marco, height=alto, wrap="word", state="disabled", font=("Consolas", 11),
            background="#F8FAFC", foreground="#20252B", relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground="#D8DEE5", padx=8)
        barra = ttk.Scrollbar(marco, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        texto.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return texto

    @staticmethod
    def _poner_texto(widget: tk.Text, contenido: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", contenido)
        widget.configure(state="disabled")

    def mostrar(self, nombre: str) -> None:
        for vista in self.vistas.values():
            vista.grid_forget()
        self.vistas[nombre].grid(row=0, column=0, sticky="nsew")
        for seccion, boton in self.botones_navegacion.items():
            boton.configure(style=(
                "ActiveNavigation.TButton" if seccion == nombre else "Navigation.TButton"))
        if nombre == "Bitácora":
            self.actualizar_bitacora()

    def crear_proceso(self) -> None:
        # El selector facilita el tipo, pero el gestor conserva la validación.
        try:
            prioridad = int(self.prioridad.get())
        except ValueError:
            prioridad = self.prioridad.get()
        resultado = self.aplicacion.create_process(self.nombre.get(), prioridad)
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.pid.set(str(resultado.datos["pid"]))
            self.estado_tabla.set("Hay cambios: pulse Listar procesos para actualizar la tabla.")

    def listar_procesos(self) -> None:
        resultado = self.aplicacion.list_processes()
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.procesos.delete(*self.procesos.get_children())
            for proceso in resultado.datos["procesos"]:
                self.procesos.insert("", "end", iid=str(proceso["pid"]), values=(
                    proceso["pid"], proceso["nombre"], proceso["estado"], proceso["prioridad"]))
            self.estado_tabla.set("Tabla del último listado solicitado.")

    def _leer_pid(self) -> int | str:
        try:
            return int(self.pid.get())
        except ValueError:
            # Enviar la entrada inválida al sistema para que genere PROC_002 y evento.
            return self.pid.get()

    def consultar_proceso(self) -> None:
        self._presentar_resultado(self.aplicacion.get_process(self._leer_pid()))

    def finalizar_proceso(self) -> None:
        resultado = self.aplicacion.terminate_process(self._leer_pid())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.estado_tabla.set("Hay cambios: pulse Listar procesos para actualizar la tabla.")

    def seleccionar_proceso(self, _evento: tk.Event) -> None:
        seleccion = self.procesos.selection()
        if seleccion:
            self.pid.set(seleccion[0])

    def crear_archivo(self) -> None:
        resultado = self.aplicacion.create_file(self.nombre_archivo.get())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self._marcar_tabla_archivos_pendiente()

    def abrir_archivo(self) -> None:
        resultado = self.aplicacion.open_file(
            self.nombre_archivo.get(), self.modo_archivo.get())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.descriptor_archivo.set(str(resultado.datos["descriptor"]))
            self._marcar_tabla_archivos_pendiente()

    def _leer_descriptor(self) -> int | str:
        try:
            return int(self.descriptor_archivo.get())
        except ValueError:
            return self.descriptor_archivo.get()

    def leer_archivo(self) -> None:
        resultado = self.aplicacion.read_file(self._leer_descriptor())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.contenido_archivo.delete("1.0", "end")
            self.contenido_archivo.insert("1.0", resultado.datos["contenido"])

    def escribir_archivo(self) -> None:
        datos = self.contenido_archivo.get("1.0", "end-1c")
        resultado = self.aplicacion.write_file(self._leer_descriptor(), datos)
        self._presentar_resultado(resultado)

    def cerrar_archivo(self) -> None:
        resultado = self.aplicacion.close_file(self._leer_descriptor())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self._marcar_tabla_archivos_pendiente()

    def eliminar_archivo(self) -> None:
        resultado = self.aplicacion.delete_file(self.nombre_archivo.get())
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self._marcar_tabla_archivos_pendiente()

    def listar_archivos(self) -> None:
        resultado = self.aplicacion.list_files()
        self._presentar_resultado(resultado)
        if resultado.estado == "EXITO":
            self.archivos.delete(*self.archivos.get_children())
            for archivo in resultado.datos["archivos"]:
                self.archivos.insert("", "end", values=(
                    archivo["nombre"], archivo["estado"],
                    archivo["descriptor"] if archivo["descriptor"] is not None else "",
                    archivo["modo"] if archivo["modo"] is not None else ""))
            self.estado_tabla_archivos.set("Tabla del último listado solicitado.")

    def seleccionar_archivo(self, _evento: tk.Event) -> None:
        seleccion = self.archivos.selection()
        if not seleccion:
            return
        valores = self.archivos.item(seleccion[0], "values")
        self.nombre_archivo.set(valores[0])
        self.descriptor_archivo.set(valores[2])
        if valores[3] in {"r", "w", "rw"}:
            self.modo_archivo.set(valores[3])

    def _marcar_tabla_archivos_pendiente(self) -> None:
        self.estado_tabla_archivos.set(
            "Hay cambios: pulse Listar archivos para actualizar la tabla.")

    def _presentar_resultado(self, resultado: Resultado) -> None:
        self._poner_texto(self.resultado, (
            f"Estado: {resultado.estado}\nCódigo: {resultado.codigo}\n"
            f"Mensaje: {resultado.mensaje}\nDatos: {json.dumps(resultado.datos, ensure_ascii=False)}"
        ))
        recorrido = ("GUI → Aplicación en modo usuario", *self.aplicacion.consultar_recorrido(),
                     "Aplicación en modo usuario → GUI: mostrar resultado")
        self._poner_texto(self.recorrido, "\n".join(recorrido))

    def actualizar_bitacora(self) -> None:
        self.eventos.delete(*self.eventos.get_children())
        for evento in self.aplicacion.consultar_bitacora():
            self.eventos.insert("", "end", iid=str(evento.numero), values=(
                evento.numero, evento.fecha_hora, evento.llamada,
                evento.resultado.estado, evento.resultado.codigo))
        self._poner_texto(self.detalle, "Seleccione un evento para consultar parámetros y resultado.")

    def mostrar_evento(self, _evento: tk.Event) -> None:
        seleccion = self.eventos.selection()
        if not seleccion:
            return
        numero = int(seleccion[0])
        for evento in self.aplicacion.consultar_bitacora():
            if evento.numero == numero:
                self._poner_texto(self.detalle, (
                    f"Evento {evento.numero} · {evento.fecha_hora}\n"
                    f"Llamada: {evento.llamada}\n"
                    f"Parámetros: {json.dumps(evento.parametros, ensure_ascii=False)}\n"
                    f"Estado: {evento.resultado.estado} · Código: {evento.resultado.codigo}\n"
                    f"Mensaje: {evento.resultado.mensaje}\n"
                    f"Datos: {json.dumps(evento.resultado.datos, ensure_ascii=False)}"
                ))
                break
