# Parte I y II — Inventario, Auditoría y Tabla de Riesgos

## Tabla de Riesgos
| Riesgo | Probabilidad | Impacto | Nivel | Recomendación |
| :--- | :---: | :---: | :---: | :--- |
| Tráfico HTTP sin cifrar (Puerto 80) | Alta | Alto | Crítico | Habilitar HTTPS (443) con certificado SSL |
| Exposición de versión de Apache y SO | Media | Medio | Medio | Configurar `ServerTokens Prod` y `ServerSignature Off` |
| Listado de directorios habilitado | Media | Alto | Alto | Desactivar `Indexes` en configuración de Apache |

## Evidencias Técnicas
### Evidencia 1: [Título]
* **¿Qué se está demostrando?:** 
* **¿Qué comando se utilizó?:**
  ```bash
  # comando aquí
  ```
* **¿Qué resultado se obtuvo?:**
  ```text
  # salida aquí
  ```
* **¿Qué significa el resultado?:** 
