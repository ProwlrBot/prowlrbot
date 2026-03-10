#!/bin/sh
# Substitute PROWLRBOT_PORT in supervisord template and start supervisord.
# Default port 8088; override at runtime with -e PROWLRBOT_PORT=3000.
set -e
export PROWLRBOT_PORT="${PROWLRBOT_PORT:-8088}"
envsubst '${PROWLRBOT_PORT}' \
  < /etc/supervisor/conf.d/supervisord.conf.template \
  > /etc/supervisor/conf.d/supervisord.conf
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
