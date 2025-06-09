# Simulador de Sistema de Atención al Público

Este repositorio contiene el código y los resultados de un **Simulador de Sistema de Atención al Público**. El objetivo del proyecto es simular diferentes configuraciones de boxes de atención para optimizar la eficiencia del servicio al cliente y minimizar los costos operativos, principalmente por la pérdida de clientes debido a demoras.

---

## 📊 Resultados de la Simulación

Se realizó una serie de simulaciones para evaluar el impacto de la cantidad de boxes de atención en métricas clave del servicio. Los resultados se resumen a continuación:

### Métricas Clave Evaluadas:

* **Clientes que ingresaron al local:** Cantidad total de clientes que intentaron acceder al servicio.
* **Clientes atendidos:** Cantidad de clientes que completaron exitosamente su atención.
* **Clientes no atendidos (abandonaron):** Clientes que se retiraron del local debido a demoras excesivas.
* **Tiempo mínimo de atención en box:** El tiempo más corto que un cliente pasó siendo atendido.
* **Tiempo máximo de atención en box:** El tiempo más largo que un cliente pasó siendo atendido.
* **Tiempo mínimo de espera en salón:** El tiempo más corto que un cliente esperó para ser atendido.
* **Tiempo máximo de espera en salón:** El tiempo más largo que un cliente esperó para ser atendido.
* **Costo de la operación:** Suma del costo de los boxes de atención y el costo estimado por la pérdida de clientes no atendidos.

---

### Resumen Comparativo de Configuraciones:

La siguiente tabla resume los resultados obtenidos al simular con diferentes números de boxes:

| Boxes | Clientes Atendidos | Clientes que Abandonaron | Tasa de Atención (%) | Costo Total |
| :---- | :----------------- | :----------------------- | :------------------- | :---------- |
| 1     | 28                 | 88                       | 24.1                 | $881,000    |
| 2     | 49                 | 41                       | 54.4                 | $412,000    |
| 3     | 69                 | 21                       | 76.7                 | $213,000    |
| 4     | 94                 | 2                        | 97.9                 | $24,000     |
| **5** | **108** | **0** | **100.0** | **$5,000** |
| 6     | 111                | 0                        | 100.0                | $6,000      |
| 7     | 112                | 0                        | 100.0                | $7,000      |
| 8     | 100                | 1                        | 99.0                 | $18,000     |
| 9     | 94                 | 0                        | 100.0                | $9,000      |
| 10    | 98                 | 0                        | 100.0                | $10,000     |

---

## ✅ Conclusión: Cantidad Óptima de Boxes

Los resultados de la simulación indican claramente que la **cantidad óptima de boxes a mantener abiertos es de 5**.

Esta configuración logra la **tasa de atención más alta (100%)**, asegurando que **ningún cliente abandona el local por demoras**. Además, presenta el **costo total de operación más bajo ($5,000.00)**, ya que elimina por completo el costo asociado a la pérdida de clientes.

Aunque otras configuraciones con más boxes (6, 7, 9 y 10) también alcanzan el 100% de atención, sus costos operativos son mayores sin ofrecer beneficios adicionales en el servicio. Esto convierte a la configuración de 5 boxes en la solución más eficiente y rentable.

---

## 🎬 Videos de Simulación

Para una comprensión más profunda del flujo de clientes y el comportamiento del sistema bajo diferentes cargas, se pueden generar videos animados en formato AVI para cada simulación. Estos videos permiten visualizar dinámicamente los procesos de atención y espera. (Se recomienda incluir una sección con los videos si están disponibles, o una nota sobre cómo generarlos).