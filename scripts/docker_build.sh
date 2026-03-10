#!/usr/bin/env bash
# Build Docker image (includes console frontend build in multi-stage).
# Run from repo root: bash scripts/docker_build.sh [IMAGE_TAG] [EXTRA_ARGS...]
# Example: bash scripts/docker_build.sh prowlrbot:latest
#          bash scripts/docker_build.sh myreg/prowlrbot:v1 --no-cache
#
# By default the Docker image excludes imessage and discord channels.
# Override via:
#   PROWLRBOT_ENABLED_CHANNELS=imessage,discord,dingtalk,feishu,qq,console \
#       bash scripts/docker_build.sh
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

DOCKERFILE="${DOCKERFILE:-$REPO_ROOT/deploy/Dockerfile}"
TAG="${1:-prowlrbot:latest}"
shift || true

# Channels to include in the image (default: exclude imessage & discord).
ENABLED_CHANNELS="${PROWLRBOT_ENABLED_CHANNELS:-dingtalk,feishu,qq,console}"

echo "[docker_build] Building image: $TAG (Dockerfile: $DOCKERFILE)"
docker build -f "$DOCKERFILE" \
    --build-arg PROWLRBOT_ENABLED_CHANNELS="$ENABLED_CHANNELS" \
    -t "$TAG" "$@" .
echo "[docker_build] Done."
echo "[docker_build] ProwlrBot app port: 8088 (default). Override with -e PROWLRBOT_PORT=<port>."
echo "[docker_build] Run: docker run -p 8088:8088 $TAG"
echo "[docker_build] Or:  docker run -e PROWLRBOT_PORT=3000 -p 3000:3000 $TAG"
