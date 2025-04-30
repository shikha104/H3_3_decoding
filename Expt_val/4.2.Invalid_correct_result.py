import pandas as pd
import os
import re

def update_h3_values():
    """
    Updates H3.1 and H3.3 values in processed CSV files based on comparison with
    corresponding .bed.result.bed files. If both H3.1 and H3.3 are 1, the script compares
    start positions from the original files and updates the values accordingly.
    
    The function prompts the user to input:
    - The directory containing processed CSV files.
    - The directories for H3.1 and H3.3 .bed.result.bed files.
    - The output directory to save the modified CSV files.
    """
    
    # Get user inputs for directory paths
    processed_dir = input("Enter processed directory path: ").strip()
    dir_h31 = input("Enter H3.1 directory path: ").strip()
    dir_h33 = input("Enter H3.3 directory path: ").strip()
    output_dir = input("Enter output directory path: ").strip()
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of processed CSV files
    processed_files = [f for f in os.listdir(processed_dir) if f.endswith("_processed.csv")]
    
    for processed_file in processed_files:
        print(f"Processing: {processed_file}")
        
        # Extract identifier from filename
        match = re.search(r'ERR\d+_\d+', processed_file)
        if not match:
            continue
        identifier = match.group()
        
        # Define file paths
        processed_csv = os.path.join(processed_dir, processed_file)
        output_csv = os.path.join(output_dir, processed_file)
        
        # Locate corresponding H3.1 and H3.3 files
        file_h31 = next((os.path.join(dir_h31, f) for f in os.listdir(dir_h31) 
                         if f.startswith(identifier) and f.endswith(".bed.result.bed")), None)
        file_h33 = next((os.path.join(dir_h33, f) for f in os.listdir(dir_h33) 
                         if f.startswith(identifier.replace("ERR2675342", "ERR2675347")) and f.endswith(".bed.result.bed")), None)
        
        # Skip if corresponding files are missing
        if not file_h31 or not file_h33:
            continue
        
        # Load processed CSV file
        df_processed = pd.read_csv(processed_csv, sep=',')
        df = df_processed.copy()
        
        # Identify rows where both H3.1 and H3.3 are 1
        condition = (df_processed['H3.1'] == 1) & (df_processed['H3.3'] == 1)
        rows_to_check = df_processed[condition]
        
        # Load H3.1 and H3.3 .bed files
        df_h31 = pd.read_csv(file_h31, sep='\t', header=None, names=['chr', 'start', 'end'])
        df_h33 = pd.read_csv(file_h33, sep='\t', header=None, names=['chr', 'start', 'end'])
        
        # Update H3.1 and H3.3 values based on start positions
        for (idx, row_csv), (idx_h31, row_h31), (idx_h33, row_h33) in zip(rows_to_check.iterrows(), df_h31.iterrows(), df_h33.iterrows()):
            start, end = row_csv['start'], row_csv['end']
            
            h31_start = row_h31['start']
            h33_start = row_h33['start']
            
            mask = (df['start'] == start) & (df['end'] == end)
            
            if h31_start > h33_start:
                df.loc[mask, 'H3.3'] = 0  # Set H3.3 to 0 if H3.1 starts later
            elif h33_start > h31_start:
                df.loc[mask, 'H3.1'] = 0  # Set H3.1 to 0 if H3.3 starts later
            else:
                print(f"No update needed for start={start}, end={end} (Both start values are the same)")
        
        # Save the updated DataFrame to a new CSV file
        df.to_csv(output_csv, sep=',', index=False)

# Run the function
update_h3_values()
