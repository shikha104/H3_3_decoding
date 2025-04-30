import os
import glob
import pandas as pd

def update_h3_columns(input_directory, output_directory):
    """
    Updates H3.1 and H3.3 values in CSV files based on neighboring values within a sliding window.
    
    If both H3.1 and H3.3 are zero at a given row, the function looks at a window of 20 rows before 
    and 20 rows after (total 41 rows including the current row). The column with the higher sum 
    within this window determines which value (H3.1 or H3.3) to set to 1.

    Parameters:
        input_directory (str): Path to the directory containing input CSV files.
        output_directory (str): Path to the directory where updated CSV files will be saved.
    """
    os.makedirs(output_directory, exist_ok=True)  # Create output directory if it doesn't exist
    csv_files = glob.glob(os.path.join(input_directory, "*.csv"))  # Get all CSV files in input directory
    
    for file in csv_files:
        df = pd.read_csv(file, sep=',')
        
        for i in range(len(df)):
            # If both H3.1 and H3.3 are 0, check the surrounding 20 rows in each direction
            if df.at[i, 'H3.1'] == 0 and df.at[i, 'H3.3'] == 0:
                start_idx = max(0, i - 20)  # Ensure index does not go below 0
                end_idx = min(len(df), i + 21)  # Ensure index does not exceed dataframe length
                
                h3_1_count = df.iloc[start_idx:end_idx]['H3.1'].sum()
                h3_3_count = df.iloc[start_idx:end_idx]['H3.3'].sum()
                
                # Assign 1 to the column with the higher sum within the window
                if h3_1_count > h3_3_count:
                    df.at[i, 'H3.1'] = 1
                elif h3_3_count > h3_1_count:
                    df.at[i, 'H3.3'] = 1
        
        # Save updated CSV file
        output_file = os.path.join(output_directory, os.path.basename(file).replace(".csv", "_updated.csv"))
        df.to_csv(output_file, sep=',', index=False)
        print(f"Processed file: {file}")

if __name__ == "__main__":
    # Get input and output directories from user
    input_directory = input("Enter the input directory path: ").strip()
    output_directory = input("Enter the output directory path: ").strip()
    
    update_h3_columns(input_directory, output_directory)
