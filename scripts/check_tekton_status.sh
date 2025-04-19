#\!/bin/bash

# Simple status check script
echo "Tekton Status Check"
echo "==================="

# Check Hermes API
if curl -s http://localhost:8100/api/health > /dev/null 2>&1; then
    echo "✅ Hermes API is running and responsive"
else
    echo "❌ Hermes API is not running or not responding"
fi

# Check port usage
echo -e "\nTekton Port Status:"
echo "--------------------"

# Function to check port
check_port() {
    local port=$1
    local name=$2
    if lsof -ti :$port > /dev/null 2>&1; then
        local pid=$(lsof -ti :$port)
        local cmd=$(ps -p $pid -o comm= 2>/dev/null)
        echo "Port $port ($name): In use by PID $pid ($cmd)"
    else
        echo "Port $port ($name): Available"
    fi
}

# Check each Tekton port
check_port 8080 "Hephaestus HTTP"
check_port 8081 "Hephaestus WebSocket"
check_port 8000 "Engram Memory"
check_port 8100 "Hermes Service Registry"
check_port 8101 "Hermes Database"
check_port 8200 "Ergon Agent System"
check_port 5005 "Synthesis Engine"

# List running Tekton processes
echo -e "\nRunning Tekton Processes:"
echo "------------------------"
ps aux | grep -E 'hermes|engram|ergon|hephaestus|synthesis' | grep -v grep
