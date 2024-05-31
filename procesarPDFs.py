import fitz
import os
import pandas as pd
import re

def extraer_texto(pdf_path):
    documento = fitz.open(pdf_path)
    texto = ""
    for pagina in documento:
        texto += pagina.get_text()
    return texto

def eliminar_tabla_contenido(texto):
    # Identificar el inicio de la tabla de contenido
    inicio_tabla = re.search(r'(?i)tabla\s+de\s+contenido', texto)
    
    if inicio_tabla:
        # Eliminar todo el texto después de la tabla de contenido
        texto = texto[:inicio_tabla.start()]
    
    return texto


def separar_por_articulos(texto, tema):
    """ 
    Expresión regular para encontrar los encabezados de los artículos, no importa si está en mayúscula o no
    Esta expresión regular busca que:
    1. Inicie con artículo o art.
    2. Luego de artículo o art. pueda contener 0 o más espacios en blanco
    3. Contenga 1 o más dígitos consecutivos
    4. Cualquier caracter que no sea punto 0 o más veces
    5. Finalice con .- 

    Casos a filtrar:
    ARTICULO 33.-
    ARTÍCULO 33.-
    ARTÍCULO 33.
    ARTÍCULO IX.-
    , flags=re.IGNORECASE
    """
    texto = eliminar_tabla_contenido(texto)
    articulos = re.split(r'(ARTICULO\s*\d+\.-|ARTÍCULO\s*\d+\.-|ARTÍCULO\s*\d+\.|ARTÍCULO\s*[IVXLCDM]+\s*\.-|Artículo\s*\d+\.-|TRANSITORIO\s*[IVXLCDM]+\.-)', texto)
    datos = []
    
    # Iterar a través de los resultados para formar artículos completos
    for i in range(1, len(articulos), 2):
        encabezado = articulos[i].strip()
        contenido = articulos[i+1].strip() if (i+1) < len(articulos) else ""
        datos.append({"tema": tema, "articulo": encabezado, "contenido": contenido})
    return datos


def procesar_pdfs(directorio):
    datos = []
    for archivo in os.listdir(directorio):
        if archivo.endswith(".pdf"):
            tema = os.path.splitext(archivo)[0]
            texto = extraer_texto(os.path.join(directorio, archivo))
            articulos = separar_por_articulos(texto, tema)
            datos.extend(articulos)
            
            # Imprimir los datos procesados para el archivo actual
            print(f"Procesado: {archivo} - Tema: {tema}")
            for articulo in articulos:
                print(f"Artículo: {articulo['articulo']}")
                print(f"Contenido: {articulo['contenido'][:200]}...")  # Imprimir solo los primeros 200 caracteres del contenido
                print("-" * 80)
    
    return pd.DataFrame(datos)



if __name__ == "__main__":
    directorio = "./Base de datos"
    df = procesar_pdfs(directorio)
    df.to_csv("datos_procesados.csv", index=False, escapechar='\\')

