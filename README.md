# Sistema de Subneteo IPv4 Adaptativo - Laboratorio 05

Este repositorio contiene el desarrollo de nuestro proyecto para el Laboratorio 05 del curso de Redes y Comunicación de Datos. Diseñamos y desarrollamos una aplicación elástica e interactiva en Python que opera de forma híbrida: mediante una Interfaz Gráfica de Usuario (GUI) con Tkinter en entornos locales o de manera automática por Consola Interactiva en servidores de desarrollo o entornos en la nube sin soporte de display gráfico (como GDB Online). El sistema realiza cálculos avanzados de subneteo IPv4 mediante la técnica FLSM (Fixed Length Subnet Mask).

## Integrantes
* Favio Andre Solórzano Vilca
* Marco Gabriel Macedo Torres

## ¿De qué trata nuestro proyecto?
A diferencia de los calculadores tradicionales de lógica restrictiva que fallan al quedarse sin bits, nuestra aplicación recibe como entrada **únicamente tres datos base** (IP Principal, Cantidad de Subredes y Hosts por Subred) y autogestiona la arquitectura de la red:

* **Escalabilidad Dinámica de Clases:** Si los requerimientos del usuario sobrepasan la capacidad física de la IP original (por ejemplo, solicitar miles de hosts en una dirección Clase C), el algoritmo rompe esa dimensión y escala automáticamente el segmento hacia los rangos privados estándar de Clase B (`172.16.0.0`) o Clase A (`10.0.0.0`) según sea necesario.
* **Cálculo de Bits Autónomo:** Aplica rigurosamente las ecuaciones $2^n - 2 \ge \text{hosts}$ y $2^s \ge \text{subredes}$ para determinar el "robo" exacto de bits e implementar la máscara óptima.
* **Mapeo de Interfaces de Red:** Identifica y separa explícitamente la dirección IP asignada para el Router (Gateway) tomando la primera IP utilizable de cada segmento, definiendo de forma independiente el rango consecutivo de hosts.
* **Persistencia de Datos (Exportación a Excel):** Integra un módulo nativo que compila toda la topología de la tabla de subneteo y la exporta con un solo clic a un archivo con formato `.csv` perfectamente estructurado para su análisis inmediato en Microsoft Excel.

## ¿Cómo ejecutar nuestro programa?

### Requisitos
Solo se requiere tener instalado **Python 3**. El sistema es completamente portable y óptimo para defensas en vivo en laboratorios académicos, ya que no depende de la instalación de librerías externas mediante `pip`; utiliza exclusivamente los módulos nativos `ipaddress`, `tkinter` y `csv`.

### Pasos para ejecutar:
1. Descargar o clonar este repositorio en tu equipo.
2. Abrir una terminal, consola de comandos (CMD) o PowerShell en la carpeta raíz del proyecto.
3. Ejecutar el script principal utilizando el nuevo nombre preciso del archivo:

```bash
python calculador_subneteo_dinamico.py
```

*Nota: El script detectará tu entorno. Si lo ejecutas localmente abrirá la interfaz visual de escritorio; si lo corres en un compilador web tipo GDB, se desplegará instantáneamente el menú interactivo por texto.*
