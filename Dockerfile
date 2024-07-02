FROM --platform=linux/amd64 python:3.11-slim as builder

RUN pip install poetry==1.6.1

# Note: We belive that we don't expose secrets ONLY because we are using a multi-stage build
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --no-root --no-cache

FROM --platform=linux/amd64 laudio/pyodbc:3.0.0 as runtime

WORKDIR /app
RUN addgroup --gid 1001 pyuser && adduser --system --uid 1000 --ingroup pyuser pyuser 

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN chown -R pyuser:pyuser .

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY naturalien ./naturalien

USER pyuser

# CMD ["ls", "naturalien"]
CMD ["python", "-m", "streamlit", "run", "naturalien/app.py", "--server.address", "0.0.0.0", "--server.port", "8080"]