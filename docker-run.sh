#!/bin/bash

# Briefcase AI Demos - Docker Runner
# Simplified way to run the demos in Docker with briefcase-ai SDK

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Briefcase AI Demos - Docker Runner${NC}"
echo "========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build     Build the Docker image"
    echo "  run       Run a demo interactively"
    echo "  jupyter   Start Jupyter notebook server"
    echo "  test      Test that briefcase-ai is working"
    echo "  shell     Get a shell in the container"
    echo "  clean     Remove containers and images"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build the demo environment"
    echo "  $0 test                     # Test SDK functionality"
    echo "  $0 run                      # Interactive demo selection"
    echo "  $0 jupyter                  # Start Jupyter on http://localhost:8889"
    echo "  $0 shell                    # Get bash shell in container"
}

# Build the Docker image
build_image() {
    echo -e "${GREEN}🔨 Building Briefcase AI demo environment...${NC}"
    docker build -t briefcase-ai-demos .
    echo -e "${GREEN}✅ Build complete!${NC}"
}

# Test briefcase-ai functionality
test_sdk() {
    echo -e "${GREEN}🧪 Testing briefcase-ai SDK...${NC}"
    docker run --rm briefcase-ai-demos python3 -c "
import briefcase
from briefcase import DecisionSnapshot, Input, Output, init
from briefcase.storage import SqliteBackend
print('✅ briefcase-ai imported successfully')
print(f'📦 Available classes: {[attr for attr in dir(briefcase) if not attr.startswith(\"_\")][:10]}')

# Initialize the SDK
init()
print('✅ Initialized briefcase-ai SDK')

# Test basic functionality
decision = DecisionSnapshot('test_function')
decision.add_input(Input('test_input', 'test_value', 'string'))
decision.add_output(Output('test_output', 'test_result', 'string'))
print('✅ Created DecisionSnapshot with Input and Output')

backend = SqliteBackend.in_memory()
decision_id = backend.save_decision(decision)
print(f'✅ Stored decision: {decision_id}')

retrieved = backend.load_decision(decision_id)
print(f'✅ Retrieved decision: {retrieved.function_name}')

print('')
print('🎉 briefcase-ai SDK is working perfectly!')
"
    echo -e "${GREEN}✅ SDK test passed!${NC}"
}

# Run demo interactively
run_demo() {
    echo -e "${GREEN}🚀 Starting Briefcase AI demo environment...${NC}"
    echo ""
    echo "Select a demo to run:"
    echo "1) Vantara Commerce - Agent Discovery"
    echo "2) Vantara Commerce - Cost Attribution"
    echo "3) Vantara Commerce - Peak Season Drift"
    echo "4) Vantara Commerce - Governance Report"
    echo "5) Custom shell (run your own commands)"
    echo ""
    read -p "Choose an option (1-5): " choice

    case $choice in
        1)
            echo -e "${GREEN}Running Agent Discovery Demo...${NC}"
            docker run -it --rm briefcase-ai-demos bash -c "cd vantara-briefcase-demo && python 01_agent_discovery/example.py"
            ;;
        2)
            echo -e "${GREEN}Running Cost Attribution Demo...${NC}"
            docker run -it --rm briefcase-ai-demos bash -c "cd vantara-briefcase-demo && python 02_cost_attribution/example.py"
            ;;
        3)
            echo -e "${GREEN}Running Peak Season Drift Demo...${NC}"
            docker run -it --rm briefcase-ai-demos bash -c "cd vantara-briefcase-demo && python 03_peak_season_drift/example.py"
            ;;
        4)
            echo -e "${GREEN}Running Governance Report Demo...${NC}"
            docker run -it --rm briefcase-ai-demos bash -c "cd vantara-briefcase-demo && python 04_governance_report/example.py"
            ;;
        5)
            echo -e "${GREEN}Opening interactive shell...${NC}"
            docker run -it --rm briefcase-ai-demos bash
            ;;
        *)
            echo "Invalid option"
            exit 1
            ;;
    esac
}

# Start Jupyter notebook
start_jupyter() {
    echo -e "${GREEN}🪐 Starting Jupyter notebook server...${NC}"
    echo ""
    echo "Jupyter will be available at: http://localhost:8889"
    echo "No password required - notebooks are in the mounted directories"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""

    docker run -it --rm \
        -p 8889:8888 \
        -v "$(pwd)/vantara-briefcase-demo:/app/vantara-briefcase-demo" \
        -v "$(pwd)/regulatory-workflows:/app/regulatory-workflows" \
        briefcase-ai-demos \
        jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.token='' --NotebookApp.password=''
}

# Get shell access
get_shell() {
    echo -e "${GREEN}🐚 Opening interactive shell...${NC}"
    docker run -it --rm \
        -v "$(pwd)/vantara-briefcase-demo:/app/vantara-briefcase-demo" \
        -v "$(pwd)/regulatory-workflows:/app/regulatory-workflows" \
        briefcase-ai-demos bash
}

# Clean up
clean_up() {
    echo -e "${GREEN}🧹 Cleaning up Docker resources...${NC}"
    docker rm -f briefcase-ai-demos briefcase-ai-jupyter 2>/dev/null || true
    docker rmi briefcase-ai-demos 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Main execution
case "${1:-}" in
    build)
        build_image
        ;;
    test)
        test_sdk
        ;;
    run)
        run_demo
        ;;
    jupyter)
        start_jupyter
        ;;
    shell)
        get_shell
        ;;
    clean)
        clean_up
        ;;
    *)
        show_usage
        exit 1
        ;;
esac