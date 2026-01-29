#!/bin/bash
set -e

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

case "${1:-upgrade}" in
    upgrade)
        echo "Running database migrations..."
        alembic upgrade head
        ;;
    downgrade)
        echo "Downgrading database..."
        alembic downgrade "${2:--1}"
        ;;
    revision)
        echo "Creating new migration..."
        alembic revision --autogenerate -m "${2:-auto}"
        ;;
    history)
        echo "Migration history:"
        alembic history
        ;;
    *)
        echo "Usage: $0 {upgrade|downgrade|revision|history}"
        exit 1
        ;;
esac
