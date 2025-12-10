
import pygame
from personaje import Personaje
from cerebro import Cerebro
import random

class Animal(Personaje):
    def __init__(self, imagen, mundo, cerebro_movimiento=None, cerebro_decision=None):
        super().__init__(mundo, imagen, cerebro_movimiento, cerebro_decision)
        
        self.objetivo = [] 
        # Los animales buscan madrigueras por defecto si no tienen nada mas? 
        # O quiza deambulan. Por ahora vacio.

    def buscar_pareja(self, clase):
        # Logica simple para buscar pareja de la misma especie
        candidatos = [p for p in self.mundo.personas if isinstance(p, clase) and p is not self and p.vivo]
        return candidatos

class Zorro(Animal):
    def __init__(self, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/Fig_Zorro.png")
        if not cerebro_decision:
            # Input: [Energia, Hambre, DistanciaConejo, DistanciaEnemigo, Edad] (5)
            # Output: [Cazar, Pelear, Comer, Reproducirse] (4)
            cerebro_decision = Cerebro(5, 8, 4)
            
        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.velocidad = 4
        self.energia_maxima = 100
        self.base_fuerza = 12
    
    def pensar(self, comidas, otros_personajes):
        """
        Zorro: Carnivoro Agresivo.
        Prioridad: Cazar (Conejos) > Atacar Humanos > Dormir
        """
        if self.dormido: 
            if self.sueño >= 100: self.dormido = False
            return

        # --- 1. CAZA / HAMBRE ---
        # Prioridad absoluta es comer carne
        conejos = [p for p in otros_personajes if isinstance(p, Conejo) and p.vivo]
        if conejos:
            # Ir por el mas cercano
            self.objetivo = conejos 
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return
            
        # --- 2. AGRESION (Humanos) ---
        # Si no hay conejos, ataca humanos por territorio o hambre
        humanos = [p for p in otros_personajes if isinstance(p, Personaje) and not isinstance(p, (Zorro, Conejo)) and p.vivo]
        if humanos and self.hambre > 50:
            self.objetivo = humanos
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # --- 3. SUEÑO ---
        if self.sueño > 90:
            if self.mundo.madrigueras: self.objetivo = self.mundo.madrigueras
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return

        # Idle
        self.objetivo = []

class Conejo(Animal):
    def __init__(self, mundo, cerebro_movimiento=None, cerebro_decision=None):
        imagen = pygame.image.load("images/Fig_Conejo.png")
        if not cerebro_decision:
            cerebro_decision = Cerebro(4, 6, 3) # Unused for now

        super().__init__(imagen, mundo, cerebro_movimiento, cerebro_decision)
        self.velocidad = 4 # Rapido
        self.energia_maxima = 70
        self.base_fuerza = 2
    
    def pensar(self, comidas, otros_personajes):
        """
        Conejo: Presa Evasiva.
        Prioridad: HUIR > Comer > Dormir
        """
        if self.dormido: 
            if self.sueño >= 100: self.dormido = False
            return
            
        # --- 1. COMIDA (Prioridad sobre evasion si tiene hambre) ---
        if self.hambre > 30:
            self.objetivo = comidas
            self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            # Aun asi detectamos peligro para el log, pero no huimos inmediatemente
            amenazas = [p for p in otros_personajes if isinstance(p, (Zorro)) and p.vivo]
            if amenazas: self.peligro = True
            else: self.peligro = False
            return

        # --- 2. EVASION ---
        # Detectar depredadores (Zorros o Humanos)
        amenazas = [p for p in otros_personajes if isinstance(p, (Zorro)) and p.vivo] # Humanos tambien?
        # Simplificacion: Si hay Zorro, HUIR
        if amenazas:
            self.peligro = True
            # Evasion Inversa: Buscar objetivo opuesto?
            # Por ahora, simulamos 'huida' yendo a la madriguera rapido o lejos
            if self.mundo.madrigueras:
                self.objetivo = self.mundo.madrigueras
                self.buscar_objetivo(self.objetivo, otros=otros_personajes)
                # Hack de velocidad
                self.mover(random.choice([-1, 1]), random.choice([-1, 1]), otros_personajes) 
                return
        else:
            self.peligro = False

        # --- 3. SUEÑO ---
        if self.sueño > 90:
            if self.mundo.madrigueras: self.objetivo = self.mundo.madrigueras
            if self.in_home: self.dormido = True
            if self.objetivo: self.buscar_objetivo(self.objetivo, otros=otros_personajes)
            return
            
        self.objetivo = []
