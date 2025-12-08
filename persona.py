'''
Crea la clase de cada persona en el juego.
controla como se ve el personaje en el mapa.
La imagen del personaje mide 191x246 píxeles. tiene 4 filas y 4 columnas de imágenes del personaje para simular movimiento.
Filas:
    -1. Abajo
    -2. Izquierda
    -3. Derecha
    -4. Arriba
cambiando de fila se cambia la direccion y cambiando de columna simula estar caminando. hay que recorer horizontalmente cada fila y la cantidad de veces por segundo simulan la velocidad.
estas personas seran controladas por redes neuronales.
'''
import pygame


class Persona:
    def __init__(self, imagen, mundo):
        self.mundo = mundo
        self.imagen = imagen
        
        # Posicion
        self.x = mundo.ANCHO // 2
        self.y = mundo.ALTO // 2
        
        # Dimensiones del sprite (4x4)
        self.ancho_sprite = self.imagen.get_width() // 4
        self.alto_sprite = self.imagen.get_height() // 4
        
        # Estado de animacion
        self.direccion = 0 # 0: Abajo, 1: Izquierda, 2: Derecha, 3: Arriba
        self.frame = 0     # 0-3
        self.velocidad = 5
        self.contador_animacion = 0
        self.velocidad_animacion = 10 # Cambiar frame cada X ticks
        
        # Rectangulo de recorte inicial
        self.src_rect = pygame.Rect(0, 0, self.ancho_sprite, self.alto_sprite)
        
    def mostrar(self):
        # Calcular rectangulo de recorte basado en direccion y frame
        # Asumiendo orden de filas: 0-Abajo, 1-Izquierda, 2-Derecha, 3-Arriba
        x_recorte = self.frame * self.ancho_sprite
        y_recorte = self.direccion * self.alto_sprite
        
        self.src_rect = pygame.Rect(x_recorte, y_recorte, self.ancho_sprite, self.alto_sprite)
        self.mundo.PANTALLA.blit(self.imagen, (self.x, self.y), self.src_rect)

    def mover(self, dx, dy):
        # Actualizar posicion
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad
        
        # Determinar direccion
        if dy > 0: self.direccion = 0 # Abajo
        elif dy < 0: self.direccion = 3 # Arriba
        
        if dx < 0: self.direccion = 1 # Izquierda
        elif dx > 0: self.direccion = 2 # Derecha
            
        # Actualizar animacion
        self.contador_animacion += 1
        if self.contador_animacion >= self.velocidad_animacion:
            self.frame = (self.frame + 1) % 4
            self.contador_animacion = 0
    
    def actualizar(self):
        # Limites de pantalla (opcional, para que no se salga)
        self.x = max(0, min(self.x, self.mundo.ANCHO - self.ancho_sprite))
        self.y = max(0, min(self.y, self.mundo.ALTO - self.alto_sprite))
