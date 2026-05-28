from fastapi import FastAPI, HTTPException, Request
#El parametro request: Request, Slowapi necesita el objeto request para poder leer
#la ip del usuario. Sin 'el no puede identificar quien está haciendo la petición y 
#el limite no funciona

#Request es un objeto de FastAPI que representa la peticion HTTP que llega a tu server
#Contiene toda la informacion de la peticion: Headers, IP del cliente, Cookies, body, etc
#Request:
# GET /weather/Barranquilla HTTP/1.1
# Host: localhost:8000
# Accept: application/json
# User-Agent: Mozilla/5.0
# X-Forwarded-For: 192.168.1.105

from slowapi import Limiter, _rate_limit_exceeded_handler
#Limiter es la clase principal que maneja el rate limiting
#_rate_limit_exceeded_handler la funcion que devuelve el error

from slowapi.util import get_remote_address
#get_remote_address funcion que obtiene la IP del usuario que hace la peticion

from slowapi.errors import RateLimitExceeded
#la excepcion que se lanza cuando se supera el limite

from scalar_fastapi import get_scalar_api_reference
from typing import Any
from schemas import Weather
import os
from dotenv import load_dotenv
import httpx
import redis
import json


redis_client = redis.Redis(host="localhost", port=6379, db=0)


app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



load_dotenv()

api_key = os.getenv("VISUAL_CROSSING_API_KEY")


@app.get('/cached_weather_keys')
def get_cached_weather_keys():
    keys = redis_client.keys("*")
    return keys


@app.get("/weather/{address}")
@limiter.limit("3/minute")
def get_weather(request: Request, address: str) -> Weather:

    cache_key = address.lower()

    cached = redis_client.get(cache_key)
    # busca en redis si existe una clave con ese nombre.
    # devuelve los datos en BYTES o devuelve None si no existe

    # si existe la ciudad en el redis cache
    if cached:
        return Weather(**json.loads(cached.decode("utf-8")))

        # cached.decode('utf-8') Redis devuelve bytes: b'{"address":"Barranquilla"...}', no devuelve texto
            # .decode('utf-8') convierte esos bytes a string normal de Python

            ## Antes (bytes)
            # b'{"address": "Barranquilla", "temp": 33.0}'

            # # Después del decode (string)
            # '{"address": "Barranquilla", "temp": 33.0}'

        # json.loads(..) convierte el string JSON a un diccionario de python, lo contrario de json.dumps()
            #json.loads('{"address": "Barranquilla"}')  
            # → {'address': 'Barranquilla'}

        #Weather(**diccionario)
        #El ** desempaqueta el diccionario y lo pasa como argumentos a la clase. Es equivalente a:
        #Weather(address='Barranquilla', temp=33.0, ...)

        ## Con **
            # Weather(**{'address': 'Barranquilla', 'temp': 33.0, 'tempmax': 34.0})

            # # Sin **, equivalente manual
            # Weather(
            #     address='Barranquilla',
            #     temp=33.0,
            #     tempmax=34.0,
            #     # ... todos los campos uno por uno
            # )




    request_example = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{address}?key={api_key}"
    response = httpx.get(request_example)  # hace una peticion HTTP GET a la url de VisualCrossing, ese json se guarda en response

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail='City not found.'
        )

    data = response.json()  # convierte la respuesta a un diccionario en python
    ResponseWeather = Weather(
        address=data["address"],
        temp=data["currentConditions"]["temp"],
        tempmax=data["days"][0]["tempmax"],
        tempmin=data["days"][0]["tempmin"],
        humidity=data["currentConditions"]["humidity"],
        windspeed=data["currentConditions"]["windspeed"],
        winddir=data["currentConditions"]["winddir"],
        conditions=data["currentConditions"]["conditions"],
        feelslike=data["currentConditions"]["feelslike"],
    )
    redis_client.set(cache_key, json.dumps(ResponseWeather.model_dump()), ex=1800)
    # ResponseWeather.model_dump()
    # Convierte el objeto Pydantic a diccionario de Python, ResponseWeather es un objeto, hay que convertirlo a diccionario
    # y cuando se convierta a diccionario, se convierte a json con json.dumps

    #entonces el redis_client.set(key, value, tiempo de expiracion)
    # key = cache_key == address
    # value = toda la info adentro del objeto, address, temp, tempmax (address tambien)
    return ResponseWeather


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
