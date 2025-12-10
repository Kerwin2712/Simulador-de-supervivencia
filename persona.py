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
from personaje import Personaje
from animal import Conejo, Zorro
import math
import random

class Persona(Personaje):
    def __init__(self, imagen, mundo, cerebro_movimiento=None, cerebro_decision=None):
        super().__init__(mundo, imagen, cerebro_movimiento, cerebro_decision)

        self.velocidad = 3

        self.inventario = []

        # Por defecto van a casa si existen
        if self.mundo.casas:
            self.objetivo = self.mundo.casas
            self.buscar_objetivo(self.objetivo)
    
    def entrar_casa(self):
        if self.mundo.casas:
            self.objetivo = self.mundo.casas
            self.buscar_objetivo(self.objetivo)
            self.mostrarme = False
            self.in_home = True
    
    def salir_casa(self):
        self.mostrarme = True
        self.in_home = False

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
        self.velocidad = 5
        self.energia_maxima = 200
        self.base_fuerza = 25 # Mas fuerte que animales
    
    def pensar(self, comidas, otros_personajes):
        """
        Hombre: Caza, pelea, come, lleva comida a casa
        Prioridad: Hambre > Defensa > Inventario > Sueño
        """
        # --- 0. HAMBRE / RECOLECCION ---
        # Si tiene hambre, la comida es prioridad (incluso sobre el sueño)
        if self.hambre > 20:
            # A. Tengo comida en inventario? -> Ir a casa a guardar/comer
            meat_in_inv = [i for i in self.inventario if isinstance(i, (Zorro, Conejo))]
            if meat_in_inv:
                if self.mundo.casas: 
                    self.objetivo = self.mundo.casas
                # Si llega a casa, la logica de guardar/comer debe estar en 'actualizar' o collision
                pass
            
            # B. Hay comida en casa? -> Ir a casa
            # (Simplificacion: Asumimos que sabe lo que hay en casa)
            # if self.mundo.casas and self.mundo.casas[0].almacen: ...
            
            # C. Cazar / Recolectar
            presas = [p for p in otros_personajes if isinstance(p, (Conejo, Zorro)) and p.vivo]
            if presas and self.fuerza > 5: # Solo caza si tiene fuerza
                self.objetivo = presas
            else:
                # Recolectar bayas
                self.objetivo = comidas
            
            if self.objetivo:
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 1. DEFENSA / AGRESION ---
        enemigos = [p for p in otros_personajes if isinstance(p, Zorro) and p.vivo]
        # Distancia segura?
        # Por ahora simple: si hay enemigos cerca, pelear
        # Se implementara busqueda de cercania real luego
        

        # --- 2. INVENTARIO (Llevar presas a casa) ---
        if self.inventario:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 3. SUEÑO ---
        if self.sueño > 90 and self.energia < 50:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
            if self.in_home:
                self.dormido = True
            if self.objetivo:
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
        self.velocidad = 5
        self.energia_maxima = 200
        self.base_fuerza = 25 # Fuerza media
    
    def pensar(self, comidas, otros_personajes):
        """
        Mujer: Cocina, alimenta a los niños, come, se defiende
        Prioridad: Cocinar (si hay en casa) > Hambre > Defensa > Inventario > Hijos > Sueño
        """

        # --- 1. COCINAR / COMER EN CASA ---
        # Si hay comida en casa, ir a cocinar
        if self.mundo.casas:
            casa = self.mundo.casas[0]
            if hasattr(casa, 'almacen') and casa.almacen and self.hambre > 20:
                self.objetivo = self.mundo.casas
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
                return

        # --- 2. HAMBRE / RECOLECCION ---
        if self.hambre > 30:
            # A. Inventario -> Casa
            if self.inventario:
                if self.mundo.casas:
                    self.objetivo = self.mundo.casas
                    self.buscar_objetivo(self.objetivo, otros=otros_personajes)
                return
        
        # --- 0. DEFENSA ---
        enemigos = [p for p in otros_personajes if isinstance(p, Zorro) and p.vivo]
        if enemigos:
            # Atacar si estan muy cerca
            self.objetivo = enemigos # Simplificado: Atacar
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return
            # B. Recolectar (Bayas) - Mujer prioriza bayas sobre caza agresiva
            # Pero puede cazar conejos si es necesario
            conejos = [p for p in otros_personajes if isinstance(p, Conejo) and p.vivo]
            if comidas:
                self.objetivo = comidas
            elif conejos:
                self.objetivo = conejos
            
            if self.objetivo:
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 3. HIJOS ---
        # Si no tiene hambre, cuida hijos
        hijos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
        if hijos:
            self.objetivo = hijos
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 4. SUEÑO ---
        if self.sueño > 90 and self.energia < 50:
            if self.mundo.casas:
                self.objetivo = self.mundo.casas
            if self.in_home:
                self.dormido = True
            if self.objetivo:
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
        self.velocidad = 5
    
    def pensar(self, comidas, otros_personajes):
        """Kid: Comer, Jugar"""
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 90:
            if self.mundo.casas: self.objetivo = self.mundo.casas
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            # Jugar con otros ninos
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
        self.velocidad = 5
    
    def pensar(self, comidas, otros_personajes):
        """Girl: Comer, Jugar"""
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 90:
            if self.mundo.casas: self.objetivo = self.mundo.casas
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
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
        self.velocidad = 5
    
    def pensar(self, comidas, otros_personajes):
        """Baby: Comer, Jugar"""
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return

        if self.sueño > 90:
            if self.mundo.casas: self.objetivo = self.mundo.casas
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer
            if self.hambre > 40:
                self.objetivo = comidas # A los bebes los alimentan, pero si tienen hambre buscan?
        elif accion == 1: # Jugar
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
        self.velocidad = 5
    
    def pensar(self, comidas, otros_personajes):
        """Baby: Comer, Jugar"""
        if self.dormido: 
            if self.sueño >= 100:
                self.dormido = False
            return
        
        if self.sueño > 90:
            if self.mundo.casas: self.objetivo = self.mundo.casas
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        inputs = [self.energia/100, self.hambre/100]
        decision = self.cerebro_decision.pensar(inputs)
        accion = decision.index(max(decision))
        
        if accion == 0: # Comer
            if self.hambre > 40:
                self.objetivo = comidas
        elif accion == 1: # Jugar
            amigos = self.buscar_familia((Kid, Girl, Baby_boy, Baby_girl))
            if amigos: self.objetivo = amigos
            
        if self.objetivo:
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)