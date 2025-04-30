import os
import pandas as pd
import ast
from joblib import Parallel, delayed

def count_transitions(lst, condition1, source1, condition2, source2):
    """
    Counts the number of transitions between specified conditions in a list.
    
    Args:
        lst (list): List of boolean values representing source states.
        condition1 (bool): First condition to check.
        source1 (list): Boolean list indicating the source1 values.
        condition2 (bool): Second condition to check.
        source2 (list): Boolean list indicating the source2 values.
    
    Returns:
        int: Count of transitions from condition1 to condition2.
    """
    return sum(1 for i in range(len(lst) - 1) 
               if lst[i] == condition1 and source1[i] == True 
               and lst[i + 1] == condition2 and source2[i + 1] == True)

def calculate_metrics(source):
    """
    Calculates transition probabilities based on the given source sequence.
    
    Args:
        source (list): List of 'true' or 'false' values representing source states.
    
    Returns:
        tuple: Computed values of mu1 and mu2 representing transition probabilities.
    """
    source = [s == 'true' for s in source]  # Convert 'true'/'false' to boolean
    total_trues = sum(source)
    total_falses = len(source) - total_trues

    mu1 = sum(1 for i in range(len(source) - 1) if source[i] and source[i + 1]) / total_trues if total_trues != 0 else 0
    mu2 = sum(1 for i in range(len(source) - 1) if not source[i] and not source[i + 1]) / total_falses if total_falses != 0 else 0
    
    return mu1, mu2

def process_file(file_path):
    """
    Processes a single CSV file by computing transition probabilities and updating the file.
    
    Args:
        file_path (str): Path to the CSV file.
    """
    df = pd.read_csv(file_path)
    df['source'] = df['source'].apply(ast.literal_eval)  # Convert string representation of list to actual list
    
    # Apply the transition metric calculation
    results = df['source'].apply(calculate_metrics)
    df[['mu1', 'mu2']] = pd.DataFrame(results.tolist(), index=df.index)
    
    # Save the updated file
    df.to_csv(file_path, index=False)
    print(f"Updated {file_path}")

def process_csv_files(input_directory, num_cores=8):
    """
    Processes all CSV files in the given directory using parallel processing.
    
    Args:
        input_directory (str): Path to the directory containing CSV files.
        num_cores (int, optional): Number of CPU cores to use. Default is 8.
    """
    files = [os.path.join(input_directory, file) for file in os.listdir(input_directory) if file.endswith(".csv")]
    
    # Parallel processing of files
    Parallel(n_jobs=num_cores)(delayed(process_file)(file) for file in files)

if __name__ == "__main__":
    input_dir = input("Enter the input directory path: ").strip()
    num_cores = int(input("Enter the number of cores to use (default is 8): ") or 8)
    process_csv_files(input_dir, num_cores)
