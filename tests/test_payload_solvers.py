import pytest

from pytest import FixtureRequest

from production_plan.models import Fuels, Payload, PowerPlant
from production_plan.payload_solvers import calculate_merit_order, solve_unit_commitment

@pytest.fixture
def fuels() -> Fuels:
    return Fuels.model_validate({
        "gas(euro/MWh)": 6,
        "kerosine(euro/MWh)": 50,
        "co2(euro/ton)": 20,
        "wind(%)": 60
    })

@pytest.fixture
def fuels_no_wind() -> Fuels:
    return Fuels.model_validate({
        "gas(euro/MWh)": 6,
        "kerosine(euro/MWh)": 50,
        "co2(euro/ton)": 20,
        "wind(%)": 0
    })

@pytest.fixture
def gasfired1() -> PowerPlant:
    return PowerPlant.model_validate({
        "name": "gasfiredbig1",
        "type": "gasfired",
        "efficiency": 0.50,
        "pmin": 100,
        "pmax": 460
    })

@pytest.fixture
def gasfired2() -> PowerPlant:
    return PowerPlant.model_validate({
        "name": "gasfiredbig2",
        "type": "gasfired",
        "efficiency": 0.60,
        "pmin": 100,
        "pmax": 460
    })

@pytest.fixture
def turbojet1() -> PowerPlant:
    return PowerPlant.model_validate({
        "name": "tj1",
        "type": "turbojet",
        "efficiency": 0.3,
        "pmin": 0,
        "pmax": 16
    })

@pytest.fixture
def windturbine1() -> PowerPlant:
    return PowerPlant.model_validate({
        "name": "windpark1",
        "type": "windturbine",
        "efficiency": 1,
        "pmin": 0,
        "pmax": 150
    })

@pytest.mark.parametrize("powerplant",[
    "gasfired1", "turbojet1", "windturbine1"
])
def test_basic_calculate_merit_order(fuels, powerplant, request: FixtureRequest):
    powerplant = request.getfixturevalue(powerplant)
    assert calculate_merit_order(fuels=fuels, powerplants=[powerplant]) == [powerplant.name]

def test_basic_calculate_merit_order_no_wind(fuels_no_wind, windturbine1):
    assert calculate_merit_order(fuels=fuels_no_wind, powerplants=[windturbine1]) == []

def test_basic_sort_calculate_merit_order(fuels, gasfired1, gasfired2):
    assert calculate_merit_order(fuels=fuels, powerplants=[gasfired1, gasfired2]) == ["gasfiredbig2", "gasfiredbig1"]

@pytest.fixture
def powerplants(gasfired1, gasfired2, windturbine1, turbojet1):
    return [gasfired1, gasfired2, windturbine1, turbojet1]

def test_calculate_merit_order(fuels, powerplants):
    assert calculate_merit_order(fuels=fuels, powerplants=powerplants) == ["windpark1", "gasfiredbig2", "gasfiredbig1", "tj1"]

def test_calculate_merit_order_no_wind(fuels_no_wind, powerplants):
    assert calculate_merit_order(fuels=fuels_no_wind, powerplants=powerplants) == ["gasfiredbig2", "gasfiredbig1", "tj1"]

@pytest.fixture
def payload(fuels, powerplants):
    return Payload(load=480, fuels=fuels, powerplants=powerplants)
    
def test_solve_commitment_exact_match(fuels, gasfired1, gasfired2):
    payload = Payload(load=460, fuels=fuels, powerplants=[gasfired1, gasfired2])
    assert solve_unit_commitment(payload) == [
        {
            "name": "gasfiredbig2",
            "p": 460.0
        },
        {
            "name": "gasfiredbig1",
            "p": 0.0
        }
    ]

def test_solve_commitment_leftover_above_pmin(fuels, gasfired1, gasfired2):
    payload = Payload(load=600, fuels=fuels, powerplants=[gasfired1, gasfired2])
    assert solve_unit_commitment(payload) == [
        {
            "name": "gasfiredbig2",
            "p": 460.0
        },
        {
            "name": "gasfiredbig1",
            "p": 140.0
        }
    ]

def test_solve_commitment_leftover_below_pmin(fuels, gasfired1, gasfired2):
    payload = Payload(load=480, fuels=fuels, powerplants=[gasfired1, gasfired2])
    assert solve_unit_commitment(payload) == [
            {
                "name": "gasfiredbig2",
                "p": 380.0
            },
            {
                "name": "gasfiredbig1",
                "p": 100.0
            }
        ]

@pytest.fixture
def gasfired3():
    return PowerPlant.model_validate({
        "name": "gasfiredsomewhatsmaller",
        "type": "gasfired",
        "efficiency": 0.37,
        "pmin": 40,
        "pmax": 210
    },)

def test_solve_commitment_leftover_below_pmin_first_in_order(fuels, gasfired1, gasfired3):
    payload = Payload(load=40, fuels=fuels, powerplants=[gasfired1, gasfired3])
    assert solve_unit_commitment(payload) == [
            {
                "name": "gasfiredbig1",
                "p": 0.0
            },
            {
                "name": "gasfiredsomewhatsmaller",
                "p": 40.0
            }
        ]

def test_solve_commitment_gas_and_turbo(fuels, gasfired1, gasfired2, gasfired3, turbojet1):
    payload = Payload(load=1146, fuels=fuels, powerplants=[gasfired1, gasfired2, gasfired3, turbojet1])
    assert solve_unit_commitment(payload) == [
        {
            "name": "gasfiredbig2",
            "p": 460.0
        },
        {
            "name": "gasfiredbig1",
            "p": 460.0
        },
        {
            "name": "gasfiredsomewhatsmaller",
            "p": 210.0
        },
        {
            "name": "tj1",
            "p": 16.0
        },
    ]

def test_solve_commitment_wind_gas(fuels, gasfired1, gasfired2, windturbine1):
    payload = Payload(load=480, fuels=fuels, powerplants=[gasfired1, gasfired2, windturbine1])
    assert solve_unit_commitment(payload) == [
        {
            "name": windturbine1.name,
            "p": 90.0
        },
        {
            "name": gasfired2.name,
            "p": 390.0
        },
        {
            "name": gasfired1.name,
            "p": 0.0
        }
    ]

def test_solve_commitment_wind_gas_no_wind(fuels_no_wind, gasfired1, gasfired2, windturbine1):
    payload = Payload(load=480, fuels=fuels_no_wind, powerplants=[gasfired1, gasfired2, windturbine1])
    assert solve_unit_commitment(payload) == [
        {
            "name": gasfired2.name,
            "p": 380.0
        },
        {
            "name": gasfired1.name,
            "p": 100.0
        },
        {
            "name": windturbine1.name,
            "p": 0.0
        }
    ]