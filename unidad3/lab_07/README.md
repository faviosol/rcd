# Sistema Avanzado de Subneteo IPv4 (VLSM) - Laboratorio 05

Este repositorio contiene el desarrollo de nuestro proyecto para el Laboratorio 05 del curso de Redes y Comunicación de Datos. Diseñamos y desarrollamos una aplicación interactiva en Python con Interfaz Gráfica de Usuario (GUI) mediante Tkinter que realiza cálculos avanzados de direccionamiento IPv4 utilizando la técnica **VLSM (Variable Length Subnet Mask)**.

## Integrantes
* Favio Andre Solórzano Vilca
* Marco Gabriel Macedo Torres

## ¿De qué trata nuestro proyecto?
A diferencia de las calculadoras tradicionales de máscara fija (FLSM) que desperdician direcciones IP asignando el mismo tamaño a todas las subredes, nuestra aplicación optimiza el espacio de red recibiendo como entrada **únicamente dos parámetros** (la IP Principal y una lista de requerimientos de hosts separados por comas) para autogestionar la topología:

* **Ordenamiento y Asignación Óptima (VLSM):** El algoritmo ordena automáticamente las solicitudes de mayor a menor cantidad de hosts y calcula el bloque exacto ($2^n - 2 \ge \text{hosts}$) para cada subred de manera contigua, evitando el solapamiento de direcciones y minimizando el desperdicio de IPs.
* **Escalabilidad Dinámica de Clases:** El sistema suma el espacio total requerido por todos los bloques. Si la demanda sobrepasa la capacidad de la red original (por ejemplo, saturar una red Clase C), escala automáticamente hacia los rangos privados estándar de Clase B (`172.16.0.0`) o Clase A (`10.0.0.0`) según sea necesario.
* **Mapeo de Interfaces de Red y Prefijos Variables:** Calcula de forma independiente el prefijo (`/25`, `/26`, `/30`, etc.), la máscara de subred, la dirección de broadcast y separa explícitamente la primera IP utilizable para el Router (Gateway) junto con el rango exacto de hosts asignados.
* **Persistencia de Datos (Exportación a Excel):** Integra un módulo nativo que compila toda la tabla de distribución VLSM (incluyendo los hosts solicitados y el prefijo de cada bloque) y la exporta con un solo clic a un archivo `.csv` listo para abrirse en Microsoft Excel.

## ¿Cómo ejecutar nuestro programa?

### Requisitos
Solo se requiere tener instalado **Python 3**. El sistema es completamente portable y óptimo para defensas en vivo en laboratorios académicos, ya que no depende de librerías externas; utiliza exclusivamente los módulos nativos `ipaddress`, `tkinter` y `csv`.

### Pasos para ejecutar:
1. Descargar o clonar este repositorio en tu equipo.
2. Abrir una terminal, consola de comandos (CMD) o PowerShell en la carpeta raíz del proyecto.
3. Ejecutar el script principal:

```bash
python Calculadora_VLSM.py
```

### Ejemplo de uso rápido:
* **IP Principal:** `192.168.1.0`
* **Hosts por Subred:** `100, 50, 25, 10, 2`
* El programa ordenará automáticamente los requerimientos y generará las 5 subredes con sus máscaras variables (`/25`, `/26`, `/27`, `/28` y `/30`) listas para visualizar o exportar.
