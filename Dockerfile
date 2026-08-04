# Rubberband. Build from the repository root:
#
#     docker build -t rubberband .
#
# The image expects an Elasticsearch instance to talk to; see docker-compose.yml
# for a stack that brings one up alongside it.

FROM python:3.13-slim AS builder

# git: requirements.txt installs IPET straight from GitHub.
# build-essential and the libxml2/libxslt headers: only needed if pip has to
# build a wheel from source for this platform.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Dependencies first, so that editing application code does not reinstall them.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements-dev.txt

# Rubberband itself, installed editable so that a bind-mounted source tree
# (see docker-compose.yml) is what actually gets imported.
WORKDIR /app
COPY . /app
RUN pip install --no-deps -e .


FROM python:3.13-slim AS runtime

# Shared libraries the lxml wheel links against, curl for the healthcheck, and
# gosu so that the entrypoint can drop privileges after fixing up mounts.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libxml2 \
        libxslt1.1 \
        curl \
        gosu \
        make \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY . /app

# The application runs as this user; the entrypoint switches to it after it has
# adjusted the ownership of anything mounted into the container. Pass
# `--user <uid>` (or `user:` in compose) to run as somebody else instead, in
# which case the entrypoint skips that step.
RUN useradd --create-home --uid 1000 rubberband && \
    chown -R rubberband:rubberband /app

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fs http://localhost:8888/ -o /dev/null || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "server.py"]
