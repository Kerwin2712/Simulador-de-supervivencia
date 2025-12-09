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
TAMANO_POBLACION = 5 # Valor por defecto inicial
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
#Crear comida 
def resetear_comida():
    comidas.empty()
    for _ in range(20): # Mas comida para 20 agentes
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

# Botones Velocidad
velocidad_simulacion = 120 # FPS Inicial
rect_boton_menos = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 110, 40, 40)
rect_boton_mas = pygame.Rect(mundo.ANCHO - 50, mundo.ALTO - 110, 40, 40)

# Boton Menu
rect_boton_menu = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 160, 200, 40)

def dibujar_ui_reset(superficie):
    # Reset
    pygame.draw.rect(superficie, (200, 50, 50), rect_boton_reset)
    texto = font_ui.render("Reiniciar Todo", True, (255, 255, 255))
    superficie.blit(texto, (rect_boton_reset.x + 20, rect_boton_reset.y + 10))
    
    # Velocidad
    # Boton -
    pygame.draw.rect(superficie, (100, 100, 100), rect_boton_menos)
    texto_menos = font_ui.render("-", True, (255, 255, 255))
    superficie.blit(texto_menos, (rect_boton_menos.x + 15, rect_boton_menos.y + 10))
    
    # Texto Velocidad
    texto_vel = font_ui.render(f"Vel: {velocidad_simulacion}", True, (255, 255, 255))
    superficie.blit(texto_vel, (mundo.ANCHO - 160, mundo.ALTO - 100))
    
    # Boton +
    pygame.draw.rect(superficie, (100, 100, 100), rect_boton_mas)
    texto_mas = font_ui.render("+", True, (255, 255, 255))
    superficie.blit(texto_mas, (rect_boton_mas.x + 12, rect_boton_mas.y + 10))

    # Boton Menu
    pygame.draw.rect(superficie, (50, 50, 200), rect_boton_menu)
    texto_menu = font_ui.render("Volver al Menú", True, (255, 255, 255))
    superficie.blit(texto_menu, (rect_boton_menu.x + 20, rect_boton_menu.y + 10))

# --- MENU DE INICIO ---
ESTADO = "MENU" # MENU o SIMULACION
input_texto = "20"
color_input_activo = (255, 255, 255)
color_input_inactivo = (150, 150, 150)
color_input = color_input_inactivo
activo = False

rect_input = pygame.Rect(mundo.ANCHO // 2 - 100, mundo.ALTO // 2 - 20, 200, 40)
rect_boton_inicio = pygame.Rect(mundo.ANCHO // 2 - 100, mundo.ALTO // 2 + 50, 200, 40)

def dibujar_menu(superficie):
    superficie.fill((30, 30, 30)) # Fondo oscuro
    
    # Titulo
    texto_titulo = font_ui.render("SIMULADOR DE SUPERVIVENCIA", True, (200, 200, 255))
    rect_titulo = texto_titulo.get_rect(center=(mundo.ANCHO//2, mundo.ALTO//2 - 100))
    superficie.blit(texto_titulo, rect_titulo)
    
    # Label
    texto_label = font_ui.render("Cantidad de Agentes:", True, (255, 255, 255))
    rect_label = texto_label.get_rect(center=(mundo.ANCHO//2, mundo.ALTO//2 - 50))
    superficie.blit(texto_label, rect_label)
    
    # Input Box
    pygame.draw.rect(superficie, color_input, rect_input, 2)
    texto_sup = font_ui.render(input_texto, True, (255, 255, 255))
    superficie.blit(texto_sup, (rect_input.x + 5, rect_input.y + 10))
    rect_input.w = max(200, texto_sup.get_width() + 10)
    
    # Boton Iniciar
    pygame.draw.rect(superficie, (50, 200, 50), rect_boton_inicio)
    texto_boton = font_ui.render("INICIAR", True, (20, 20, 20))
    rect_texto_boton = texto_boton.get_rect(center=rect_boton_inicio.center)
    superficie.blit(texto_boton, rect_texto_boton)

#Bucle principal
while True:
    # 1. Eventos
    eventos = pygame.event.get()
    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            quit()
            
        if ESTADO == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_input.collidepoint(evento.pos):
                    activo = not activo
                else:
                    activo = False
                color_input = color_input_activo if activo else color_input_inactivo
                
                if rect_boton_inicio.collidepoint(evento.pos):
                    # INICIAR SIMULACION
                    try:
                        nueva_poblacion_n = int(input_texto)
                        TAMANO_POBLACION = max(1, nueva_poblacion_n) # Minimo 1
                    except ValueError:
                        TAMANO_POBLACION = 5 # Default si hay error
                    
                    poblacion, generacion = crear_poblacion()
                    resetear_comida()
                    ESTADO = "SIMULACION"
                    
            if evento.type == pygame.KEYDOWN:
                if activo:
                    if evento.key == pygame.K_RETURN:
                        # Enter tambien inicia
                        try:
                            nueva_poblacion_n = int(input_texto)
                            TAMANO_POBLACION = max(1, nueva_poblacion_n)
                        except ValueError:
                            TAMANO_POBLACION = 5
                        
                        poblacion, generacion = crear_poblacion()
                        resetear_comida()
                        ESTADO = "SIMULACION"
                        
                    elif evento.key == pygame.K_BACKSPACE:
                        input_texto = input_texto[:-1]
                    else:
                        if evento.unicode.isdigit(): # Solo numeros
                            input_texto += evento.unicode
                            
        elif ESTADO == "SIMULACION":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_boton_reset.collidepoint(evento.pos):
                    reiniciar_simulacion()
                
                # Control Velocidad
                if rect_boton_menos.collidepoint(evento.pos):
                    velocidad_simulacion = max(10, velocidad_simulacion - 100)
                if rect_boton_mas.collidepoint(evento.pos):
                    velocidad_simulacion += 100

                # Volver al Menu
                if rect_boton_menu.collidepoint(evento.pos):
                    ESTADO = "MENU"

    # 2. Actualizar y Dibujar segun Estado
    if ESTADO == "MENU":
        dibujar_menu(mundo.PANTALLA)
        pygame.display.update()
        mundo.RELOJ.tick(60)
        
    elif ESTADO == "SIMULACION":
        # Logica de simulacion original
    
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
            # continue # Saltar renderizado de frame muerto <- No podemos usar continue aqui facilmente porque estamos dentro de un if/elif gigante dentro del while.
            # En lugar de continue, simplemente no dibujamos o hacemos un pass.
            # Pero si nueva_generacion retorna poblacion llena, podemos seguir.
            # El continue original saltaba al inicio del while True.
            # Ahora saltaria al final del if/elif... que es el fin del loop.
            # Asi que esta bien? 
            # Revisitamos la logica original:
            # if not alguien_vivo:
            #    poblacion = nueva_generacion(poblacion)
            #    continue
            # El continue saltaba el "3. Dibujar" y "4. Actualizar pantalla"
            # Si lo dejo, saltará al inicio del while... lo cual es correcto para reiniciar el ciclo.
            # PERO, debo asegurarme de que el continue este identado correctamente.
            pass 
        else:
            # Solo dibujamos si hay gente viva (o si acabamos de generar nueva, tal vez deberiamos dibujar?)
            # En el original, si no habia vivo, generaba y hacia continue -> no dibujaba ese frame.
            # Si pongo 'pass' aqui, dibujará el frame con la nueva generación inmediatamente sin esperar un tick extra?
            # El continue es mas seguro para replicar comportamiento.
            pass

        # Si volvio alguien vivo o se regenero...
        # Espera, si hago nueva_generacion, YA hay gente viva (la nueva).
        # El continue original era para no dibujar el estado "muerto" antes de reiniciar?
        # O para que se procese logica de nuevo antes de dibujar?
        # Simplemente mantendre el flujo: Si generamos nueva, ya, seguimos.
    
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
        # dibujar_estadisticas(mundo.PANTALLA, poblacion) # Sidebar removida
        dibujar_ui_reset(mundo.PANTALLA)
        texto_gen = font_ui.render(f"Gen: {generacion} | Vivos: {personas_vivas}", True, (255, 255, 255))
        mundo.PANTALLA.blit(texto_gen, (10, 10))
        
        # 4. Actualizar pantalla
        pygame.display.update()
        # Acelerar un poco para entrenar mas rapido si se desea (o quitar el limitador FPS)
        # mundo.RELOJ.tick(mundo.FPS) 
        mundo.RELOJ.tick(velocidad_simulacion) # Velocidad variable

