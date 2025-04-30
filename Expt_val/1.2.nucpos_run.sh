#!/bin/bash

# This script runs the NucPosSimulator on all .bed files in the specified input directory.
# It uses GNU Parallel to process multiple files concurrently, utilizing up to 15 CPU cores.

# Check if the input directory is provided
if [[ -z $1 ]]; then
    echo "Usage: $0 <input_directory>"
    exit 1
fi

# Set the input directory containing the .bed files
input_dir=$1

# Set the path to the NucPosSimulator directory (Update this path if necessary)
nucpossimulator_dir="/home/shikha/NucPosSimulator_linux64/"

# Ensure write permissions for the input directory and subdirectories
chmod -R u+w "$input_dir"

# Export variables and define the function for parallel execution
export nucpossimulator_dir

# Function to run NucPosSimulator on a given .bed file
run_simulator() {
    local bed_file="$1"  # Get the .bed file name
    local bed_file_abs
    bed_file_abs=$(realpath "$bed_file")  # Get the absolute path of the .bed file

    # Navigate to the NucPosSimulator directory
    cd "$nucpossimulator_dir" || exit 1

    # Run NucPosSimulator on the .bed file using the params.txt configuration
    ./NucPosSimulator "$bed_file_abs" "params.txt"

    # Check if the NucPosSimulator ran successfully
    if [[ $? -ne 0 ]]; then
        echo "Error: NucPosSimulator failed for '$bed_file_abs'."
    else
        echo "NucPosSimulator ran successfully for '$bed_file_abs'."
    fi
}

# Export the function for use with GNU Parallel
export -f run_simulator

# Display the number of CPU cores being used
echo "Using 15 CPU cores for parallel execution."

# Find all .bed files in the input directory and its subdirectories
bed_files=$(find "$input_dir" -type f -name "*.bed")

# Use GNU Parallel to process the .bed files with a maximum of 15 concurrent jobs
echo "$bed_files" | parallel --jobs 15 --bar run_simulator {}

echo "Processing complete."
