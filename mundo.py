'''
Inicia la ventana de pygame. el fondo es un mapa y el personaje es un sprite que se mueve por el mapa.
Muestra el escenario 
- Exterior 
- Una casa
'''

import pygame

# Inicialización de pygame
pygame.init()

class Mundo:
    def __init__(self):
        self.ANCHO, self.ALTO = 1200, 600
        self.PANTALLA = pygame.display.set_mode((self.ANCHO, self.ALTO))
        self.RELOJ = pygame.time.Clock()
        self.FPS = 60
        self.fondo = pygame.image.load("images/Pista.png")
        self.fondo = pygame.transform.scale(self.fondo, (self.ANCHO, self.ALTO))
        self.casas = []
        self.alimentos = []
        self.conejos = []
        self.madrigueras = []
        self.cuevas = []
        self.personas = []
    
    def mostrar(self):
        self.PANTALLA.blit(self.fondo, (0, 0))

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()

    def actualizar(self):
        pass


