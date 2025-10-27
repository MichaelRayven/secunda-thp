FROM python:3.13-slim

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN pip install uv
RUN uv sync

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]
