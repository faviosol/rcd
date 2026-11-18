import csv
import ipaddress
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

INCLUIR_ROUTER = True

CLASES = {
    "C": {"prefijo": 24, "red_privada": "192.168.0.0"},
    "B": {"prefijo": 16, "red_privada": "172.16.0.0"},
    "A": {"prefijo": 8, "red_privada": "10.0.0.0"},
}

ORDEN_CLASES = ["C", "B", "A"]


def detectar_clase(ip):
    primer_octeto = int(str(ip).split(".")[0])
    if 1 <= primer_octeto <= 126:
        return "A"
    if 128 <= primer_octeto <= 191:
        return "B"
    if 192 <= primer_octeto <= 223:
        return "C"
    return None


def bits_para_hosts(cantidad):
    n = 2
    while 2**n - 2 < cantidad:
        n += 1
    return n


def elegir_clase_vlsm(clase_inicial, total_direcciones_necesarias):
    for clase in ORDEN_CLASES[ORDEN_CLASES.index(clase_inicial) :]:
        bits_disponibles = 32 - CLASES[clase]["prefijo"]
        if total_direcciones_necesarias <= (2**bits_disponibles):
            return clase
    return None


class AppSubnettingVLSM:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema Avanzado de Subneteo IPv4 - VLSM")
        self.ventana.geometry("1150x700")
        self.ventana.configure(bg="#f1f5f9")
        self.resultados_vlsm = []
        self.crear_interfaz()

    def crear_interfaz(self):
        encabezado = tk.Frame(self.ventana, bg="#1e3a8a", pady=15)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text="CALCULADORA DE SUBNETEO VLSM AUTOMÁTICA",
            bg="#1e3a8a",
            fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack()

        panel = tk.Frame(
            self.ventana, bg="white", padx=15, pady=15, bd=1, relief="groove"
        )
        panel.pack(fill="x", padx=15, pady=15)

        self.txt_ip = self.crear_campo(
            panel, "IP Principal:", "192.168.1.0", 0, 0
        )
        self.txt_hosts_lista = self.crear_campo(
            panel,
            "Hosts por Subred (separados por coma):",
            "100, 50, 25, 10, 2",
            0,
            1,
        )

        btn_frame = tk.Frame(panel, bg="white")
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Calcular Distribución VLSM",
            command=self.calcular,
        ).pack(side="left", padx=5)

        self.btn_exportar = ttk.Button(
            btn_frame,
            text="Exportar a Excel (.csv)",
            command=self.exportar_excel,
            state="disabled",
        )
        self.btn_exportar.pack(side="left", padx=5)

        tabla_frame = tk.Frame(self.ventana)
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = (
            "num",
            "req",
            "red",
            "prefijo",
            "mask",
            "broad",
            "router",
            "hosts",
        )
        self.tabla = ttk.Treeview(
            tabla_frame, columns=columnas, show="headings"
        )

        self.tabla.heading("num", text="N°")
        self.tabla.heading("req", text="Hosts Pedidos")
        self.tabla.heading("red", text="Dirección de Red")
        self.tabla.heading("prefijo", text="Prefijo")
        self.tabla.heading("mask", text="Máscara de Subred")
        self.tabla.heading("broad", text="Broadcast")
        self.tabla.heading("router", text="IP Router (Gateway)")
        self.tabla.heading("hosts", text="Rango de Hosts Asignados")

        self.tabla.column("num", width=40, anchor="center")
        self.tabla.column("req", width=100, anchor="center")
        self.tabla.column("red", width=140, anchor="center")
        self.tabla.column("prefijo", width=70, anchor="center")
        self.tabla.column("mask", width=140, anchor="center")
        self.tabla.column("broad", width=140, anchor="center")
        self.tabla.column("router", width=140, anchor="center")
        self.tabla.column("hosts", width=280, anchor="w")

        scroll = ttk.Scrollbar(
            tabla_frame, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def crear_campo(self, padre, etiqueta, valor, fila, col):
        frame = tk.Frame(padre, bg="white")
        frame.grid(row=fila, column=col, padx=10, pady=5, sticky="ew")
        tk.Label(
            frame, text=etiqueta, bg="white", font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        entrada = ttk.Entry(frame, font=("Segoe UI", 10))
        entrada.pack(fill="x", pady=2)
        entrada.insert(0, valor)
        padre.grid_columnconfigure(col, weight=1)
        return entrada

    def calcular(self):
        try:
            self.tabla.delete(*self.tabla.get_children())
            ip_obj = ipaddress.IPv4Address(self.txt_ip.get().strip())
            clase_original = detectar_clase(ip_obj)

            if not clase_original:
                raise ValueError(
                    "La IP pertenece a una clase reservada o experimental (D/E)."
                )

            raw_hosts = self.txt_hosts_lista.get().strip()
            if not raw_hosts:
                raise ValueError("Ingrese al menos una cantidad de hosts.")

            lista_hosts = [
                int(h.strip()) for h in raw_hosts.split(",") if h.strip()
            ]
            if any(h <= 0 for h in lista_hosts):
                raise ValueError(
                    "Todas las cantidades de hosts deben ser mayores a 0."
                )

            lista_hosts.sort(reverse=True)

            bloques_necesarios = []
            total_ips_requeridas = 0

            for h in lista_hosts:
                hosts_a_contar = h + 1 if INCLUIR_ROUTER else h
                b_host = bits_para_hosts(hosts_a_contar)
                tamano_bloque = 2**b_host
                total_ips_requeridas += tamano_bloque
                bloques_necesarios.append((h, b_host, tamano_bloque))

            clase_elegida = elegir_clase_vlsm(
                clase_original, total_ips_requeridas
            )
            if not clase_elegida:
                raise ValueError(
                    "Requerimiento imposible: Se excede la capacidad total de una red Clase A."
                )

            prefijo_clase = CLASES[clase_elegida]["prefijo"]

            if clase_elegida != clase_original:
                base_ip = CLASES[clase_elegida]["red_privada"]
                messagebox.showinfo(
                    "Cambio Automático de Clase",
                    f"La clase {clase_original} original no tiene espacio suficiente para todas las subredes VLSM.\n\n"
                    f"El sistema escaló automáticamente a Clase {clase_elegida} usando: {base_ip}/{prefijo_clase}",
                )
            else:
                base_ip = str(ip_obj)

            red_base = ipaddress.IPv4Network(
                f"{base_ip}/{prefijo_clase}", strict=False
            )
            ip_actual = red_base.network_address

            self.resultados_vlsm = []

            for idx, (hosts_pedidos, b_host, tamano_bloque) in enumerate(
                bloques_necesarios, start=1
            ):
                prefijo_subred = 32 - b_host
                subred = ipaddress.IPv4Network(
                    f"{ip_actual}/{prefijo_subred}", strict=True
                )

                router = subred.network_address + 1
                p_host = (
                    subred.network_address + 2
                    if INCLUIR_ROUTER
                    else subred.network_address + 1
                )
                u_host = (
                    subred.network_address + 1 + hosts_pedidos
                    if INCLUIR_ROUTER
                    else subred.network_address + hosts_pedidos
                )
                rango_txt = f"{p_host} - {u_host}"

                fila_datos = {
                    "num": idx,
                    "req": hosts_pedidos,
                    "red": str(subred.network_address),
                    "prefijo": f"/{prefijo_subred}",
                    "mask": str(subred.netmask),
                    "broad": str(subred.broadcast_address),
                    "router": str(router) if INCLUIR_ROUTER else "N/A",
                    "hosts": rango_txt,
                }
                self.resultados_vlsm.append(fila_datos)

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        fila_datos["num"],
                        fila_datos["req"],
                        fila_datos["red"],
                        fila_datos["prefijo"],
                        fila_datos["mask"],
                        fila_datos["broad"],
                        fila_datos["router"],
                        fila_datos["hosts"],
                    ),
                )

                ip_actual = subred.broadcast_address + 1

            self.btn_exportar.configure(state="normal")

        except ValueError as e:
            messagebox.showerror(
                "Error de Validación",
                f"Verifique los datos ingresados.\nDetalle: {e}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def exportar_excel(self):
        if not self.resultados_vlsm:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV (Excel)", "*.csv")],
        )
        if not filepath:
            return

        try:
            with open(
                filepath, mode="w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(
                    [
                        "N°",
                        "Hosts Pedidos",
                        "Direccion de Red",
                        "Prefijo",
                        "Mascara de Subred",
                        "Broadcast",
                        "IP del Router (Gateway)",
                        "Rango de Hosts Asignados",
                    ]
                )

                for item in self.resultados_vlsm:
                    writer.writerow(
                        [
                            item["num"],
                            item["req"],
                            item["red"],
                            item["prefijo"],
                            item["mask"],
                            item["broad"],
                            item["router"],
                            item["hosts"],
                        ]
                    )

            messagebox.showinfo(
                "Éxito",
                "Tabla VLSM exportada correctamente para abrir en Excel.",
            )
        except Exception as e:
            messagebox.showerror(
                "Error al Exportar", f"No se pudo guardar el archivo: {e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AppSubnettingVLSM(root)
    root.mainloop()