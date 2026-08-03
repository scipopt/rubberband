#!/bin/sh
# Container entrypoint. Runs as root to fix up the ownership of mounted
# directories, then drops to the unprivileged 'rubberband' user before handing
# over to the command (server.py by default).
#
# RUBBERBAND_BOOTSTRAP_INDICES=0 skips creating the Elasticsearch indices, for
# instance when running a one-off command against a cluster already set up.
set -e

APP_USER=rubberband
STATIC_DIR=/app/staticfiles

if [ "$(id -u)" = "0" ]; then
    # A volume mounted at staticfiles/ (see docker-compose.yml) is created
    # owned by root, so imports would fail to write their log bundles.
    if [ -d "$STATIC_DIR" ] && [ "$(stat -c '%u' "$STATIC_DIR")" = "0" ]; then
        echo "entrypoint: taking ownership of $STATIC_DIR"
        chown "$APP_USER:$APP_USER" "$STATIC_DIR"
    fi
    set -- gosu "$APP_USER" "$@"
fi

if [ "${RUBBERBAND_BOOTSTRAP_INDICES:-1}" != "0" ]; then
    echo "entrypoint: ensuring Elasticsearch indices exist"
    if [ "$(id -u)" = "0" ]; then
        gosu "$APP_USER" python /app/bin/rubberband-ctl create-indices
    else
        python /app/bin/rubberband-ctl create-indices
    fi
fi

exec "$@"
