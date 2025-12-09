'''
Punto de entrada, inicia el mundo y agrega personas
'''
import pygame
from mundo import Mundo
from persona import Persona
from recursos import Comida
import random
import pickle
import os

#Inica el mundo y el personaje
pygame.init()
mundo = Mundo(pygame.image.load("images/Pista.png"))

# Configuración Evolución
# Configuración Evolución
TAMANO_POBLACION = 10
poblacion = []
imagen_persona = pygame.image.load("images/LIDER.png").convert_alpha()
ARCHIVO_POBLACION = "poblacion.pkl"

def guardar_progreso(gen, pob):
    datos = {
        "generacion": gen,
        "cerebros": [p.cerebro for p in pob]
    }
    with open(ARCHIVO_POBLACION, "wb") as f:
        pickle.dump(datos, f)
    print(f"Progreso guardado: Generación {gen}")

def cargar_progreso():
    if not os.path.exists(ARCHIVO_POBLACION):
        return None
    try:
        with open(ARCHIVO_POBLACION, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error cargando archivo: {e}")
        return None

def crear_poblacion():
    datos = cargar_progreso()
    pob = []
    gen_inicio = 1
    
    if datos:
        print(f"Cargando partida guardada. Generación: {datos['generacion']}")
        gen_inicio = datos['generacion']
        cerebros = datos['cerebros']
        # Ajustar si el tamaño de poblacion cambio, o tomar los que hay
        for c in cerebros:
            p = Persona(imagen_persona, mundo, cerebro=c)
            pob.append(p)
        
        # Rrellenar si falta (si cambiamos TAMANO_POBLACION)
        while len(pob) < TAMANO_POBLACION:
            p = Persona(imagen_persona, mundo)
            pob.append(p)
        # Recortar si sobran
        pob = pob[:TAMANO_POBLACION]
    else:
        print("Iniciando nueva partida.")
        for _ in range(TAMANO_POBLACION):
            p = Persona(imagen_persona, mundo)
            pob.append(p)
            
    return pob, gen_inicio

poblacion, generacion = crear_poblacion()

comidas = pygame.sprite.Group()
def resetear_comida():
    comidas.empty()
    for _ in range(10): # Mas comida para 20 agentes
        x = random.randint(0, mundo.ANCHO)
        y = random.randint(0, mundo.ALTO)
        comida = Comida(x, y, mundo=mundo)
        comidas.add(comida)

resetear_comida()


font_ui = pygame.font.SysFont(None, 30)

def nueva_generacion(poblacion_actual):
    global generacion
    print(f"--- Generación {generacion} Finalizada ---")
    
    # Calcular Fitness: Comida * 50 + Tiempo vivo
    # Esto le da MUCHA prioridad a la comida.
    for p in poblacion_actual:
        p.fitness = (p.comidas_comidas * 50) + p.tiempo_vivo

    # Ordenar por Fitness
    poblacion_actual.sort(key=lambda p: p.fitness, reverse=True)
    
    # Filtrar solo los que han comido
    comedores = [p for p in poblacion_actual if p.comidas_comidas > 0]
    
    padres = []
    
    if not comedores:
        print("¡Nadie comió! Seleccionando a los más cercanos (Fitness Shaping).")
        # Si nadie comió, usamos la distancia mínima para seleccionar a los "menos peores"
        # Ordenar por min_dist_food ascendente (menor es mejor)
        poblacion_actual.sort(key=lambda p: p.min_dist_food)
        padres = poblacion_actual[:5] # Top 5 más cercanos
    else:
        # Si hay comedores, ellos son la elite.
        # Ordenar por score compuesto: muchas comidas > pocas comidas > tiempo vivo
        comedores.sort(key=lambda p: (p.comidas_comidas * 1000) + p.tiempo_vivo, reverse=True)
        padres = comedores

    nueva_pob = []
    
    # 1. Elitismo (Los mejores 5 padres pasan intactos)
    for i in range(5):
        if i < len(padres):
            elite = Persona(imagen_persona, mundo, cerebro=padres[i].cerebro)
            nueva_pob.append(elite)
            
    # 2. Descendencia (Mezclas de los padres seleccionados)
    while len(nueva_pob) < TAMANO_POBLACION:
        # Padres elegidos al azar del pool de padres
        padre1 = random.choice(padres)
        padre2 = random.choice(padres)
        
        cerebro_hijo = padre1.cerebro.cruzar(padre2.cerebro)
        cerebro_hijo.mutar(0.05)
        
        hijo = Persona(imagen_persona, mundo, cerebro=cerebro_hijo)
        nueva_pob.append(hijo)
        
    generacion += 1
    guardar_progreso(generacion, nueva_pob)
    resetear_comida()
    return nueva_pob

def dibujar_estadisticas(superficie, poblacion):
    # Crear superficie semitransparente para el panel
    panel = pygame.Surface((220, mundo.ALTO))
    panel.set_alpha(150) # Transparencia
    panel.fill((0, 0, 0)) # Negro
    
    superficie.blit(panel, (mundo.ANCHO - 220, 0))
    
    y = 10
    titulo = font_ui.render("Energía Agentes", True, (255, 255, 255))
    superficie.blit(titulo, (mundo.ANCHO - 210, y))
    y += 30
    
    for i, p in enumerate(poblacion):
        # Color basado en estado
        color = (0, 255, 0) if p.vivo else (100, 100, 100)
        
        # Etiqueta
        texto = font_ui.render(f"#{i+1}", True, (255, 255, 255))
        superficie.blit(texto, (mundo.ANCHO - 210, y))
        
        # Barra de energia
        ancho_barra = int(p.energia)
        rect_barra = pygame.Rect(mundo.ANCHO - 160, y + 5, ancho_barra, 10)
        pygame.draw.rect(superficie, color, rect_barra)
        
        y += 20


def reiniciar_simulacion():
    global poblacion, generacion
    if os.path.exists(ARCHIVO_POBLACION):
        os.remove(ARCHIVO_POBLACION)
        print("Archivo de población eliminado.")
    
    generacion = 1
    poblacion, _ = crear_poblacion() # Esto recargará (o creará nueva si no hay archivo)
    # Como acabamos de borrar el archivo, crear_poblacion iniciara de 0
    resetear_comida()
    print("Simulación reiniciada.")

# Boton Reset
rect_boton_reset = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 60, 200, 40)
def dibujar_ui_reset(superficie):
    pygame.draw.rect(superficie, (200, 50, 50), rect_boton_reset)
    texto = font_ui.render("Reiniciar Todo", True, (255, 255, 255))
    superficie.blit(texto, (rect_boton_reset.x + 20, rect_boton_reset.y + 10))

#Bucle principal
while True:
    # 1. Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            quit()
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if rect_boton_reset.collidepoint(evento.pos):
                reiniciar_simulacion()
    
    # 2. Actualizar logica
    
    # Verificar si hay alguien vivo
    alguien_vivo = False
    for p in poblacion:
        if p.vivo:
            alguien_vivo = True
            p.pensar(comidas, poblacion) # IA decide
            
            # Comprobar colisiones con comida
            lista_colisiones = pygame.sprite.spritecollide(p, comidas, True)
            for comida in lista_colisiones:
                p.alimentarse(comida.valor)
                # Respawn inmediato de comida
                x = random.randint(0, mundo.ANCHO)
                y = random.randint(0, mundo.ALTO)
                nueva_comida = Comida(x, y, mundo=mundo)
                comidas.add(nueva_comida)
            
            p.actualizar()
    
    if not alguien_vivo:
        poblacion = nueva_generacion(poblacion)
        continue # Saltar renderizado de frame muerto
    
    # 3. Dibujar
    mundo.mostrar()
    
    for comida in comidas:
        comida.mostrar()
        
    personas_vivas = 0
    for p in poblacion:
        if p.vivo:
            personas_vivas += 1
            p.mostrar()
            # Opcional: mostrar estado de todos satura la pantalla, quizas solo del mejor o ninguno
            # p.mostrar_estado() 
    
    # UI
    dibujar_estadisticas(mundo.PANTALLA, poblacion)
    dibujar_ui_reset(mundo.PANTALLA)
    texto_gen = font_ui.render(f"Gen: {generacion} | Vivos: {personas_vivas}", True, (255, 255, 255))
    mundo.PANTALLA.blit(texto_gen, (10, 10))
    
    # 4. Actualizar pantalla
    pygame.display.update()
    # Acelerar un poco para entrenar mas rapido si se desea (o quitar el limitador FPS)
    # mundo.RELOJ.tick(mundo.FPS) 
    mundo.RELOJ.tick(1000) # Sin limite practico para simular rapido

