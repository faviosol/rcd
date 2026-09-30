# Laboratorio 04 – Comunicación simplex, dúplex y orientada a conexión

## Integrantes

| Alumno | Tarea realizada | Porcentaje |
|---|---|---|
| Ampuero Gonzales, Luis Fernando | Configuración de Docker y contenedores | 100% |
| Chipana Benavente, Brayan Gabriel | Captura y análisis simplex y dúplex | 100% |
| Macedo Torres, Marco Gabriel | Captura y análisis TCP en Wireshark | 100% |
| Solórzano Vilca, Favio Andre | Redacción y estructuración del informe | 100% |

---

## 1. Objetivo

Comprobar en la práctica tres tipos de comunicación entre procesos que corren en contenedores distintos, y observar en Wireshark cómo se ve cada una en la red:

- **Simplex:** los datos viajan en un solo sentido.
- **Dúplex:** los datos viajan en ambos sentidos.
- **Orientada a conexión:** se establece una conexión antes de enviar los datos (TCP).

---

## 2. Entorno utilizado

Se trabajó en Windows con **Docker Desktop (opción C de la guía)**. Se levantaron tres contenedores basados en `eclipse-temurin:17-jdk` conectados a la red `rcd_lab04_network_escobedo`. Las pruebas se hicieron entre `container1` y `container2`. El `container3` quedó levantado pero no se usó.

Como Wireshark de Windows no ve la red interna de Docker, la captura de paquetes se hizo con `tcpdump` dentro de `container2`. Cada captura se guardó en un archivo `.pcap` y luego se abrió en Wireshark para analizarla.

### 2.1 Clonación del repositorio

Se clonó el repositorio con `git clone https://github.com/rescobedoulasalle/rcd.git`. La salida confirma la descarga completa de los objetos y la verificación del directorio de trabajo mediante `dir`:

![Paso 1](images/1.png)

A continuación, se navegó a la carpeta de trabajo `unidad2\lab04`, comprobando la existencia de los archivos base del laboratorio (`docker-compose.yml`, `Dockerfile`, `Ejemplo1Emisor.java`, `Ejemplo1Receptor.java`, entre otros):

![Paso 2](images/2.png)

### 2.2 Levantar los contenedores

Se ejecutó `docker compose up -d --build`. Docker descargó la imagen base de Java 17 (`eclipse-temurin:17-jdk`) y construyó la imagen personalizada en aproximadamente 36 segundos:

![Paso 3](images/3.png)

Al finalizar la construcción, el entorno creó la red `rcd_lab04_network_escobedo` e inició los tres contenedores (`container1`, `container2` y `container3`) reportando el estado *Started*:

![Paso 4](images/4.png)

Mediante el comando `docker ps` se verificó la ejecución activa de los tres contenedores en estado *Up*:

![Paso 5](images/5.png)

### 2.3 Copiar y compilar el código

Se creó la carpeta `/root/lab` dentro de `container1` y `container2` para copiar los archivos con `docker cp`. Se incluyeron los programas base y los cuatro desarrollados para este laboratorio:

- `Ejemplo2DuplexServidor.java` y `Ejemplo2DuplexCliente.java` (UDP bidireccional).
- `Ejemplo3TCPServidor.java` y `Ejemplo3TCPCliente.java` (TCP con conexión).

Posteriormente, se ejecutó `javac *.java` dentro de los contenedores y se corroboró la creación de los seis archivos `.class`:

![Paso 6](images/6.png)

### 2.4 Direcciones IP

Con el comando `hostname -i` ejecutado en cada contenedor se obtuvieron las direcciones IP asignadas dinámicamente por la red de Docker:

| Contenedor | Rol | Dirección IP |
|---|---|---|
| `container1` | Emisor / Cliente | `172.18.0.4` |
| `container2` | Receptor / Servidor | `172.18.0.2` |

![Paso 7](images/7.png)
---

## 3. Comunicación simplex (UDP)

En la comunicación simplex la transmisión de datos ocurre en un único sentido. Se utilizaron los programas `Ejemplo1Receptor` en `container2` (puerto `5000`) y `Ejemplo1Emisor` en `container1`.

**Pasos realizados**

1. Se inició la captura en segundo plano guardando el tráfico en `/root/lab/simplex.pcap`.
2. Se ejecutó el receptor a la escucha en el puerto `5000`.
3. Desde `container1` se envió el mensaje `Hola simplex` hacia la IP `172.18.0.2`.

En la terminal dividida se observa la ejecución simultánea de los comandos en ambos contenedores:

![Paso 8](images/8.png)
Una vez finalizado el envío del mensaje, se detuvo el proceso de `tcpdump` con `pkill` y se extrajo el archivo `simplex.pcap` hacia la máquina física en Windows para su revisión:

![Paso 9](images/9.png)
**Análisis en Wireshark**

Al abrir `simplex.pcap` sin filtros se visualizan tres paquetes en total:

1. **ARP (request):** `container1` consulta por broadcast quién posee la IP `172.18.0.2`.
2. **ARP (reply):** `container2` responde indicando su dirección MAC física.
3. **UDP:** Datagrama desde `172.18.0.4` (puerto `38298`) hacia `172.18.0.2` (puerto `5000`), con una carga útil de `Len=12` (correspondiente a los 12 caracteres del texto `Hola simplex`).

![Paso 1](images/10.png)
Aplicando el filtro `udp.port == 5000` se aísla de manera limpia la transmisión del protocolo de transporte:

![Paso 1](images/11.png)
**Conclusión:** Se verifica la presencia de un único datagrama de datos del emisor al receptor sin acuse de recibo ni paquete de respuesta, confirmando la naturaleza **simplex** del esquema.

---

## 4. Comunicación dúplex (UDP)

En la comunicación dúplex ambos extremos intercambian mensajes. El servidor `Ejemplo2DuplexServidor` (puerto `5001`) procesa la solicitud entrante y responde de manera automática al origen. El cliente `Ejemplo2DuplexCliente` envía el mensaje y se queda esperando el retorno.

Antes de la transmisión, se inició la captura en `duplex.pcap` y se dejaron preparados los procesos en ambas terminales:

![Paso 1](images/12.png)
**Resultado en las terminales**

Tras la ejecución del cliente, ambas consolas despliegan la recepción de sus respectivos mensajes:

- **Servidor (`container2`):** `Servidor recibio: Hola duplex`
- **Cliente (`container1`):** `Cliente recibio: Respuesta a: Hola duplex`

![Paso 1](images/13.png)
**Análisis en Wireshark** (filtro `udp.port == 5001`)

La captura confirma la secuencia bidireccional mediante dos paquetes independientes:

| Paquete | Origen → Destino | Puertos | Carga útil (Payload) |
|---|---|---|---|
| 1 | `172.18.0.4` → `172.18.0.2` | `38380` → `5001` | 11 bytes (`Hola duplex`) |
| 2 | `172.18.0.2` → `172.18.0.4` | `5001` → `38380` | 24 bytes (`Respuesta a: Hola duplex`) |

![Paso 1](images/14.png)
**Conclusión:** Existen dos paquetes (ida y vuelta). A pesar de viajar en ambos sentidos (dúplex), al emplear UDP no existe un protocolo de enlace previo ni señalizaciones de control.

---

## 5. Comunicación orientada a conexión (TCP)

Para el esquema orientado a conexión se utilizaron `Ejemplo3TCPServidor` (puerto `5002`) y `Ejemplo3TCPCliente`. A diferencia de UDP, TCP exige establecer una sesión válida antes de transferir datos de aplicación.

En la primera fase, el servidor pasa a estado de escucha mostrando el mensaje `Esperando conexion...` mientras la captura `tcp.pcap` permanece activa:

![Paso 1](images/15.png)
**Resultado en las terminales**

Una vez efectuada la conexión y el intercambio, los registros confirman la entrega garantizada:

- **Servidor (`container2`):** `Servidor recibio: Hola TCP`
- **Cliente (`container1`):** `Cliente recibio: Respuesta TCP a: Hola TCP`

![Paso 1](images/16.png)
**Análisis en Wireshark** (filtro `tcp.port == 5002`)

La captura expone un total de 10 paquetes que detallan el ciclo de vida completo del socket TCP:

| Fase del Protocolo | Paquetes | Descripción Técnica |
|---|---|---|
| **Establecimiento (Saludo de tres vías / Handshake)** | 1 `[SYN]`, 2 `[SYN, ACK]`, 3 `[ACK]` | Petición de conexión del cliente, respuesta con aceptación del servidor y confirmación final. |
| **Transmisión de Datos** | 4 `[PSH, ACK]` (Len=9), 5 `[ACK]` | Envío de `Hola TCP` (8 caracteres + `\n`) con empuje inmediato (`PSH`) y confirmación (`ACK`). |
| **Respuesta del Servidor** | 6 `[PSH, ACK]` (Len=26), 7 `[ACK]` | Retorno de `Respuesta TCP a: Hola TCP` y su respectivo `ACK` de recepción por el cliente. |
| **Cierre de Conexión (Desconexión de cuatro vías)** | 8 `[FIN, ACK]`, 9 `[FIN, ACK]`, 10 `[ACK]` | Cierre ordenado de los sockets en ambos sentidos finalizando la sesión. |

![Paso 1](images/17.png)
**Conclusión:** TCP garantiza la confiabilidad en la entrega mediante el saludo de tres vías, el control de flujo y el cierre formal. Esto incrementa la sobrecarga en la red (10 paquetes TCP frente a los 2 de UDP dúplex).

---

## 6. Comparación de esquemas

| Criterio | Simplex (UDP) | Dúplex (UDP) | Orientada a Conexión (TCP) |
|---|---|---|---|
| **Total paquetes (sin ARP)** | 1 | 2 | 10 |
| **Flujo de datos** | Unidireccional | Bidireccional | Bidireccional |
| **Fase de negociación** | No requiere | No requiere | Sí (`SYN` → `SYN-ACK` → `ACK`) |
| **Confirmación de entrega** | No (`Best-effort`) | No (`Best-effort`) | Sí (`ACK` por segmento) |
| **Finalización de sesión** | N/A | N/A | Sí (`FIN` / `ACK`) |

---

## 7. Conclusiones

- **Diferencia de sobrecarga (Overhead):** UDP no requiere negociación previa ni manejo de estado. En simplex requiere solo 1 datagrama y en dúplex 2 datagramas independientes. TCP requiere 10 paquetes para realizar exactamente el mismo intercambio útil de datos debido a la gestión de la sesión.
- **Fiabilidad vs. Rendimiento:** TCP compensa su sobrecarga asegurando la llegada, el orden y la integridad de los mensajes. UDP prioriza la velocidad y la simplicidad a costa de no garantizar la entrega.
- **Captura interna en entornos virtualizados:** Dado que las redes virtuales puente (`bridge`) de Docker Desktop en Windows no son expuestas directamente a la interfaz física del sistema anfitrión, la técnica de capturar internamente con `tcpdump` y exportar archivos `.pcap` es una solución efectiva para el análisis de tráfico con Wireshark.