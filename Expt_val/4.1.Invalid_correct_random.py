import pandas as pd
import numpy as np
import os

# Define input and output directories
input_dir = "update_mod"  # Directory containing input CSV files
output_dir = "random_s_files"  # Directory to save modified CSV files
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Process all CSV files in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith(".csv"):  # Only process CSV files
        input_path = os.path.join(input_dir, file_name)
        output_path = os.path.join(output_dir, file_name)
        
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(input_path, sep=",")
        
        # Iterate through the dataframe and randomly modify H3.1 and H3.3 columns
        for index, row in df.iterrows():
            # If both H3.1 and H3.3 are 1, randomly set one to 0
            if row['H3.1'] == 1 and row['H3.3'] == 1:
                if np.random.rand() <= 0.5:
                    df.at[index, 'H3.3'] = 0  # Set H3.3 to 0 with 50% probability
                else:
                    df.at[index, 'H3.1'] = 0  # Otherwise, set H3.1 to 0
        
        # Save the modified dataframe to a new CSV file
        df.to_csv(output_path, sep=",", index=False)
