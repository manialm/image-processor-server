FROM python:3.12

WORKDIR /workspace

SHELL ["/bin/bash", "-c"]

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .
RUN uv sync --locked

CMD ["uv", "run", "--", "fastapi", "run", "app/api.py"]