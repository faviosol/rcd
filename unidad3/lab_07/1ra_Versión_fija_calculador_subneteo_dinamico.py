import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

# Configuración académica de la consigna
INCLUIR_ROUTER = True
CLASES = {
    "C": {"prefijo": 24, "red_privada": "192.168.0.0"},
    "B": {"prefijo": 16, "red_privada": "172.16.0.0"},
    "A": {"prefijo": 8, "red_privada": "10.0.0.0"},
}
ORDEN_CLASES = ["C", "B", "A"]

def detectar_clase(ip):
    primer_octeto = int(str(ip).split(".")[0])
    if 1 <= primer_octeto <= 126: return "A"
    if 128 <= primer_octeto <= 191: return "B"
    if 192 <= primer_octeto <= 223: return "C"
    return None

def bits_para_subredes(cantidad):
    return (cantidad - 1).bit_length()

def bits_para_hosts(cantidad):
    n = 2
    while 2**n - 2 < cantidad:
        n += 1
    return n

def elegir_clase(clase_inicial, bits_necesarios):
    for clase in ORDEN_CLASES[ORDEN_CLASES.index(clase_inicial):]:
        bits_disponibles = 32 - CLASES[clase]["prefijo"]
        if bits_necesarios <= bits_disponibles:
            return clase
    return None

class AppSubnetting:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema Avanzado de Subneteo IPv4")
        self.ventana.geometry("1100x700")
        self.ventana.configure(bg="#f1f5f9")
        self.subredes_calculadas = []
        self.num_hosts_pedidos = 0
        self.crear_interfaz()

    def crear_interfaz(self):
        # Encabezado estético
        encabezado = tk.Frame(self.ventana, bg="#1e3a8a", pady=15)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="CALCULADORA DE SUBNETEO AUTOMÁTICA", bg="#1e3a8a", fg="white", font=("Segoe UI", 16, "bold")).pack()
        
        # Panel de entrada de datos
        panel = tk.Frame(self.ventana, bg="white", padx=15, pady=15, bd=1, relief="groove")
        panel.pack(fill="x", padx=15, pady=15)
        
        self.txt_ip = self.crear_campo(panel, "IP Principal:", "192.168.1.10", 0, 0)
        self.txt_subredes = self.crear_campo(panel, "Cantidad de Subredes:", "2", 0, 1)
        self.txt_hosts = self.crear_campo(panel, "Hosts por Subred:", "50", 0, 2)
        
        # Botones de acción
        btn_frame = tk.Frame(panel, bg="white")
        btn_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=(10,0))
        
        ttk.Button(btn_frame, text="Calcular Distribución", command=self.calcular).pack(side="left", padx=5)
        self.btn_exportar = ttk.Button(btn_frame, text="Exportar a Excel (.csv)", command=self.exportar_excel, state="disabled")
        self.btn_exportar.pack(side="left", padx=5)
        
        # Tabla de resultados visual
        tabla_frame = tk.Frame(self.ventana)
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        columnas = ("num", "red", "mask", "broad", "router", "hosts")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        
        self.tabla.heading("num", text="N°")
        self.tabla.heading("red", text="Dirección de Red")
        self.tabla.heading("mask", text="Máscara de Subred")
        self.tabla.heading("broad", text="Broadcast")
        self.tabla.heading("router", text="IP Router (Gateway)")
        self.tabla.heading("hosts", text="Rango de Hosts Asignados")
        
        self.tabla.column("num", width=40, anchor="center")
        self.tabla.column("red", width=150, anchor="center")
        self.tabla.column("mask", width=150, anchor="center")
        self.tabla.column("broad", width=150, anchor="center")
        self.tabla.column("router", width=150, anchor="center")
        self.tabla.column("hosts", width=300, anchor="w")
        
        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def crear_campo(self, padre, etiqueta, valor, fila, col):
        frame = tk.Frame(padre, bg="white")
        frame.grid(row=fila, column=col, padx=10, pady=5, sticky="ew")
        tk.Label(frame, text=etiqueta, bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
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
                raise ValueError("La IP pertenece a una clase reservada o experimental (D/E).")
                
            num_subredes = int(self.txt_subredes.get().strip())
            num_hosts = int(self.txt_hosts.get().strip())
            self.num_hosts_pedidos = num_hosts
            
            if num_subredes <= 0 or num_hosts <= 0:
                raise ValueError("Los valores numéricos deben ser mayores a 0.")
                
            hosts_a_contar = num_hosts + 1 if INCLUIR_ROUTER else num_hosts
            bits_subred = bits_para_subredes(num_subredes)
            bits_host = bits_para_hosts(hosts_a_contar)
            bits_necesarios = bits_subred + bits_host
            
            clase_elegida = elegir_clase(clase_original, bits_necesarios)
            if not clase_elegida:
                raise ValueError(f"Requerimiento imposible: Se necesitan {bits_necesarios} bits en total. ¡Incluso la Clase A es pequeña!")
            
            prefijo_clase = CLASES[clase_elegida]["prefijo"]
            prefijo_final = 32 - bits_host
            
            if clase_elegida != clase_original:
                base_ip = CLASES[clase_elegida]["red_privada"]
                messagebox.showinfo("Cambio Automático de Clase", f"La clase {clase_original} original no cuenta con bits suficientes.\n\nEl sistema escaló automáticamente a Clase {clase_elegida} usando el segmento privado: {base_ip}/{prefijo_clase}")
            else:
                base_ip = str(ip_obj)
                
            red_base = ipaddress.IPv4Network(f"{base_ip}/{prefijo_clase}", strict=False)
            
            self.subredes_calculadas = []
            for idx, red in enumerate(red_base.subnets(new_prefix=prefijo_final), start=1):
                self.subredes_calculadas.append(red)
                
                router = red.network_address + 1
                p_host = red.network_address + 2 if INCLUIR_ROUTER else red.network_address + 1
                u_host = red.network_address + 1 + num_hosts if INCLUIR_ROUTER else red.network_address + num_hosts
                
                rango_txt = f"{p_host} - {u_host}"
                
                self.tabla.insert("", "end", values=(idx, str(red.network_address), str(red.netmask), str(red.broadcast_address), str(router), rango_txt))
                
                if idx == num_subredes:
                    break
                    
            self.btn_exportar.configure(state="normal")
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def exportar_excel(self):
        if not self.subredes_calculadas:
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivo CSV (Excel)", "*.csv")])
        if not filepath:
            return
            
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(["N°", "Direccion de Red", "Mascara de Subred", "Broadcast", "IP del Router (Gateway)", "Rango de Hosts Asignados"])
                
                for idx, red in enumerate(self.subredes_calculadas, start=1):
                    router = red.network_address + 1
                    p_host = red.network_address + 2
                    u_host = red.network_address + 1 + self.num_hosts_pedidos
                    writer.writerow([idx, str(red.network_address), str(red.netmask), str(red.broadcast_address), str(router), f"{p_host} - {u_host}"])
                    
            messagebox.showinfo("Éxito", "Tabla de subneteo exportada correctamente para abrir en Excel.")
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppSubnetting(root)
    root.mainloop()