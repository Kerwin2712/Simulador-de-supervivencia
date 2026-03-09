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
from agents.cerebro import Cerebro
from agents.personaje import Personaje
from agents.animales.animal import Conejo, Zorro
import math
import random

class Persona(Personaje):
    def __init__(self, imagen, mundo, cerebro_movimiento=None, cerebro_decision=None):
        super().__init__(mundo, imagen, cerebro_movimiento, cerebro_decision)

        self.velocidad_base = 3


        self.inventario = []

        # Por defecto van a casa si existen
        if self.mundo.casas:
            self.objetivo = self.mundo.casas
            self.buscar_objetivo(self.objetivo)
    
    def entrar_casa(self, modo="descansar", hogar=None):
        if self.mundo.casas:
            self.objetivo = self.mundo.casas
            self.buscar_objetivo(self.objetivo)
        super().entrar_casa(modo=modo, hogar=hogar)
    
    def salir_casa(self):
        super().salir_casa()

    def guardar_item(self, item):
        if len(self.inventario) < 10:
            self.inventario.append(item)
            
    def buscar_familia(self, tipos):
        candidatos = [p for p in self.mundo.personas if isinstance(p, tipos) and p is not self and p.vivo]
        return candidatos

    def pensar(self, comidas, otros_personajes):
        # Implementacion generica o abstracta
        pass

class Hombre(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/hombre.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191, 246))
        if not cerebro_decision:
            # Inputs: Energia, Hambre, DistanciaPresa (Conejo), DistanciaEnemigo (Zorro)
            # Outputs: Caza, Pelea, Come
            cerebro_decision = Cerebro(4, 6, 3) 
            
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5
        self.energia_maxima = 200

        self.base_fuerza = 25 # Mas fuerte que animales
    
    def pensar(self, comidas, otros_personajes):
        """
        Hombre: Prioridad: Defensa > Sueño > Comer en casa > Inventario -> Caza > Jugar
        """
        self.razon_ir_casa = None
        
        # --- 0. DEFENSA / AGRESION ---
        enemigos = [p for p in otros_personajes if isinstance(p, Zorro) and p.vivo]
        if enemigos:
            self.objetivo = enemigos
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 1. SUEÑO ---
        if self.sueño > 70:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 2. COMER EN CASA ---
        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 3. INVENTARIO (Llevar presas a casa) ---
        if self.inventario:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "descansar" # Solo va a dejar algo
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 4. HAMBRE / RECOLECCION EXTERIOR ---
        if self.hambre > 20:
            presas = [p for p in otros_personajes if isinstance(p, (Conejo, Zorro)) and p.vivo]
            if presas and self.fuerza > 5:
                self.objetivo = presas
            else:
                self.objetivo = comidas
            
            if self.objetivo:
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 5. JUGAR ---
        if self.energia > 60 and self.hambre < 30 and self.sueño < 30 and random.random() < 0.05:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return
            
        # Default: Patrullar o Idle
        self.objetivo = []


class Mujer(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/mujer.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191, 246))
        if not cerebro_decision:
            # Inputs: Energia, Hambre, DistanciaHijo
            # Outputs: Cocina (Casa), Alimenta (Hijo), Come
            cerebro_decision = Cerebro(3, 6, 3)
            
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5
        self.energia_maxima = 200

        self.base_fuerza = 25 # Fuerza media
    
    def pensar(self, comidas, otros_personajes):
        """
        Mujer: Defensa > Sueño > Cocinar/Comer > Inventario > Caza
        """
        self.razon_ir_casa = None
        
        # --- 0. DEFENSA ---
        enemigos = [p for p in otros_personajes if isinstance(p, Zorro) and p.vivo]
        if enemigos:
            self.objetivo = enemigos 
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 1. SUEÑO ---
        if self.sueño > 70:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 2. COMER EN CASA ---
        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 3. RECOLECCION / CAZA ---
        if self.hambre > 30:
            if self.inventario:
                if self.mundo.casas:
                    self.objetivo = self.mundo.casas
                    self.razon_ir_casa = "descansar" # Solo a dejar
                    self.buscar_objetivo(self.objetivo, otros=otros_personajes)
                return
        
            conejos = [p for p in otros_personajes if isinstance(p, Conejo) and p.vivo]
            if comidas:
                self.objetivo = comidas
            elif conejos:
                self.objetivo = conejos
            
            if self.objetivo:
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 4. HIJOS ---
        hijos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
        if hijos:
            self.objetivo = hijos
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 5. JUGAR ---
        if self.energia > 60 and self.hambre < 30 and self.sueño < 30 and random.random() < 0.05:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        self.objetivo = []


class Kid(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/kid.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191, 246))
        if not cerebro_decision:
            # Input: Energia, Hambre
            # Output: Comer, Jugar
            cerebro_decision = Cerebro(2, 4, 2)

        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5

    
    def pensar(self, comidas, otros_personajes):
        """Kid: Comer, Jugar"""
        self.razon_ir_casa = None
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 70:
            if self.mundo.casas: 
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer exterior
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            # 50% chance de ir a jugar a la casa
            if random.random() < 0.5 and self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
            else:
                amigos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
                if amigos: self.objetivo = amigos
            
        if self.objetivo:
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)


class Girl(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/girl.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191, 246))
        if not cerebro_decision:
            cerebro_decision = Cerebro(2, 4, 2)
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5

    
    def pensar(self, comidas, otros_personajes):
        """Girl: Comer, Jugar"""
        self.razon_ir_casa = None
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 70:
            if self.mundo.casas: 
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer exterior
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            if random.random() < 0.5 and self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
            else:
                amigos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
                if amigos: self.objetivo = amigos
            
        if self.objetivo:
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)


class Baby_boy(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/baby_boy.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191-40, 246-40))
        if not cerebro_decision:
            cerebro_decision = Cerebro(2, 4, 2)
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5

    
    def pensar(self, comidas, otros_personajes):
        """Baby: Comer, Jugar"""
        self.razon_ir_casa = None
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 70:
            if self.mundo.casas: 
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer exterior
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            if random.random() < 0.5 and self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
            else:
                amigos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
                if amigos: self.objetivo = amigos
            
        if self.objetivo:
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)


class Baby_girl(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/baby_girl.png")
        #Escalar imagen
        imagen = pygame.transform.scale(imagen, (191-40, 246-40))
        if not cerebro_decision:
            cerebro_decision = Cerebro(2, 4, 2)
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.nombre = nombre
        self.velocidad_base = 5

    
    def pensar(self, comidas, otros_personajes):
        """Baby: Comer, Jugar"""
        self.razon_ir_casa = None
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 70:
            if self.mundo.casas: 
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "dormir"
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        if self.hambre > 40 and self.mundo.casas and hasattr(self.mundo.casas[0], 'almacen') and self.mundo.casas[0].almacen:
            self.objetivo = self.mundo.casas
            self.razon_ir_casa = "comer"
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer exterior
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            if random.random() < 0.5 and self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.razon_ir_casa = "jugar"
            else:
                amigos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
                if amigos: self.objetivo = amigos
            
        if self.objetivo:
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)


class Kerwin(Persona):
    def __init__(self, nombre, mundo, cerebro_movimiento=None):
        # Usar la imagen específica de kerwin
        try:
            imagen = pygame.image.load("images/kerwin.png")
        except:
            # Fallback if image not found, use a placeholder or hombre
            imagen = pygame.image.load("images/hombre.png")
            
        # Escalar imagen (asumiendo las mismas proporciones de los otros sprays)
        imagen = pygame.transform.scale(imagen, (191, 246))
        
        # Kerwin no usa cerebro de decisión automático para objetivos.
        # El usuario es quien decide qué hacer.
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision=None)
        self.nombre = nombre
        self.velocidad_base = 6 # Un poco más rápido por ser héroe
        self.energia_maxima = 300
        self.base_fuerza = 40
        
        self.accion_pendiente = None # 'atacar', 'atrapar', 'comer'
        self.objetivo_manual = None  # Entidad seleccionada por el usuario

    def pensar(self, comidas, otros_personajes):
        """
        Kerwin no decide solo. Solo se mueve si el usuario le dio un objetivo.
        """
        if self.objetivo_manual:
            # Caso A: Objetivo es una entidad (objeto con rect)
            if hasattr(self.objetivo_manual, 'rect'):
                if hasattr(self.objetivo_manual, 'vivo') and not self.objetivo_manual.vivo and self.accion_pendiente != 'comer':
                    # Si murió y no vamos a comerlo, reseteamos? 
                    # Dejamos que llegue para 'guardar' si es la accion
                    pass 
                self.buscar_objetivo(self.objetivo_manual, otros=otros_personajes)
            
            # Caso B: Objetivo es una coordenada (tupla x, y)
            elif isinstance(self.objetivo_manual, (tuple, list)):
                target_pos = self.objetivo_manual
                cx, cy = self.x + self.ancho_sprite/2, self.y + self.alto_sprite/2
                dx = target_pos[0] - cx
                dy = target_pos[1] - cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 5: # Radio de parada
                    # Calcular dirección normalizada
                    ndx = dx / dist
                    ndy = dy / dist
                    # Suavizar llegada: si está cerca de 15px, reducir fuerza
                    fuerza_llegada = min(1.0, dist / 15.0)
                    self.mover(ndx * fuerza_llegada, ndy * fuerza_llegada, otros_personajes)
                    self.moving = True
                else:
                    # Llegó al punto: frenado fuerte
                    self.vx *= 0.2
                    self.vy *= 0.2
                    self.moving = False
                    self.objetivo_manual = None 

        else:
            self.moving = False

