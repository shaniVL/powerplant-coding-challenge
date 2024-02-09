from production_plan.models import Fuels, Payload, PowerPlant, PowerplantType
   
def calculate_merit_order(fuels: Fuels, powerplants: list[PowerPlant]) -> list[str]:
    merit_order: dict[str, float] = {}
    for powerplant in powerplants:
        if powerplant.type == PowerplantType.gasfired:
            merit_order[powerplant.name] = fuels.gas / powerplant.efficiency
        if powerplant.type == PowerplantType.turbojet:
            merit_order[powerplant.name] = fuels.gas / powerplant.efficiency
        if powerplant.type == PowerplantType.windturbine and fuels.wind != 0:
            merit_order[powerplant.name] = 0
    sorted_merit_order = dict(sorted(merit_order.items(), key=lambda item: item[1]))
    
    return list(sorted_merit_order.keys())

def solve_unit_commitment(payload: Payload):
    unit_commitments: list[dict] = []
    merit_order: list[str] = calculate_merit_order(payload.fuels, payload.powerplants)
    for powerplant_name in merit_order:
        powerplant: PowerPlant = list(filter(lambda p: p.name == powerplant_name, payload.powerplants))[0]
        if powerplant.type == PowerplantType.windturbine:
            powerplant.pmax = powerplant.pmax * payload.fuels.wind / 100
        if payload.load == 0:
            unit_commitments.append({
                "name": powerplant_name,
                "p": 0.0
            })
        elif payload.load - powerplant.pmax >= 0:
            unit_commitments.append({
                "name": powerplant_name,
                "p": powerplant.pmax
            })
            payload.load = payload.load - powerplant.pmax
        elif payload.load <= powerplant.pmax and payload.load >= powerplant.pmin:
            unit_commitments.append({
                "name": powerplant_name,
                "p": payload.load
            })
            payload.load = 0
        elif payload.load < powerplant.pmin and len(unit_commitments) == 0:
            unit_commitments.append({
                "name": powerplant_name,
                "p": 0.0
            })
        elif payload.load < powerplant.pmin:
            remainder = powerplant.pmin - payload.load
            unit_commitments[len(unit_commitments) - 1]["p"] -= remainder
            unit_commitments.append({
                "name": powerplant_name,
                "p": powerplant.pmin
            })
            payload.load = 0
    if payload.fuels.wind == 0:
        for windpark in list(filter(lambda p: p.type == PowerplantType.windturbine, payload.powerplants)):
            unit_commitments.append({
                "name": windpark.name,
                "p": 0.0
            })
    return unit_commitments