#!/bin/sh
set -e

if ! ls | grep -q "^\.env$"; then
    cp .env.example .env
    echo ".env created from .env.example"
else
    echo ".env already exists, skipping"
fi

INPUT_GID=$(getent group input | cut -d: -f3)
sed -i "s/INPUT_GID=changeme/INPUT_GID=${INPUT_GID}/" .env
echo "Input GID set to ${INPUT_GID}"