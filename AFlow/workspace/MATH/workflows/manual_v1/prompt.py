MATH_SOLVER_INSTRUCTIONS = [
    """You are solving a competition math problem.
Write a clear derivation, avoid skipping algebra, and end with a final answer in \\boxed{...}.

Problem:
""",
    """Solve the following math problem using an independent approach.
Check definitions, constraints, and edge cases. End with a final answer in \\boxed{...}.

Problem:
""",
    """Find the answer to the math problem. Use calculation or symbolic reasoning when helpful.
After solving, verify the result and end with a final answer in \\boxed{...}.

Problem:
""",
]

FINALIZE_INSTRUCTION = """You are given a math problem and a candidate solution.
Rewrite only the final cleaned solution. Preserve the correct reasoning and make the final answer easy to extract.
The final line must contain exactly one answer wrapped as \\boxed{...}.

Problem and candidate solution:
"""
