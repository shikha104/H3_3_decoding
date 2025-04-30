import time
import argparse
import os
import numpy as np
import pandas as pd
from Variant_sim import run_sim

"""
To run on command line give the file name with input parameters.
for example:  python3 run_code.py   --batch_name "TestBatch" --alpha1_eval "[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]"   --beta1_eval "[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]" --alpha2 0.2 --beta2 0.2  --mu1 0.6   --mu2 0.4   --rho 0.5   --seed 42   --n_samples 10   --seq_length 100   --verbose_level 5
"""

def main():
    """
    Runs batch simulations for variant modeling using given parameters and stores the results in a CSV file.
    
    Parses command-line arguments to configure simulation parameters, iterates over combinations of alpha1 and beta1,
    executes the simulation, computes the average bit error rate, and logs the results.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run batch simulations for variant modeling")
    parser.add_argument('--batch_name', type=str, required=True, help='Name of the batch')
    parser.add_argument('--alpha1_eval', type=str, required=True, help='String to evaluate as the alpha1 list')
    parser.add_argument('--beta1_eval', type=str, required=True, help='String to evaluate as the beta1 list')
    parser.add_argument('--alpha2', type=float, required=True, help='Alpha2 value for H3.3')
    parser.add_argument('--beta2', type=float, required=True, help='Beta2 value for H3.3')
    parser.add_argument('--mu1', type=float, required=True, help='Mu1 value for H3.1')
    parser.add_argument('--mu2', type=float, required=True, help='Mu2 value for H3.3')
    parser.add_argument('--rho', type=float, default=0.5, help='Rho value for the simulation')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--n_samples', type=int, default=10000, help='Number of samples')
    parser.add_argument('--seq_length', type=int, default=100, help='Sequence length')
    parser.add_argument('--verbose_level', type=int, default=5, help='Verbose level')
    
    args = parser.parse_args()
    
    full_start = time.time()
    
    # Extract arguments
    batch_name = args.batch_name
    alpha1_eval = args.alpha1_eval
    beta1_eval = args.beta1_eval
    alpha2 = args.alpha2
    beta2 = args.beta2
    mu1 = args.mu1
    mu2 = args.mu2
    rho = args.rho
    seed = args.seed
    n_samples = args.n_samples
    seq_length = args.seq_length
    verbose_level = args.verbose_level
    
    # Convert evaluated strings into lists
    a1_list = eval(alpha1_eval)
    b1_list = eval(beta1_eval)
    
    # Create results directory if it doesn't exist
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Prepare output file
    output_file = os.path.join(results_dir, f'{batch_name}_BitError_Combinations.csv')
    with open(output_file, 'w') as f:
        f.write('Alpha1,Beta1,Average_Bit_Error_Rate\n')
    
    # Run simulations
    for alpha1 in a1_list:
        for beta1 in b1_list:
            sim_start = time.time()
            results_df = run_sim(
                sim_id=batch_name,
                seed=seed,
                alpha1=round(alpha1, 1),
                alpha2=alpha2,
                beta1=round(beta1, 1),
                beta2=beta2,
                mu1=mu1,
                mu2=mu2,
                rho=rho,
                n_samples=n_samples,
                seq_length=seq_length,
                verbose_level=verbose_level
            )
            sim_end = time.time()
            
            # Compute average bit error rate
            avg_bit_error = results_df['Average_Bit_Error_Rate'].mean()
            print(f"Alpha -- {alpha1}, Beta -- {beta1} --- Execution Time = {round(sim_end - sim_start, 4)} --- BitError = {Average_Bit_Error_Rate}")

            
            # Append results to CSV
            with open(output_file, 'a') as f:
                f.write(f'{round(alpha1, 1)},{round(beta1, 1)},{Average_Bit_Error_Rate}\n')
    
    # Log execution time
    full_end = time.time()
    print(f"Total Execution time = {round(full_end - full_start, 4)} seconds")
    
    log_file = os.path.join(results_dir, f'{batch_name}_Batch_Log.txt')
    with open(log_file, 'w') as f:
        f.write(f'Log File - Batch Simulation :: {batch_name}\n')
        f.write(f"Total Execution time = {round(full_end - full_start, 4)} seconds\n\n")
        f.write(f'##INPUTS##\n')
        f.write(f'alpha2 = {alpha2}\n')
        f.write(f'beta2 = {beta2}\n')
        f.write(f'alpha1_eval = {alpha1_eval}\n')
        f.write(f'beta1_eval = {beta1_eval}\n')
        f.write(f'mu1 = {mu1}\n')
        f.write(f'mu2 = {mu2}\n')
        f.write(f'rho = {rho}\n')
        f.write(f'n_samples = {n_samples}\n')
        f.write(f'seq_length = {seq_length}\n')
        f.write(f'verbose_level = {verbose_level}\n')

if __name__ == "__main__":
    main()

