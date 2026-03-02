'''
Inicia la ventana de pygame. El fondo es un mapa y el personaje es un sprite que se mueve por el mapa.
Muestra el escenario 
- Espacio 
- Objetos
- personajes
'''

import pygame

# Inicialización de pygame
pygame.init()

class Mundo:
    def __init__(self):
        #Instancia de constantes
        self.ANCHO, self.ALTO = 1200, 600
        self.PANTALLA = pygame.display.set_mode((self.ANCHO, self.ALTO))
        self.RELOJ = pygame.time.Clock()
        self.FPS = 60

        #Carga y transformacion de graficos
        self.fondo = pygame.image.load("images/Pista.png")
        self.fondo = pygame.transform.scale(self.fondo, (self.ANCHO, self.ALTO))
        
        #Listas de elementos contenidos
        self.casas = []
        self.alimentos = []
        self.conejos = []
        self.madrigueras = []
        self.cuevas = []
        self.personas = []
    
    def mostrar(self): #Muestra los graficos 
        self.PANTALLA.blit(self.fondo, (0, 0))

    def eventos(self): #Administrador de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()

    def actualizar(self):
        pass


