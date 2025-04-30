import os
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

def generate_mother_sequence(alpha1, beta1, alpha2, beta2, mu1, mu2, n=1000):
    """
    Generate a mother sequence using transition probabilities for H3.1 and H3.3.
    - Starts with 1 from H3.1.
    - Uses one random number to decide H3.1 ↔ H3.3 transitions using mu1/mu2.
    - Uses another random number to decide 0s/1s using alpha/beta.

    :param alpha1: Probability that 1 is followed by 1 in H3.1.
    :param beta1: Probability that 0 is followed by 0 in H3.1.
    :param alpha2: Probability that 1 is followed by 1 in H3.3.
    :param beta2: Probability that 0 is followed by 0 in H3.3.
    :param mu1: Probability of staying in H3.1.
    :param mu2: Probability of staying in H3.3.
    :param n: Length of the mother sequence.
    :return: Tuple (mother_sequence, source) where:
             - mother_sequence contains 0s and 1s.
             - source is a boolean array (True for H3.1, False for H3.3).
    """
    mother_sequence = np.zeros(n, dtype=int)
    source = np.zeros(n, dtype=bool)

    # Start with 1 from H3.1
    mother_sequence[0] = 1
    source[0] = True  # True = H3.1, False = H3.3
    current_state = "H3.1"

    for i in range(1, n):
        # Generate a single random number for state transition
        transition_rand = np.random.random()

        # Decide if we stay in the current state or switch
        if current_state == "H3.1":
            source[i] = True
            current_state = "H3.1" if transition_rand <= mu1 else "H3.3"
        else:
            source[i] = False
            current_state = "H3.3" if transition_rand <= mu2 else "H3.1"

        # Generate another random number for sequence values
        sequence_rand = np.random.random()

        # Determine next value based on alpha/beta probabilities
        if mother_sequence[i - 1] == 1:
            mother_sequence[i] = 1 if sequence_rand <= (alpha1 if source[i] else alpha2) else 0
        else:
            mother_sequence[i] = 0 if sequence_rand <= (beta1 if source[i] else beta2) else 1

    return mother_sequence, source

def generate_daughter(mom, rho = 0.5):
    """
    This function generates a daughter sequence from a mother sequence.
    It randomly mutates a node with a 50% probability of flipping.
    :param mom: The mother sequence that is to be used.
    :param rho: The probablity that mutation occurs for a bit if a mutation is possible.
    :return: a numpy vector containing the sequence of the daughter.
    """
    daughter_sequence = np.copy(mom)
    for i in range(daughter_sequence.size):
        if daughter_sequence[i] == 1 and np.random.random() <= rho:
            daughter_sequence[i] = 0
    return daughter_sequence
    
def decode_H3_3(mother_sequence, daughter_sequence, source_sequence):
    """
    Restores `1`s in the daughter sequence that originated from H3.3 in the mother sequence
    and were flipped to `0`.

    :param mother_sequence: List or numpy array representing the mother sequence.
    :param daughter_sequence: List or numpy array representing the daughter sequence.
    :param source_sequence: List or numpy array indicating source of each bit (True for H3.1, False for H3.3).
    :return: Modified daughter sequence with restored `1`s from H3.3.
    """
    # Ensure inputs are numpy arrays for efficient processing
    mother_sequence = np.array(mother_sequence)
    decoded_h33 = daughter_sequence.copy()
    source_sequence = np.array(source_sequence)
    # Iterate through the sequences to restore H3.3 flipped bits
    for i in range(len(decoded_h33)):
        if not source_sequence[i]:  # Check if bit originates from H3.3
            if mother_sequence[i] == 1 and decoded_h33[i] == 0:  # If flipped, restore it
                decoded_h33[i] = 1
    return decoded_h33

def decode_zeros(num_interim_zeros, alpha1, beta1, alpha2, beta2, mu1, mu2, start_node=0, end_node=0, start_source=True, end_source=True):
    """
    Decodes a sequence of zero values based on transition probabilities and path metrics.

    Parameters:
    -----------
    num_interim_zeros : int
        The number of interim zero values to decode.
    alpha1, beta1 : float
        Transition probabilities for H3.1.
    alpha2, beta2 : float
        Transition probabilities for H3.3.
    mu1, mu2 : float
        Source probabilities affecting the transition decisions.
    start_node : int, optional
        The starting node (0 or 1).
    end_node : int, optional
        The ending node (0 or 1).
    start_source : bool, optional
        Indicates whether the start node comes from source H3.3 (True) or H3.1 (False).
    end_source : bool, optional
        Indicates whether the end node comes from source H3.3 (True) or H3.1 (False).

    Returns:
    --------
    decoded_sequence : ndarray
        A numpy array of decoded values (0s and 1s).

    Raises:
    -------
    ValueError
        If invalid start or end node values are provided.
    """
    
    branch_metric = np.zeros(4)
    
    """
    Branch Metrics Explanation:
    ---------------------------
    branch_metric[0] : Probability of transitioning from state 1 to 0 (yn=0, xn=0, xn-1=1)
                       Formula: mu1 * (1 - alpha1)
    branch_metric[1] : Probability of transitioning from state 1 to 1 (yn=0, xn=1, xn-1=1)
                       Formula: mu1 * alpha1 / 2
    branch_metric[2] : Probability of transitioning from state 0 to 0 (yn=0, xn=0, xn-1=0)
                       Formula: mu1 * beta1
    branch_metric[3] : Probability of transitioning from state 0 to 1 (yn=0, xn=1, xn-1=0)
                       Formula: (mu1 * (1 - beta1)) / 2
    """
    
    # Branch metrics based on transitions
    branch_metric[0] = (mu1 * (1 - alpha1))  # yn=0, xn=0, xn-1=1
    branch_metric[1] = mu1 * alpha1 / 2      # yn=0, xn=1, xn-1=1
    branch_metric[2] = mu1 * beta1           # yn=0, xn=0, xn-1=0
    branch_metric[3] = (mu1 * (1 - beta1)) / 2  # yn=0, xn=1, xn-1=0

    decoded_sequence = np.zeros(num_interim_zeros)

    """
    Node Path Metrics Explanation:
    ------------------------------
    node_path_metric_xn_0[q, 0] : Path metric for state 0 at step q.
    node_path_metric_xn_1[q, 0] : Path metric for state 1 at step q.
    node_path_metric_xn_0[q, 1] : Previous state leading to state 0 at step q.
    node_path_metric_xn_1[q, 1] : Previous state leading to state 1 at step q.
    """

    # Path metrics initialization
    node_path_metric_xn_0 = np.zeros((num_interim_zeros + 1, 2))
    node_path_metric_xn_1 = np.zeros((num_interim_zeros + 1, 2))

    for q in range(0, num_interim_zeros + 1):
        if q == 0:
            # Initialization for start node
            if start_node == 1 and start_source == True:
                node_path_metric_xn_0[q, 0] = branch_metric[0]  # 1 -> 0
                node_path_metric_xn_1[q, 0] = branch_metric[1]  # 1 -> 1
                node_path_metric_xn_0[q, 1] = 1
                node_path_metric_xn_1[q, 1] = 1
            elif start_node == 1 and start_source == False:
                node_path_metric_xn_0[q, 0] = (1 - alpha1) * (1 - mu2)  # 1 -> 0
                node_path_metric_xn_1[q, 0] = (alpha1 / 2) * (1 - mu2)  # 1 -> 1
                node_path_metric_xn_0[q, 1] = 1
                node_path_metric_xn_1[q, 1] = 1
            elif start_node == 0 and start_source == False:
                node_path_metric_xn_0[q, 0] = ((1 - mu2) * beta1)  # 0 -> 0
                node_path_metric_xn_1[q, 0] = ((1 - beta1) * (1 - mu2)) / 2  # 0 -> 1
                node_path_metric_xn_0[q, 1] = 0
                node_path_metric_xn_1[q, 1] = 0
            else:
                raise ValueError("Start Node Error")
        elif q>0:
            # Calculate path metrics for q > 0
            path_metric_1_0 = node_path_metric_xn_1[q - 1, 0] * (mu1 * ( 1 - alpha1))  # 1 -> 0
            path_metric_0_0 = node_path_metric_xn_0[q - 1, 0] * (mu1 * beta1)  # 0 -> 0

            if path_metric_1_0 > path_metric_0_0:
                node_path_metric_xn_0[q, 0] = path_metric_1_0
                node_path_metric_xn_0[q, 1] = 1
            else:
                node_path_metric_xn_0[q, 0] = path_metric_0_0
                node_path_metric_xn_0[q, 1] = 0

            path_metric_0_1 = node_path_metric_xn_0[q - 1, 0] * branch_metric[3]  # 0 -> 1
            path_metric_1_1 = node_path_metric_xn_1[q - 1, 0] * branch_metric[1]  # 1 -> 1

            if path_metric_1_1 > path_metric_0_1:
                node_path_metric_xn_1[q, 0] = path_metric_1_1
                node_path_metric_xn_1[q, 1] = 1
            else:
                node_path_metric_xn_1[q, 0] = path_metric_0_1
                node_path_metric_xn_1[q, 1] = 0

    if end_node == 1 and end_source == True:
        # Transition to node 1 with source H3.3
        path_metric_1_1 = node_path_metric_xn_1[num_interim_zeros - 1, 0] * mu1 * (alpha1 / 2)
        path_metric_0_1 = node_path_metric_xn_0[num_interim_zeros - 1, 0] * mu1 * ((1 - beta1) / 2)

        # Decide if last interim zero flips to 1
        if path_metric_1_1 > path_metric_0_1:
            decoded_sequence[num_interim_zeros - 1] = 1
        else:
            decoded_sequence[num_interim_zeros - 1] = 0

    elif end_node == 1 and end_source == False:
        # Transition to node 1 with source H3.1
        path_metric_1_1 = node_path_metric_xn_1[num_interim_zeros - 1, 0] * alpha2 * (1 - mu1)
        path_metric_0_1 = node_path_metric_xn_0[num_interim_zeros - 1, 0] * (1 - beta2) * (1 - mu1)

        # Decide if last interim zero flips to 1
        if path_metric_1_1 > path_metric_0_1:
            decoded_sequence[num_interim_zeros - 1] = 1
        else:
            decoded_sequence[num_interim_zeros - 1] = 0

    elif end_node == 0 and end_source == False:
        # Transition to node 0 with source H3.1
        path_metric_1_0 = node_path_metric_xn_1[num_interim_zeros - 1, 0] * (1 - alpha2) * (1 - mu1)
        path_metric_0_0 = node_path_metric_xn_0[num_interim_zeros - 1, 0] * (1 - mu1) * beta2

        # Decide if last interim zero remains 0
        if path_metric_1_0 > path_metric_0_0:
            decoded_sequence[num_interim_zeros - 1] = 1
        else:
            decoded_sequence[num_interim_zeros - 1] = 0

    else:
        raise ValueError("End Node Error")

    # Backtracking to decode the sequence
    for q in range(num_interim_zeros - 1, 0, -1):
        if decoded_sequence[q] == 0:
            decoded_sequence[q - 1] = node_path_metric_xn_0[q, 1]
        elif decoded_sequence[q] == 1:
            decoded_sequence[q - 1] = node_path_metric_xn_1[q, 1]

    return decoded_sequence

def viterbi_decode(decoded_h33, source, alpha1, beta1, alpha2, beta2, mu1, mu2):
    """
    Decodes zeros in the input sequence based on specific conditions and updates them.

    Parameters:
        decoded_h33 (list[int]): Input sequence with values to decode.
        source (list[bool]): Boolean values indicating valid positions for decoding.
        alpha1, beta1, alpha2, beta2, mu1, mu2: Parameters for the decode_zeros function.

    Returns:
        list[int]: Corrected sequence with decoded zeros.
    """
    corrected_sequence = []
    i = 0

    while i < len(decoded_h33):
        if decoded_h33[i] == 0 and source[i]:  # Check for valid zero stretches
            count = 0
            start_index = i

            # Count zeros in the stretch
            while i < len(decoded_h33) and decoded_h33[i] == 0 and source[i]:
                count += 1
                i += 1

            # Ensure there's a valid stretch and enough context for border transitions
            start_node = decoded_h33[start_index - 1] if start_index > 0 else None
            end_index = i  # Index after the last zero in the stretch
            end_node = decoded_h33[end_index] if end_index < len(decoded_h33) else None

            start_source = source[start_index - 1] if start_index > 0 else True
            end_source = source[end_index] if end_index < len(decoded_h33) else True

            # Condition: Start or end node can't be zero if source[i] is True
            if (start_node == 0 and start_source) or (end_node == 0 and end_source):
                # Keep zeros if either border node is zero and source is True
                corrected_sequence.extend([0] * count)
            elif start_node is None or end_node is None:
                # If either border is missing, keep zeros as they are
                corrected_sequence.extend([0] * count)
            elif not ((start_node == 1 and end_node == 1) or
                      (not start_source and not end_source) or
                      (start_node == 0 and end_node == 0) or
                      (not start_source and end_source) or
                      (start_source and not end_source)):
                # If the border conditions are not met, keep zeros as they are
                corrected_sequence.extend([0] * count)
            else:
                # If conditions are met, decode the stretch
                try:
                    decoded_zeros = decode_zeros(
                        num_interim_zeros=count,
                        alpha1=alpha1,
                        beta1=beta1,
                        alpha2=alpha2,
                        beta2=beta2,
                        mu1=mu1,
                        mu2=mu2,
                        start_node=start_node,
                        end_node=end_node,
                        start_source=start_source,
                        end_source=end_source
                    )
                    corrected_sequence.extend(decoded_zeros.astype(int))
                except ValueError as e:
                    # Handle errors from decode_zeros gracefully
                    print(f"Error during decoding: {e}. Keeping original stretch of zeros.")
                    corrected_sequence.extend([0] * count)
        else:
            # Non-zero or zeros with source[i] == False are kept as they are
            corrected_sequence.append(decoded_h33[i])
            i += 1

    return corrected_sequence

def calculate_biterror(seq1, seq2):
    if len(seq1) != len(seq2):
        raise ValueError("Sequences must be of the same length.")
    seq1, seq2 = np.array(seq1), np.array(seq2)
    xor = np.logical_xor(seq1, seq2).astype(int)
    biterror = np.sum(xor) / len(seq1)
    return biterror

class Dataframe:
    """
    Represents a dataframe for one simulation with a single mother sequence.
    Stores the mother sequence, source sequence, multiple corrupted daughters,
    decoded daughters, Viterbi-decoded daughters, and bit error rates.
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
        self.viterbi_daughter_list = np.zeros((n_daughters, mom_length))
        self.biterror_list = np.zeros(n_daughters)

        # Generate daughters
        for j in range(n_daughters):
            self.corrupt_daughter_list[j] = generate_daughter(self.mother_sequence, self.rho)

    def perform_decoding(self):
        """Perform decoding on corrupted daughters."""
        for j in range(self.n_daughters):
            # Decode using decode_H3_3
            self.decoded_daughter_list[j] = decode_H3_3(
                self.mother_sequence,
                self.corrupt_daughter_list[j],
                self.source_sequence
            )

            # Perform Viterbi decoding on the decoded daughter
            self.viterbi_daughter_list[j] = viterbi_decode(
                self.decoded_daughter_list[j],
                self.source_sequence,
                alpha1=self.alpha1,
                alpha2=self.alpha2,
                beta1=self.beta1,
                beta2=self.beta2,
                mu1=self.mu1,
                mu2=self.mu2
            )

    def calc_biterror(self):
        """Calculate bit error rates between mother and Viterbi-decoded daughters."""
        for j in range(self.n_daughters):
            self.biterror_list[j] = calculate_biterror(
                self.mother_sequence, self.viterbi_daughter_list[j]
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
        np.savetxt(f"{dir_name}/Mother_Sequences.csv", self.mom_list, delimiter=',', fmt='%d')
        np.savetxt(f"{dir_name}/Source_Sequences.csv", self.source_list.astype(int), delimiter=',', fmt='%d')
        np.savetxt(f"{dir_name}/Corrupted_Daughters.csv", self.corrupt_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{dir_name}/Decoded_Daughters.csv", self.decoded_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{dir_name}/Viterbi_Daughters.csv", self.viterbi_daughter_list, delimiter=',', fmt='%d')
        np.savetxt(f"{dir_name}/BitError_Mom_Viterbi.csv", self.biterror_list, delimiter=',')

        # Display summary
        if level > 0:
            print(f"Alpha1 = {self.alpha1}, Alpha2 = {self.alpha2}")
            print(f"Beta1 = {self.beta1}, Beta2 = {self.beta2}")
            print(f"Mu1 = {self.mu1}, Mu2 = {self.mu2}")
            print(f"Average BitError (Mom vs Corrected Daughters): {np.mean(self.biterror_list):.4f}")

            if level >= 2:
                print(f"BitError (Mom vs Viterbi): {self.biterror_list}")

                if level >= 3:
                    print("\nMother Sequence")
                    print(self.mother_sequence)
                    print("\nCorrupted Daughter Sequences")
                    print(self.corrupt_daughter_list)
                    print("\nDecoded Daughter Sequences")
                    print(self.decoded_daughter_list)
                    print("\nViterbi-Decoded Daughter Sequences")
                    print(self.viterbi_daughter_list)

        return 0

def run_sim(sim_id, seed, alpha1, alpha2, beta1, beta2, mu1, mu2, rho, n_samples, seq_length, verbose_level=0):
    """
    Runs the simulation with the given parameters.

    :param sim_id: A Unique ID(string) so that no 2 sims replace the dirs created by the other unless specified.
    :param seed: Random seed for reproducibility.
    :param alpha1: The probability that the next element node in the sequence is 1 given that the current node is 1 in H3.1.
    :param alpha2: The probability that the next element node in the sequence is 1 given that the current node is 1 in H3.3.
    :param beta1: The probability that the next element node in the sequence is 0 given that the current node is 0 in H3.1.
    :param beta2: The probability that the next element node in the sequence is 0 given that the current node is 0 in H3.3.
    :param mu1: The probability of staying in H3.1.
    :param mu2: The probability of staying in H3.3.
    :param rho: The probability that a mutation pushes the node to 0.
    :param n_samples: The number of samples used for training.
    :param seq_length: The length of the sequences.
    :param verbose_level: The level of verbosity during the run.
    
    :return: The name of the simulation and the bit error rate after testing for the selected alpha and beta values.
    """
    np.random.seed(seed)
    
    # Directory for results
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define ranges for alpha2 and beta2
    alpha1_range = np.round(np.arange(0.10, 1.00, 0.10), 2)
    beta1_range = np.round(np.arange(0.10, 1.00, 0.10), 2)
    
    # Fixed values for alpha1 and beta1
    alpha2_fixed = alpha1
    beta2_fixed = beta1
    
    # List to store the results
    results = []
    
    for alpha1 in alpha1_range:
        for beta1 in beta1_range:
            all_bit_errors = []
            
            for mother_idx in range(n_samples):
                sim_instance_id = f"{sim_id}_A2_{alpha2}_B2_{beta2}_mother_{mother_idx}"
                
                # Create and run the simulation
                data = Dataframe(
                    alpha1=alpha1,
                    alpha2=alpha2_fixed,
                    beta1=beta1,
                    beta2=beta2_fixed,
                    mu1=mu1,
                    mu2=mu2,
                    rho=rho,
                    mom_length=seq_length
                )
                
                data.perform_decoding()
                data.calc_biterror()
                
                all_bit_errors.extend(data.biterror_list)
            
            # Compute and store average bit error rate
            avg_bit_error_rate = np.mean(all_bit_errors)
            results.append((alpha2, beta2, avg_bit_error_rate))
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results, columns=['Alpha1', 'Beta1', 'Average Bit Error Rate'])
    
    if verbose_level > 0:
        print(f"Simulation '{sim_id}' completed.")
    
    return results_df

