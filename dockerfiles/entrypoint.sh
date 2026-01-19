#!/bin/bash
set -e

# Fetch WANDB_API_KEY from Google Cloud Secret Manager if not already set
if [ -z "$WANDB_API_KEY" ]; then
    echo "Fetching WANDB_API_KEY from Secret Manager..."

    # Try to fetch the secret, capture both stdout and stderr
    SECRET_OUTPUT=$(gcloud secrets versions access latest --secret="WANDB_API_KEY" 2>&1) && SECRET_SUCCESS=true || SECRET_SUCCESS=false

    if [ "$SECRET_SUCCESS" = true ]; then
        export WANDB_API_KEY="$SECRET_OUTPUT"
        echo "WANDB_API_KEY loaded from Secret Manager"
    else
        echo "WARNING: Could not fetch WANDB_API_KEY from Secret Manager."
        echo "Error: $SECRET_OUTPUT"
        echo "wandb logging may not work."
    fi
fi

# Set wandb mode (default to online)
export WANDB_MODE=${WANDB_MODE:-online}

# Execute the main command
exec uv run python main.py "$@"
