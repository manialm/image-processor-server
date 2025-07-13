FROM python:3.12

WORKDIR /app

SHELL ["/bin/bash", "-c"]

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN source ~/.local/bin/env
ENV PATH="$HOME/.local/bin/:$PATH"

COPY . .

CMD ~/.local/bin/uv run -- python3 main.py
# CMD uv run -- python3 main.py
