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
    def __init__(self, fondo):
        self.ANCHO, self.ALTO = fondo.get_width(), fondo.get_height()
        self.PANTALLA = pygame.display.set_mode((self.ANCHO, self.ALTO))
        self.RELOJ = pygame.time.Clock()
        self.FPS = 60
        self.fondo = fondo
    
    def mostrar(self):
        self.PANTALLA.blit(self.fondo, (0, 0))

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()

    def actualizar(self):
        pass


