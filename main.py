'''
Punto de entrada, inicia el mundo y agrega personas
'''
import pygame
from mundo import Mundo
from persona import Persona


#Inica el mundo y el personaje
pygame.init()
mundo = Mundo(pygame.image.load("images/Pista.png"))
persona = Persona(pygame.image.load("images/LIDER.png").convert_alpha(), mundo)

pasos = 0

#Bucle principal
while True:
    # 1. Eventos
    mundo.eventos()
    
    # 2. Actualizar logica
    mundo.actualizar()
    
    # Manejo de teclas
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    moving = False
    
    if keys[pygame.K_LEFT]:
        dx = -1
        moving = True
    elif keys[pygame.K_RIGHT]:
        dx = 1
        moving = True
        
    if keys[pygame.K_UP]:
        dy = -1
        moving = True
    elif keys[pygame.K_DOWN]:
        dy = 1
        moving = True
        
    if moving:
        persona.mover(dx, dy)
    else:
        # Resetear al frame de pie si no se mueve (opcional)
        persona.frame = 0
        
    persona.actualizar()
    
    # 3. Dibujar
    mundo.mostrar()
    persona.mostrar()
    
    # 4. Actualizar pantalla
    pygame.display.update()
    mundo.RELOJ.tick(mundo.FPS)

