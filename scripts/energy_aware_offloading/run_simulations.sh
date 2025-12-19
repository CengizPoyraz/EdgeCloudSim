#!/bin/bash

##############################################################
# EdgeCloudSim Energy-Aware Offloading Simulation Runner
##############################################################

echo "=================================================="
echo "Energy-Aware Task Offloading Simulation Runner"
echo "=================================================="

# Default parameters
PARALLEL_PROCESSES=4
ITERATIONS=10

# Parse command line arguments
if [ $# -ge 1 ]; then
    PARALLEL_PROCESSES=$1
fi

if [ $# -ge 2 ]; then
    ITERATIONS=$2
fi

# Set paths
EDGECLOUDSIM_HOME="$(cd ../.. && pwd)"
LIB_DIR="$EDGECLOUDSIM_HOME/lib"
BIN_DIR="$EDGECLOUDSIM_HOME/bin"
CONFIG_DIR="$EDGECLOUDSIM_HOME/config/energy_aware_offloading"

# Configuration files
CONFIG_FILE="$CONFIG_DIR/config.properties"
EDGE_DEVICES_FILE="$CONFIG_DIR/edge_devices.xml"
APPLICATIONS_FILE="$CONFIG_DIR/applications.xml"

echo ""
echo "Configuration:"
echo "  Parallel Processes: $PARALLEL_PROCESSES"
echo "  Iterations per Policy: $ITERATIONS"
echo "  Config File: $CONFIG_FILE"
echo "  Edge Devices: $EDGE_DEVICES_FILE"
echo "  Applications: $APPLICATIONS_FILE"
echo ""

# Check if files exist
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    echo "Please create the configuration files first"
    exit 1
fi

if [ ! -d "$BIN_DIR" ]; then
    echo "Error: Binary directory not found. Please compile first!"
    echo "Run: ./compile.sh"
    exit 1
fi

# Build classpath
CLASSPATH="$BIN_DIR"
for jar in "$LIB_DIR"/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done

# Update config file with iteration count
echo "Updating configuration..."
sed -i.bak "s/^iteration_number=.*/iteration_number=$ITERATIONS/" "$CONFIG_FILE"

echo ""
echo "=================================================="
echo "Starting Simulation"
echo "=================================================="
echo ""

# Create logs directory
mkdir -p logs

# Run simulation
java -Xms2g -Xmx4g \
     -cp "$CLASSPATH" \
     edu.boun.edgecloudsim.applications.energy_aware_offloading.MainApp \
     "$CONFIG_FILE" \
     "$EDGE_DEVICES_FILE" \
     "$APPLICATIONS_FILE" \
     2>&1 | tee logs/simulation_$(date +%Y%m%d_%H%M%S).log

# Check execution result
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✓ Simulation completed successfully!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Extract results: cd sim_results && tar -xzf ite$ITERATIONS/*.tgz"
    echo "  2. Analyze results: python3 ../scripts/analyze_results.py"
    echo "  3. View generated graphs and summary report"
    echo ""
else
    echo ""
    echo "=================================================="
    echo "✗ Simulation failed!"
    echo "=================================================="
    echo ""
    echo "Check logs/simulation_*.log for error details"
    exit 1
fi

exit 0