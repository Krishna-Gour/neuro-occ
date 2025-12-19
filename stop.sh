#!/bin/bash

# Neuro-OCC Stop Script
# This script stops all Neuro-OCC services

echo "🛑 Stopping Neuro-OCC System..."
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Attempt graceful shutdown using runtime PID registry
RUNTIME_STATE=".neuro_occ_runtime/pids"

if [ -f "$RUNTIME_STATE" ]; then
    print_status "Stopping services via runtime registry..."
    while IFS=: read -r name pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            print_status "Stopping $name (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "$name still running, forcing shutdown"
                kill -9 "$pid" 2>/dev/null || true
            fi
            print_success "$name stopped"
        fi
    done < "$RUNTIME_STATE"
    rm -f "$RUNTIME_STATE"
else
    print_status "Runtime registry not found; falling back to port-based shutdown"
fi

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local name=$2

    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        print_status "Stopping $name on port $port (PID: $pid)..."
        kill $pid 2>/dev/null || true
        sleep 2
        # Check if it's still running
        if lsof -ti:$port >/dev/null 2>&1; then
            print_warning "Force killing $name..."
            kill -9 $pid 2>/dev/null || true
        fi
        print_success "$name stopped"
    else
        print_status "$name not running on port $port"
    fi
}

# Stop services by port (fallback / double-check)
kill_port 3000 "Dashboard"
kill_port 8004 "Brain API"
kill_port 8003 "Regulatory MCP"
kill_port 8002 "Fleet MCP"
kill_port 8001 "Crew MCP"

# Kill any remaining Python processes related to the project
print_status "Cleaning up any remaining Python processes..."
pkill -f "python.*mcp_server" 2>/dev/null || true
pkill -f "python.*brain_api" 2>/dev/null || true
pkill -f "python.*crew_mcp" 2>/dev/null || true
pkill -f "python.*fleet_mcp" 2>/dev/null || true
pkill -f "python.*reg_mcp" 2>/dev/null || true

# Kill React development server
print_status "Cleaning up React development server..."
pkill -f "react-scripts start" 2>/dev/null || true

print_success "🧹 Neuro-OCC System stopped and cleaned up!"
echo ""
echo "💡 To restart the system, run: ./start.sh"