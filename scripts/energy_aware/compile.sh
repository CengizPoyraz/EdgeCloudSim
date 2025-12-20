#!/bin/bash

# Compile the Energy-Aware Task Offloading simulation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../.."

echo "Compiling EdgeCloudSim with Energy-Aware scenario..."

cd "$PROJECT_DIR"

# Create output directory for compiled classes
mkdir -p out

# Find all Java source files
SOURCES=$(find src -name "*.java")

# Find all JAR files in lib directory
CLASSPATH=""
for jar in lib/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done
CLASSPATH="${CLASSPATH:1}"  # Remove leading colon

# Compile
echo "Compiling Java sources..."
javac -d out -cp "$CLASSPATH" $SOURCES

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
else
    echo "Compilation failed!"
    exit 1
fi
