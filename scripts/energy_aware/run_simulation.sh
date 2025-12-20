#!/bin/bash

# Run Energy-Aware Task Offloading simulation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../.."
CONFIG_DIR="$SCRIPT_DIR/config"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Number of simulation iterations (for statistical significance)
ITERATIONS=${1:-3}

echo "Running Energy-Aware Task Offloading Simulation"
echo "================================================"
echo "Iterations: $ITERATIONS"
echo "Output Directory: $OUTPUT_DIR"

cd "$PROJECT_DIR"

# Build classpath
CLASSPATH="out"
for jar in lib/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run simulations
for ((i=1; i<=ITERATIONS; i++)); do
    echo ""
    echo "Running iteration $i of $ITERATIONS..."
    
    java -cp "$CLASSPATH" edu.boun.edgecloudsim.applications.energy_aware_scenario.MainApp \
        "$CONFIG_DIR/default_config.properties" \
        "$CONFIG_DIR/edge_devices.xml" \
        "$CONFIG_DIR/applications.xml" \
        "$OUTPUT_DIR" \
        $i
    
    if [ $? -ne 0 ]; then
        echo "Simulation iteration $i failed!"
        exit 1
    fi
done

echo ""
echo "All simulations completed successfully!"
echo "Results saved to: $OUTPUT_DIR"
