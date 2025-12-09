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
La energia debe bajar con el tiempo y cuando llegue a 0 la persona muere.
'''
import pygame
from cerebro import Cerebro
import math
import random

class Persona:
    def __init__(self, imagen, mundo, cerebro=None):
        self.mundo = mundo
        self.imagen = imagen
        
        if cerebro:
            self.cerebro = cerebro
        else:
            # 2 entradas (dx, dy a comida), 6 ocultas, 4 salidas (arriba, abajo, izq, der)
            self.cerebro = Cerebro(2, 6, 4)
        
        # Dimensiones del sprite (4x4)
        self.ancho_sprite = self.imagen.get_width() // 4
        self.alto_sprite = self.imagen.get_height() // 4

        # Posicion
        self.x = random.randint(0, mundo.ANCHO - self.ancho_sprite)
        self.y = random.randint(0, mundo.ALTO - self.alto_sprite)
        
        # Estado de animacion
        self.direccion = 0 # 0: Abajo, 1: Izquierda, 2: Derecha, 3: Arriba
        self.frame = 0     # 0-3
        self.velocidad = 4
        self.contador_animacion = 0
        self.velocidad_animacion = 10 # Cambiar frame cada X ticks
        
        #Estado de la persona
        self.vivo = True
        self.moving = False
        self.energia = 100
        self.tiempo_vivo = 0 # Fitness
        self.comidas_comidas = 0 # Cantidad de comida ingerida
        self.contador_energia = 0
        self.velocidad_energia = 1
        
        # Rectangulo de recorte inicial
        self.src_rect = pygame.Rect(0, 0, self.ancho_sprite, self.alto_sprite)
        self.rect = pygame.Rect(self.x, self.y, self.ancho_sprite, self.alto_sprite)
        
        # Fuente para mostrar estado
        self.font = pygame.font.SysFont(None, 24)
    
    def get_vivo(self): return self.vivo
    def get_moving(self): return self.moving
    def set_vivo(self, vivo): self.vivo = vivo
    def set_moving(self, moving): self.moving = moving

    def mostrar(self):
        # Calcular rectangulo de recorte basado en direccion y frame
        # Asumiendo orden de filas: 0-Abajo, 1-Izquierda, 2-Derecha, 3-Arriba
        x_recorte = self.frame * self.ancho_sprite
        y_recorte = self.direccion * self.alto_sprite
        
        self.src_rect = pygame.Rect(x_recorte, y_recorte, self.ancho_sprite, self.alto_sprite)
        self.mundo.PANTALLA.blit(self.imagen, (self.x, self.y), self.src_rect)
        
        # --- BARRA DE VIDA ---
        # Dibujar barra sobre la cabeza (y - 10)
        ancho_barra_total = self.ancho_sprite
        alto_barra = 5
        x_barra = self.x
        y_barra = self.y - 10
        
        # Fondo rojo (daño/vacío)
        pygame.draw.rect(self.mundo.PANTALLA, (255, 0, 0), (x_barra, y_barra, ancho_barra_total, alto_barra))
        
        # Frente verde (energia actual)
        pixeles_vida = int((self.energia / 100) * ancho_barra_total)
        pygame.draw.rect(self.mundo.PANTALLA, (0, 255, 0), (x_barra, y_barra, pixeles_vida, alto_barra))

    def mover(self, dx, dy, otros):
        # --- MOVIEMIENTO EN X ---
        futuro_x = self.x + dx * self.velocidad
        futuro_rect_x = pygame.Rect(futuro_x, self.y, self.ancho_sprite, self.alto_sprite)
        
        colision_x = False
        if otros:
            for otro in otros:
                if otro is not self and otro.vivo:
                    if futuro_rect_x.colliderect(otro.rect):
                        colision_x = True
                        break
        
        if not colision_x:
            self.x = futuro_x

        # --- MOVIEMIENTO EN Y ---
        futuro_y = self.y + dy * self.velocidad
        # Usamos self.x ya actualizado (o no) para el rectangulo de Y
        futuro_rect_y = pygame.Rect(self.x, futuro_y, self.ancho_sprite, self.alto_sprite)
        
        colision_y = False
        if otros:
            for otro in otros:
                if otro is not self and otro.vivo:
                    if futuro_rect_y.colliderect(otro.rect):
                        colision_y = True
                        break
        
        if not colision_y:
            self.y = futuro_y
            
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
        if self.vivo:
            self.tiempo_vivo += 1
            
        # Limites de pantalla
        self.contador_energia += 1
        if self.contador_energia >= self.velocidad_energia:
            self.energia -= 1
            self.contador_energia = 0
        
        if self.energia <= 0:
            self.morir()
            
        self.x = max(0, min(self.x, self.mundo.ANCHO - self.ancho_sprite))
        self.y = max(0, min(self.y, self.mundo.ALTO - self.alto_sprite))
        self.rect.topleft = (self.x, self.y)
            
    def alimentarse(self, valor):
        self.energia += valor
        self.comidas_comidas += 1
        if self.energia > 100:
            self.energia = 100

    def pensar(self, comidas, otros=None):
        if not hasattr(self, 'min_dist_food'):
            self.min_dist_food = float('inf')
            
        if not comidas:
            self.target_food = None
            return

        # Buscar comida mas cercana
        cx, cy = self.x + self.ancho_sprite/2, self.y + self.alto_sprite/2
        cercana = None
        dist_min = float('inf')
        
        for comida in comidas:
            dx = comida.rect.centerx - cx
            dy = comida.rect.centery - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < dist_min:
                dist_min = dist
                cercana = (dx, dy)
                self.target_food = comida.rect.center # Guardar para dibujar linea
        
        # Actualizar mejor distancia historica (Fitness Shaping)
        # Solo actualizamos si encontramos comida
        if cercana:
            if dist_min < self.min_dist_food:
                self.min_dist_food = dist_min
        
        dx_mov, dy_mov = 0, 0
        if cercana:
            # Normalizar entradas (dividir por diagonal aprox para que esten entre -1 y 1)
            # Diagonal de 800x600 es 1000
            inputs = [cercana[0] / 1000, cercana[1] / 1000]
            outputs = self.cerebro.pensar(inputs)
            
            # Outputs: [Arriba, Abajo, Izq, Der]
            # Usar diferencia para movimiento continuo
            # Dy = Abajo - Arriba
            # Dx = Derecha - Izquierda
            
            val_arriba = outputs[0]
            val_abajo = outputs[1]
            val_izq = outputs[2]
            val_der = outputs[3]
            
            # Si la diferencia es positiva va hacia una direccion, negativa hacia la otra
            dy_neto = val_abajo - val_arriba
            dx_neto = val_der - val_izq
            
            # --- ATRACCION / INSTINTO ---
            # Agregar un vector de "instinto" hacia la comida
            distancia = math.sqrt(cercana[0]**2 + cercana[1]**2)
            if distancia > 0:
                instinto_x = cercana[0] / distancia
                instinto_y = cercana[1] / distancia
                
                # Peso del instinto (0.3 = 30% influencia)
                PESO_INSTINTO = 0.3
                
                dx_neto += instinto_x * PESO_INSTINTO
                dy_neto += instinto_y * PESO_INSTINTO

            # Umbral pequeño para evitar drifting
            if abs(dy_neto) > 0.1:
                dy_mov = 1 if dy_neto > 0 else -1
            
            if abs(dx_neto) > 0.1:
                dx_mov = 1 if dx_neto > 0 else -1
            
        if dx_mov != 0 or dy_mov != 0:
            self.moving = True
            self.mover(dx_mov, dy_mov, otros)
        else:
            self.moving = False
    
    def morir(self):
        self.vivo = False

