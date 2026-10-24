# Production image for the Rukmani backend.
#
#   docker build -t rukmani-backend .
#   docker run -p 8000:8000 --env-file .env -v rukmani-data:/data rukmani-backend
#
# Conversations are saved in /data — mount a persistent volume there.

FROM python:3.11-slim

# uv installs the exact versions pinned in uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first, so code changes don't reinstall them (faster rebuilds).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY config ./config
COPY src ./src
RUN uv sync --frozen --no-dev

# Run as a normal user, with a writable folder for the conversations database.
RUN useradd --create-home rukmani && mkdir /data && chown rukmani /data
USER rukmani

ENV PATH="/app/.venv/bin:$PATH" \
    CONVERSATIONS_DB=/data/conversations.sqlite

EXPOSE 8000
# Hosts like Railway pass the port in $PORT. --proxy-headers lets the app see
# the visitor's real IP behind the host's proxy (needed for rate limits).
CMD ["sh", "-c", "uvicorn kapruka_agent.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
