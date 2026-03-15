#!/usr/bin/env bash
set -e

if command -v bashio &> /dev/null; then
    VOICE=$(bashio::config 'voice')
    DEBUG=$(bashio::config 'debug')
else
    CONFIG_PATH=/data/options.json
    VOICE=$(jq -r '.voice // "af_heart"' "$CONFIG_PATH")
    DEBUG=$(jq -r '.debug // false' "$CONFIG_PATH")
fi

ARGS=(--host "0.0.0.0" --port "10200" --voice "$VOICE")
[ "$DEBUG" = "true" ] && ARGS+=(--debug)

# Register the Wyoming service with the HA Supervisor.
# HA addon hostnames use {repo}_{slug} format (underscores), but DNS requires
# hyphens — this normalization is critical for the URI to resolve correctly.
send_discovery() {
    local max_wait=300
    local waited=0
    echo "Waiting for Wyoming server to be ready..."
    while [ $waited -lt $max_wait ]; do
        if echo '{"type":"describe"}' | nc -w 2 localhost 10200 2>/dev/null | grep -q "Kokoro"; then
            echo "Server ready after ${waited}s"
            break
        fi
        sleep 2
        waited=$((waited + 2))
    done

    if [ -n "$SUPERVISOR_TOKEN" ]; then
        local hostname
        hostname=$(hostname | tr '_' '-')
        echo "Registering Wyoming discovery: tcp://${hostname}:10200"
        local retry=0
        while [ $retry -lt 3 ]; do
            local resp
            resp=$(curl -s -X POST \
                -H "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
                -H "Content-Type: application/json" \
                -d "{\"service\": \"wyoming\", \"config\": {\"uri\": \"tcp://${hostname}:10200\"}}" \
                "http://supervisor/discovery" 2>&1)
            if echo "$resp" | grep -q '"result".*"ok"'; then
                echo "Discovery registered successfully"
                return 0
            fi
            retry=$((retry + 1))
            sleep 2
        done
        echo "Warning: discovery registration failed after 3 attempts"
    else
        echo "No SUPERVISOR_TOKEN — skipping discovery (not running in HA)"
    fi
}

send_discovery &

exec python3 -m kokoro_wyoming "${ARGS[@]}"
