# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock README.md* ./

# Синхронизируем зависимости в виртуальное окружение
RUN uv sync --frozen --no-dev


# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Создаём non-root пользователя
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 -m -d /home/appuser appuser && \
    chown -R appuser:appuser /app

# Копируем uv из builder stage
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Копируем виртуальное окружение из builder stage
COPY --from=builder /app/.venv /app/.venv

# Копируем код приложения
COPY --chown=appuser:appuser . .

# Переключаемся на non-root пользователя
USER appuser

# Добавляем .venv в PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "poe", "run_server"]
