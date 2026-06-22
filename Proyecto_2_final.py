"""
TEC 
Ingeniería en Computación
Taller de Programación
Proyecto 2
Profesor: Mauricio Avilés
Estudiantes: Luis Alejandro Mora, Sergio Aarón Cambronero Fonseca
Graficador de Espacio en Disco
"""

import os
import sys
import pygame
import random

# CONSTANTES GLOBALES

ANCHO_VENTANA        = 1400
ALTO_VENTANA         = 800
MAX_NIVEL            = 6
ALTO_HEADER          = 55
ANCHO_PANEL_DERECHO  = 340
ANCHO_TREEMAP        = ANCHO_VENTANA - ANCHO_PANEL_DERECHO
MARGEN               = 10
CANTIDAD_TOP_ARCHIVOS    = 10
CANTIDAD_TOP_DIRECTORIOS = 10

C_BG_MAIN        = (15,  20,  35)
C_BG_HEADER      = (22,  28,  48)
C_BG_PANEL       = (18,  23,  40)
C_BG_CARD        = (28,  35,  55)
C_BG_CARD_ALT    = (24,  30,  50)
C_BORDER         = (38,  48,  72)
C_BORDER_GLOW    = (55,  70, 110)
C_TEXT_PRIMARY   = (220, 225, 240)
C_TEXT_DIM       = (100, 115, 150)
C_ACCENT_CYAN    = ( 80, 210, 220)
C_ACCENT_TEAL    = ( 60, 190, 160)
C_ACCENT_VIOLET  = (160, 110, 240)
C_ACCENT_AMBER   = (240, 180,  50)


# CÓDIGO DE LUIS – RF 1, 2, 3, 4
# Contiene correcciones no muy grandes por Aarón
def color_aleatorio():
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )

def solicitar_directorio():
    while True:
        ruta = input("Digite la ruta del directorio a analizar: ")
        if os.path.isdir(ruta):
            return ruta
        print("ERROR: La ruta no existe o no es un directorio.")

def convertir_tamano(bytes_):
    unidades = ["B", "KB", "MB", "GB", "TB"]
    tam = float(bytes_)
    indice = 0
    while tam >= 1024 and indice < len(unidades) - 1:
        tam /= 1024
        indice += 1
    return f"{tam:.2f} {unidades[indice]}"

def _sumar_tamano_recursivo(ruta):
    """Suma el tamaño de un directorio sin límite de nivel ni construir nodos."""
    total = 0
    try:
        for elemento in os.listdir(ruta):
            ruta_completa = os.path.join(ruta, elemento)
            try:
                if os.path.isfile(ruta_completa) or os.path.islink(ruta_completa):
                    total += os.path.getsize(ruta_completa)
                elif os.path.isdir(ruta_completa):
                    total += _sumar_tamano_recursivo(ruta_completa)
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass
    return total

def analizar_directorio(ruta, nivel=0, lista_archivos=None, dict_directorios=None):
    """Analiza directorios recursivamente. Máximo 6 niveles de profundidad."""
    if lista_archivos is None:
        lista_archivos = []
    if dict_directorios is None:
        dict_directorios = {}

    if nivel > MAX_NIVEL:
        return None
    datos = {
        "nombre": os.path.basename(ruta) if os.path.basename(ruta) else ruta,
        "ruta": ruta,
        "tamano": 0,
        "hijos": [],
        "color": color_aleatorio()
    }
    archivos_directos = 0
    try:
        for elemento in os.listdir(ruta):
            ruta_completa = os.path.join(ruta, elemento)
            try:
                if os.path.isfile(ruta_completa) or os.path.islink(ruta_completa):
                    tam = os.path.getsize(ruta_completa)
                    datos["tamano"] += tam
                    archivos_directos += 1
                    lista_archivos.append({
                        "ruta":   ruta_completa,
                        "nombre": os.path.basename(ruta_completa),
                        "tamaño": tam
                    })
                elif os.path.isdir(ruta_completa):
                    if nivel + 1 > MAX_NIVEL:
                        datos["tamano"] += _sumar_tamano_recursivo(ruta_completa)
                    else:
                        hijo = analizar_directorio(
                            ruta_completa,
                            nivel + 1,
                            lista_archivos,
                            dict_directorios
                        )
                        if hijo is not None:

                            datos["hijos"].append(hijo)
                            datos["tamano"] += hijo["tamano"]
            except PermissionError:
                pass
            except OSError:
                pass
    except PermissionError:
        print(f"Sin permisos para acceder a: {ruta}")
    except Exception as error:
        print(f"Error en {ruta}: {error}")
    dict_directorios[ruta] = archivos_directos
    return datos

def _color_texto(color_fondo):
    r, g, b = color_fondo
    luminancia = 0.299 * r + 0.587 * g + 0.114 * b
    return (20, 20, 20) if luminancia > 140 else (235, 235, 235)

def dibujar_treemap(superficie, nodo, x, y, ancho, alto, horizontal, fuente):
    if nodo["tamano"] <= 0 or ancho < 4 or alto < 4:
        return
    color = nodo["color"]
    pygame.draw.rect(superficie, color, (int(x), int(y), int(ancho), int(alto)))
    pygame.draw.rect(superficie, (0, 0, 0), (int(x), int(y), int(ancho), int(alto)), 1)

    color_txt = _color_texto(color)
    PAD = 5
    if ancho > 60 and alto > 20:
        texto = fuente.render(nodo["nombre"], True, color_txt)
        superficie.blit(texto, (int(x) + PAD, int(y) + PAD))
    if ancho > 60 and alto > 36:
        tam_txt = fuente.render(convertir_tamano(nodo["tamano"]), True, color_txt)
        superficie.blit(tam_txt, (int(x) + PAD, int(y) + PAD + 16))

    if not nodo["hijos"]:
        return
    total = sum(h["tamano"] for h in nodo["hijos"] if h["tamano"] > 0)
    if total == 0:
        return
    desplazamiento = 0
    for hijo in nodo["hijos"]:
        if hijo["tamano"] <= 0:
            continue
        proporcion = hijo["tamano"] / total
        if horizontal:
            ancho_hijo = ancho * proporcion
            dibujar_treemap(superficie, hijo, x + desplazamiento, y, ancho_hijo, alto, not horizontal, fuente)
            desplazamiento += ancho_hijo
        else:
            alto_hijo = alto * proporcion
            dibujar_treemap(superficie, hijo, x, y + desplazamiento, ancho, alto_hijo, not horizontal, fuente)
            desplazamiento += alto_hijo


# CÓDIGO DE AARÓN – RF 5, 6, 7, 8


def obtener_top_diez_archivos_mas_grandes(lista_todos_los_archivos):
    """
    Ordena todos los archivos por tamaño y devuelve los 10 más grandes.

    Entradas: lista de diccionarios con "ruta", "nombre" y "tamaño".
    Salidas: lista de hasta 10 diccionarios, del más grande al más pequeño.
    Restricciones: la lista debe tener al menos un elemento.
    """
    return sorted(
        lista_todos_los_archivos,
        key=lambda archivo: archivo["tamaño"],
        reverse=True
    )[:CANTIDAD_TOP_ARCHIVOS]

def obtener_top_diez_directorios_con_mas_archivos(diccionario_conteo):
    """
    Ordena los directorios por cantidad de archivos y devuelve los 10 con más.

    Entradas: diccionario donde cada llave es una ruta y el valor es la cantidad de archivos.
    Salidas: lista de hasta 10 tuplas (ruta, cantidad), de mayor a menor.
    Restricciones: el diccionario debe tener al menos un elemento.
    """
    return sorted(
        diccionario_conteo.items(),
        key=lambda par: par[1],
        reverse=True
    )[:CANTIDAD_TOP_DIRECTORIOS]


def dibujar_texto_recortado(superficie, fuente, texto, color, x, y, ancho_max):
    """
    Dibuja un texto y si no cabe en el espacio disponible lo recorta con "..." al final.

    Entradas: superficie donde dibujar, fuente a usar, texto, color RGB, coordenadas x e y,
    y el ancho máximo permitido en píxeles.
    Salidas: ninguna, dibuja directamente sobre la superficie.
    Restricciones: el ancho máximo debe ser mayor al ancho de un solo carácter.
    """
    superficie_texto = fuente.render(texto, True, color)

    if superficie_texto.get_width() <= ancho_max:
        superficie.blit(superficie_texto, (x, y))
        return

    while len(texto) > 1:
        texto = texto[:-1]
        candidato = fuente.render(texto + "…", True, color)
        if candidato.get_width() <= ancho_max:
            superficie.blit(candidato, (x, y))
            return


def dibujar_linea_separadora(superficie, x1, y, x2, color=None):
    """
    Dibuja una línea horizontal de 1 píxel de grosor.

    Entradas: superficie donde dibujar, coordenadas x1 y x2 como extremos,
    y la posición vertical y. El color es opcional y usa C_BORDER si no se pasa.
    Salidas: ninguna.
    Restricciones: x2 debe ser mayor que x1.
    """
    pygame.draw.line(superficie, color or C_BORDER, (x1, y), (x2, y), 1)


def dibujar_badge(superficie, fuente, texto, color_texto, color_fondo, x, y, padding_h=8, padding_v=3, radio=4):
    """
    Dibuja una etiqueta con fondo redondeado y texto adentro.
    Sirve para mostrar cosas cortas como extensiones o tamaños de forma resaltada.

    Entradas: superficie, fuente, texto a mostrar, color del texto, color del fondo,
    posición x e y. El relleno horizontal, vertical y el radio de las esquinas son opcionales.
    Salidas: el ancho total de la etiqueta en píxeles, útil para ubicar elementos a su derecha.
    Restricciones: el radio no debe ser mayor a la mitad de la altura de la etiqueta.
    """
    sup_texto   = fuente.render(texto, True, color_texto)
    ancho_badge = sup_texto.get_width()  + padding_h * 2
    alto_badge  = sup_texto.get_height() + padding_v * 2
    rect_badge  = pygame.Rect(x, y, ancho_badge, alto_badge)
    pygame.draw.rect(superficie, color_fondo, rect_badge, border_radius=radio)
    superficie.blit(sup_texto, (x + padding_h, y + padding_v))
    return ancho_badge


def dibujar_header(superficie, ruta_analizada, tamaño_total, total_archivos, total_dirs, fuentes):
    """
    Dibuja la barra de encabezado con el nombre del directorio analizado
    y tres métricas: tamaño total, cantidad de archivos y cantidad de carpetas.

    Entradas: superficie principal, ruta del directorio raíz, bytes totales,
    cantidad de archivos, cantidad de carpetas y el diccionario de fuentes pygame.
    Salidas: ninguna, dibuja directamente sobre la superficie.
    Restricciones: debe llamarse después de pygame.display.set_mode().
    """
    rect_header = pygame.Rect(0, 0, ANCHO_VENTANA, ALTO_HEADER)
    pygame.draw.rect(superficie, C_BG_HEADER, rect_header)

    dibujar_linea_separadora(
        superficie, 0, ALTO_HEADER - 1, ANCHO_VENTANA, C_BORDER_GLOW
        )

    nombre_dir = os.path.basename(ruta_analizada) or ruta_analizada
    sup_nombre = fuentes["titulo"].render(f"  {nombre_dir}", True, C_TEXT_PRIMARY)
    superficie.blit(sup_nombre, (MARGEN, 10))

    sup_ruta = fuentes["micro"].render(ruta_analizada, True, C_TEXT_DIM)
    superficie.blit(sup_ruta, (MARGEN + 2, 32))

    metricas = [
        (convertir_tamano(tamaño_total), "TOTAL"),
        (f"{total_archivos:,}",          "ARCHIVOS"),
        (f"{total_dirs:,}",              "CARPETAS"),
    ]
    x_metrica = ANCHO_VENTANA - ANCHO_PANEL_DERECHO - 20
    for valor, etiqueta in metricas:
        sup_val = fuentes["subtit"].render(valor, True, C_ACCENT_CYAN)
        sup_lab = fuentes["micro"].render(etiqueta, True, C_TEXT_DIM)
        superficie.blit(sup_val, (x_metrica, 8))
        superficie.blit(sup_lab, (x_metrica, 28))
        x_metrica += 130


def dibujar_panel_lateral(superficie, top_archivos, top_directorios, fuentes):
    """
    Dibuja el panel lateral derecho completo. Arriba muestra el top 10 de archivos
    más grandes y abajo el top 10 de carpetas con más archivos. Cada elemento
    aparece en una tarjeta con su ranking, nombre, ruta y tamaño o cantidad.

    Entradas: superficie principal, lista de top archivos, lista de top directorios
    y el diccionario de fuentes pygame.
    Salidas: ninguna, dibuja directamente sobre la superficie.
    Restricciones: el panel empieza en x igual a ANCHO_TREEMAP más MARGEN por 2.
    Los elementos se cortan si no caben verticalmente en pantalla.
    """
    x_panel = ANCHO_TREEMAP + MARGEN * 2
    y_panel = ALTO_HEADER + MARGEN
    ancho = ANCHO_PANEL_DERECHO - MARGEN

    rect_panel = pygame.Rect(
        x_panel - MARGEN // 2,
        ALTO_HEADER,
        ANCHO_PANEL_DERECHO + MARGEN,
        ALTO_VENTANA - ALTO_HEADER
    )
    pygame.draw.rect(superficie, C_BG_PANEL, rect_panel)

    dibujar_linea_separadora(
        superficie,
        x_panel - MARGEN // 2, ALTO_HEADER,
        x_panel - MARGEN // 2,
        color=C_BORDER_GLOW
    )

    sup_sec1 = fuentes["subtit"].render("ARCHIVOS MÁS GRANDES", True, C_ACCENT_CYAN)
    superficie.blit(sup_sec1, (x_panel, y_panel))
    y_panel += sup_sec1.get_height() +6

    dibujar_linea_separadora(superficie, x_panel, y_panel, x_panel + ancho, C_BORDER_GLOW)
    y_panel += 8

    for indice, archivo in enumerate(top_archivos):
        if y_panel + 46 > ALTO_VENTANA // 2:
            break

        color_card = C_BG_CARD if indice % 2 == 0 else C_BG_CARD_ALT
        rect_card  = pygame.Rect(x_panel, y_panel, ancho, 42)
        pygame.draw.rect(superficie, color_card, rect_card, border_radius=4)

        color_rank = C_ACCENT_AMBER if indice == 0 else C_TEXT_DIM
        sup_rank   = fuentes["subtit"].render(f"#{indice + 1}", True, color_rank)
        superficie.blit(sup_rank, (x_panel + 6, y_panel + 5))

        dibujar_texto_recortado(
            superficie, fuentes["normal"], archivo["nombre"],
            C_TEXT_PRIMARY, x_panel +36, y_panel + 5, ancho - 90
        )

        tam_str = convertir_tamano(archivo["tamaño"])
        sup_tam = fuentes["normal"].render(tam_str, True, C_ACCENT_TEAL)
        superficie.blit(sup_tam,
                        (x_panel + ancho - sup_tam.get_width() - 6, y_panel + 5))

        dibujar_texto_recortado(
            superficie, fuentes["micro"], archivo["ruta"],
            C_TEXT_DIM, x_panel + 36, y_panel + 24, ancho - 42
        )

        y_panel += 46

    y_panel += 10
    sup_sec2 = fuentes["subtit"].render("CARPETAS CON MÁS ARCHIVOS", True, C_ACCENT_VIOLET)
    superficie.blit(sup_sec2, (x_panel, y_panel))
    y_panel += sup_sec2.get_height() + 6

    dibujar_linea_separadora(superficie, x_panel, y_panel,
                             x_panel + ancho, C_BORDER_GLOW)
    y_panel += 8

    for indice, (ruta_dir, cantidad) in enumerate(top_directorios):
        if y_panel + 46 > ALTO_VENTANA - 10:
            break

        color_card = C_BG_CARD if indice % 2 == 0 else C_BG_CARD_ALT
        rect_card  = pygame.Rect(x_panel, y_panel, ancho, 42)
        pygame.draw.rect(superficie, color_card, rect_card, border_radius=4)

        color_rank = C_ACCENT_AMBER if indice == 0 else C_TEXT_DIM
        sup_rank   = fuentes["subtit"].render(f"#{indice + 1}", True, color_rank)
        superficie.blit(sup_rank, (x_panel + 6, y_panel + 5))

        nombre_dir = os.path.basename(ruta_dir) or ruta_dir
        dibujar_texto_recortado(
            superficie, fuentes["normal"], nombre_dir,
            C_TEXT_PRIMARY, x_panel + 36, y_panel + 5, ancho - 90
        )

        cant_str = f"{cantidad} arch."
        sup_cant = fuentes["normal"].render(cant_str, True, C_ACCENT_VIOLET)
        superficie.blit(sup_cant,
                        (x_panel + ancho - sup_cant.get_width() - 6, y_panel + 5))

        dibujar_texto_recortado(
            superficie, fuentes["micro"], ruta_dir,
            C_TEXT_DIM, x_panel + 36, y_panel + 24, ancho - 42
        )

        y_panel += 46

# MAIN


def main():
    ruta = solicitar_directorio()
    print("\nAnalizando directorio...\n")
    lista_archivos   = []
    dict_directorios = {}
    datos = analizar_directorio(ruta, 0, lista_archivos, dict_directorios)
    print("Análisis completado.")
    print("Tamaño total:", convertir_tamano(datos["tamano"]))

    top_archivos    = obtener_top_diez_archivos_mas_grandes(lista_archivos)
    top_directorios = obtener_top_diez_directorios_con_mas_archivos(dict_directorios)

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Graficador de Espacio en Disco")

    fuentes = {
        "titulo": pygame.font.SysFont(None, 22),
        "subtit": pygame.font.SysFont(None, 16),
        "normal": pygame.font.SysFont(None, 15),
        "micro":  pygame.font.SysFont(None, 13),
    }
    fuente_treemap = pygame.font.SysFont(None, 15)

    superficie_estatica = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
    superficie_estatica.fill(C_BG_MAIN)

    area_treemap = pygame.Surface((ANCHO_TREEMAP, ALTO_VENTANA - ALTO_HEADER))
    area_treemap.fill((240, 240, 240))
    dibujar_treemap(
        area_treemap,
        datos,
        0, 0,
        ANCHO_TREEMAP,
        ALTO_VENTANA - ALTO_HEADER,
        True,
        fuente_treemap
    )
    superficie_estatica.blit(area_treemap, (0, ALTO_HEADER))

    dibujar_header(
        superficie_estatica, ruta, datos["tamano"],
        len(lista_archivos), len(dict_directorios), fuentes
    )
    dibujar_panel_lateral(
        superficie_estatica, top_archivos, top_directorios, fuentes
    )

    reloj        = pygame.time.Clock()
    en_ejecucion = True

    while en_ejecucion:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                en_ejecucion = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    en_ejecucion = False

        pantalla.blit(superficie_estatica, (0, 0))
        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()
    sys.exit(0)
    
# Unión de los archivos y correcciones por Aarón

if __name__ == "__main__":
    main()
