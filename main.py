#uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import pandas as pd
from datetime import datetime

import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

app = FastAPI()

class Libro(BaseModel):
    titulo: str
    autor: str
    paginas: int
    editorial: Optional [str]



#-----------------------------------------

df = pd.read_csv('movies_dataset.csv')
movies = df

def convert(obj): 
    if isinstance(obj, str) and '{' in obj:
        L=[]
        for i in ast.literal_eval(obj):
            L.append(i['name']);
        return L
    
def convert2(obj): 
    if isinstance(obj, str) and '{' in obj:
        dic = ast.literal_eval(obj)
        return dic['name']
    
df['genres'] = df['genres'].apply(convert)
df['belongs_to_collection'] = df['belongs_to_collection'].apply(convert2)
df['production_companies'] = df['production_companies'].apply(convert)
df['production_countries'] = df['production_countries'].apply(convert)
df['spoken_languages'] = df['spoken_languages'].apply(convert)

# Rellenar los valores nulos con 0
df[['revenue', 'budget']] = df[['revenue', 'budget']].fillna(0)

df['release_year'] = df['release_date'].str.slice(0, 4)

df['release_date'] = pd.to_datetime(df['release_date'], format='%Y-%m-%d', errors='coerce')

# Eliminamos las filas con valores nulos en la columna "release_date"
df = df.dropna(subset=['release_date'])

df = df.drop(['video', 'imdb_id', 'adult', 'original_title', 'vote_count', 'poster_path', 'homepage'], axis=1)

df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
df['return'] = df.apply(lambda row: row['revenue'] / row['budget'] if row['budget'] != 0 else 0, axis=1)

#Funcion peliculas por mes


df['release_date'] = pd.to_datetime(df['release_date'])
df['month'] = df['release_date'].dt.strftime('%B')


# Crear un diccionario con las correspondencias de los meses

meses_dict = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'septiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
}

# Aplicar la conversión a la columna de los meses en inglés
df['month'] = df['month'].map(meses_dict)


@app.get("/peliculas_mes/{mes}")
def peliculas_mes(mes: str):
   cantidad_m = len(df[df['month'] == mes])
   return {'cantidad de peliculas por mes': cantidad_m}


# Funciones peliculas_dia


df['release_date'] = pd.to_datetime(df['release_date']) # convertimos la columna a formato de fecha
df['day_of_week'] = df['release_date'].dt.day_name() # agregamos la columna del día de la semana


# Creamos un diccionario de mapeo
dias_ingles_espanol = {'Monday': 'lunes', 'Tuesday': 'martes', 'Wednesday': 'miércoles', 'Thursday': 'jueves', 'Friday': 'viernes', 'Saturday': 'sábado', 'Sunday': 'domingo'}

# Aplicamos el mapeo a la columna day_of_week
df['day_of_week'] = df['day_of_week'].map(dias_ingles_espanol)


#FUNCION PELICULAS POR DIA
@app.get("/peliculas_dia/{dia}")
def peliculas_dia(dia: str):
    cantidad_d = len(df[df['day_of_week'] == dia])
    return {'cantidad de peliculas por día': cantidad_d}


#FUNCION PELICULAS POR PAIS
@app.get("/peliculas_pais/{pais}")
def peliculas_pais(pais: str):
    count = 0
    for countries in df['production_countries']:
        if countries is not None and pais in countries:
            count += 1
    return {'cantidad de peliculas por pais': count}

#FUNCION PELICULAS POR PRODUCTORA
@app.get("/productoras/{productora}")
def productoras(productora: str): 

    revenue = 0
    movie_count = 0
    for companies, rev in zip(df['production_companies'], df['revenue']):
        if companies is not None and productora in companies:
            revenue += rev
            movie_count += 1
    return {'productora':productora, 'ganancia_total':revenue, 'cantidad':movie_count}            
    


#FUNCION RETORNO DE PELICULA
@app.get("/retorno/{pelicula}")
def retorno(pelicula: str):
    # Filtrar la fila correspondiente al título de la película
    movie_row = df.loc[df['title'] == pelicula]
    
    # Obtener los valores de inversión, ganancia y año de lanzamiento
    budget = movie_row['budget'].values[0]
    revenue = movie_row['revenue'].values[0]
    release_year = movie_row['release_year'].values[0]
    
    # Calcular el retorno y la ganancia
    if budget == 0:
        investment = "Unknown"
        return_on_investment = "Unknown"
    else:
        investment = budget
        return_on_investment = (revenue - budget) / budget
    
    if revenue == 0:
        profit = "Unknown"
    else:
        profit = revenue - budget
    
    # Devolver los valores como un diccionario
    return {'inversion': investment, 
            'ganancia': profit, 
            'retorno': return_on_investment, 
            'año': release_year}
            

@app.get("/franquicia/{nombre_franquicia}")
def franquicia(nombre_franquicia: str):
    # Función lambda para sumar la ganancia de las películas de la franquicia
    sumar_ganancia = lambda x: x['revenue'] if nombre_franquicia in str(x['belongs_to_collection']) else 0

    # Filtrar las filas que corresponden a la franquicia
    franquicia_df = df[df['belongs_to_collection'].apply(lambda x: nombre_franquicia in str(x))]

    # Calcular la ganancia total, promedio y cantidad de películas
    ganancia_total = franquicia_df.apply(sumar_ganancia, axis=1).sum()
    ganancia_promedio = franquicia_df.apply(sumar_ganancia, axis=1).mean()
    cant_peliculas = len(franquicia_df)
    
    return {'franquicia':nombre_franquicia, 'cantidad':cant_peliculas, 'ganancia_total':ganancia_total, 'ganancia_promedio':ganancia_promedio}


@app.get("/recomendacion/{title}")
def recomendacion(title: str):
    movies = pd.read_csv('movies_dataset.csv')
  #Filtra por genero
  # Buscar la película por título
    dfr = movies[movies['title'].str.lower() == title.lower()]

    # Si no se encuentra la película, devuelve un mensaje de error
    if dfr.empty:
        return "No se encontró la película"

    # Obtener la lista de géneros de la película
    genre_list = dfr.iloc[0]['genres'].split(',')

    # Filtrar el dataframe por el género de la película
    metadata = movies[movies['genres'].apply(lambda x: any(item for item in genre_list if item in x.split(',')))]


    
    from sklearn.feature_extraction.text import TfidfVectorizer

    
    tfidf = TfidfVectorizer(stop_words='english')

    
    metadata['overview'] = metadata['overview'].fillna('')

  
    tfidf_matrix = tfidf.fit_transform(metadata['overview'])

    
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    
    indices = pd.Series(metadata.index, index=metadata['title']).drop_duplicates()

    
    idx = indices[title]

    
    sim_scores = list(enumerate(cosine_sim[idx]))

    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    
    sim_scores = sim_scores[1:6]

    
    movie_indices = [i[0] for i in sim_scores]

    
    mi_lista = metadata['title'].iloc[movie_indices].values.tolist()
    return mi_lista