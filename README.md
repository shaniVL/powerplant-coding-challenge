# Powerplant coding challenge

I used FastAPI to create the api for a couple of reasons:
* it is very easy and very fast to create apis 
* documentation is nearly fully automatic
* pydantic is already integrated so data validation is easy
* it has integrated test clients that integrate easily with pytest

## Pre-requisites
This repository uses poetry as a dependency manager. See the [installation instructions](https://python-poetry.org/docs/#installation) for how to install the tool.

## Instructions
To run locally you can use poetry install to install the necessary production dependencies and then run api.py using python3.
```bash
poetry install --no-root
poetry run python3 -m production_plan.api
```

This will run the endpoint on http://localhost:8888/production_plan and accepts jsons in a format similar to the ones in [example_payloads](example_payloads/)

It is also possible to run the api through the docker container:
```bash
docker build --rm -t production_plan:latest -f Dockerfile .
docker run --rm -p 8888:8888 production_plan
```

## Usage
An easy way to use the api is through a python shell that has access to the requests module. This is a part of the dev dependencies of the [pyproject.toml](pyproject.toml) file and can be installed using:
```bash
poetry install --no-root --with dev
```
You can then try out the endpoint with the utility script [call_endpoint.py](call_endpoint.py) that a path to a payload json as an argument.
```bash
poetry run python3 call_endpoint.py example_payloads/payload1.json
```

## Tests
Unit tests are included for the functions in [payload_solvers.py](production_plan/payload_solvers.py). These can be run with pytest which is part of the development dependencies:
```bash
poetry install --no-root --with dev
poetry run pytest
```