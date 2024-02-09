from fastapi import FastAPI
import uvicorn
from production_plan.models import Payload
from production_plan.payload_solvers import solve_unit_commitment

app = FastAPI()

@app.post("/productionplan")
def create_production_plan(payload: Payload):
    return solve_unit_commitment(payload)

if __name__ == "__main__":
    uvicorn.run(app, port=8888)