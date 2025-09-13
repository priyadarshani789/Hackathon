# Goal: Create a function to calculate a compliance score based on a list of findings.
#
# Instructions:
# 1. Create a single function `calculate_score(findings: list) -> int:`.
# 2. Inside the function, define the severity weights as a dictionary: `weights = {"Critical": 3, "Major": 2, "Minor": 1}`.
# 3. Initialize a `total_penalty` variable to 0.
# 4. Loop through the input `findings` list.
# 5. For each finding dictionary, get its 'severity' and add the corresponding weight from the dictionary to `total_penalty`.
# 6. After the loop, calculate the final score using the formula: `score = max(0, 100 - total_penalty)`. This ensures the score cannot be negative.
# 7. Return the final integer score.

def calculate_score(findings: list) -> int:
    """
    Calculates a compliance score from 0 to 100 based on a list of findings.
    
    Args:
        findings (list): List of finding dictionaries, each containing a 'severity' key
    
    Returns:
        int: Compliance score from 0 to 100 (higher is better)
    """
    # Define severity weights
    weights = {"Critical": 3, "Major": 2, "Minor": 1}
    
    # Initialize total penalty
    total_penalty = 0
    
    # Loop through findings and accumulate penalties
    for finding in findings:
        severity = finding.get('severity', 'Minor')  # Default to 'Minor' if severity not found
        penalty = weights.get(severity, 1)  # Default to 1 if severity not in weights
        total_penalty += penalty
    
    # Calculate final score (ensure it's not negative)
    score = max(0, 100 - total_penalty)
    
    return score
