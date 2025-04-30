import os
import pandas as pd

def update_h3_3_column(h3_1_dir: str, h3_3_dir: str, output_dir: str):
    """
    Updates H3.1 processed CSV files by adding the corresponding H3.3 values from matching files.
    
    Parameters:
    h3_1_dir (str): Directory containing H3.1 processed CSV files.
    h3_3_dir (str): Directory containing H3.3 processed CSV files.
    output_dir (str): Directory to save the updated CSV files.
    """
    # Get all relevant CSV files from both directories
    h3_1_files = [f for f in os.listdir(h3_1_dir) if f.startswith('ERR2675342') and f.endswith('_processed.csv')]
    h3_3_files = [f for f in os.listdir(h3_3_dir) if f.startswith('ERR2675347') and f.endswith('_processed.csv')]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for h3_1_file in h3_1_files:
        # Find the corresponding H3.3 file
        matching_h3_3_file = h3_1_file.replace('ERR2675342', 'ERR2675347')

        if matching_h3_3_file in h3_3_files:
            h3_1_path = os.path.join(h3_1_dir, h3_1_file)
            h3_3_path = os.path.join(h3_3_dir, matching_h3_3_file)

            try:
                # Load CSVs into pandas DataFrames
                df_h3_1 = pd.read_csv(h3_1_path)
                df_h3_3 = pd.read_csv(h3_3_path)

                # Strip spaces from column names to avoid mismatches
                df_h3_1.columns = df_h3_1.columns.str.strip()
                df_h3_3.columns = df_h3_3.columns.str.strip()

                # Rename last column in H3.3 file if it is incorrectly labeled
                if 'H3.3' not in df_h3_3.columns:
                    df_h3_3.rename(columns={df_h3_3.columns[-1]: 'H3.3'}, inplace=True)

                # Ensure required columns exist in both DataFrames
                required_columns_h3_1 = {'chromosome', 'start', 'end', 'H3.1'}
                required_columns_h3_3 = {'chromosome', 'start', 'end', 'H3.3'}

                if not required_columns_h3_1.issubset(df_h3_1.columns) or not required_columns_h3_3.issubset(df_h3_3.columns):
                    print(f'Skipping {h3_1_file} due to missing columns.')
                    continue

                # Merge data from H3.3 into H3.1 based on chromosome, start, and end columns
                df_new = df_h3_1.merge(df_h3_3[['chromosome', 'start', 'end', 'H3.3']], 
                                       on=['chromosome', 'start', 'end'], 
                                       how='left')

                # Fill missing H3.3 values with 0 and ensure integer type
                df_new['H3.3'] = df_new['H3.3'].fillna(0).astype(int)

                # Save the updated CSV file to the output directory
                output_path = os.path.join(output_dir, f'updated_{h3_1_file}')
                df_new.to_csv(output_path, index=False)
                print(f'Saved updated file: {output_path}')

            except Exception as e:
                print(f"Error processing {h3_1_file}: {e}")

if __name__ == '__main__':
    # Get user input for directory paths
    h3_1_directory = input("Enter the path for H3.1 directory: ").strip()
    h3_3_directory = input("Enter the path for H3.3 directory: ").strip()
    output_directory = input("Enter the output directory path: ").strip()
    
    # Run the function
    update_h3_3_column(h3_1_directory, h3_3_directory, output_directory)
