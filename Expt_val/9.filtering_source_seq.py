import os
import pandas as pd

def process_csv(file_path):
    """
    Reads a CSV file, filters rows based on mu1 and mu2 conditions, and returns the filtered DataFrame.
    
    Conditions:
    - mu1 must be between 0.5 and 0.6 (exclusive)
    - mu2 must be between 0.5 and 0.6 (exclusive)
    """
    try:
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
        df = pd.read_csv(file_path, usecols=dtypes.keys(), dtype=dtypes)
        df_filtered = df[(df["mu1"] > 0.5) & (df["mu1"] < 0.6) & (df["mu2"] > 0.5) & (df["mu2"] < 0.6)]
        return df_filtered
    except Exception as e:
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error processing {file_path}: {e}\n")
        return None

def main():
    """
    Prompts the user for input and output file paths, processes CSV files, filters data,
    and saves the final results to an output file.
    """
    input_dir = input("Enter the input directory path: ").strip()
    output_file = input("Enter the intermediate output file name: ").strip()
    final_output_file = input("Enter the final output file name: ").strip()
    
    csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".csv")]
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    first_write = not os.path.exists(output_file)
    data_saved = False
    
    for file in csv_files:
        print(f"Processing: {file}")
        df_filtered = process_csv(file)
        if df_filtered is not None and not df_filtered.empty:
            df_filtered.to_csv(output_file, mode="a", index=False, header=first_write)
            first_write = False
            data_saved = True
    
    if data_saved:
        print(f"Filtered data saved to {output_file}")
    else:
        print("No sequences met the filtering criteria. No data saved.")
        return
    
    # Load the intermediate CSV file
    df = pd.read_csv(output_file)
    
    # Drop unnecessary columns
    df = df.drop(columns=["sequence", "alpha1", "beta1", "alpha2", "beta2"], errors='ignore')
    
    # Round mu1 and mu2 to one decimal place (floor rounding)
    df["mu1"] = df["mu1"].apply(lambda x: (x * 10) // 1 / 10)
    df["mu2"] = df["mu2"].apply(lambda x: (x * 10) // 1 / 10)
    
    # Filter rows where mu1 == mu2
    filtered_df = df[df["mu1"] == df["mu2"]]
    
    # Save to final output CSV
    filtered_df.to_csv(final_output_file, index=False)
    print(f"Final filtered data saved to {final_output_file}")

if __name__ == "__main__":
    main()
