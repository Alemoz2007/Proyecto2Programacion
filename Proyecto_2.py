import os
import pygame
import random

ANCHO = 1200
ALTO = 700
MAX_NIVEL = 6

def solicitar_directorio():
    while True:
        ruta = input("Digite la ruta del directorio a analizar: ")
        if os.path.isdir(ruta):
            return ruta
        print("ERROR: La ruta no existe o no es un directorio.")

def analizar_directorio(ruta, nivel=0):
    if nivel > MAX_NIVEL:
        return None
    datos = {
        "nombre": os.path.basename(ruta) if os.path.basename(ruta) else ruta,
        "ruta": ruta,
        "tamano": 0,
        "hijos": []
    }
    try:
        elementos = os.listdir(ruta)
        for elemento in elementos:
            ruta_completa = os.path.join(ruta, elemento)
            try:
                if os.path.isfile(ruta_completa):
                    tam = os.path.getsize(ruta_completa)
                    datos["hijos"].append({
                        "nombre": elemento,
                        "ruta": ruta_completa,
                        "tamano": tam,
                        "hijos": []
                    })
                    datos["tamano"] += tam
                elif os.path.isdir(ruta_completa):
                    hijo = analizar_directorio(
                        ruta_completa,
                        nivel + 1
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
    return datos

def convertir_tamano(bytes_):
    unidades = ["B", "KB", "MB", "GB", "TB"]
    tam = float(bytes_)
    indice = 0
    while tam >= 1024 and indice < len(unidades)-1:
        tam /= 1024
        indice += 1
    return f"{tam:.2f} {unidades[indice]}"

def color_aleatorio():
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )

def dibujar_treemap(
        pantalla,
        nodo,
        x,
        y,
        ancho,
        alto,
        horizontal=True,
        fuente=None):
    if nodo["tamano"] <= 0:
        return
    color = color_aleatorio()
    pygame.draw.rect(
        pantalla,
        color,
        (x, y, ancho, alto)
    )
    pygame.draw.rect(
        pantalla,
        (0, 0, 0),
        (x, y, ancho, alto),
        1
    )
    if fuente and ancho > 60 and alto > 20:
        texto = fuente.render(
            nodo["nombre"],
            True,
            (0, 0, 0)
        )
        pantalla.blit(
            texto,
            (x + 3, y + 3)
        )
    if not nodo["hijos"]:
        return
    total = sum(
        hijo["tamano"]
        for hijo in nodo["hijos"]
        if hijo["tamano"] > 0
    )
    if total == 0:
        return
    desplazamiento = 0
    for hijo in nodo["hijos"]:
        proporcion = hijo["tamano"] / total
        if horizontal:
            ancho_hijo = ancho * proporcion
            dibujar_treemap(
                pantalla,
                hijo,
                x + desplazamiento,
                y,
                ancho_hijo,
                alto,
                not horizontal,
                fuente
            )
            desplazamiento += ancho_hijo
        else:
            alto_hijo = alto * proporcion
            dibujar_treemap(
                pantalla,
                hijo,
                x,
                y + desplazamiento,
                ancho,
                alto_hijo,
                not horizontal,
                fuente
            )
            desplazamiento += alto_hijo

def imprimir_resumen(nodo, nivel=0):
    print(
        "   " * nivel +
        f"{nodo['nombre']} - "
        f"{convertir_tamano(nodo['tamano'])}"
    )
    for hijo in nodo["hijos"]:
        imprimir_resumen(hijo, nivel + 1)

def main():
    ruta = solicitar_directorio()
    print("\nAnalizando directorio...\n")
    datos = analizar_directorio(ruta)
    print("Análisis completado.\n")
    print("Resumen:\n")
    imprimir_resumen(datos)
    pygame.init()
    pantalla = pygame.display.set_mode(
        (ANCHO, ALTO)
    )
    pygame.display.set_caption(
        "Graficador de Espacio en Disco"
    )
    fuente = pygame.font.SysFont(None, 18)
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
        pantalla.fill((240, 240, 240))
        dibujar_treemap(
            pantalla,
            datos,
            0,
            0,
            ANCHO,
            ALTO,
            True,
            fuente
        )
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
