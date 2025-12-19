#!/bin/bash

##############################################################
# EdgeCloudSim Energy-Aware Offloading Compilation Script
##############################################################

echo "=========================================="
echo "Compiling Energy-Aware Offloading Project"
echo "=========================================="

# Set paths
EDGECLOUDSIM_HOME="$(cd ../.. && pwd)"
LIB_DIR="$EDGECLOUDSIM_HOME/lib"
SRC_DIR="$EDGECLOUDSIM_HOME/src"
BIN_DIR="$EDGECLOUDSIM_HOME/bin"

# Check if directories exist
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Source directory not found at $SRC_DIR"
    exit 1
fi

if [ ! -d "$LIB_DIR" ]; then
    echo "Error: Library directory not found at $LIB_DIR"
    exit 1
fi

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

echo ""
echo "Configuration:"
echo "  EdgeCloudSim Home: $EDGECLOUDSIM_HOME"
echo "  Source Directory: $SRC_DIR"
echo "  Library Directory: $LIB_DIR"
echo "  Binary Directory: $BIN_DIR"
echo ""

# Build classpath
CLASSPATH="$BIN_DIR"
for jar in "$LIB_DIR"/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done

echo "Building classpath..."
echo "  Classpath: $CLASSPATH"
echo ""

# Compile Java files
echo "Compiling Java source files..."
echo ""

# Find all Java files
JAVA_FILES=$(find "$SRC_DIR" -name "*.java")
FILE_COUNT=$(echo "$JAVA_FILES" | wc -l)

echo "Found $FILE_COUNT Java files to compile"
echo ""

# Compile
javac -d "$BIN_DIR" -cp "$CLASSPATH" -sourcepath "$SRC_DIR" $JAVA_FILES

# Check compilation result
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Compilation successful!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Run simulations: ./run_simulations.sh"
    echo "  2. Or use IDE to run MainApp.java"
    echo ""
    exit 0
else
    echo ""
    echo "=========================================="
    echo "✗ Compilation failed!"
    echo "=========================================="
    echo ""
    echo "Please check error messages above"
    exit 1
fi