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
        raiz.title("Simulador de System Calls — Incremento 3")
        raiz.geometry("1050x780")
        raiz.minsize(850, 700)
        raiz.columnconfigure(1, weight=1)
        raiz.rowconfigure(1, weight=1)

        ttk.Label(raiz, text="Simulador de interfaz de llamadas al sistema",
                  font=("Segoe UI", 16, "bold"), padding=16).grid(
                      row=0, column=0, columnspan=2, sticky="w")

        lateral = ttk.Frame(raiz, padding=12)
        lateral.grid(row=1, column=0, sticky="ns")

        self.contenido = ttk.Frame(raiz, padding=12)
        self.contenido.grid(row=1, column=1, sticky="nsew")
        self.contenido.columnconfigure(0, weight=1)
        self.contenido.rowconfigure(0, weight=1)
        self.vistas: dict[str, ttk.Frame] = {}

        for nombre in ("Inicio", "Procesos", "Archivos", "Bitácora"):
            ttk.Button(lateral, text=nombre, command=lambda n=nombre: self.mostrar(n)).pack(
                fill="x", pady=5)

        ttk.Button(lateral, text="Salir", command=raiz.destroy).pack(fill="x", pady=20)

        self._crear_inicio()
        self._crear_procesos()
        self._crear_archivos()
        self._crear_bitacora()

        panel_resultado = ttk.LabelFrame(raiz, text="Resultado de la última llamada", padding=8)
        panel_resultado.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=5)
        self.resultado = self._texto_lectura(panel_resultado, 5)
        self._poner_texto(self.resultado, "Todavía no se ha enviado ninguna solicitud.")

        panel_recorrido = ttk.LabelFrame(
            raiz, text="Recorrido conceptual — no cambia privilegios del procesador", padding=8)
        panel_recorrido.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(5, 12))
        self.recorrido = self._texto_lectura(panel_recorrido, 12)
        self._poner_texto(self.recorrido, "El recorrido aparecerá después de una llamada.")
        self.mostrar("Inicio")

    def _vista(self, nombre: str) -> ttk.Frame:
        vista = ttk.Frame(self.contenido)
        self.vistas[nombre] = vista
        return vista

    def _crear_inicio(self) -> None:
        vista = self._vista("Inicio")
        ttk.Label(vista, text="Procesos y archivos simulados", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(vista, wraplength=620, justify="left", text=(
            "Este incremento incorpora las cuatro operaciones de procesos y las siete de archivos.\n\n"
            "GUI → Aplicación en modo usuario → System Call Interface → Kernel simulado → "
            "Dispatcher → Gestor correspondiente → Resultado/error → retorno al usuario.\n\n"
            "Cada solicitud genera un evento de bitácora. Los procesos no son procesos de Windows "
            "y los descriptores no son manejadores del sistema operativo.\n\n"
            "Finalizar conserva el proceso en estado Finalizado. Las consultas no cambian estados. "
            "No hay activación automática de Ejecutando ni planificación del procesador.\n\n"
            "Los archivos físicos quedan confinados en datos/archivos y sobreviven al cierre; "
            "las aperturas y los descriptores solo duran durante la sesión."
        )).pack(anchor="w", pady=16)

    def _crear_procesos(self) -> None:
        vista = self._vista("Procesos")
        vista.columnconfigure(1, weight=1)
        vista.rowconfigure(7, weight=1)
        ttk.Label(vista, text="Gestión de procesos", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(vista, text="Nombre (1 a 50 caracteres)").grid(row=1, column=0, sticky="w", pady=6)
        self.nombre = tk.StringVar()
        self.entrada_nombre = ttk.Entry(vista, textvariable=self.nombre, width=40)
        self.entrada_nombre.grid(row=1, column=1, padx=12)
        ttk.Label(vista, text="Prioridad (1 baja · 5 alta)").grid(row=2, column=0, sticky="w", pady=6)
        self.prioridad = tk.StringVar(value="3")
        ttk.Combobox(vista, textvariable=self.prioridad, values=(1, 2, 3, 4, 5),
                     state="readonly", width=10).grid(row=2, column=1, sticky="w", padx=12)
        ttk.Button(vista, text="Crear proceso", command=self.crear_proceso).grid(
            row=3, column=0, sticky="w", pady=6)
        ttk.Button(vista, text="Listar procesos", command=self.listar_procesos).grid(
            row=3, column=1, sticky="w", padx=12)
        ttk.Label(vista, text="PID (escriba o seleccione una fila)").grid(row=4, column=0, sticky="w")
        self.pid = tk.StringVar()
        ttk.Entry(vista, textvariable=self.pid, width=15).grid(row=4, column=1, sticky="w", padx=12)
        ttk.Button(vista, text="Consultar proceso", command=self.consultar_proceso).grid(
            row=5, column=0, sticky="w", pady=6)
        ttk.Button(vista, text="Finalizar proceso", command=self.finalizar_proceso).grid(
            row=5, column=1, sticky="w", padx=12)
        self.estado_tabla = tk.StringVar(value="Pulse Listar procesos para consultar el estado actual.")
        ttk.Label(vista, textvariable=self.estado_tabla).grid(row=6, column=0, columnspan=2, sticky="w")
        tabla = ttk.Frame(vista)
        tabla.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=4)
        self.procesos = ttk.Treeview(tabla, columns=("pid", "nombre", "estado", "prioridad"),
                                    show="headings", height=4)
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
        vista.columnconfigure(1, weight=1)
        vista.rowconfigure(7, weight=1)
        ttk.Label(vista, text="Gestión de archivos confinados",
                  font=("Segoe UI", 14, "bold")).grid(
                      row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        ttk.Label(vista, text="Nombre simple").grid(row=1, column=0, sticky="w", pady=4)
        self.nombre_archivo = tk.StringVar()
        ttk.Entry(vista, textvariable=self.nombre_archivo, width=32).grid(
            row=1, column=1, sticky="ew", padx=8)
        ttk.Button(vista, text="Crear", command=self.crear_archivo).grid(row=1, column=2)

        ttk.Label(vista, text="Modo").grid(row=2, column=0, sticky="w", pady=4)
        self.modo_archivo = tk.StringVar(value="rw")
        ttk.Combobox(vista, textvariable=self.modo_archivo, values=("r", "w", "rw"),
                     state="readonly", width=8).grid(row=2, column=1, sticky="w", padx=8)
        ttk.Button(vista, text="Abrir", command=self.abrir_archivo).grid(row=2, column=2)

        ttk.Label(vista, text="Descriptor").grid(row=3, column=0, sticky="w", pady=4)
        self.descriptor_archivo = tk.StringVar()
        ttk.Entry(vista, textvariable=self.descriptor_archivo, width=12).grid(
            row=3, column=1, sticky="w", padx=8)
        acciones = ttk.Frame(vista)
        acciones.grid(row=3, column=2, rowspan=2, sticky="n")
        ttk.Button(acciones, text="Leer", command=self.leer_archivo).pack(fill="x", pady=1)
        ttk.Button(acciones, text="Escribir", command=self.escribir_archivo).pack(fill="x", pady=1)
        ttk.Button(acciones, text="Cerrar", command=self.cerrar_archivo).pack(fill="x", pady=1)
        ttk.Button(acciones, text="Eliminar", command=self.eliminar_archivo).pack(fill="x", pady=1)

        ttk.Label(vista, text="Contenido (la escritura reemplaza todo)").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))
        marco_texto = ttk.Frame(vista)
        marco_texto.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=4)
        marco_texto.columnconfigure(0, weight=1)
        self.contenido_archivo = tk.Text(marco_texto, height=4, wrap="word", font=("Consolas", 10))
        barra_texto = ttk.Scrollbar(marco_texto, orient="vertical", command=self.contenido_archivo.yview)
        self.contenido_archivo.configure(yscrollcommand=barra_texto.set)
        self.contenido_archivo.grid(row=0, column=0, sticky="nsew")
        barra_texto.grid(row=0, column=1, sticky="ns")

        barra_acciones = ttk.Frame(vista)
        barra_acciones.grid(row=6, column=0, columnspan=3, sticky="ew", pady=3)
        ttk.Button(barra_acciones, text="Listar archivos", command=self.listar_archivos).pack(side="left")
        self.estado_tabla_archivos = tk.StringVar(
            value="Pulse Listar archivos para consultar el estado actual.")
        ttk.Label(barra_acciones, textvariable=self.estado_tabla_archivos).pack(side="left", padx=12)

        tabla = ttk.Frame(vista)
        tabla.grid(row=7, column=0, columnspan=3, sticky="nsew")
        self.archivos = ttk.Treeview(
            tabla, columns=("nombre", "estado", "descriptor", "modo"), show="headings", height=4)
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
        ttk.Label(vista, text="Bitácora de la sesión (solo lectura)",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))

        tabla = ttk.Frame(vista)
        tabla.pack(fill="both", expand=True)
        columnas = ("evento", "hora", "llamada", "estado", "codigo")
        self.eventos = ttk.Treeview(tabla, columns=columnas, show="headings", height=5)
        for columna, ancho in zip(columnas, (55, 175, 145, 70, 80)):
            self.eventos.heading(columna, text=columna.capitalize())
            self.eventos.column(columna, width=ancho, minwidth=45)
        barra = ttk.Scrollbar(tabla, orient="vertical", command=self.eventos.yview)
        self.eventos.configure(yscrollcommand=barra.set)
        self.eventos.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.eventos.bind("<<TreeviewSelect>>", self.mostrar_evento)
        self.detalle = self._texto_lectura(vista, 7)

    @staticmethod
    def _texto_lectura(padre: ttk.Frame, alto: int) -> tk.Text:
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True)
        texto = tk.Text(marco, height=alto, wrap="word", state="disabled", font=("Consolas", 10))
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
