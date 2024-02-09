import uvicorn
import sys

from fastapi import FastAPI
from production_plan.models import Payload
from production_plan.payload_solvers import solve_unit_commitment

app = FastAPI()

@app.post("/productionplan")
def create_production_plan(payload: Payload) -> list[dict]:
    """Endpoint used to calculate the production plan for the given payload

    Args:
        payload (Payload): the payload passed to the endpoint as a json 
            cast to a pydantic model by fastapi.

    Returns:
        list[dict]: the production plan as a list of dictionaries
    """
    return solve_unit_commitment(payload)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        uvicorn.run(app, port=8888)
    else:
        # For use in docker container to run on 0.0.0.0
        uvicorn.run(app, host=sys.argv[1], port=8888)