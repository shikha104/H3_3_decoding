import os
import pandas as pd
import glob

def process_bed_files(input_directory, output_directory):
    """
    Processes BED files from the input directory, bins the genomic coordinates into 200bp intervals,
    and saves the processed data to the output directory.
    
    Parameters:
    input_directory (str): Path to the directory containing input .bed.result.bed files.
    output_directory (str): Path to the directory where processed CSV files will be saved.
    """
    # Check if the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist.")
        return
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Iterate over all .bed.result.bed files in the input directory
    for file in glob.glob(os.path.join(input_directory, "*.bed.result.bed")):
        df = pd.read_csv(file, sep="\t", header=None, names=["chromosome", "start", "end"])
        
        # Skip empty files
        if df.empty:
            print(f"Skipping empty file: {file}")
            continue
        
        # Determine the binning range (rounded to the nearest 200bp)
        start_min = (df["start"].min() // 200) * 200
        end_max = ((df["end"].max() + 9) // 200) * 200
        
        chromosome = df.iloc[0, 0]  # Extract chromosome name
        bins = list(range(start_min, end_max + 1, 200))  # Create bins of 200bp intervals
        
        # Create a DataFrame with bins and initialize H3.3 column to 0
        bin_df = pd.DataFrame({
            "chromosome": chromosome, 
            "start": bins, 
            "end": [x + 200 for x in bins],
            "H3.3": 0
        })
        
        # Function to check if any start coordinate falls within a bin range
        def mark_h3(start, end):
            return 1 if ((df["start"] >= start) & (df["start"] < end)).any() else 0
        
        # Apply the function to each bin
        bin_df["H3.3"] = bin_df.apply(lambda row: mark_h3(row["start"], row["end"]), axis=1)
        
        # Generate output file path and save processed data as CSV
        output_file = os.path.join(output_directory, os.path.basename(file).replace(".bed.result.bed", "_processed.csv"))
        bin_df.to_csv(output_file, index=False)
        
        print(f"Processed: {file} -> {output_file}")

if __name__ == "__main__":
    # Get user input for directories
    input_directory = input("Enter the input directory path: ").strip()
    output_directory = input("Enter the output directory path: ").strip()
    
    # Run the processing function
    process_bed_files(input_directory, output_directory)
