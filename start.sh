#!/bin/bash

# Neuro-OCC Bootstrap Script
# One-touch startup: provisions the Python/Node stacks, seeds the database,
# runs health checks, and launches every service needed for the demo.

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ROOT_DIR"

LOG_DIR="$ROOT_DIR/.runtime_logs"
RUNTIME_STATE="$ROOT_DIR/.neuro_occ_runtime"
PY_ENV="venv"

mkdir -p "$LOG_DIR"
mkdir -p "$RUNTIME_STATE"

echo "🚀 Starting Neuro-OCC System"
echo "================================="

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

ensure_root() {
    if [[ ! -f "config.yaml" || ! -d "dashboard" || ! -d "mcp_servers" ]]; then
        print_error "Run this script from the Neuro-OCC project root."
        exit 1
    fi
}

command_exists() { command -v "$1" >/dev/null 2>&1; }

check_port_free() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $port is already in use. Stop the conflicting service first."
        exit 1
    fi
}

wait_for_http() {
    local url=$1
    local name=$2
    local attempts=${3:-40}

    print_status "Waiting for $name ($url)..."
    for ((i=1; i<=attempts; i++)); do
        if curl -sSf "$url" >/dev/null 2>&1; then
            print_success "$name is online"
            return 0
        fi
        sleep 1
    done
    print_error "$name failed to respond within $attempts seconds"
    return 1
}

cleanup() {
    print_warning "Stopping Neuro-OCC services..."
    if [[ -f "$RUNTIME_STATE/pids" ]]; then
        while IFS=: read -r name pid; do
            if [[ -n "$pid" && $(kill -0 "$pid" 2>/dev/null && echo "alive") ]]; then
                print_status "Stopping $name (PID $pid)"
                kill "$pid" 2>/dev/null || true
            fi
        done < "$RUNTIME_STATE/pids"
    fi
    pkill -f "react-scripts start" 2>/dev/null || true
    rm -f "$RUNTIME_STATE/pids"
    print_success "Services stopped."
}

trap cleanup EXIT INT TERM

ensure_root

print_status "Verifying prerequisites..."
command_exists python3 || { print_error "python3 is not installed."; exit 1; }
command_exists node || { print_error "Node.js is required."; exit 1; }
command_exists npm || { print_error "npm is required."; exit 1; }
command_exists curl || { print_error "curl is required."; exit 1; }

# Virtual environment
print_status "Configuring Python environment..."
if [[ ! -d "$PY_ENV" ]]; then
    print_status "Creating virtual environment ($PY_ENV)..."
    python3 -m venv "$PY_ENV"
fi

source "$PY_ENV/bin/activate"
print_success "Virtual environment activated"

pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null
print_success "Python dependencies installed"

export PYTHONPATH="$ROOT_DIR"

# Prepare database
print_status "Preparing database..."
python - <<'PY'
from database import Base, engine, SessionLocal, Pilot, Aircraft, Flight, Airport
from migrate_data import migrate_data

Base.metadata.create_all(bind=engine)

session = SessionLocal()
try:
        has_data = session.query(Pilot).first() is not None
finally:
        session.close()

if not has_data:
        migrate_data()
        print("Database seeded with synthetic data")
else:
        print("Database already populated; skipping seeding")
PY

# Node dependencies
print_status "Installing dashboard dependencies..."
pushd dashboard >/dev/null
npm install --silent
popd >/dev/null
print_success "Node modules ready"

# Ensure ports are free
print_status "Checking port availability..."
for port in 8001 8002 8003 8004 3000; do
    check_port_free "$port"
done
print_success "All ports are available"

echo "" > "$RUNTIME_STATE/pids"

start_service() {
    local name=$1
    local log_file=$2
    shift 2
    "$@" >"$log_file" 2>&1 &
    local pid=$!
    echo "$name:$pid" >> "$RUNTIME_STATE/pids"
    print_status "$name started (PID $pid) — logs: $log_file"
}

print_status "Launching backend services..."
start_service "Crew MCP" "$LOG_DIR/crew_mcp.log" python mcp_servers/crew_mcp.py
start_service "Fleet MCP" "$LOG_DIR/fleet_mcp.log" python mcp_servers/fleet_mcp.py
start_service "Regulatory MCP" "$LOG_DIR/reg_mcp.log" python mcp_servers/reg_mcp.py
start_service "Brain API" "$LOG_DIR/brain_api.log" python brain_api.py

wait_for_http "http://localhost:8001/health" "Crew MCP"
wait_for_http "http://localhost:8002/health" "Fleet MCP"
wait_for_http "http://localhost:8003/health" "Regulatory MCP"
wait_for_http "http://localhost:8004/health" "Brain API"

print_status "Fetching fleet readiness snapshot..."
python - <<'PY'
import requests

summary = {}

try:
        summary['pilots'] = len(requests.get('http://localhost:8001/pilots', timeout=5).json())
except Exception:
        summary['pilots'] = 'unavailable'

try:
        summary['aircraft'] = len(requests.get('http://localhost:8002/aircraft', timeout=5).json())
except Exception:
        summary['aircraft'] = 'unavailable'

try:
        summary['flights'] = len(requests.get('http://localhost:8002/flights', timeout=5).json())
except Exception:
        summary['flights'] = 'unavailable'

print(f"   • Pilots loaded: {summary['pilots']}")
print(f"   • Aircraft loaded: {summary['aircraft']}")
print(f"   • Flights scheduled: {summary['flights']}")
PY

print_status "Starting Neuro-OCC dashboard..."
pushd dashboard >/dev/null
npm start -- --host 0.0.0.0 >"$LOG_DIR/dashboard.log" 2>&1 &
DASHBOARD_PID=$!
popd >/dev/null
echo "Dashboard:$DASHBOARD_PID" >> "$RUNTIME_STATE/pids"
print_status "Dashboard started (PID $DASHBOARD_PID) — logs: $LOG_DIR/dashboard.log"

wait_for_http "http://localhost:3000" "Dashboard" 90

print_success "Neuro-OCC system is live!"
echo ""
echo "� Access points"
echo "   • Dashboard           -> http://localhost:3000"
echo "   • Crew MCP API        -> http://localhost:8001"
echo "   • Fleet MCP API       -> http://localhost:8002"
echo "   • Regulatory MCP API  -> http://localhost:8003"
echo "   • Brain API           -> http://localhost:8004"
echo ""
print_warning "Press Ctrl+C to stop the stack (or run ./stop.sh)"

wait