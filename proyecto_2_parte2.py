"""
TEC
Ingeniería en Computación
Taller de Programación
Profesor: Mauricio Avilés
Estudiante: Sergio Aarón Cambronero Fonseca
Este archivo esta creado antes de ver e unirse al archivo de luis que tiene
los requisitos funcionales 1, 2, 3, 4.
Graficador de Espacio en Disco
"""

import os
import pygame


# TOP 10 ARCHIVOS MÁS GRANDES
# Llamada desde main(), paso 5:
# top_archivos = obtener_top_diez_archivos_mas_grandes(lista_global_archivos)
#
# "lista_global_archivos" es la lista que llenó analizar_directorio_recursivo().
# Cada elemento es un diccionario con las claves: "ruta", "nombre", "tamaño".

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
    )[:CANTIDAD_TOP_ARCHIVOS]   #ejemplo: CANTIDAD_TOP_ARCHIVOS = 10 

# TOP 10 DIRECTORIOS CON MÁS ARCHIVOS
# Llamada desde main(), paso 5:
#top_directorios = obtener_top_diez_directorios_con_mas_archivos(dict_global_directorios)
#
# "dict_global_directorios" es el diccionario que llenó analizar_directorio_recursivo().
# Su formato es: { ruta_directorio (str): cantidad_archivos_directos (int) }

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
    )[:CANTIDAD_TOP_DIRECTORIOS]  #ejemplo: CANTIDAD_TOP_ARCHIVOS = 10


# HELPERS DE DIBUJO REUTILIZABLES
# Estas tres funciones son usadas por dibujar_header() y dibujar_panel_lateral()
# Requisito funcional 7, y también por dibujar_treemap_recursivo() de Luis.
# Deben estar definidas ANTES de las funciones que las llaman.

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



# DIBUJO DEL ENCABEZADO Y PANEL LATERAL

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
        (obtener_tamaño_legible(tamaño_total), "TOTAL"),
        (f"{total_archivos:,}",                "ARCHIVOS"),
        (f"{total_dirs:,}",                    "CARPETAS"),
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
    y_panel += sup_sec1.get_height() + 6

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
            C_TEXT_PRIMARY, x_panel + 36, y_panel + 5, ancho - 90
        )

        tam_str = obtener_tamaño_legible(archivo["tamaño"])
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


# Requisitos funcionales 8 – BUCLE DE EVENTOS PYGAME
# Este bloque va DENTRO de main(), en el paso 8, reemplazando o completando
# el bucle que Luis haya hecho.

#   reloj = pygame.time.Clock()
#   en_ejecucion = True
#
#   while en_ejecucion:
#       for evento in pygame.event.get():
#           if evento.type == pygame.QUIT:        # clic en X de la ventana
#               en_ejecucion = False
#           elif evento.type == pygame.KEYDOWN:
#               if evento.key == pygame.K_ESCAPE: # tecla ESC
#                   en_ejecucion = False
#
#       # Única operación por frame: copiar el Surface ya pre-renderizado.
#       # Así no hay flasheos ni recálculos innecesarios.
#       ventana.blit(superficie_estatica, (0, 0))
#       pygame.display.flip()
#       reloj.tick(30)   # máximo 30 FPS 
#
#   pygame.quit()
#   sys.exit(0)
