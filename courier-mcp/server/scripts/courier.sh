#!/bin/bash

# Capture the directory where the script was invoked from
invoke_directory="$(pwd)"

source_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd $source_directory/../

if [ ! -d venv ]; then
    python3 -m venv venv
fi

venv/bin/pip install --upgrade pip
venv/bin/pip install -e .


if [ -f $invoke_directory/.env ]; then
    source $invoke_directory/.env
    export INVOKE_DIR="$invoke_directory"
    venv/bin/python -m courier_mcp.server
elif [ -f $invoke_directory/.env.op ]; then
    op run --env-file=$invoke_directory/.env.op -- env INVOKE_DIR="$invoke_directory" venv/bin/python -m courier_mcp.server
else
    export INVOKE_DIR="$invoke_directory"
    venv/bin/python -m courier_mcp.server
fi
