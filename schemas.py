from pydantic import BaseModel, Field



#estructura de la respuesta
class Weather(BaseModel):
    address: str
    temp : float
    tempmax: float
    tempmin: float
    feelslike: float
    humidity : float
    windspeed: float
    winddir: int
    conditions: str
    