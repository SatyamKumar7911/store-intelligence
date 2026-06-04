#!/bin/bash
set -e

VIDEO_PATH=$1

if [ -z "$VIDEO_PATH" ]; then
    echo "Usage: ./run.sh <path_to_video>"
    exit 1
fi

python3 -m pipeline.detect --video "$VIDEO_PATH"
