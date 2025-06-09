import random
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usar backend sin interfaz gráfica
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime, timedelta
from collections import deque
import time
import os

class Cliente:
    """Clase que representa un cliente en el sistema"""
    def __init__(self, id_cliente, tiempo_llegada):
        self.id = id_cliente
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_inicio_atencion = None
        self.tiempo_fin_atencion = None
        self.tiempo_espera = 0
        self.atendido = False
        self.abandono = False
        self.box_asignado = None

class Box:
    """Clase que representa un box de atención"""
    def __init__(self, id_box):
        self.id = id_box
        self.ocupado = False
        self.cliente_actual = None
        self.tiempo_fin_atencion = None
        self.tiempo_total_atencion = 0
        self.clientes_atendidos = 0

class SimuladorAtencionPublico:
    """Simulador principal del sistema de atención al público"""
    
    def __init__(self, num_boxes=1):
        # Parámetros del sistema
        self.num_boxes = num_boxes
        self.hora_apertura = 8 * 3600  # 8:00 AM en segundos
        self.hora_cierre = 12 * 3600   # 12:00 PM en segundos
        self.duracion_simulacion = self.hora_cierre - self.hora_apertura  # 4 horas
        self.prob_ingreso = 1/144  # Probabilidad por segundo
        self.tiempo_max_espera = 30 * 60  # 30 minutos en segundos
        self.media_atencion = 10 * 60  # 10 minutos en segundos
        self.desvio_atencion = 5 * 60   # 5 minutos en segundos
        self.costo_box = 1000
        self.perdida_cliente = 10000
        
        # Estado del sistema
        self.tiempo_actual = 0
        self.boxes = [Box(i) for i in range(num_boxes)]
        self.cola = deque()
        self.clientes = []
        self.id_cliente_contador = 0
        
        # Estadísticas
        self.clientes_ingresados = 0
        self.clientes_atendidos = 0
        self.clientes_abandonaron = 0
        self.tiempos_atencion = []
        self.tiempos_espera = []
        
        # Para animación
        self.historial_animacion = []
    
    def generar_tiempo_atencion(self):
        """Genera tiempo de atención según distribución normal"""
        tiempo = np.random.normal(self.media_atencion, self.desvio_atencion)
        return max(60, tiempo)  # Mínimo 1 minuto
    
    def llegada_cliente(self):
        """Verifica si llega un nuevo cliente"""
        return random.random() < self.prob_ingreso
    
    def asignar_cliente_a_box(self):
        """Asigna cliente de la cola a un box disponible"""
        if self.cola:
            for box in self.boxes:
                if not box.ocupado:
                    cliente = self.cola.popleft()
                    cliente.tiempo_inicio_atencion = self.tiempo_actual
                    cliente.tiempo_espera = self.tiempo_actual - cliente.tiempo_llegada
                    cliente.box_asignado = box.id
                    
                    tiempo_atencion = self.generar_tiempo_atencion()
                    box.ocupado = True
                    box.cliente_actual = cliente
                    box.tiempo_fin_atencion = self.tiempo_actual + tiempo_atencion
                    
                    self.tiempos_espera.append(cliente.tiempo_espera)
                    break
    
    def procesar_boxes(self):
        """Procesa la atención en cada box"""
        for box in self.boxes:
            if box.ocupado and self.tiempo_actual >= box.tiempo_fin_atencion:
                # Cliente termina atención
                cliente = box.cliente_actual
                cliente.tiempo_fin_atencion = self.tiempo_actual
                cliente.atendido = True
                
                tiempo_atencion = cliente.tiempo_fin_atencion - cliente.tiempo_inicio_atencion
                self.tiempos_atencion.append(tiempo_atencion)
                
                box.ocupado = False
                box.cliente_actual = None
                box.tiempo_fin_atencion = None
                box.clientes_atendidos += 1
                box.tiempo_total_atencion += tiempo_atencion
                
                self.clientes_atendidos += 1
    
    def verificar_abandonos(self):
        """Verifica si algún cliente abandona por tiempo de espera"""
        clientes_a_remover = []
        for i, cliente in enumerate(self.cola):
            tiempo_espera = self.tiempo_actual - cliente.tiempo_llegada
            if tiempo_espera >= self.tiempo_max_espera:
                cliente.abandono = True
                clientes_a_remover.append(i)
                self.clientes_abandonaron += 1
        
        # Remover clientes que abandonan (de atrás hacia adelante)
        for i in reversed(clientes_a_remover):
            del list(self.cola)[i]
        
        # Reconstruir cola sin los clientes que abandonaron
        nueva_cola = deque([cliente for cliente in self.cola if not cliente.abandono])
        self.cola = nueva_cola
    
    def guardar_estado_animacion(self):
        """Guarda el estado actual para la animación"""
        estado = {
            'tiempo': self.tiempo_actual,
            'cola_size': len(self.cola),
            'boxes_ocupados': sum(1 for box in self.boxes if box.ocupado),
            'clientes_atendidos': self.clientes_atendidos,
            'clientes_abandonaron': self.clientes_abandonaron
        }
        self.historial_animacion.append(estado)
    
    def simular(self, mostrar_progreso=True):
        """Ejecuta la simulación completa"""
        print(f"Iniciando simulación con {self.num_boxes} boxes...")
        print("=" * 50)
        
        for segundo in range(self.duracion_simulacion):
            self.tiempo_actual = segundo
            
            # Solo aceptar nuevos clientes durante horario de atención
            if segundo < self.duracion_simulacion:
                if self.llegada_cliente():
                    nuevo_cliente = Cliente(self.id_cliente_contador, segundo)
                    self.clientes.append(nuevo_cliente)
                    self.cola.append(nuevo_cliente)
                    self.id_cliente_contador += 1
                    self.clientes_ingresados += 1
            
            # Procesar atención en boxes
            self.procesar_boxes()
            
            # Asignar clientes a boxes disponibles
            self.asignar_cliente_a_box()
            
            # Verificar abandonos
            self.verificar_abandonos()
            
            # Guardar estado para animación (cada 60 segundos)
            if segundo % 60 == 0:
                self.guardar_estado_animacion()
            
            # Mostrar progreso cada 30 minutos simulados
            if mostrar_progreso and segundo % 1800 == 0:
                hora = 8 + segundo // 3600
                minuto = (segundo % 3600) // 60
                print(f"Tiempo: {hora:02d}:{minuto:02d} | "
                      f"Cola: {len(self.cola)} | "
                      f"Atendidos: {self.clientes_atendidos} | "
                      f"Abandonos: {self.clientes_abandonaron}")
        
        # Continuar atendiendo clientes después del cierre (solo los que ya están)
        tiempo_extra = 0
        while any(box.ocupado for box in self.boxes) and tiempo_extra < 3600:  # Máximo 1 hora extra
            self.tiempo_actual = self.duracion_simulacion + tiempo_extra
            self.procesar_boxes()
            tiempo_extra += 1
        
        # Marcar clientes restantes en cola como no atendidos
        for cliente in self.cola:
            cliente.abandono = True
            self.clientes_abandonaron += 1
        
        print("\nSimulación completada!")
    
    def generar_reporte(self):
        """Genera el reporte final de la simulación"""
        costo_total = (self.num_boxes * self.costo_box) + (self.clientes_abandonaron * self.perdida_cliente)
        
        print("\n" + "=" * 60)
        print("REPORTE FINAL DE SIMULACIÓN")
        print("=" * 60)
        
        print(f"1) Clientes que ingresaron al local: {self.clientes_ingresados}")
        print(f"2) Clientes atendidos: {self.clientes_atendidos}")
        print(f"3) Clientes no atendidos (abandonaron): {self.clientes_abandonaron}")
        
        if self.tiempos_atencion:
            print(f"4) Tiempo mínimo de atención: {min(self.tiempos_atencion)/60:.2f} minutos")
            print(f"5) Tiempo máximo de atención: {max(self.tiempos_atencion)/60:.2f} minutos")
        else:
            print("4) Tiempo mínimo de atención: N/A")
            print("5) Tiempo máximo de atención: N/A")
        
        if self.tiempos_espera:
            print(f"6) Tiempo mínimo de espera: {min(self.tiempos_espera)/60:.2f} minutos")
            print(f"7) Tiempo máximo de espera: {max(self.tiempos_espera)/60:.2f} minutos")
        else:
            print("6) Tiempo mínimo de espera: 0.00 minutos")
            print("7) Tiempo máximo de espera: N/A")
        
        print(f"8) Costo total de operación: ${costo_total:,.2f}")
        print(f"   - Costo de boxes ({self.num_boxes} boxes): ${self.num_boxes * self.costo_box:,.2f}")
        print(f"   - Pérdida por clientes no atendidos: ${self.clientes_abandonaron * self.perdida_cliente:,.2f}")
        
        # Estadísticas adicionales
        if self.clientes_ingresados > 0:
            tasa_atencion = (self.clientes_atendidos / self.clientes_ingresados) * 100
            print(f"\nTasa de atención: {tasa_atencion:.2f}%")
        
        if self.tiempos_espera:
            tiempo_promedio_espera = np.mean(self.tiempos_espera) / 60
            print(f"Tiempo promedio de espera: {tiempo_promedio_espera:.2f} minutos")
        
        if self.tiempos_atencion:
            tiempo_promedio_atencion = np.mean(self.tiempos_atencion) / 60
            print(f"Tiempo promedio de atención: {tiempo_promedio_atencion:.2f} minutos")
        
        print("=" * 60)
        
        return {
            'clientes_ingresados': self.clientes_ingresados,
            'clientes_atendidos': self.clientes_atendidos,
            'clientes_abandonaron': self.clientes_abandonaron,
            'costo_total': costo_total,
            'tasa_atencion': (self.clientes_atendidos / self.clientes_ingresados) * 100 if self.clientes_ingresados > 0 else 0
        }
    
    def crear_animacion(self, velocidad=1, guardar_archivo=False):
        """Crea una animación del proceso simulado"""
        if not self.historial_animacion:
            print("No hay datos de animación disponibles.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'Simulación Sistema de Atención - {self.num_boxes} Boxes', fontsize=14)
        
        # Preparar datos para gráficos
        tiempos = [estado['tiempo']/3600 + 8 for estado in self.historial_animacion]  # Convertir a horas
        cola_sizes = [estado['cola_size'] for estado in self.historial_animacion]
        boxes_ocupados = [estado['boxes_ocupados'] for estado in self.historial_animacion]
        atendidos = [estado['clientes_atendidos'] for estado in self.historial_animacion]
        abandonos = [estado['clientes_abandonaron'] for estado in self.historial_animacion]
        
        def animate(frame):
            # Limpiar axes
            ax1.clear()
            ax2.clear()
            ax3.clear()
            ax4.clear()
            
            # Gráfico 1: Tamaño de cola en tiempo real
            ax1.plot(tiempos[:frame+1], cola_sizes[:frame+1], 'b-', linewidth=2)
            ax1.set_title('Tamaño de Cola')
            ax1.set_xlabel('Hora del día')
            ax1.set_ylabel('Clientes en cola')
            ax1.grid(True)
            ax1.set_xlim(8, 12)
            if cola_sizes:
                ax1.set_ylim(0, max(cola_sizes) + 2)
            
            # Gráfico 2: Boxes ocupados
            ax2.plot(tiempos[:frame+1], boxes_ocupados[:frame+1], 'g-', linewidth=2)
            ax2.set_title('Boxes Ocupados')
            ax2.set_xlabel('Hora del día')
            ax2.set_ylabel('Boxes en uso')
            ax2.grid(True)
            ax2.set_xlim(8, 12)
            ax2.set_ylim(0, self.num_boxes + 1)
            
            # Gráfico 3: Clientes atendidos acumulado
            ax3.plot(tiempos[:frame+1], atendidos[:frame+1], 'orange', linewidth=2)
            ax3.set_title('Clientes Atendidos (Acumulado)')
            ax3.set_xlabel('Hora del día')
            ax3.set_ylabel('Total atendidos')
            ax3.grid(True)
            ax3.set_xlim(8, 12)
            if atendidos:
                ax3.set_ylim(0, max(atendidos) + 5)
            
            # Gráfico 4: Comparación atendidos vs abandonos
            ax4.plot(tiempos[:frame+1], atendidos[:frame+1], 'g-', label='Atendidos', linewidth=2)
            ax4.plot(tiempos[:frame+1], abandonos[:frame+1], 'r-', label='Abandonos', linewidth=2)
            ax4.set_title('Atendidos vs Abandonos')
            ax4.set_xlabel('Hora del día')
            ax4.set_ylabel('Cantidad')
            ax4.legend()
            ax4.grid(True)
            ax4.set_xlim(8, 12)
            if atendidos or abandonos:
                ax4.set_ylim(0, max(max(atendidos) if atendidos else 0, max(abandonos) if abandonos else 0) + 5)
            
            plt.tight_layout()
        
        # Crear animación
        frames = len(self.historial_animacion)
        interval = max(50, 500 // velocidad)  # Ajustar velocidad
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=interval, repeat=True)
        
        if guardar_archivo:
            # Intentar guardar como AVI primero
            try:
                print("Guardando animación como 'simulacion_atencion.avi'...")
                anim.save('simulacion_atencion.avi', writer='ffmpeg', fps=10, 
                         extra_args=['-vcodec', 'libx264'])
                print("Animación AVI guardada exitosamente!")
            except Exception as e:
                print(f"No se pudo guardar como AVI (requiere ffmpeg): {e}")
                print("Guardando como GIF alternativo...")
                anim.save('simulacion_atencion.gif', writer='pillow', fps=10)
                print("Animación GIF guardada exitosamente!")
        
        plt.show()
        return anim
    
    def crear_video_avi(self, velocidades=[1, 2, 5], mostrar_menu=True):
        """Crea videos AVI con diferentes velocidades"""
        if not self.historial_animacion:
            print("No hay datos de animación disponibles.")
            return
        
        # Mostrar datos de la simulación antes de generar videos
        print("\n" + "=" * 60)
        print("DATOS DE LA SIMULACIÓN PARA GENERACIÓN DE VIDEO")
        print("=" * 60)
        self.generar_reporte()
        
        if mostrar_menu:
            print("\n¿Qué velocidades de video deseas generar?")
            print("1. Velocidad normal (1x)")
            print("2. Velocidad rápida (2x)")
            print("3. Velocidad muy rápida (5x)")
            print("4. Todas las velocidades")
            print("5. Velocidades personalizadas")
            
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                velocidades = [1]
            elif opcion == '2':
                velocidades = [2]
            elif opcion == '3':
                velocidades = [5]
            elif opcion == '4':
                velocidades = [1, 2, 5]
            elif opcion == '5':
                vel_input = input("Ingresa velocidades separadas por comas (ej: 1,3,10): ")
                try:
                    velocidades = [int(v.strip()) for v in vel_input.split(',')]
                except:
                    print("Error en formato, usando velocidades por defecto.")
                    velocidades = [1, 2, 5]
        
        for velocidad in velocidades:
            print(f"\nGenerando video a velocidad {velocidad}x...")
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Simulación Sistema de Atención - {self.num_boxes} Boxes (Velocidad {velocidad}x)', fontsize=14)
            
            # Preparar datos para gráficos
            tiempos = [estado['tiempo']/3600 + 8 for estado in self.historial_animacion]
            cola_sizes = [estado['cola_size'] for estado in self.historial_animacion]
            boxes_ocupados = [estado['boxes_ocupados'] for estado in self.historial_animacion]
            atendidos = [estado['clientes_atendidos'] for estado in self.historial_animacion]
            abandonos = [estado['clientes_abandonaron'] for estado in self.historial_animacion]
            
            def animate(frame):
                ax1.clear()
                ax2.clear()
                ax3.clear()
                ax4.clear()
                
                # Gráfico 1: Tamaño de cola
                ax1.plot(tiempos[:frame+1], cola_sizes[:frame+1], 'b-', linewidth=2)
                ax1.set_title('Tamaño de Cola')
                ax1.set_xlabel('Hora del día')
                ax1.set_ylabel('Clientes en cola')
                ax1.grid(True)
                ax1.set_xlim(8, 12)
                if cola_sizes:
                    ax1.set_ylim(0, max(cola_sizes) + 2)
                
                # Gráfico 2: Boxes ocupados
                ax2.plot(tiempos[:frame+1], boxes_ocupados[:frame+1], 'g-', linewidth=2)
                ax2.set_title('Boxes Ocupados')
                ax2.set_xlabel('Hora del día')
                ax2.set_ylabel('Boxes en uso')
                ax2.grid(True)
                ax2.set_xlim(8, 12)
                ax2.set_ylim(0, self.num_boxes + 1)
                
                # Gráfico 3: Clientes atendidos
                ax3.plot(tiempos[:frame+1], atendidos[:frame+1], 'orange', linewidth=2)
                ax3.set_title('Clientes Atendidos (Acumulado)')
                ax3.set_xlabel('Hora del día')
                ax3.set_ylabel('Total atendidos')
                ax3.grid(True)
                ax3.set_xlim(8, 12)
                if atendidos:
                    ax3.set_ylim(0, max(atendidos) + 5)
                
                # Gráfico 4: Atendidos vs abandonos
                ax4.plot(tiempos[:frame+1], atendidos[:frame+1], 'g-', label='Atendidos', linewidth=2)
                ax4.plot(tiempos[:frame+1], abandonos[:frame+1], 'r-', label='Abandonos', linewidth=2)
                ax4.set_title('Atendidos vs Abandonos')
                ax4.set_xlabel('Hora del día')
                ax4.set_ylabel('Cantidad')
                ax4.legend()
                ax4.grid(True)
                ax4.set_xlim(8, 12)
                if atendidos or abandonos:
                    ax4.set_ylim(0, max(max(atendidos) if atendidos else 0, max(abandonos) if abandonos else 0) + 5)
                
                # Agregar indicador de tiempo actual
                tiempo_actual = tiempos[frame] if frame < len(tiempos) else tiempos[-1]
                fig.suptitle(f'Simulación Sistema de Atención - {self.num_boxes} Boxes (Velocidad {velocidad}x) - Hora: {tiempo_actual:.2f}', fontsize=14)
                
                plt.tight_layout()
            
            frames = len(self.historial_animacion)
            interval = max(20, 200 // velocidad)  # Ajustar intervalo según velocidad
            fps = min(30, 10 * velocidad)  # FPS más alto para velocidades rápidas
            
            anim = animation.FuncAnimation(fig, animate, frames=frames, interval=interval, repeat=False)
            
            # Guardar video AVI
            archivo_avi = f'simulacion_atencion_velocidad_{velocidad}x.avi'
            try:
                anim.save(archivo_avi, writer='ffmpeg', fps=fps, 
                         extra_args=['-vcodec', 'libx264', '-preset', 'medium'])
                print(f"✓ Video guardado: {archivo_avi}")
            except Exception as e:
                print(f"✗ Error guardando {archivo_avi}: {e}")
                # Fallback a GIF
                archivo_gif = f'simulacion_atencion_velocidad_{velocidad}x.gif'
                try:
                    anim.save(archivo_gif, writer='pillow', fps=min(10, fps))
                    print(f"✓ GIF alternativo guardado: {archivo_gif}")
                except Exception as e2:
                    print(f"✗ Error guardando GIF: {e2}")
            
            plt.close(fig)  # Cerrar figura para liberar memoria
        
        # Mostrar resumen de datos utilizados para los videos
        print(f"\n" + "=" * 60)
        print("RESUMEN DE DATOS UTILIZADOS EN LOS VIDEOS")
        print("=" * 60)
        print(f"• Duración de simulación: 4 horas (08:00 - 12:00)")
        print(f"• Puntos de datos capturados: {len(self.historial_animacion)} (cada 60 segundos)")
        print(f"• Número de boxes simulados: {self.num_boxes}")
        print(f"• Probabilidad de llegada: {self.prob_ingreso:.6f} por segundo")
        print(f"• Tiempo máximo de espera: {self.tiempo_max_espera/60:.0f} minutos")
        print(f"• Tiempo promedio de atención: {self.media_atencion/60:.0f} ± {self.desvio_atencion/60:.0f} minutos")
        
        if self.historial_animacion:
            cola_max = max(estado['cola_size'] for estado in self.historial_animacion)
            boxes_max_usado = max(estado['boxes_ocupados'] for estado in self.historial_animacion)
            print(f"• Tamaño máximo de cola observado: {cola_max} clientes")
            print(f"• Máximo de boxes simultáneamente ocupados: {boxes_max_usado}")
        
        print(f"• Videos generados para velocidades: {velocidades}")
        print("=" * 60)
        
        print(f"\n¡Generación de videos completada!")
        return True

def comparar_configuraciones():
    """Compara diferentes configuraciones de boxes"""
    print("ANÁLISIS COMPARATIVO DE CONFIGURACIONES")
    print("=" * 60)
    
    configuraciones = range(1, 11)  # De 1 a 10 boxes
    resultados = []
    
    for num_boxes in configuraciones:
        print(f"\nProbando configuración con {num_boxes} boxes...")
        simulador = SimuladorAtencionPublico(num_boxes)
        simulador.simular(mostrar_progreso=False)
        resultado = simulador.generar_reporte()
        resultado['num_boxes'] = num_boxes
        resultados.append(resultado)
    
    # Encontrar configuración óptima
    mejor_config = min(resultados, key=lambda x: x['costo_total'])
    
    print("\n" + "=" * 60)
    print("RESUMEN COMPARATIVO")
    print("=" * 60)
    print(f"{'Boxes':<6} {'Atendidos':<10} {'Abandonos':<10} {'Tasa %':<8} {'Costo Total':<12}")
    print("-" * 60)
    
    for resultado in resultados:
        print(f"{resultado['num_boxes']:<6} "
              f"{resultado['clientes_atendidos']:<10} "
              f"{resultado['clientes_abandonaron']:<10} "
              f"{resultado['tasa_atencion']:<8.1f} "
              f"${resultado['costo_total']:<12,.0f}")
    
    print("\n" + "=" * 60)
    print(f"CONFIGURACIÓN ÓPTIMA: {mejor_config['num_boxes']} boxes")
    print(f"Costo total: ${mejor_config['costo_total']:,.2f}")
    print(f"Tasa de atención: {mejor_config['tasa_atencion']:.2f}%")
    print("=" * 60)

def main():
    """Función principal del programa"""
    print("SIMULADOR DE SISTEMA DE ATENCIÓN AL PÚBLICO")
    print("=" * 50)
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Simular con configuración específica")
        print("2. Comparar diferentes configuraciones")
        print("3. Generar videos AVI de simulación")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == '1':
            try:
                num_boxes = int(input("Ingresa el número de boxes (1-10): "))
                if 1 <= num_boxes <= 10:
                    simulador = SimuladorAtencionPublico(num_boxes)
                    simulador.simular()
                    simulador.generar_reporte()
                    
                    mostrar_animacion = input("\n¿Deseas ver la animación? (s/n): ").strip().lower()
                    if mostrar_animacion == 's':
                        velocidad = int(input("Velocidad de animación (1-5): ") or "2")
                        guardar = input("¿Guardar animación como AVI/GIF? (s/n): ").strip().lower() == 's'
                        simulador.crear_animacion(velocidad=velocidad, guardar_archivo=guardar)
                    
                    generar_videos = input("\n¿Deseas generar videos AVI con diferentes velocidades? (s/n): ").strip().lower()
                    if generar_videos == 's':
                        simulador.crear_video_avi()
                else:
                    print("Número de boxes debe estar entre 1 y 10.")
            except ValueError:
                print("Por favor ingresa un número válido.")
        
        elif opcion == '2':
            comparar_configuraciones()
        
        elif opcion == '3':
            try:
                num_boxes = int(input("Ingresa el número de boxes para el video (1-10): "))
                if 1 <= num_boxes <= 10:
                    print("Ejecutando simulación para generar datos del video...")
                    simulador = SimuladorAtencionPublico(num_boxes)
                    simulador.simular(mostrar_progreso=False)
                    # El reporte se mostrará automáticamente en crear_video_avi
                    simulador.crear_video_avi()
                else:
                    print("Número de boxes debe estar entre 1 y 10.")
            except ValueError:
                print("Por favor ingresa un número válido.")
        
        elif opcion == '4':
            print("¡Gracias por usar el simulador!")
            break
        
        else:
            print("Opción no válida. Por favor selecciona 1, 2, 3 o 4.")

if __name__ == "__main__":
    main()