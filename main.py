'''
Punto de entrada, inicia el mundo y agrega personas
'''
import pygame
from space.mundo import Mundo
from agents.humanos.persona import Persona, Hombre, Mujer, Kid, Girl, Baby_boy, Baby_girl, Kerwin
from agents.animales.animal import Zorro, Conejo
from elements.hogar import Hogar
from elements.recursos import Comida
import random
import pickle
import os

#Inica el mundo y el personaje
pygame.init()
mundo = Mundo()

# Configuración Inicial
poblacion = []
kerwin = None
entidad_seleccionada = None
menu_interaccion_rect = None
opciones_menu = []



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
    global kerwin
    kerwin = Kerwin("Kerwin", mundo)
    pob.append(kerwin)
    
    hombre = Hombre("Adan", mundo)
    mujer = Mujer("Eva", mundo)
    pob.extend([hombre, mujer])

    for _ in range(2):
        pob.append(Zorro(mundo))
        
    for _ in range(20):
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

font_ui = pygame.font.SysFont(None, 20)

# --- MENU DE INICIO ---
rect_boton_inicio = pygame.Rect(mundo.ANCHO // 2 - 100, mundo.ALTO // 2 - 20, 200, 40)
rect_boton_editor = pygame.Rect(mundo.ANCHO // 2 - 100, mundo.ALTO // 2 + 40, 200, 40)
ESTADO = "MENU"

def dibujar_menu(superficie):
    superficie.fill((30, 30, 30))
    
    texto_titulo = font_ui.render("SIMULADOR DE SUPERVIVENCIA", True, (200, 200, 255))
    rect_titulo = texto_titulo.get_rect(center=(mundo.ANCHO//2, mundo.ALTO//2 - 80))
    superficie.blit(texto_titulo, rect_titulo)
    
    # Boton Iniciar
    pygame.draw.rect(superficie, (50, 200, 50), rect_boton_inicio)
    texto_boton = font_ui.render("SIMULACION ALEATORIA", True, (20, 20, 20))
    rect_texto_boton = texto_boton.get_rect(center=rect_boton_inicio.center)
    superficie.blit(texto_boton, rect_texto_boton)

    # Boton Editor
    pygame.draw.rect(superficie, (200, 150, 50), rect_boton_editor)
    texto_boton_ed = font_ui.render("EDITOR DE ESCENARIOS", True, (20, 20, 20))
    rect_texto_boton_ed = texto_boton_ed.get_rect(center=rect_boton_editor.center)
    superficie.blit(texto_boton_ed, rect_texto_boton_ed)

def reiniciar_simulacion():
    global poblacion
    poblacion = crear_poblacion_inicial()
    resetear_comida()
    print("Simulación reiniciada.")

# Boton Reset
rect_boton_reset = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 60, 200, 40)

# Botones Velocidad
velocidad_simulacion = 120 # FPS Inicial
rect_boton_menos = pygame.Rect(mundo.ANCHO - 210, mundo.ALTO - 170, 40, 40)
rect_boton_mas = pygame.Rect(mundo.ANCHO - 50, mundo.ALTO - 170, 40, 40)

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

    # Velocity
    pygame.draw.rect(superficie, (0, 0, 0), rect_boton_menos)
    texto_menu = font_ui.render("-", True, (255, 255, 255))
    superficie.blit(texto_menu, (rect_boton_menos.x + 70, rect_boton_menos.y + 10))
    pygame.draw.rect(superficie, (0, 0, 0), rect_boton_mas)
    texto_menu = font_ui.render("+", True, (255, 255, 255))
    superficie.blit(texto_menu, (rect_boton_mas.x + 70, rect_boton_mas.y + 10))


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

# --- VARIABLES DEL EDITOR ---
herramientas_ed = ["Kerwin", "Hombre", "Mujer", "Zorro", "Conejo", "Casa", "Madriguera", "Cueva", "Comida"]
herramienta_seleccionada = None

rects_herramientas = []
btn_w, btn_h = 100, 30
for i, h in enumerate(herramientas_ed):
    r = pygame.Rect(10, 10 + i*(btn_h+5), btn_w, btn_h)
    rects_herramientas.append((r, h))

rect_btn_ed_iniciar = pygame.Rect(mundo.ANCHO - 150, 10, 140, 40)
rect_btn_ed_limpiar = pygame.Rect(mundo.ANCHO - 150, 60, 140, 40)
rect_btn_ed_menu = pygame.Rect(mundo.ANCHO - 150, 110, 140, 40)
rect_btn_ed_guardar = pygame.Rect(mundo.ANCHO - 150, 160, 140, 40)
rect_btn_ed_cargar = pygame.Rect(mundo.ANCHO - 150, 210, 140, 40)

def guardar_escenario(ruta="escenario.json"):
    import json
    data = {"poblacion": [], "casas": [], "madrigueras": [], "cuevas": [], "comidas": []}
    
    for p in poblacion:
        tipo = type(p).__name__
        p_data = {"tipo": tipo, "x": getattr(p, 'x', p.rect.x), "y": getattr(p, 'y', p.rect.y)}
        if hasattr(p, 'cerebro_decision') and p.cerebro_decision:
            p_data["cerebro_decision"] = p.cerebro_decision.to_dict()
        data["poblacion"].append(p_data)
        
    for c in mundo.casas: data["casas"].append({"x": c.rect.x, "y": c.rect.y})
    for m in mundo.madrigueras: data["madrigueras"].append({"x": m.rect.x, "y": m.rect.y})
    for c in mundo.cuevas: data["cuevas"].append({"x": c.rect.x, "y": c.rect.y})
    for c in comidas: data["comidas"].append({"x": c.rect.x, "y": c.rect.y})
        
    with open(ruta, "w") as f:
        json.dump(data, f)
    print("Escenario guardado")

def cargar_escenario(ruta="escenario.json"):
    import json, os
    if not os.path.exists(ruta): return
        
    with open(ruta, "r") as f:
        data = json.load(f)
        
    global poblacion, kerwin
    poblacion.clear()
    mundo.casas.clear()
    mundo.madrigueras.clear()
    mundo.cuevas.clear()
    comidas.empty()
    mundo.alimentos.clear()
    kerwin = None
    
    for p_data in data.get("poblacion", []):
        tipo = p_data["tipo"]
        x, y = p_data["x"], p_data["y"]
        if tipo == "Kerwin":
            kerwin = Kerwin("Kerwin", mundo)
            kerwin.x, kerwin.y = x, y
            kerwin.rect.topleft = (x, y)
            poblacion.append(kerwin)
        elif tipo == "Hombre":
            h = Hombre(f"Hombre_{random.randint(1,100)}", mundo)
            h.x, h.y = x, y
            h.rect.topleft = (x, y)
            if "cerebro_decision" in p_data:
                from agents.cerebro import Cerebro
                h.cerebro_decision = Cerebro.from_dict(p_data["cerebro_decision"])
            poblacion.append(h)
        elif tipo == "Mujer":
            h = Mujer(f"Mujer_{random.randint(1,100)}", mundo)
            h.x, h.y = x, y
            h.rect.topleft = (x, y)
            if "cerebro_decision" in p_data:
                from agents.cerebro import Cerebro
                h.cerebro_decision = Cerebro.from_dict(p_data["cerebro_decision"])
            poblacion.append(h)
        elif tipo == "Zorro":
            z = Zorro(mundo)
            z.x, z.y = x, y
            z.rect.topleft = (x, y)
            if "cerebro_decision" in p_data:
                from agents.cerebro import Cerebro
                z.cerebro_decision = Cerebro.from_dict(p_data["cerebro_decision"])
            poblacion.append(z)
        elif tipo == "Conejo":
            c = Conejo(mundo)
            c.x, c.y = x, y
            c.rect.topleft = (x, y)
            if "cerebro_decision" in p_data:
                from agents.cerebro import Cerebro
                c.cerebro_decision = Cerebro.from_dict(p_data["cerebro_decision"])
            poblacion.append(c)
            
    for c_data in data.get("casas", []): mundo.casas.append(Hogar(mundo, c_data["x"], c_data["y"], "casa"))
    for m_data in data.get("madrigueras", []): mundo.madrigueras.append(Hogar(mundo, m_data["x"], m_data["y"], "madriguera"))
    for c_data in data.get("cuevas", []): mundo.cuevas.append(Hogar(mundo, c_data["x"], c_data["y"], "cueva"))
    for c_data in data.get("comidas", []):
        comida = Comida(c_data["x"], c_data["y"], mundo=mundo)
        comidas.add(comida)
        mundo.alimentos.append(comida)
    print("Escenario cargado")

def dibujar_editor(superficie):
    superficie.fill((40, 60, 40)) # Fondo verde oscuro para diferenciar
    
    # Dibujar entidades colocadas
    for c in mundo.casas: c.mostrar()
    for c in mundo.madrigueras: c.mostrar()
    for c in mundo.cuevas: c.mostrar()
    for comida in comidas: comida.mostrar()
    for p in poblacion: p.mostrar()

    # UI Tools
    pygame.draw.rect(superficie, (50, 50, 50), (0, 0, 120, mundo.ALTO))
    for r, h in rects_herramientas:
        color = (100, 200, 100) if herramienta_seleccionada == h else (100, 100, 100)
        pygame.draw.rect(superficie, color, r)
        txt = font_ui.render(h, True, (0,0,0))
        superficie.blit(txt, (r.x + 5, r.y + 5))
        
    # UI Buttons
    pygame.draw.rect(superficie, (50, 200, 50), rect_btn_ed_iniciar)
    superficie.blit(font_ui.render("INICIAR", True, (0,0,0)), (rect_btn_ed_iniciar.x + 10, rect_btn_ed_iniciar.y + 10))
    
    pygame.draw.rect(superficie, (200, 50, 50), rect_btn_ed_limpiar)
    superficie.blit(font_ui.render("LIMPIAR", True, (0,0,0)), (rect_btn_ed_limpiar.x + 10, rect_btn_ed_limpiar.y + 10))
    
    pygame.draw.rect(superficie, (50, 50, 200), rect_btn_ed_menu)
    superficie.blit(font_ui.render("MENU", True, (255,255,255)), (rect_btn_ed_menu.x + 10, rect_btn_ed_menu.y + 10))

    pygame.draw.rect(superficie, (200, 150, 50), rect_btn_ed_guardar)
    superficie.blit(font_ui.render("GUARDAR", True, (0,0,0)), (rect_btn_ed_guardar.x + 10, rect_btn_ed_guardar.y + 10))
    
    pygame.draw.rect(superficie, (50, 150, 200), rect_btn_ed_cargar)
    superficie.blit(font_ui.render("CARGAR", True, (0,0,0)), (rect_btn_ed_cargar.x + 10, rect_btn_ed_cargar.y + 10))

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
                elif rect_boton_editor.collidepoint(evento.pos):
                    poblacion = []
                    mundo.casas = []
                    mundo.madrigueras = []
                    mundo.cuevas = []
                    mundo.personas = []
                    comidas.empty()
                    ESTADO = "EDITOR"
                    herramienta_seleccionada = None
                    
        elif ESTADO == "EDITOR":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Click izquierdo (Colocar)
                    if rect_btn_ed_iniciar.collidepoint(evento.pos):
                        mundo.personas = [p for p in poblacion if isinstance(p, Persona)]
                        ESTADO = "SIMULACION"
                    elif rect_btn_ed_limpiar.collidepoint(evento.pos):
                        poblacion.clear()
                        mundo.casas.clear()
                        mundo.madrigueras.clear()
                        mundo.cuevas.clear()
                        comidas.empty()
                    elif rect_btn_ed_menu.collidepoint(evento.pos):
                        ESTADO = "MENU"
                    elif rect_btn_ed_guardar.collidepoint(evento.pos):
                        guardar_escenario()
                    elif rect_btn_ed_cargar.collidepoint(evento.pos):
                        cargar_escenario()
                    else:
                        tool_clicked = False
                        for r, h in rects_herramientas:
                            if r.collidepoint(evento.pos):
                                herramienta_seleccionada = h
                                tool_clicked = True
                                break
                        
                        if not tool_clicked and herramienta_seleccionada:
                            if evento.pos[0] > 120:
                                ex, ey = evento.pos
                                if herramienta_seleccionada == "Kerwin":
                                    if kerwin and kerwin in poblacion:
                                        poblacion.remove(kerwin)
                                    kerwin = Kerwin("Kerwin", mundo)
                                    kerwin.x, kerwin.y = ex, ey
                                    kerwin.rect.topleft = (ex, ey)
                                    poblacion.append(kerwin)
                                elif herramienta_seleccionada == "Hombre":
                                    h_obj = Hombre(f"Hombre_{random.randint(1,100)}", mundo)
                                    h_obj.x, h_obj.y = ex, ey
                                    h_obj.rect.topleft = (ex, ey)
                                    poblacion.append(h_obj)
                                elif herramienta_seleccionada == "Mujer":
                                    h_obj = Mujer(f"Mujer_{random.randint(1,100)}", mundo)
                                    h_obj.x, h_obj.y = ex, ey
                                    h_obj.rect.topleft = (ex, ey)
                                    poblacion.append(h_obj)
                                elif herramienta_seleccionada == "Zorro":
                                    h_obj = Zorro(mundo)
                                    h_obj.x, h_obj.y = ex, ey
                                    h_obj.rect.topleft = (ex, ey)
                                    poblacion.append(h_obj)
                                elif herramienta_seleccionada == "Conejo":
                                    h_obj = Conejo(mundo)
                                    h_obj.x, h_obj.y = ex, ey
                                    h_obj.rect.topleft = (ex, ey)
                                    poblacion.append(h_obj)
                                elif herramienta_seleccionada == "Casa":
                                    mundo.casas.append(Hogar(mundo, ex, ey, "casa"))
                                elif herramienta_seleccionada == "Madriguera":
                                    mundo.madrigueras.append(Hogar(mundo, ex, ey, "madriguera"))
                                elif herramienta_seleccionada == "Cueva":
                                    mundo.cuevas.append(Hogar(mundo, ex, ey, "cueva"))
                                elif herramienta_seleccionada == "Comida":
                                    nueva_comida = Comida(ex, ey, mundo=mundo)
                                    comidas.add(nueva_comida)
                                    mundo.alimentos.append(nueva_comida)
                                    
                elif evento.button == 3: # Click derecho (Borrar)
                    if evento.pos[0] > 120:
                        ex, ey = evento.pos
                        for p in poblacion[:]:
                            if hasattr(p, 'rect') and p.rect.collidepoint(ex, ey):
                                poblacion.remove(p)
                                break
                        for c in comidas:
                            if hasattr(c, 'rect') and c.rect.collidepoint(ex, ey):
                                c.kill()
                                break
                        for c in mundo.casas[:]:
                            if c.rect.collidepoint(ex, ey): mundo.casas.remove(c)
                        for c in mundo.madrigueras[:]:
                            if c.rect.collidepoint(ex, ey): mundo.madrigueras.remove(c)
                        for c in mundo.cuevas[:]:
                            if c.rect.collidepoint(ex, ey): mundo.cuevas.remove(c)
                    
        elif ESTADO == "SIMULACION":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_boton_reset.collidepoint(evento.pos):
                    reiniciar_simulacion()
                if rect_boton_menu.collidepoint(evento.pos):
                    ESTADO = "MENU"
                
                # Interacción con Kerwin
                if menu_interaccion_rect and menu_interaccion_rect.collidepoint(evento.pos):
                    # Clic en una opción del menú
                    for i, (rect, accion) in enumerate(opciones_menu):
                        if rect.collidepoint(evento.pos):
                            kerwin.accion_pendiente = accion
                            kerwin.objetivo_manual = entidad_seleccionada
                            agregar_evento(f"Kerwin: Objetivo {accion} fijado")
                            menu_interaccion_rect = None
                            break
                else:
                    # Buscar si se hizo clic en una entidad
                    entidad_seleccionada = None
                    menu_interaccion_rect = None
                    for p in poblacion:
                        if p.vivo and not p.in_home and p.rect.collidepoint(evento.pos) and p != kerwin:
                            entidad_seleccionada = p
                            # Crear menú de opciones
                            x, y = evento.pos
                            opciones = ["Atacar", "Comer", "Guardar en Casa"] if isinstance(p, Conejo) else ["Atacar"]
                            opciones_menu = []
                            for i, opt in enumerate(opciones):
                                r = pygame.Rect(x, y + i*25, 120, 25)
                                opciones_menu.append((r, opt.lower()))
                            menu_interaccion_rect = pygame.Rect(x, y, 120, len(opciones)*25)
                            break
                            
                    # Buscar si se hizo clic en una Casa
                    if not entidad_seleccionada:
                        for h in mundo.casas:
                            if h.rect.collidepoint(evento.pos):
                                entidad_seleccionada = h
                                x, y = evento.pos
                                opciones = ["Entrar", "Dormir", "Comer", "Jugar"]
                                opciones_menu = []
                                for i, opt in enumerate(opciones):
                                    r = pygame.Rect(x, y + i*25, 120, 25)
                                    opciones_menu.append((r, opt.lower()))
                                menu_interaccion_rect = pygame.Rect(x, y, 120, len(opciones)*25)
                                break

                    
                    # Si no se clicó ninguna entidad, Kerwin camina hacia el punto del clic
                    if not entidad_seleccionada:
                        kerwin.objetivo_manual = evento.pos
                        kerwin.accion_pendiente = None
                        agregar_evento(f"Kerwin moviéndose a {evento.pos}")


    if ESTADO == "MENU":
        dibujar_menu(mundo.PANTALLA)
        pygame.display.update()
        mundo.RELOJ.tick(60)
        
    elif ESTADO == "EDITOR":
        dibujar_editor(mundo.PANTALLA)
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
                        if p == kerwin:
                            # Kerwin solo ataca si fue mandado especificamente
                            if kerwin.objetivo_manual == otro and kerwin.accion_pendiente in ["atacar", "atrapar", "comer"]:
                                es_enemigo = True
                        else:
                            # IA ataca Zorros en defensa propia siempre, Conejos solo si cazan
                            if isinstance(otro, Zorro):
                                es_enemigo = True
                            elif isinstance(otro, Conejo) and p.hambre > 20:
                                es_enemigo = True
                    
                    if es_enemigo:
                        p.atacar(otro)
                        if not otro.vivo:
                            nombre_otro = getattr(otro, 'nombre', type(otro).__name__)
                            # EVENTO CAZA
                            agregar_evento(f"{nombre_p} Cazo un {nombre_otro}")
                            
                            # LOOT
                            if isinstance(p, Persona) and p != kerwin: # Solo humanos recogen inventario (Kerwin se maneja manual)
                                p.guardar_item(otro) # Guardar referencia del muerto

                                # mensaje = f"{p.nombre if hasattr(p,'nombre') else 'Alguien'} recogio un {type(otro).__name__}"
                                # agregar_evento(mensaje)
                                # print(mensaje)

                # --- HOGAR (Almacenar / Comer / Dormir) ---
                hogares = mundo.casas + mundo.madrigueras + mundo.cuevas
                # Manual collision check
                possible_homes = [h for h in hogares if hasattr(h, 'rect') and p.rect.colliderect(h.rect)]
                
                for h in possible_homes:
                    # Que quieren hacer en la casa
                    razon = getattr(p, 'razon_ir_casa', None)
                    modo_entrar = None
                    
                    if razon == "dormir" or p.sueño > 70:
                        modo_entrar = "dormir"
                    elif razon == "descansar" or (isinstance(p, Conejo) and getattr(p, 'peligro', False) and h in mundo.madrigueras):
                        modo_entrar = "descansar"
                    
                    if modo_entrar:
                        if not p.in_home:
                            # Verify capacity
                            if len(h.ocupantes) < h.capacidad:
                                p.entrar_casa(modo_entrar, hogar=h)
                        
                    elif razon == "jugar":
                        p.jugar()
                        p.razon_ir_casa = None
                        
                    # Gestion de Inventario (Solo Casas y Humanos)
                    if isinstance(p, Persona) and h in mundo.casas:
                        # A. Guardar items
                        items_a_remover = []
                        for item in p.inventario:
                            h.guardar(item)
                            items_a_remover.append(item)
                            agregar_evento(f"{p.nombre} guardo comida en casa.")
                        
                        for i in items_a_remover:
                            p.inventario.remove(i)
                            
                        # B. Comer del almacen
                        if (razon == "comer" or p.hambre > 40) and hasattr(h, 'almacen') and h.almacen:
                            # Verify if there is space inside to eat
                            if len(h.ocupantes) < h.capacidad:
                                comida_guardada = h.consumir()
                                if comida_guardada:
                                    p.alimentarse(50) 
                                    p.entrar_casa("comer", hogar=h)
                                    agregar_evento(f"{p.nombre} entró a comer de la casa.")
                                    if razon == "comer":
                                        p.razon_ir_casa = None

                    # --- LOGICA MANUEL DE KERWIN ---
                    if p == kerwin and kerwin.objetivo_manual and hasattr(kerwin.objetivo_manual, 'rect') and p.rect.colliderect(kerwin.objetivo_manual.rect):
                        target = kerwin.objetivo_manual
                        accion = kerwin.accion_pendiente
                        
                        if accion == "atacar":
                            p.atacar(target)
                            if not target.vivo:
                                agregar_evento(f"Kerwin eliminó a {type(target).__name__}")
                                kerwin.objetivo_manual = None
                                
                        elif accion in ["entrar", "dormir", "comer", "jugar"] and isinstance(target, Hogar):
                            if len(target.ocupantes) < target.capacidad:
                                if accion == "entrar":
                                    p.entrar_casa("descansar", hogar=target)
                                    agregar_evento("Kerwin ha entrado a descansar")
                                elif accion == "dormir":
                                    p.entrar_casa("dormir", hogar=target)
                                    agregar_evento("Kerwin se ha ido a dormir")
                                elif accion == "jugar":
                                    p.entrar_casa("jugar", hogar=target) # Assuming playing logic internally uses entrar_casa but UI logic here overrides 
                                    agregar_evento("Kerwin esta jugando")
                                elif accion == "comer":
                                    target_h = target
                                    if target_h.almacen:
                                        comida_guardada = target_h.consumir()
                                        p.alimentarse(50)
                                        p.entrar_casa("comer", hogar=target)
                                        agregar_evento("Kerwin entró a comer de la casa")
                                    else:
                                        agregar_evento("No hay comida en la casa")
                            else:
                                agregar_evento("¡No hay espacio en este hogar!")
                            kerwin.objetivo_manual = None
                        
                        elif accion == "comer":
                            if not getattr(target, 'vivo', True) or isinstance(target, Comida):
                                p.alimentarse(40)
                                agregar_evento("Kerwin se ha alimentado")
                                if hasattr(target, 'morir'): target.morir()
                                elif isinstance(target, pygame.sprite.Sprite): target.kill()
                                kerwin.objetivo_manual = None
                        
                        elif accion == "guardar en casa":
                            # Llevar a casa (simplificado: desaparece y va al almacen de la primera casa)
                            if mundo.casas:
                                mundo.casas[0].guardar(target)
                                if hasattr(target, 'kill'): target.kill()
                                elif hasattr(target, 'vivo'): target.vivo = False
                                agregar_evento("Kerwin guardó la presa en casa")
                                kerwin.objetivo_manual = None



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
        
        # Dibujar Menú de Interacción si existe
        if menu_interaccion_rect:
            pygame.draw.rect(mundo.PANTALLA, (50, 50, 50), menu_interaccion_rect)
            for rect, texto in opciones_menu:
                pygame.draw.rect(mundo.PANTALLA, (100, 100, 100), rect, 1)
                txt_surf = font_ui.render(texto.capitalize(), True, (255, 255, 255))
                mundo.PANTALLA.blit(txt_surf, (rect.x + 5, rect.y + 5))

        pygame.display.update()

        mundo.RELOJ.tick(60)
