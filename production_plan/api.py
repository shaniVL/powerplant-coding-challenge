import uvicorn
import sys

from fastapi import FastAPI
from production_plan.models import Payload
from production_plan.payload_solvers import solve_unit_commitment

app = FastAPI()

@app.post("/productionplan")
def create_production_plan(payload: Payload):
    return solve_unit_commitment(payload)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        uvicorn.run(app, port=8888)
    else:
        # For use in docker container to run on 0.0.0.0
        uvicorn.run(app, host=sys.argv[1], port=8888)