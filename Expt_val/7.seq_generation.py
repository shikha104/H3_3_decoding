import pandas as pd
import os

def process_csv():
    """
    Processes CSV files from an input directory, extracts a sliding window of size 1000,
    generates a 'source_sequence' based on H3.1 and H3.3 values, and saves the results
    with chromosome information in an output directory.
    """
    
    # Prompt user for input and output directories
    input_dir = input("Enter the input directory: ")
    output_dir = input("Enter the output directory: ")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Iterate through all CSV files in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_dir, file_name)
            df = pd.read_csv(file_path, sep=',')  # Read CSV file into DataFrame
            window_size = 1000  # Define sliding window size
            results = []  # Initialize list to store processed data
            
            # Iterate through the DataFrame with a sliding window approach
            for start_idx in range(len(df) - window_size + 1):
                window = df.iloc[start_idx:start_idx + window_size]
                chromosome = window['chromosome'].iloc[0]  # Assume chromosome remains constant within a window

                # Generate 'source_sequence' based on H3.1 and H3.3 values, skipping invalid rows
                source_sequence = [
                    'true' if h3_1 == 1 and h3_3 == 0 else 'false' if h3_3 == 1 and h3_1 == 0 else None
                    for h3_1, h3_3 in zip(window['H3.1'], window['H3.3'])
                    if not (h3_1 == 0 and h3_3 == 0)  # Skip rows where both H3.1 and H3.3 are zero
                ]
                
                # Append valid results
                if source_sequence:
                    results.append({'chromosome': chromosome, 'Source': source_sequence})
            
            # Save results if there is valid data
            if results:
                result_df = pd.DataFrame(results)
                output_file = os.path.join(output_dir, f"filtered_{file_name}")
                result_df.to_csv(output_file, index=False)  # Save processed data to CSV

# Run the processing function
process_csv()
