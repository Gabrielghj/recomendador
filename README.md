

INTRODUCCION 

El presente trabajo consiste en un modelo de recomendación,para ser 
utilizado en una startup que provee servicios de agregación de plataformas de streaming.

El mismo fue realizado en su totalidad en Google Colaboratory.
El enlace para accederlo es el siguiente:

	https://colab.research.google.com/drive/10Llk8kH9GojGcxBC9d7cxF356K6Vqiev?usp=sharing


MPV

Las transformaciónes consisten, en desanidar los campos previstos por el 
Dataset para poder ser accedidos, eliminar o rellenar valores nulos con ceros, modificar el formato 
de fecha crear nuevas columnas necesarias para utilizar en los en points requeridos y eliminar 
columnas no utilizadas.

API

Disponibilizar los datos de la empresa usando el framework FastAPI.
Se crean 6 funciones para los endpoints que se consumirán en la API

def peliculas_mes(mes): '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se 
estrenaron ese mes (nombre del mes, en str, ejemplo 'enero') historicamente''' return {'mes':mes, 'cantidad':respuesta}

def peliculas_dia(dia): '''Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron 
ese dia (de la semana, en str, ejemplo 'lunes') historicamente''' return {'dia':dia, 'cantidad':respuesta}

def franquicia(franquicia): '''Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y 
promedio''' return {'franquicia':franquicia, 'cantidad':respuesta, 'ganancia_total':respuesta, 'ganancia_promedio':respuesta}

def peliculas_pais(pais): '''Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo''' 
return {'pais':pais, 'cantidad':respuesta}

def productoras(productora): '''Ingresas la productora, retornando la ganancia total y la cantidad de peliculas 
que produjeron''' return {'productora':productora, 'ganancia_total':respuesta, 'cantidad':respuesta}

def retorno(pelicula): '''Ingresas la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que 
se lanzo''' return {'pelicula':pelicula, 'inversion':respuesta, 'ganacia':respuesta,'retorno':respuesta, 'anio':respuesta}


SISTEMA DE RECOMENDACION

Se crea un sistema que recomienda películas similares a una película en elegida. 
Para ello se calcula los puntajes de similitud por pares para todas las películas en función de sus descripciones de trama y 
recomenda películas basadas en ese  puntuación de similitud coseno
