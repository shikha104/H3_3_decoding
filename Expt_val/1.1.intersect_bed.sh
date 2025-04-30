#!/bin/bash

# This script splits a BED file into multiple smaller BED files, each covering 5MB regions.
# It processes an input BED file and groups entries based on chromosome and 5MB window boundaries.
# Each output file is named based on the original filename and the region index.

input_file="/home/shikha/expt_val/h3k27me/SRR227472.bed"  # Change this to your actual input file

awk -v filename="${input_file%.bed}" '
BEGIN {
    # Initialize variables
    region_start = -1;
    region_end = -1;
    prev_chr = "";
    region_count = 0;
}
{
    # If this is the first line or a new chromosome, start a new region
    if (region_start == -1 || $1 != prev_chr) {
        region_start = $2;
        region_end = region_start + 5000000;  # Define the 5MB window
        prev_chr = $1;
        region_count++;
    }

    # If the entry is within the current 5MB window and same chromosome, append to the file
    if ($3 <= region_end && $1 == prev_chr) {
        print $0 >> (filename "_" region_count ".bed");
    } else {
        # If out of range OR new chromosome, start a new region
        region_count++;
        region_start = $2;
        region_end = region_start + 5000000;
        prev_chr = $1;
        
        print $0 >> (filename "_" region_count ".bed");
    }
}
' "$input_file"
