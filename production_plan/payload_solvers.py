from production_plan.models import Fuels, Payload, PowerPlant, PowerplantType
   
def calculate_merit_order(fuels: Fuels, powerplants: list[PowerPlant]) -> list[str]:
    """Calculates the merit order based on the fuel cost
    as well as the thermal efficiency and returns the names in a list.

    Args:
        fuels (Fuels): representation of fuels containing the cost of each fuel type
        powerplants (list[PowerPlant]): list of powerplants

    Returns:
        list[str]: list of names of powerplants in the correct merit order based
            on the price of the fuel used by the powerplant as well as the thermal
            efficiency of that powerplant.
    """
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

def solve_unit_commitment(payload: Payload) -> list[dict[str, str | float]]:
    """Calculates the unit commitment based on the merit order of the
    given payload and returns a list containing the powerplants that
    need to activate for a given value p to match the necessary load
    for the next hour.
    

    Args:
        payload (Payload): the payload for which the unit commitment needs to be calculated

    Returns:
        list[dict[str, str | float]]: list of dictionaries where each dictionary represents
            a powerstation and the part of the load that that powerstation has to produce.
    """
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