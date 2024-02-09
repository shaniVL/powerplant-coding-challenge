from pydantic import BaseModel, Field
from enum import Enum

class PowerplantType(Enum):
    gasfired = "gasfired"
    turbojet = "turbojet"
    windturbine = "windturbine"

class Fuels(BaseModel):
    gas: float = Field(alias="gas(euro/MWh)")
    kerosine: float = Field(alias="kerosine(euro/MWh)")
    co2: float = Field(alias="co2(euro/ton)")
    wind: float = Field(alias="wind(%)")

class PowerPlant(BaseModel):
    name: str
    type: PowerplantType
    efficiency: float
    pmin: float
    pmax: float

class Payload(BaseModel):
    load: float
    fuels: Fuels
    powerplants: list[PowerPlant]