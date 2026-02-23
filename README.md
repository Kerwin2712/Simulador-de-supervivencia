# Simulador de Supervivencia: Ecosistema con Neuroevolución

Este proyecto es una simulación de ecosistema dinámico donde agentes inteligentes (Humanos, Zorros y Conejos) coexisten y evolucionan en un entorno competitivo. Utiliza **Redes Neuronales** y **Algoritmos Genéticos** para dictar el comportamiento y la supervivencia de los individuos.

## 🚀 Características Principales

- **Inteligencia Artificial (Neuroevolución)**: Cada agente posee un "Cerebro" (Red Neuronal Feedforward) que procesa estímulos del entorno para tomar decisiones en tiempo real.
- **Algoritmos Genéticos**: Los individuos más aptos transmiten sus pesos sinápticos a la siguiente generación mediante cruce y mutación.
- **Ecosistema Completo**: Ciclos de hambre, sueño, reproducción, caza y recolección de recursos.
- **Interfaz Gráfica**: Visualización interactiva desarrollada con **Pygame**.
- **Gestión de Inventario y Hogar**: Los humanos pueden recolectar comida, almacenarla en casas y refugiarse para descansar.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.x
- **Gráficos**: Pygame
- **IA**: Redes Neuronales (Implementación propia sin librerías externas para lógica base)
- **Persistencia**: Pickle (para guardar/cargar poblaciones evolucionadas)

## 📋 Requisitos e Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/Kerwin2712/Simulador-de-supervivencia.git
   cd Simulador-de-supervivencia
   ```

2. **Instalar dependencias**:
   Asegúrate de tener Python instalado y luego instala Pygame:
   ```bash
   pip install pygame
   ```

3. **Ejecutar la simulación**:
   ```bash
   python main.py
   ```

## 🧠 Detalles Técnicos

### El Cerebro (Red Neuronal)
El archivo `cerebro.py` implementa una red neuronal con capas de entrada, oculta y salida. 
- **Entradas**: Posición de comida, enemigos cercanos, nivel de hambre y energía.
- **Salidas**: Vector de movimiento (Arriba, Abajo, Izquierda, Derecha, Interactuar).
- **Activación**: Función Sigmoide para la toma de decisiones probabilísticas.

### Evolución y Genética
Cuando los agentes se reproducen o la población se reinicia basándose en los mejores individuos:
- **Cruce**: Se combinan los pesos de dos padres exitosos para crear un nuevo cerebro.
- **Mutación**: Pequeños cambios aleatorios en los pesos (ruido gaussiano) permiten la exploración de nuevos comportamientos.

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada y gestión del bucle de simulación.
- `cerebro.py`: Implementación de la Red Neuronal y lógica genética.
- `persona.py`, `animal.py`: Definición de los agentes y sus comportamientos específicos.
- `mundo.py`, `hogar.py`, `recursos.py`: Definición del entorno y elementos interactuables.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.
