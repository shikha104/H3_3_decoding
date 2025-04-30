import pandas as pd
import numpy as np
import ast  # To safely convert string representation of a list to an actual list
from joblib import Parallel, delayed

def generate_mother_sequence(alpha, beta, n=1000):
    """
    Generate a mother sequence using only alpha and beta probabilities.
    - Starts with 1.
    - Uses alpha for P(1 → 1) and beta for P(0 → 0).

    :param alpha: Probability that 1 is followed by 1.
    :param beta: Probability that 0 is followed by 0.
    :param n: Length of the mother sequence.
    :return: NumPy array containing the mother sequence.
    """
    mother_sequence = np.zeros(n, dtype=int)
    mother_sequence[0] = 1  # Start with 1

    for i in range(1, n):
        sequence_rand = np.random.random()
        if mother_sequence[i - 1] == 1:
            mother_sequence[i] = 1 if sequence_rand <= alpha else 0
        else:
            mother_sequence[i] = 0 if sequence_rand <= beta else 1

    return mother_sequence  # Ensure output is a NumPy array
    
    
def generate_daughter(mother_sequence, rho=0.5):
    daughter_sequence = np.copy(mother_sequence)  # Ensure it's initialized
    print(f"Type of daughter_sequence: {type(daughter_sequence)}")
    
    for i in range(len(daughter_sequence)):  # This should now work
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
    branch_metric = np.zeros(4)
    # Branch metrics based on transitions
    branch_metric[0] = (mu1 * (1 - alpha1))  # yn=0, xn=0, xn-1=1
    branch_metric[1] = mu1 * alpha1 / 2      # yn=0, xn=1, xn-1=1
    branch_metric[2] = mu1 * beta1           # yn=0, xn=0, xn-1=0
    branch_metric[3] = (mu1 * (1 - beta1)) / 2  # yn=0, xn=1, xn-1=0

    decoded_sequence = np.zeros(num_interim_zeros)

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


# Load input CSV file
input_csv = "/home/group_nithya01/Desktop/Shikha_project/expt/filtered_output_07.csv"  # Update with actual file path
df = pd.read_csv(input_csv)

# Initialize a variable to store total bit errors
total_bit_error = 0
num_sequences = len(df)

# Initialize list to store results
results = []

# Process each sequence
for index, row in df.iterrows():
    print(f"Processing Sequence {index + 1}/{len(df)}")

    # Convert source column from string to a boolean array, handling None values
    if pd.notna(row["source"]):  # Check if source is not NaN
        source_sequence = ast.literal_eval(row["source"])  # Convert string list to Python list
        source_sequence = [s.lower() == "true" for s in source_sequence if s is not None]  # Remove None values
    else:
        source_sequence = []  # Set an empty list if source is NaN

    # Ensure source_sequence is not empty before proceeding
    if not source_sequence:
        print(f"Skipping sequence {index + 1} due to empty source sequence.")
        continue

    # Determine sequence length dynamically
    sequence_length = len(source_sequence)
    print(f"Sequence length: {sequence_length}")

    # Generate mother sequence dynamically
    alpha, beta = 0.9, 0.9
    mother_sequence = generate_mother_sequence(alpha, beta, sequence_length)

    # Extract other values
    alpha1, alpha2 = alpha, alpha
    beta1, beta2 = beta, beta
    mu1, mu2 = row["mu1"], row["mu2"]

    # Step 2: Generate a daughter sequence
    daughter_sequence = generate_daughter(mother_sequence, rho=0.5)

    # Step 3: Decode the daughter sequence
    decoded_daughter = decode_H3_3(mother_sequence, daughter_sequence, source_sequence)

    # Step 4: Correct the decoded sequence
    corrected_sequence = viterbi_decode(
        decoded_daughter, source_sequence, alpha1, beta1, alpha2, beta2, mu1, mu2
    )

    # Step 5: Calculate bit error
    bit_error = calculate_biterror(mother_sequence, corrected_sequence)

    # Store result in a list
    results.append({
        "alpha1": alpha1,
        "beta1": beta1,
        "alpha2": alpha2,
        "beta2": beta2,
        "mu1": mu1,
        "mu2": mu2,
        "bit_error": bit_error
    })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
output_csv = "bit_errors_07.csv"
results_df.to_csv(output_csv, index=False)

print(f"Results saved to {output_csv}")
