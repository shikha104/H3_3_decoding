import os
import pandas as pd
import numpy as np

def process_csv(file_path, output_dir, window_size=7):
    """
    Processes a CSV file by applying a sliding window median-based correction to the H3.1 and H3.3 columns.
    
    Parameters:
        file_path (str): Path to the input CSV file.
        output_dir (str): Path to the directory where the processed file will be saved.
        window_size (int, optional): Size of the sliding window. Default is 7.
    """
    df = pd.read_csv(file_path, sep=',')
    
    # Apply the sliding window correction
    for i in range(len(df) - window_size + 1):
        window = df.iloc[i:i+window_size]
        
        # Process H3.1 column
        median_val = np.median(window['H3.1'].drop(index=i))  # Exclude current row
        if df.at[i, 'H3.1'] == 1 and median_val == 0:
            df.at[i, 'H3.1'] = 0
        elif df.at[i, 'H3.1'] == 0 and median_val == 1:
            df.at[i, 'H3.1'] = 1
        
        # Process H3.3 column
        median_val = np.median(window['H3.3'].drop(index=i))  # Exclude current row
        if df.at[i, 'H3.3'] == 1 and median_val == 0:
            df.at[i, 'H3.3'] = 0
        elif df.at[i, 'H3.3'] == 0 and median_val == 1:
            df.at[i, 'H3.3'] = 1
    
    # Save the processed CSV file
    output_file = os.path.join(output_dir, os.path.basename(file_path))
    df.to_csv(output_file, sep=',', index=False)
    print(f"Processed: {file_path} -> {output_file}")

def process_directory():
    """
    Prompts the user for input and output directories and processes all CSV files in the input directory.
    """
    # Get user input for directories
    input_dir = input("Enter the input directory path: ").strip()
    output_dir = input("Enter the output directory path: ").strip()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each CSV file in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_dir, file_name)
            process_csv(file_path, output_dir)

# Run the script
if __name__ == "__main__":
    process_directory()
