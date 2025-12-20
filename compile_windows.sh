#!/bin/bash
cd c:\\PROJECTS\\Git\\EdgeCloudSim

# Create out directory if it doesn't exist
mkdir -p out

# Build classpath
CLASSPATH=""
for jar in lib/*.jar; do
    CLASSPATH="$CLASSPATH;$jar"
done
CLASSPATH="${CLASSPATH:1}"

echo "Compiling with classpath: $CLASSPATH"

# Get all Java files
SOURCES=""
for file in $(find src -name "*.java"); do
    SOURCES="$SOURCES $file"
done

echo "Compiling sources..."
c:/DEV/Java/jdk-25/bin/javac.exe -d out -cp "$CLASSPATH" $SOURCES

echo "Compilation done!"
