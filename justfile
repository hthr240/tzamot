# Optional wrappers around the local launcher.
# Install Just: https://github.com/casey/just

set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
set shell := ["bash", "-cu"]

# Start DB, migrate, API (:8000), and frontend (:5500).
# Pass --seed to load the fixed dataset after migrations.
up *args:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ "{{os()}}" == "windows" ]]; then
      powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./dev-up.ps1 {{args}}
    else
      ./dev-up.sh {{args}}
    fi

# Stop the database container without deleting its volume.
down:
    docker compose down
