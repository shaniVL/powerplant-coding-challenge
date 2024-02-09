FROM python:3.10-buster

RUN pip install poetry==1.7.0
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY production_plan ./production_plan

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

EXPOSE 8888

ENTRYPOINT ["poetry", "run", "python3", "-m", "production_plan.api", "0.0.0.0"]