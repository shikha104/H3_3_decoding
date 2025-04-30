import os
import pandas as pd

def process_csv(file_path):
    """
    Reads a CSV file, filters rows based on mu1 and mu2 conditions, processes them dynamically, and returns the filtered DataFrame.
    
    Parameters:
    file_path (str): Path to the CSV file.
    
    Returns:
    pd.DataFrame or None: Processed DataFrame if successful, None if an error occurs.
    """
    try:
        # Define data types for the expected columns
        dtypes = {
            "sequence": str,
            "source": str,
            "alpha1": float,
            "beta1": float,
            "alpha2": float,
            "beta2": float,
            "mu1": float,
            "mu2": float,
        }
        
        # Read the CSV file with specific columns and data types
        df = pd.read_csv(file_path, usecols=dtypes.keys(), dtype=dtypes)
        
        # Filter rows where mu1 and mu2 are between 0.5 and 0.6
        df_filtered = df[(df["mu1"] > 0.5) & (df["mu1"] < 0.6) & (df["mu2"] > 0.5) & (df["mu2"] < 0.6)]
        
        # Drop unnecessary columns
        df_filtered = df_filtered.drop(columns=["sequence", "alpha1", "beta1", "alpha2", "beta2"], errors='ignore')
        
        # Round mu1 and mu2 to one decimal place using floor rounding
        df_filtered["mu1"] = df_filtered["mu1"].apply(lambda x: (x * 10) // 1 / 10)
        df_filtered["mu2"] = df_filtered["mu2"].apply(lambda x: (x * 10) // 1 / 10)
        
        # Filter rows where mu1 is equal to mu2
        return df_filtered[df_filtered["mu1"] == df_filtered["mu2"]]
    except Exception as e:
        # Log errors in case of file processing failure
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error processing {file_path}: {e}\n")
        return None

def main():
    """
    Main function to process CSV files in a directory and dynamically filter the data without intermediate output.
    """
    input_dir = input("Enter the directory containing CSV files: ").strip()
    if not os.path.isdir(input_dir):
        print("Invalid directory. Please enter a valid path.")
        return
    
    final_output_file = input("Enter the output CSV file name: ").strip()
    
    # Get a list of all CSV files in the input directory
    csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".csv")]

    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame

    # Process each CSV file and combine results
    for file in csv_files:
        print(f"Processing: {file}")
        df_filtered = process_csv(file)
        if df_filtered is not None and not df_filtered.empty:
            combined_df = pd.concat([combined_df, df_filtered], ignore_index=True)
    
    if not combined_df.empty:
        # Save the final filtered data to a new CSV file
        combined_df.to_csv(final_output_file, index=False)
        print(f"Final filtered data saved to {final_output_file}")
    else:
        print("No sequences met the filtering criteria. No data saved.")

if __name__ == "__main__":
    main()

