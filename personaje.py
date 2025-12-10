from cerebro import Cerebro
import pygame
import random
import math

class Personaje:
    def __init__(self, mundo, imagen, cerebro_movimiento=None, cerebro_decision=None):
        self.mundo = mundo
        self.imagen = imagen
        self.mostrarme = True
        # Dimensiones del sprite (4x4)
        self.ancho_sprite = self.imagen.get_width() // 4
        self.alto_sprite = self.imagen.get_height() // 4
        
        # Fuente para estados
        self.font_estado = pygame.font.SysFont(None, 12)
        
        #Posicion inicial
        self.x = random.randint(0, max(0, mundo.ANCHO - self.ancho_sprite))
        self.y = random.randint(0, max(0, mundo.ALTO - self.alto_sprite))
        # Rectangulo de recorte inicial
        self.src_rect = pygame.Rect(0, 0, self.ancho_sprite, self.alto_sprite)
        self.rect = pygame.Rect(self.x, self.y, self.ancho_sprite, self.alto_sprite)
        # Cerebro de Movimiento (Navegacion Local): Input: dx, dy a objetivo. Output: up, down, left, right
        if cerebro_movimiento:
            self.cerebro_movimiento = cerebro_movimiento
        else:
            # 2 entradas (dx, dy a objetivo), 6 ocultas, 4 salidas (arriba, abajo, izq, der)
            self.cerebro_movimiento = Cerebro(2, 6, 4)
            
        # Cerebro de Decision (Acciones Alto Nivel): Input: Estado. Output: Acciones (Objetivos)
        self.cerebro_decision = cerebro_decision

        # Estado de animacion
        self.direccion = 0 # 0: Abajo, 1: Izquierda, 2: Derecha, 3: Arriba
        self.frame = 0     # 0-3
        self.velocidad_base = 3
        self.velocidad = self.velocidad_base
        self.contador_animacion = 0
        self.velocidad_animacion = self.velocidad_base # Cambiar frame cada X ticks
        #Estado de la persona
        self.vivo = True
        self.peligro = False
        self.moving = False
        self.in_home = False
        
        # Estadisticas
        self.energia_maxima = 100
        self.energia = self.energia_maxima
        self.hambre = random.randint(50, 100)
        self.sueño = random.randint(0, 50)
        self.dormido = False
        
        self.edad = 0
        self.objetivo = [] 
        
        # Combate / Inventario
        self.base_fuerza = 10 
        self.inventario = []
        
        # Flags para eventos UI
        self.evento_muerte_reportado = False
        self.evento_dormir_reportado = False
        self.evento_peligro_reportado = False
        
        if self.objetivo:
            self.buscar_objetivo(self.objetivo)

    def entrar_casa(self):
        self.mostrarme = False
        self.in_home = True
        self.dormido = True # Asumimos que entra a descansar o dormir
    
    def salir_casa(self):
        self.mostrarme = True
        self.in_home = False
        self.dormido = False

    def mostrar(self):
        if not self.mostrarme:
            return
        
        # Calcular rectangulo de recorte basado en direccion y frame
        # Asumiendo orden de filas: 0-Abajo, 1-Izquierda, 2-Derecha, 3-Arriba
        x_recorte = self.frame * self.ancho_sprite
        y_recorte = self.direccion * self.alto_sprite
        
        self.src_rect = pygame.Rect(x_recorte, y_recorte, self.ancho_sprite, self.alto_sprite)
        self.mundo.PANTALLA.blit(self.imagen, (self.x, self.y), self.src_rect)
        
        # --- BARRAS DE ESTADO ---
        ancho_barra_total = self.ancho_sprite
        alto_barra = 4
        x_barra = self.x
        
        # 1. Energia (Verde)
        y_energia = self.y - 15
        pygame.draw.rect(self.mundo.PANTALLA, (100, 0, 0), (x_barra, y_energia, ancho_barra_total, alto_barra))
        pixeles_energia = int((self.energia / 100) * ancho_barra_total)
        pygame.draw.rect(self.mundo.PANTALLA, (0, 255, 0), (x_barra, y_energia, pixeles_energia, alto_barra))
        
        # 2. Hambre (Amarillo/Naranja) - Invertido visualmente? No, lleno = mucha hambre
        y_hambre = self.y - 10
        pygame.draw.rect(self.mundo.PANTALLA, (50, 50, 0), (x_barra, y_hambre, ancho_barra_total, alto_barra))
        pixeles_hambre = int((self.hambre / 100) * ancho_barra_total)
        pygame.draw.rect(self.mundo.PANTALLA, (255, 165, 0), (x_barra, y_hambre, pixeles_hambre, alto_barra))

        # 3. Sueño (Azul)
        y_sueno = self.y - 5
        pygame.draw.rect(self.mundo.PANTALLA, (0, 0, 50), (x_barra, y_sueno, ancho_barra_total, alto_barra))
        pixeles_sueno = int((self.sueño / 100) * ancho_barra_total)
        pygame.draw.rect(self.mundo.PANTALLA, (0, 100, 255), (x_barra, y_sueno, pixeles_sueno, alto_barra))

        # --- TEXTO ESTADO (z...z...z... / Grrr...) ---
        if self.dormido:
            texto = self.font_estado.render("z...z...z...", True, (255, 255, 255))
            self.mundo.PANTALLA.blit(texto, (x_barra, y_sueno + 5))
        elif self.hambre > 50:
            texto = self.font_estado.render("Grrr...", True, (255, 255, 255))
            self.mundo.PANTALLA.blit(texto, (x_barra, y_sueno + 5))

    
    def mover(self, dx, dy, otros):
        # Velocidad proporcional a energia
        # Si energia 100 -> 100% velocidad. Si 0 -> 0% (o minimo 10% para moverse lento)
        factor_energia = max(0.1, self.energia / 100.0)
        velocidad_actual = self.velocidad_base * factor_energia
        
        # --- MOVIEMIENTO EN X ---
        futuro_x = self.x + dx * velocidad_actual
        futuro_rect_x = pygame.Rect(futuro_x, self.y, self.ancho_sprite, self.alto_sprite)
        
        colision_x = False
        if otros:
            for otro in otros:
                if otro is not self and otro.vivo and otro.mostrarme: # Solo colisionar con visibles
                    # A veces otros es una lista mixta, asegurar que tenga rect
                    if hasattr(otro, 'rect') and futuro_rect_x.colliderect(otro.rect):
                        colision_x = True
                        break
        
        if not colision_x:
            self.x = futuro_x

        # --- MOVIEMIENTO EN Y ---
        futuro_y = self.y + dy * velocidad_actual
        # Usamos self.x ya actualizado (o no) para el rectangulo de Y
        futuro_rect_y = pygame.Rect(self.x, futuro_y, self.ancho_sprite, self.alto_sprite)
        
        colision_y = False
        if otros:
            for otro in otros:
                if otro is not self and otro.vivo and otro.mostrarme:
                    if hasattr(otro, 'rect') and futuro_rect_y.colliderect(otro.rect):
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
        if not self.vivo:
            return
            
        self.edad += 0.01 # Lento envejecimiento
        
        # --- DINAMICAS DE ESTADO ---
        if self.dormido or self.in_home:
            # Recuperar energia y bajar sueño
            self.energia += 0.2
            self.sueño -= 0.3
            self.hambre += 0.01 # Hambre sube lento al dormir
            
            # Despertar si sueño es 0 O si la energia es suficiente (> 50) O si tiene hambre (> 60)
            if self.sueño <= 0 or self.energia > 50 or self.hambre > 60:
                self.sueño = 0
                self.dormido = False
                self.salir_casa() # Salir al despertar
        else:
            # Despierto
            self.sueño += 0.05
            
            # Hambre
            tasa_hambre = 0.05
            if self.moving:
                tasa_hambre = 0.1
            self.hambre += tasa_hambre
            
            # Hambre afecta Energia
            if self.hambre > 80:
                self.energia -= 0.1
            
            # Sueño maximo causa daño (Agotamiento)
            if self.sueño >= 100:
                self.sueño = 100
                self.energia -= 0.1 # Daño por no dormir
                # self.dormido = True # REMOVIDO: Solo duerme en casa
        
        # Limites
        self.energia = max(0, min(100, self.energia))
        self.hambre = max(0, min(100, self.hambre))
        self.sueño = max(0, min(100, self.sueño))
        
        if self.energia <= 0:
            self.morir()
        
        #manejar limites de pantalla 
        self.x = max(0, min(self.x, self.mundo.ANCHO - self.ancho_sprite))
        self.y = max(0, min(self.y, self.mundo.ALTO - self.alto_sprite))

        self.rect.topleft = (self.x, self.y)
    
    def alimentarse(self, valor):
        self.hambre -= valor
        self.energia += (valor / 2) # Comida tambien da algo de energia
        if self.hambre < 0: self.hambre = 0
        if self.energia > 100: self.energia = 100
        
    @property
    def fuerza(self):
        # Fuerza proporcional a energia
        return self.base_fuerza * (self.energia / self.energia_maxima)

    def atacar(self, objetivo):
        damage = self.fuerza
        objetivo.energia -= damage
        pos_damage = max(0, damage)
        # print(f"{self} atacó a {objetivo} por {pos_damage:.2f} daño") # Debug
        if objetivo.energia <= 0:
            objetivo.morir()
            # Si muere, logica de loot se maneja afuera o aqui?
            # Dejemos que la accion 'pensar' maneje el loot
    
    def buscar_objetivo(self, objetivo, otros=None):
        if self.dormido and not self.in_home:
            # Si se durmio fuera, no se mueve
            self.moving = False
            return 
            
        if not hasattr(self, 'min_dist_objetivo'):
            self.min_dist_objetivo = float('inf')
            
        if not objetivo:
            self.target_objetivo = None
            return

        # Buscar objetivo mas cercano
        cx, cy = self.x + self.ancho_sprite/2, self.y + self.alto_sprite/2
        cercana = None
        dist_min = float('inf')
        
        lista_objs = []
        if isinstance(objetivo, pygame.sprite.Group):
            lista_objs = objetivo.sprites()
        elif isinstance(objetivo, list):
            lista_objs = objetivo
        else:
            lista_objs = [objetivo] # Un solo objeto paso
            
        for item in lista_objs:
            dx = item.rect.centerx - cx
            dy = item.rect.centery - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < dist_min:
                dist_min = dist
                cercana = (dx, dy)
                self.target_objetivo = item.rect.center
        
        if cercana:
            if dist_min < self.min_dist_objetivo:
                self.min_dist_objetivo = dist_min
        
        dx_mov, dy_mov = 0, 0
        if cercana:
            inputs = [cercana[0] / 1000, cercana[1] / 1000]
            outputs = self.cerebro_movimiento.pensar(inputs)
            
            val_arriba = outputs[0]
            val_abajo = outputs[1]
            val_izq = outputs[2]
            val_der = outputs[3]
            
            dy_neto = val_abajo - val_arriba
            dx_neto = val_der - val_izq
            
            # --- ATRACCION / INSTINTO (FUERTE) ---
            distancia = math.sqrt(cercana[0]**2 + cercana[1]**2)
            if distancia > 0:
                instinto_x = cercana[0] / distancia
                instinto_y = cercana[1] / distancia
                
                # AUMENTADO a 2.0 para asegurar movimiento hacia objetivo
                PESO_INSTINTO = 2.0 
                
                dx_neto += instinto_x * PESO_INSTINTO
                dy_neto += instinto_y * PESO_INSTINTO

        else:
            # Si no hay objetivo, movimiento aleatorio para evitar estancamiento
            dx_neto = random.uniform(-0.5, 0.5)
            dy_neto = random.uniform(-0.5, 0.5)

        # --- REPULSION DE PAREDES ---
        margin = 60
        force_wall = 5.0 
        
        if self.x < margin:
            dx_neto += force_wall
        elif self.x > self.mundo.ANCHO - margin - self.ancho_sprite:
            dx_neto -= force_wall
            
        if self.y < margin:
            dy_neto += force_wall
        elif self.y > self.mundo.ALTO - margin - self.alto_sprite:
            dy_neto -= force_wall

        dx_mov, dy_mov = 0, 0
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