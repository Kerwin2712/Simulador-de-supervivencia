import pygame

class Comida(pygame.sprite.Sprite):
    def __init__(self, x, y, valor=30, mundo=None):
        super().__init__()
        self.mundo = mundo
        # Creamos una representación simple de la comida (un círculo verde)
        self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 150, 0), (5, 5), 5) 
        
        self.rect = self.image.get_rect(center=(x, y))
        self.valor = valor # Cuánta energía proporciona
    
    def mostrar(self):
        self.mundo.PANTALLA.blit(self.image, self.rect)
    