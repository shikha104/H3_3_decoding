import argparse
import os
import pandas as pd
from k6_fill import run_sim as run_sim_k6
from k_threshold import run_sim as run_sim_k_threshold

def main():
    parser = argparse.ArgumentParser(description="Run H3 simulation with varying alpha1 and beta1.")
    parser.add_argument("--sim_id", type=str, required=True, help="Simulation ID for output files.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--rho", type=float, required=True, help="Rho parameter.")
    parser.add_argument("--n_samples", type=int, default=100, help="Number of mother sequences.")
    parser.add_argument("--seq_length", type=int, default=1000, help="Length of sequences.")
    parser.add_argument("--verbose", type=int, default=1, help="Verbosity level (0-3).")
    parser.add_argument("--method", type=str, choices=["k6_fill", "k_threshold"], required=True, help="Method to use for simulation.")
    
    args = parser.parse_args()
    
    alpha2 = beta2 = mu1 = mu2 = 0.9  # Fixed values
    
    os.makedirs("results", exist_ok=True)
    all_results = []
    
    run_sim = run_sim_k6 if args.method == "k6_fill" else run_sim_k_threshold
    
    for alpha1 in [round(x, 1) for x in list(range(1, 10))]:
        alpha1 /= 10
        for beta1 in [round(x, 1) for x in list(range(1, 10))]:
            beta1 /= 10
            sim_id = f"{args.sim_id}_A1_{alpha1}_B1_{beta1}"
            
            results_df = run_sim(
                sim_id=sim_id,
                seed=args.seed,
                alpha1=alpha1,
                alpha2=alpha2,
                beta1=beta1,
                beta2=beta2,
                mu1=mu1,
                mu2=mu2,
                rho=args.rho,
                n_samples=args.n_samples,
                seq_length=args.seq_length,
                verbose_level=args.verbose
            )
            
            results_df["alpha1"] = alpha1
            results_df["beta1"] = beta1
            all_results.append(results_df)
    
    final_results = pd.concat(all_results, ignore_index=True)
    
    # Modify the output file name to include the chosen method
    output_file = f"results/{args.sim_id}_{args.method}_varying_A1_B1_results.csv"
    final_results.to_csv(output_file, index=False)
    
    if args.verbose > 0:
        print("Results saved to:", output_file)

if __name__ == "__main__":
    main()

