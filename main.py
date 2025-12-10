'''
Punto de entrada, inicia el mundo y agrega personas
'''
import pygame
from mundo import Mundo
from persona import Persona, Hombre, Mujer, Kid, Girl, Baby_boy, Baby_girl
from animal import Zorro, Conejo
from hogar import Hogar
from recursos import Comida
import random
import pickle
import os

#Inica el mundo y el personaje
pygame.init()
mundo = Mundo()

# Configuración Inicial
poblacion = []
# Imagenes (ya cargadas en las clases o aqui si se pasan)
# Nota: Las clases ahora cargan sus propias imagenes por defecto si no se pasan, 
# pero mantendremos la compatibilidad si es necesario.

def crear_poblacion_inicial():
    pob = []
    
    # 1. Crear Entorno (Hogar, Cueva)
    mundo.casas = []
    mundo.madrigueras = []
    mundo.cuevas = []
    
    casa = Hogar(mundo, mundo.ANCHO - 300, 50, "casa")
    mundo.casas.append(casa)
    
    madriguera = Hogar(mundo, 100, 100, "madriguera")
    mundo.madrigueras.append(madriguera)

    cueva = Hogar(mundo, 100,mundo.ALTO - 100, "cueva")
    mundo.cuevas.append(cueva)
    
    # 2. Crear Personajes
    hombre = Hombre("Adan", mundo)
    mujer = Mujer("Eva", mundo)
    pob.extend([hombre, mujer])

    for _ in range(2):
        pob.append(Zorro(mundo))
        
    for _ in range(6):
        pob.append(Conejo(mundo))
    
    # Actualizar listas en mundo para referencias globales
    mundo.personas = [p for p in pob if isinstance(p, Persona)]
    # Zorro y Conejo son Animales
    
    return pob

poblacion = []
comidas = pygame.sprite.Group()

def resetear_comida():
    comidas.empty()
    for _ in range(20): 
        x = random.randint(0, mundo.ANCHO)
        y = random.randint(0, mundo.ALTO)
        comida = Comida(x, y, mundo=mundo)
        comidas.add(comida)

font_ui = pygame.font.SysFont(None, 30)

# --- MENU DE INICIO ---
rect_boton_inicio = pygame.Rect(mundo.ANCHO // 2 - 100, mundo.ALTO // 2 - 20, 200, 40)
ESTADO = "MENU"

def dibujar_menu(superficie):
    superficie.fill((30, 30, 30))
    
    texto_titulo = font_ui.render("SIMULADOR DE SUPERVIVENCIA", True, (200, 200, 255))
    rect_titulo = texto_titulo.get_rect(center=(mundo.ANCHO//2, mundo.ALTO//2 - 80))
    superficie.blit(texto_titulo, rect_titulo)
    
    # Boton Iniciar
    pygame.draw.rect(superficie, (50, 200, 50), rect_boton_inicio)
    texto_boton = font_ui.render("INICIAR SIMULACION", True, (20, 20, 20))
    rect_texto_boton = texto_boton.get_rect(center=rect_boton_inicio.center)
    superficie.blit(texto_boton, rect_texto_boton)

def reiniciar_simulacion():
    global poblacion
    poblacion = crear_poblacion_inicial()
    resetear_comida()
    print("Simulación reiniciada.")

# Boton Reset
rect_boton_reset = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 60, 200, 40)

# Botones Velocidad
velocidad_simulacion = 120 # FPS Inicial
rect_boton_menos = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 110, 40, 40)
rect_boton_mas = pygame.Rect(mundo.ANCHO - 50, mundo.ALTO - 110, 40, 40)

# Boton Menu
rect_boton_menu = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 110, 200, 40)

def dibujar_ui_simulacion(superficie):
    # Reset
    pygame.draw.rect(superficie, (200, 50, 50), rect_boton_reset)
    texto = font_ui.render("Reiniciar", True, (255, 255, 255))
    superficie.blit(texto, (rect_boton_reset.x + 60, rect_boton_reset.y + 10))
    
    # Menu
    pygame.draw.rect(superficie, (50, 50, 200), rect_boton_menu)
    texto_menu = font_ui.render("Menu", True, (255, 255, 255))
    superficie.blit(texto_menu, (rect_boton_menu.x + 70, rect_boton_menu.y + 10))

    # --- HISTORIAL DE EVENTOS ---
    y_pos = 10
    for evento in historial_eventos:
        texto_evento = font_ui.render(evento, True, (255, 255, 255))
        superficie.blit(texto_evento, (10, y_pos))
        y_pos += 25
        
    # --- ESTADISTICAS (Top Right) ---
    # Calcular conteos
    humanos = [p for p in poblacion if isinstance(p, Persona) and p.vivo]
    zorros = [p for p in poblacion if isinstance(p, Zorro) and p.vivo]
    conejos = [p for p in poblacion if isinstance(p, Conejo) and p.vivo]
    
    h_casa = len([p for p in humanos if p.in_home])
    z_casa = len([p for p in zorros if p.in_home])
    c_casa = len([p for p in conejos if p.in_home])
    
    stats = [
        f"Humanos: {len(humanos)} (Casa: {h_casa})",
        f"Zorros: {len(zorros)} (Cueva: {z_casa})",
        f"Conejos: {len(conejos)} (Madriguera: {c_casa})"
    ]
    
    y_stats = 10
    for linea in stats:
        texto_stat = font_ui.render(linea, True, (200, 200, 255))
        rect_stat = texto_stat.get_rect(topright=(mundo.ANCHO - 10, y_stats))
        superficie.blit(texto_stat, rect_stat)
        y_stats += 25

# --- HISTORIAL ---
historial_eventos = []
def agregar_evento(texto):
    historial_eventos.append(texto)
    if len(historial_eventos) > 5:
        historial_eventos.pop(0)

# Bucle principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            quit()
            
        if ESTADO == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_boton_inicio.collidepoint(evento.pos):
                    poblacion = crear_poblacion_inicial()
                    resetear_comida()
                    ESTADO = "SIMULACION"
                    
        elif ESTADO == "SIMULACION":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_boton_reset.collidepoint(evento.pos):
                    reiniciar_simulacion()
                if rect_boton_menu.collidepoint(evento.pos):
                    ESTADO = "MENU"

    if ESTADO == "MENU":
        dibujar_menu(mundo.PANTALLA)
        pygame.display.update()
        mundo.RELOJ.tick(60)
        
    elif ESTADO == "SIMULACION":
        # Actualizar Mundo (listas globales si cambian)
        mundo.personas = [p for p in poblacion if isinstance(p, Persona) and p.vivo]
        
        # Logica
        alguien_vivo = False
        for p in poblacion:
            if p.vivo:
                alguien_vivo = True
                # Pensar: Pasar comidas (objetos) y poblacion (otros agentes)
                # Nota: comidas es un Group, pensar espera Group o lista.
                # poblacion tiene a todos.
                p.pensar(comidas, poblacion)
                
                # Colisiones Comida
                lista_colisiones = pygame.sprite.spritecollide(p, comidas, True)
                for comida in lista_colisiones:
                    p.alimentarse(comida.valor)
                    # Respawnear comida
                    nueva_comida = Comida(random.randint(0, mundo.ANCHO), random.randint(0, mundo.ALTO), mundo=mundo)
                    comidas.add(nueva_comida)
                    mundo.alimentos.append(nueva_comida)
                
                p.actualizar() # Mover, envejecer, animar
                
                # --- EVENTOS DE ESTADO (Muerte / Sueño) ---
                nombre_p = getattr(p, 'nombre', type(p).__name__)
                
                if not p.vivo and not p.evento_muerte_reportado:
                    agregar_evento(f"{nombre_p} Murio")
                    p.evento_muerte_reportado = True
                    
                if p.dormido and not p.evento_dormir_reportado:
                    agregar_evento(f"{nombre_p} esta durmiendo")
                    p.evento_dormir_reportado = True
                elif not p.dormido:
                    p.evento_dormir_reportado = False
                    
                # if getattr(p, 'peligro', False) and not getattr(p, 'evento_peligro_reportado', False):
                #     agregar_evento(f"{nombre_p} se siente en peligro") # REMOVED LOG
                #     p.evento_peligro_reportado = True
                # elif not getattr(p, 'peligro', False):
                #     p.evento_peligro_reportado = False

                # --- COMBATE & INTERACCION ---
                colisiones_otros = pygame.sprite.spritecollide(p, [o for o in poblacion if o is not p and o.vivo and not o.in_home], False)
                for otro in colisiones_otros:
                    # Logica de ataque simple: Si es enemigo, ataca
                    es_enemigo = False
                    # Zorro ataca humanos y conejos
                    if isinstance(p, Zorro) and isinstance(otro, (Conejo, Persona)):
                        es_enemigo = True
                    # Humano ataca Zorro y Conejo
                    elif isinstance(p, Persona) and isinstance(otro, (Zorro, Conejo)):
                        es_enemigo = True
                    
                    if es_enemigo:
                        p.atacar(otro)
                        if not otro.vivo:
                            nombre_otro = getattr(otro, 'nombre', type(otro).__name__)
                            # EVENTO CAZA
                            agregar_evento(f"{nombre_p} Cazo un {nombre_otro}")
                            
                            # LOOT
                            if isinstance(p, Persona): # Solo humanos recogen inventario
                                p.guardar_item(otro) # Guardar referencia del muerto
                                # mensaje = f"{p.nombre if hasattr(p,'nombre') else 'Alguien'} recogio un {type(otro).__name__}"
                                # agregar_evento(mensaje)
                                # print(mensaje)

                # --- HOGAR (Almacenar / Comer / Dormir) ---
                hogares = mundo.casas + mundo.madrigueras + mundo.cuevas
                # Manual collision check
                possible_homes = [h for h in hogares if hasattr(h, 'rect') and p.rect.colliderect(h.rect)]
                
                for h in possible_homes:
                    # Entrar a dormir (si tiene sueño) O REFUGIO (Conejo en peligro)
                    entrar = False
                    if p.sueño > 70:
                        entrar = True
                    elif isinstance(p, Conejo) and getattr(p, 'peligro', False) and h in mundo.madrigueras:
                        entrar = True
                    
                    if entrar:
                        was_in_home = p.in_home
                        p.entrar_casa()
                        if not was_in_home and p.in_home:
                            pass
                            # Log especifico
                            # if isinstance(p, Conejo) and h in mundo.madrigueras:
                            #    agregar_evento(f"{nombre_p} entro a la madriguera")
                        
                    # Gestion de Inventario (Solo Casas y Humanos)
                    # "Haz que los humanos solo puedan comer y guardar ... si van hasta la casa"
                    if isinstance(p, Persona) and h in mundo.casas:
                        # A. Guardar items
                        items_a_remover = []
                        for item in p.inventario:
                            # Guardar todo lo que sea comida (Conejos/Zorros muertos)
                            h.guardar(item)
                            items_a_remover.append(item)
                            agregar_evento(f"{p.nombre} guardo comida en casa.")
                        
                        for i in items_a_remover:
                            p.inventario.remove(i)
                            
                        # B. Comer del almacen si hambre
                        if p.hambre > 20 and h.almacen:
                            comida_guardada = h.consumir()
                            if comida_guardada:
                                p.alimentarse(50) # Valor arbitrario o basado en item
                                agregar_evento(f"{p.nombre} comio del almacen.")

        # Dibujar
        mundo.mostrar() # Fondo
        
        # Dibujar casas y cuevas
        for c in mundo.casas: c.mostrar()
        for c in mundo.madrigueras: c.mostrar()
        for c in mundo.cuevas: c.mostrar()
        
        for comida in comidas:
            comida.mostrar()
            
        for p in poblacion:
            if p.vivo and not p.in_home:
                p.mostrar()
        
        dibujar_ui_simulacion(mundo.PANTALLA)
        
        pygame.display.update()
        mundo.RELOJ.tick(60)
