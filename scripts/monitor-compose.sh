#!/usr/bin/env bash
# Monitor the Compose stack from the host. This script must not run in a
# container: Docker socket access grants root-equivalent host privileges.
set -euo pipefail

: "${PROJECT_DIR:?Set PROJECT_DIR in /etc/web-church-monitor.env}"

DOCKER_BIN="${DOCKER_BIN:-docker}"
CURL_BIN="${CURL_BIN:-curl}"
STATE_DIRECTORY="${STATE_DIRECTORY:-/var/lib/web-church-monitor}"
STATE_FILE="$STATE_DIRECTORY/state.tsv"
SERVICES="${SERVICES:-db web photo support-bot caddy}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env}"
BOT_TOKEN_FILE="${BOT_TOKEN_FILE:-$PROJECT_DIR/secrets/bot_token}"

umask 077
mkdir -p "$STATE_DIRECTORY"

if [[ ! -r "$ENV_FILE" ]]; then
    echo "Monitor cannot read project .env file: $ENV_FILE" >&2
    exit 1
fi

# Parse only a numeric Telegram chat ID. Group and channel IDs are negative.
# Do not source .env: it is
# configuration data, not shell code, and must never be executed by systemd.
if [[ -z "${CHAT_ID:-}" ]]; then
    CHAT_ID="$(sed -nE 's/^CHAT_ID=(-?[0-9]+)[[:space:]]*$/\1/p' "$ENV_FILE" | tail -n 1)"
fi
if [[ ! "$CHAT_ID" =~ ^-?[0-9]+$ || "$CHAT_ID" == "0" ]]; then
    echo "Monitor requires a non-zero numeric CHAT_ID in $ENV_FILE" >&2
    exit 1
fi

if [[ ! -r "$BOT_TOKEN_FILE" ]]; then
    echo "Monitor cannot read BOT_TOKEN_FILE: $BOT_TOKEN_FILE" >&2
    exit 1
fi

BOT_TOKEN="$(<"$BOT_TOKEN_FILE")"
if [[ -z "$BOT_TOKEN" ]]; then
    echo "Monitor BOT_TOKEN_FILE is empty: $BOT_TOKEN_FILE" >&2
    exit 1
fi

notify() {
    local text="$1"
    "$CURL_BIN" --fail --silent --show-error --max-time 15 \
        --data-urlencode "chat_id=$CHAT_ID" \
        --data-urlencode "text=$text" \
        "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" >/dev/null
}

previous_value() {
    local service="$1"
    [[ -f "$STATE_FILE" ]] || return 0
    awk -F $'\t' -v service="$service" '$1 == service { print $2 "\t" $3; exit }' "$STATE_FILE"
}

write_state() {
    local temporary_file
    temporary_file="$(mktemp "$STATE_DIRECTORY/state.tsv.XXXXXX")"
    printf '%s\n' "$@" >"$temporary_file"
    mv "$temporary_file" "$STATE_FILE"
}

is_initial_run=false
if [[ ! -f "$STATE_FILE" ]]; then
    is_initial_run=true
fi

if ! "$DOCKER_BIN" compose --project-directory "$PROJECT_DIR" version >/dev/null 2>&1; then
    previous="$(previous_value __docker__ || true)"
    if [[ "$is_initial_run" == false && "${previous%%$'\t'*}" != "docker-unavailable" ]]; then
        notify $'🚨 ALARM\nweb_church monitor: Docker Compose is unavailable on the host.'
    fi
    write_state $'__docker__\tdocker-unavailable\t0'
    exit 1
fi

next_state=()
if [[ "$is_initial_run" == false ]]; then
    previous_docker="$(previous_value __docker__ || true)"
    if [[ "${previous_docker%%$'\t'*}" == "docker-unavailable" ]]; then
        notify $'✅ RECOVERED\nweb_church monitor: Docker Compose is available again.'
    fi
fi
next_state+=( $'__docker__\tok\t0' )

for service in $SERVICES; do
    previous="$(previous_value "$service" || true)"
    previous_status="${previous%%$'\t'*}"
    previous_restart="${previous#*$'\t'}"
    [[ "$previous" == "$previous_restart" ]] && previous_restart=""

    container_id="$("$DOCKER_BIN" compose --project-directory "$PROJECT_DIR" ps --all --quiet "$service" | head -n 1)"
    if [[ -z "$container_id" ]]; then
        status="missing"
        restart_count=0
    else
        inspection="$("$DOCKER_BIN" inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.RestartCount}}' "$container_id")"
        IFS='|' read -r container_status health_status restart_count <<<"$inspection"
        case "$container_status:$health_status" in
            running:|running:healthy|running:starting)
                status="ok"
                ;;
            running:*)
                status="unhealthy"
                ;;
            *)
                status="$container_status"
                ;;
        esac
    fi

    next_state+=( "$service"$'\t'"$status"$'\t'"$restart_count" )

    if [[ "$is_initial_run" == true ]]; then
        continue
    fi

    if [[ "$status" == "ok" ]]; then
        if [[ -n "$previous_status" && "$previous_status" != "ok" ]]; then
            notify $'✅ RECOVERED\nweb_church: container '"'$service'"$' is healthy again.'
        elif [[ -n "$previous_restart" && "$restart_count" -gt "$previous_restart" ]]; then
            notify $'🚨 ALARM\nweb_church: container '"'$service'"$' restarted unexpectedly (restart count: '"$restart_count"$').'
        fi
    elif [[ "$status" != "$previous_status" ]]; then
        notify $'🚨 ALARM\nweb_church: container '"'$service'"$' is '"$status"$'.'
    fi
done

write_state "${next_state[@]}"
