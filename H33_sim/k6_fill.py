import time
import argparse
import os
import numpy as np
import pandas as pd
from Variant_sim import generate_mother_sequence, generate_daughter, decode_H3_3, calculate_biterror

def k_fill(decoded_sequence, source_sequence):
    """
    Corrects a daughter sequence by filling stretches of zeros belonging to H3.1.
    Stretches must:
        - Be bordered by `1`s (from H3.1 or H3.3).
        - Contain ≤ 6 zeros.
        - Not include zeros belonging to H3.3.
        - Have both borders present (e.g., no edge-only borders like `1000`).

    Parameters:
        decoded_sequence (list): Sequence to correct (list of 0s and 1s).
        source_sequence (list): Boolean list indicating source regions (True = H3.1, False = H3.3).

    Returns:
        corrected_sequence (list): Corrected version of the daughter sequence.
    """
    corrected_sequence = decoded_sequence[:]
    n = len(corrected_sequence)

    i = 0
    while i < n:
        if corrected_sequence[i] == 0:
            # Find the start and end of the zero stretch
            start = i
            while i < n and corrected_sequence[i] == 0:
                i += 1
            end = i - 1

            # Check if stretch meets criteria
            if (
                (end - start + 1 <= 6)  # Zeros count ≤ 6
                and start > 0 and end < n - 1  # Bordered on both sides
                and corrected_sequence[start - 1] == 1 and corrected_sequence[end + 1] == 1  # Both sides must be `1`
                and all(source_sequence[j] for j in range(start, end + 1))  # Zeros must belong to H3.1
            ):
                # Apply the correction: change zeros to ones
                corrected_sequence[start:end + 1] = [1] * (end - start + 1)
        else:
            i += 1

    return corrected_sequence

class Dataframe:
    """
    Represents a dataframe for one simulation with a single mother sequence.
    Stores the mother sequence, source sequence, multiple corrupted daughters,
    decoded daughters, k-filled daughters, and bit error rates.
    """

    def __init__(self, alpha1, alpha2, beta1, beta2, mu1, mu2, rho, mom_length, n_daughters=100):
        self.alpha1 = alpha1
        self.alpha2 = alpha2
        self.beta1 = beta1
        self.beta2 = beta2
        self.mu1 = mu1
        self.mu2 = mu2
        self.rho = rho
        self.n_daughters = n_daughters

        # Initialize arrays for single mother and multiple daughters
        self.mother_sequence, self.source_sequence = generate_mother_sequence(
            alpha1=self.alpha1,
            alpha2=self.alpha2,
            beta1=self.beta1,
            beta2=self.beta2,
            mu1=self.mu1,
            mu2=self.mu2,
            n=mom_length
        )
        self.mom_list = np.zeros((1, mom_length))  # Single mother
        self.source_list = np.zeros((1, mom_length), dtype=bool)  # Single source        
        self.corrupt_daughter_list = np.zeros((n_daughters, mom_length))
        self.decoded_daughter_list = np.zeros((n_daughters, mom_length))
        self.kfill_daughter_list = np.zeros((n_daughters, mom_length))  # K-filled daughters
        self.biterror_list = np.zeros(n_daughters)

        # Generate corrupted daughters
        for j in range(n_daughters):
            self.corrupt_daughter_list[j] = generate_daughter(self.mother_sequence, self.rho)

    def perform_kfill(self):
        """Perform decoding on corrupted daughters and apply k-fill correction."""
        for j in range(self.n_daughters):
            # Decode using decode_H3_3
            self.decoded_daughter_list[j] = decode_H3_3(
                self.mother_sequence,
                self.corrupt_daughter_list[j],
                self.source_sequence
            )

            # Apply k-fill correction to the decoded daughter
            self.kfill_daughter_list[j] = k_fill(self.decoded_daughter_list[j], self.source_sequence)

    def calc_biterror(self):
        """Calculate bit error rates between mother and k-filled daughters."""
        for j in range(self.n_daughters):
            self.biterror_list[j] = calculate_biterror(
                self.mother_sequence, self.kfill_daughter_list[j]
            )

    def conclusions(self, sim_name='Untitled_Sim', level=3):
        """
        Generate a summary of the simulation and save results to files.
        :param sim_name: Name of the simulation for output files.
        :param level: Verbosity level for summary.
        """
        # Perform decoding and error calculation
        self.perform_decoding()
        self.calc_biterror()

        # Save the results
        np.savetxt(f"{sim_name}/Mother_Sequences.csv", self.mom_list, delimiter=',', fmt='%d')
        np.savetxt(f"{sim_name}/Source_Sequences.csv", self.source_list.astype(int), delimiter=',', fmt='%d')
        np.savetxt(f"{sim_name}/Corrupted_Daughters.csv", self.corrupt_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{sim_name}/Decoded_Daughters.csv", self.decoded_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{sim_name}/KFill_Daughters.csv", self.kfill_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{sim_name}/BitError_Mom_KFill.csv", self.biterror_list, delimiter=',')

        # Display summary
        if level > 0:
            print(f"Alpha1 = {self.alpha1}, Alpha2 = {self.alpha2}")
            print(f"Beta1 = {self.beta1}, Beta2 = {self.beta2}")
            print(f"Mu1 = {self.mu1}, Mu2 = {self.mu2}")
            print(f"Average BitError (Mom vs K-Filled Daughters): {np.mean(self.biterror_list):.4f}")

            if level >= 2:
                print(f"BitError (Mom vs K-Fill): {self.biterror_list}")

                if level >= 3:
                    print("\nMother Sequence")
                    print(self.mother_sequence)
                    print("\nCorrupted Daughter Sequences")
                    print(self.corrupt_daughter_list)
                    print("\nDecoded Daughter Sequences")
                    print(self.decoded_daughter_list)
                    print("\nK-Filled Daughter Sequences")
                    print(self.kfill_daughter_list)

        return 0

def run_sim(sim_id, seed, alpha1, alpha2, beta1, beta2, mu1, mu2, rho, n_samples, seq_length, verbose_level=0):
    """
    Runs the simulation with the given parameters.

    :param sim_id: A Unique ID (string) so that no two sims replace each other's directories unless specified.
    :param seed: Random seed for reproducibility.
    :param alpha1: Probability that the next node is 1 given that the current node is 1 in H3.1.
    :param alpha2: Probability that the next node is 1 given that the current node is 1 in H3.3.
    :param beta1: Probability that the next node is 0 given that the current node is 0 in H3.1.
    :param beta2: Probability that the next node is 0 given that the current node is 0 in H3.3.
    :param mu1: Probability of staying in H3.1.
    :param mu2: Probability of staying in H3.3.
    :param rho: Probability that a mutation pushes the node to 0.
    :param n_samples: Number of samples used for training.
    :param seq_length: Length of the sequences.
    :param verbose_level: Level of verbosity during the run.
    :return: The name of the simulation and the bit error rate after testing.
    """
    np.random.seed(seed)
    os.makedirs("results", exist_ok=True)
    
    all_bit_errors = []
    
    for mother_idx in range(n_samples):
        sim_instance_id = f"{sim_id}_A1_{alpha1}_B1_{beta1}_A2_{alpha2}_B2_{beta2}_mother_{mother_idx}"
        
        # Create and run the simulation
        data = Dataframe(
            alpha1=alpha1,
            alpha2=alpha2,
            beta1=beta1,
            beta2=beta2,
            mu1=mu1,
            mu2=mu2,
            rho=rho,
            mom_length=seq_length
        )
        
        data.perform_kfill()
        data.calc_biterror()
        
        all_bit_errors.extend(data.biterror_list)
    
    # Compute average bit error rate
    avg_bit_error_rate = np.mean(all_bit_errors)
    results_df = pd.DataFrame([(alpha1, beta1, alpha2, beta2, avg_bit_error_rate)],
                               columns=['Alpha1', 'Beta1', 'Alpha2', 'Beta2', 'Average Bit Error Rate'])
    
    if verbose_level > 0:
        print(f"Simulation '{sim_id}' completed.")
    
    return results_df

