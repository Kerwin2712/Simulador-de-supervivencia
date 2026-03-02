import pygame
import random

class Hogar:
    def __init__(self, mundo, x, y, tipo):
        self.mundo = mundo
        if tipo == "casa":
            self.imagen = pygame.image.load("images/casa.png")
            self.imagen = pygame.transform.scale(self.imagen, (300, 200))
        elif tipo == "cueva":
            self.imagen = pygame.image.load("images/cueva.png")
            self.imagen = pygame.transform.scale(self.imagen, (100, 70))
        elif tipo == "madriguera":
            self.imagen = pygame.image.load("images/madriguera.png")
            self.imagen = pygame.transform.scale(self.imagen, (100, 70))
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.imagen.get_width(), self.imagen.get_height())
        
        self.almacen = [] # Para guardar comida
        
    def guardar(self, item):
        self.almacen.append(item)
        
    def consumir(self):
        if self.almacen:
            return self.almacen.pop(0) # FIFO o LIFO da igual
        return None
    
    def mostrar(self):
        self.mundo.PANTALLA.blit(self.imagen, (self.x, self.y))
