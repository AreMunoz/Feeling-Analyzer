import os  # Librería necesaria para leer el contenido de un directorio.
import pymupdf
import re
import json
import pandas as pd
import matplotlib.pyplot as plt

ListaArchivo = []  # Variable global para almacenar los archivos PDF en el directorio.
EXPRESIONES_FILE = "expresiones.json"

# Clasificación de sentimientos en categorías
CATEGORIAS = {
    "positivo": ["Alegría", "Felicidad", "Esperanza", "Amor"],
    "negativo": ["Tristeza", "Miedo", "Asco", "Ira", "Disgusto", "Susto", "Vergüenza", "Ansiedad", "Frustración", "Culpa", "Disgusto"],
    "neutral": ["Neutro", "Sorpresa", "Sorprendido", "Calma", "Confusión"]
}

def cargarExpresiones():
    if os.path.exists(EXPRESIONES_FILE):
        with open(EXPRESIONES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {
        "Tristeza": "triste[z][a]",
        "Alegría": "alegr[eíi][as]?",
        "Felicidad": "felicidad|feliz",
        "Sorpresa": "sorprend[io][da]s?",
        "Miedo": "mied[o]s?",
        "Asco": "asco|asquead[oa]s?",
        "Ira": "ira|enfad[ao]s?",
        "Neutro": "neutr[oa]s?",
        "Sorprendido": "sorprendid[oa]s?",
        "Susto": "sust[o]s?",
        "Disgusto": "disgust[o]s?",
        "Ansiedad": "ansiedad|ansios[oa]s?",
        "Calma": "calm[oa]s?|serenid[aá]d",
        "Confusión": "confusi[oó]n|confundid[oa]s?",
        "Culpa": "culp[a]|culpabl[ea]s?",
        "Esperanza": "esperanz[a]|optimist[ao]s?",
        "Frustración": "frustraci[oó]n|frustrad[oa]s?",
        "Orgullo": "orgull[o]|orgullos[oa]s?",
        "Amor": "amor|amoros[oa]s?|cariñ[oa]s?",
    }

def guardarExpresiones(expresiones):
    with open(EXPRESIONES_FILE, "w", encoding="utf-8") as file:
        json.dump(expresiones, file, indent=4, ensure_ascii=False)

def mostrarExpresiones(expresiones):
    print("\nLista de sentimientos y sus expresiones regulares:")
    for sentimiento, expresion in expresiones.items():
        print(f"{sentimiento}: {expresion}")

def agregarExpresion(expresiones):
    while True:
        print("\nIngrese una nueva expresión regular o escriba 'salir' para terminar:")
        sentimiento = input("Ingrese el nombre del sentimiento: ").strip()
        if sentimiento.lower() == "salir":
            break
        
        if any(sentimiento.lower() == key.lower() for key in expresiones.keys()):
            print(f"El sentimiento '{sentimiento}' ya existe. Intente con otro nombre.")
            continue
        
        expresion = input(f"Ingrese la expresión regular para '{sentimiento}': ")
        expresiones[sentimiento] = expresion
        print("Expresión agregada exitosamente!")
    guardarExpresiones(expresiones)
    return expresiones

def editarExpresion(expresiones):
    while True:
        print("\nIngrese el sentimiento cuya expresión desea editar o escriba 'salir' para terminar:")
        sentimiento = input("Sentimiento a editar: ").strip()
        if sentimiento.lower() == "salir":
            break
        
        if sentimiento not in expresiones:
            print(f"El sentimiento '{sentimiento}' no existe. Intente de nuevo.")
            continue
        
        nueva_expresion = input(f"Ingrese la nueva expresión regular para '{sentimiento}': ")
        expresiones[sentimiento] = nueva_expresion
        print("Expresión actualizada exitosamente!")
    guardarExpresiones(expresiones)
    return expresiones

def leerArchivo(pArchivo, ExpRegSentimientos):
    text = ""
    Sentimientos = {key: 0 for key in ExpRegSentimientos.keys()}

    doc = pymupdf.open(pArchivo)
    for page in doc:
        text += page.get_text()
    doc.close()
    
    lineas = text.split("\n")
    
    for linea in lineas:
        for key in ExpRegSentimientos:
            validacionRE = re.search(r'\b' + ExpRegSentimientos[key] + r'\b', linea.lower())
            if validacionRE:
                Sentimientos[key] += 1
    
    for key in Sentimientos:
        print(f"Sentimiento:{key} Valor:{Sentimientos[key]}")

    generarReporteFinal(Sentimientos, pArchivo)  # Pasar el nombre del archivo aquí

def generarReporteFinal(sentimientos, archivo_pdf):
    """
    Genera un reporte final mostrando los sentimientos detectados con sus porcentajes,
    e indica si el reporte es mayormente positivo, negativo o neutral.
    """
    reporte = f"\n--- REPORTE FINAL ({archivo_pdf}) ---\n"
    sentimientos_filtrados = {k: v for k, v in sentimientos.items() if v > 0}
    total = sum(sentimientos_filtrados.values())
    
    if not sentimientos_filtrados:
        reporte += "No se detectaron sentimientos en los archivos analizados.\n"
    else:
        for sentimiento, valor in sentimientos_filtrados.items():
            porcentaje = (valor / total) * 100 if total > 0 else 0
            reporte += f"{sentimiento}: {valor} ({porcentaje:.2f}%)\n"
    
    # Evaluación de sentimiento mayoritario
    categorias_contador = {"positivo": 0, "negativo": 0, "neutral": 0}
    for sentimiento, cantidad in sentimientos_filtrados.items():
        for categoria, lista in CATEGORIAS.items():
            if sentimiento in lista:
                categorias_contador[categoria] += cantidad
    
    categoria_mayoritaria = max(categorias_contador, key=categorias_contador.get)
    reporte += f"\nSentimiento predominante: {categoria_mayoritaria.upper()}\n"
    
    print(reporte)
    
    # Generar gráfica de pastel con pandas y matplotlib
    if sentimientos_filtrados:
        df = pd.DataFrame(list(sentimientos_filtrados.items()), columns=["Sentimiento", "Frecuencia"])
        df.set_index("Sentimiento", inplace=True)
        df.plot.pie(y="Frecuencia", autopct='%1.1f%%', figsize=(8, 8), legend=False, startangle=90, colormap='tab10')
        plt.title(f"Distribución de Sentimientos - {archivo_pdf}")
        plt.ylabel("")  # Eliminar la etiqueta del eje Y
        plt.show()
    
    return reporte



def funcionPrincipal():
   # dirTemp = "/content/drive/MyDrive/Proyectos_Colab/pdf"
    dirTemp = ".\\"
    directorioAnalizado = input(f"Ingrese la ruta del directorio a analizar (Enter para usar por defecto: {dirTemp}): ") or dirTemp

    ExpRegSentimientos = cargarExpresiones()
    
    if input("Desea ver los sentimientos y expresiones regulares guardadas? (si/no): ").lower() == "si":
        mostrarExpresiones(ExpRegSentimientos)
    
    if input("Desea agregar nuevas expresiones regulares? (si/no): ").lower() == "si":
        ExpRegSentimientos = agregarExpresion(ExpRegSentimientos)
    
    if input("Desea editar alguna expresión regular? (si/no): ").lower() == "si":
        ExpRegSentimientos = editarExpresion(ExpRegSentimientos)

    leerDirectorio(directorioAnalizado)
    for archivo in ListaArchivo:
        print("----------------------------------------------------")
        print("Archivo: " + archivo)
        leerArchivo(archivo, ExpRegSentimientos)

def leerDirectorio(pDir):
    with os.scandir(pDir) as ficheros:
        for fichero in ficheros:
            if fichero.is_dir() and not (fichero.path.endswith("error") or fichero.path.endswith("procesado")):
                leerDirectorio(fichero.path)
            else:
                if fichero.path.endswith(".pdf"):
                    ListaArchivo.append(fichero.path)

funcionPrincipal() #comentar cuando se ocupe en google colab
