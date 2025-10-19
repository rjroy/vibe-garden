#!/bin/bash

# Capture the directory where the script was invoked from
invoke_directory="$(pwd)"

source_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd $source_directory/../

if [ ! -d venv ]; then
    python3 -m venv venv
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -e .
fi

if [ -f $invoke_directory/.env ]; then
    source $invoke_directory/.env
    env WYRD_INVOKE_DIR="$invoke_directory"
    venv/bin/python -m wyrd_gen_mcp.server
elif [ -f $invoke_directory/.env.op ]; then
    op run --env-file=$invoke_directory/.env.op -- env WYRD_INVOKE_DIR="$invoke_directory" venv/bin/python -m wyrd_gen_mcp.server
else
    echo "Error: No .env or .env.op file found in '$invoke_directory' directory." >&2
    exit 1
fi
