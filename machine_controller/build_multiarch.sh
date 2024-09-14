#!/bin/sh
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t ghcr.io/acm-uiuc/merch-embedded:latest --push .
